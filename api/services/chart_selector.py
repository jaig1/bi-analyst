from __future__ import annotations
"""
Automatically selects the most appropriate chart type based on the shape and
content of the query result set.

Returns:
  chart_type: "bar" | "line" | "pie" | "kpi" | "table"
  x_key:      column name for labels / X-axis (None for KPI)
  y_keys:     list of column names for numeric series
"""
import re

# Column name patterns that strongly suggest a time series
_DATE_PATTERN = re.compile(
    r"(date|month|week|day|year|quarter|period|time|at|_on)$",
    re.IGNORECASE,
)

_NUMERIC_TYPES = (int, float)


def select(rows: list[dict]) -> tuple[str, str | None, list[str]]:
    """
    Analyse *rows* and return (chart_type, x_key, y_keys).
    Falls back to "table" when no appropriate visualisation is found.
    """
    if not rows:
        return "table", None, []

    columns = list(rows[0].keys())
    numeric_cols = [c for c in columns if _is_numeric(rows, c)]
    categorical_cols = [c for c in columns if c not in numeric_cols]

    # ── KPI: single numeric value ──────────────────────────────────────────
    if len(columns) == 1 and len(numeric_cols) == 1 and len(rows) == 1:
        return "kpi", None, numeric_cols

    # ── KPI: single row, a few labelled numbers ────────────────────────────
    if len(rows) == 1 and len(numeric_cols) >= 1 and len(categorical_cols) == 0:
        return "kpi", None, numeric_cols

    # ── Line: first categorical column looks like a date/time ─────────────
    if categorical_cols and _DATE_PATTERN.search(categorical_cols[0]) and numeric_cols:
        return "line", categorical_cols[0], numeric_cols

    # ── Pie: exactly 1 categorical + 1 numeric, ≤ 12 rows, values sum nicely
    if (
        len(categorical_cols) == 1
        and len(numeric_cols) == 1
        and 2 <= len(rows) <= 12
        and _looks_like_share(rows, numeric_cols[0])
    ):
        return "pie", categorical_cols[0], numeric_cols

    # ── Bar: 1 categorical + 1-3 numeric columns, ≤ 25 rows ───────────────
    if categorical_cols and numeric_cols and len(rows) <= 25:
        return "bar", categorical_cols[0], numeric_cols[:3]

    # ── Default: table ─────────────────────────────────────────────────────
    return "table", columns[0] if columns else None, numeric_cols


def _is_numeric(rows: list[dict], col: str) -> bool:
    """Return True if the majority of non-None values in *col* are numeric."""
    values = [row[col] for row in rows if row[col] is not None]
    if not values:
        return False
    numeric_count = sum(1 for v in values if isinstance(v, _NUMERIC_TYPES))
    return numeric_count / len(values) >= 0.8


def _looks_like_share(rows: list[dict], col: str) -> bool:
    """
    Heuristic: if values are percentages (0-100) or if they sum to roughly
    100 or to a common total, a pie chart makes sense.
    """
    values = [row[col] for row in rows if isinstance(row[col], _NUMERIC_TYPES)]
    if not values:
        return False
    total = sum(values)
    # Already percentages
    if all(0 <= v <= 100 for v in values) and 95 <= total <= 105:
        return True
    # Proportional parts that sum to a meaningful total
    return total > 0
