from __future__ import annotations
"""
Role-based access control.

Roles:
  owner   — full access, no row filters
  manager — sees only their region (injected as WHERE clause fragment)
  staff   — not permitted to run ad-hoc queries (read-only audit endpoint only)

The SQL filter is appended to the generated SQL as a CTE wrapper so the AI's
query is never modified directly (avoids breaking JOINs).
"""
from fastapi import HTTPException, status

ROLES = {"owner", "manager", "staff"}


def require_role(*allowed: str):
    """Returns a dependency that raises 403 if the user's role isn't in *allowed*."""
    def _check(payload: dict) -> dict:
        if payload.get("role") not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of roles: {', '.join(allowed)}",
            )
        return payload
    return _check


def apply_row_filter(sql: str, role: str, region: str | None) -> str:
    """
    Wrap the generated SQL in a CTE and append a row-level filter based on role.

    owner   → no change
    manager → filter to their region on orders/customers tables via the CTE alias
    staff   → blocked at route level; this should never be called for staff
    """
    if role == "owner":
        return sql

    if role == "manager":
        if not region:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Manager token missing region claim",
            )
        # Wrap the original query so we can filter on region columns
        return f"""
WITH _base AS (
    {sql.rstrip(';')}
)
SELECT * FROM _base
WHERE region = '{region}'
""".strip()

    # staff — should not reach here
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Staff are not permitted to run ad-hoc queries",
    )
