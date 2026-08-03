from __future__ import annotations
"""
Executes a validated SELECT query against the Neon database and returns
the results as a list of dicts along with the execution time in milliseconds.
"""
import time
from decimal import Decimal
from datetime import datetime, date, timedelta
from api.db.connection import get_conn

MAX_ROWS = 500  # hard cap — never return more than this regardless of query


def run(sql: str) -> tuple[list[dict], int]:
    """
    Execute *sql* and return (rows, execution_ms).
    Rows are JSON-serialisable (Decimal → float, datetime → ISO string, etc.)
    """
    start = time.monotonic()

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            raw_rows = cur.fetchmany(MAX_ROWS)

    execution_ms = int((time.monotonic() - start) * 1000)
    rows = [_serialise(dict(row)) for row in raw_rows]
    return rows, execution_ms


def _serialise(row: dict) -> dict:
    """Convert Postgres types that aren't JSON-native."""
    out = {}
    for k, v in row.items():
        if isinstance(v, Decimal):
            out[k] = float(v)
        elif isinstance(v, (datetime, date)):
            out[k] = v.isoformat()
        elif isinstance(v, timedelta):
            # e.g. days_since_last_order interval → total days float
            out[k] = round(v.total_seconds() / 86400, 1)
        else:
            out[k] = v
    return out
