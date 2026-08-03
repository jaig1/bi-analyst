"""
Database connection for Vercel serverless (psycopg2, one connection per request).
DATABASE_URL is set automatically by the Neon integration in Vercel.
"""
import os
import psycopg2
import psycopg2.extras
from contextlib import contextmanager


def _get_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL environment variable is not set")
    return url


@contextmanager
def get_conn():
    """Context manager that yields a psycopg2 connection and commits/closes cleanly."""
    conn = psycopg2.connect(_get_url(), cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
