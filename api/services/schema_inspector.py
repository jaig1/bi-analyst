"""
Introspects the live Neon database and returns a structured schema context string
that is injected into the text-to-SQL system prompt.

Includes:
  - Table + column names, data types, nullable flags
  - Primary and foreign key relationships
  - View definitions (vw_*)
  - Business glossary for SMB retail domain terms
  - Three few-shot example Q → SQL pairs
"""
from api.db.connection import get_conn

# Business-specific terminology to include in every prompt
BUSINESS_GLOSSARY = """
Business Glossary (use these definitions when interpreting questions):
- "revenue"       → SUM(order_items.quantity * order_items.unit_price) for completed orders
- "cost"          → SUM(order_items.quantity * order_items.unit_cost)
- "gross profit"  → revenue - cost
- "margin" / "margin %" → (gross_profit / revenue) * 100
- "top products"  → ranked by revenue or units_sold descending
- "churned" / "not reordered" → customers whose last order was more than N days ago
- "last quarter"  → the most recently completed calendar quarter
- "active customers" → customers with at least one completed order in the last 90 days
- "region"        → one of: North, South, East, West
- "segment"       → one of: SMB, Enterprise, Consumer
""".strip()

FEW_SHOT_EXAMPLES = """
Example Q&A pairs:

Q: What were my top 5 products last quarter by revenue?
SQL:
SELECT
    p.name AS product_name,
    SUM(oi.quantity * oi.unit_price) AS revenue
FROM order_items oi
JOIN orders o ON o.id = oi.order_id
JOIN products p ON p.id = oi.product_id
WHERE o.status = 'completed'
  AND o.ordered_at >= date_trunc('quarter', now() - interval '3 months')
  AND o.ordered_at <  date_trunc('quarter', now())
GROUP BY p.name
ORDER BY revenue DESC
LIMIT 5;

Q: Which customers haven't reordered in 90 days?
SQL:
SELECT
    c.name AS customer_name,
    c.email,
    c.region,
    MAX(o.ordered_at) AS last_order_at,
    EXTRACT(DAY FROM now() - MAX(o.ordered_at)) AS days_since_last_order
FROM customers c
JOIN orders o ON o.customer_id = c.id AND o.status = 'completed'
GROUP BY c.id, c.name, c.email, c.region
HAVING MAX(o.ordered_at) < now() - interval '90 days'
ORDER BY last_order_at ASC;

Q: Where are we losing margin? Show margin by category.
SQL:
SELECT
    cat.name AS category,
    SUM(oi.quantity * oi.unit_price) AS revenue,
    SUM(oi.quantity * oi.unit_cost)  AS cost,
    ROUND(
        100.0 * SUM(oi.quantity * (oi.unit_price - oi.unit_cost))
              / NULLIF(SUM(oi.quantity * oi.unit_price), 0), 2
    ) AS margin_pct
FROM order_items oi
JOIN orders o   ON o.id = oi.order_id AND o.status = 'completed'
JOIN products p ON p.id = oi.product_id
JOIN categories cat ON cat.id = p.category_id
GROUP BY cat.name
ORDER BY margin_pct ASC;
""".strip()


def build_schema_context() -> str:
    """
    Introspect the database and return a prompt-ready schema context string.
    """
    tables = _get_tables()
    views = _get_views()

    lines = ["DATABASE SCHEMA\n" + "=" * 60]

    for table in tables:
        lines.append(f"\nTable: {table['name']}")
        for col in table["columns"]:
            nullable = "" if col["nullable"] else " NOT NULL"
            pk = " [PK]" if col["is_pk"] else ""
            fk = f" → {col['fk_table']}.{col['fk_col']}" if col.get("fk_table") else ""
            lines.append(f"  {col['name']:30s} {col['type']}{nullable}{pk}{fk}")

    if views:
        lines.append("\n\nVIEWS (pre-built aggregations, prefer these when applicable)")
        for v in views:
            lines.append(f"  {v}")

    lines.append("\n\n" + BUSINESS_GLOSSARY)
    lines.append("\n\n" + FEW_SHOT_EXAMPLES)

    return "\n".join(lines)


def _get_tables() -> list[dict]:
    """Return table names with column metadata and FK relationships."""
    query = """
        SELECT
            c.table_name,
            c.column_name,
            c.data_type,
            c.is_nullable,
            CASE WHEN pk.column_name IS NOT NULL THEN TRUE ELSE FALSE END AS is_pk,
            fk.foreign_table_name,
            fk.foreign_column_name
        FROM information_schema.columns c
        LEFT JOIN (
            SELECT ku.table_name, ku.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage ku
                ON tc.constraint_name = ku.constraint_name
                AND tc.table_schema = ku.table_schema
            WHERE tc.constraint_type = 'PRIMARY KEY'
              AND tc.table_schema = 'public'
        ) pk ON pk.table_name = c.table_name AND pk.column_name = c.column_name
        LEFT JOIN (
            SELECT
                kcu.table_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage ccu
                ON ccu.constraint_name = tc.constraint_name
                AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
              AND tc.table_schema = 'public'
        ) fk ON fk.table_name = c.table_name AND fk.column_name = c.column_name
        WHERE c.table_schema = 'public'
          AND c.table_name NOT LIKE 'vw_%'
          AND c.table_name NOT IN ('_prisma_migrations')
        ORDER BY c.table_name, c.ordinal_position;
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()

    tables: dict[str, dict] = {}
    for row in rows:
        name = row["table_name"]
        if name not in tables:
            tables[name] = {"name": name, "columns": []}
        tables[name]["columns"].append({
            "name": row["column_name"],
            "type": row["data_type"],
            "nullable": row["is_nullable"] == "YES",
            "is_pk": row["is_pk"],
            "fk_table": row["foreign_table_name"],
            "fk_col": row["foreign_column_name"],
        })

    return list(tables.values())


def _get_views() -> list[str]:
    """Return names of views that start with vw_."""
    query = """
        SELECT table_name FROM information_schema.views
        WHERE table_schema = 'public' AND table_name LIKE 'vw_%'
        ORDER BY table_name;
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            return [row["table_name"] for row in cur.fetchall()]
