"""
Writes a record to query_audit after every NL query execution.
"""
from __future__ import annotations
from api.db.connection import get_conn


def log_query(
    *,
    user_id: str,
    user_role: str,
    question: str,
    generated_sql: str,
    row_count: int | None,
    execution_ms: int | None,
    chart_type: str | None,
) -> None:
    sql = """
        INSERT INTO query_audit
            (user_id, user_role, question, generated_sql, row_count, execution_ms, chart_type)
        VALUES
            (%(user_id)s, %(user_role)s, %(question)s, %(generated_sql)s,
             %(row_count)s, %(execution_ms)s, %(chart_type)s)
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, {
                "user_id": user_id,
                "user_role": user_role,
                "question": question,
                "generated_sql": generated_sql,
                "row_count": row_count,
                "execution_ms": execution_ms,
                "chart_type": chart_type,
            })
