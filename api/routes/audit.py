"""
GET /api/audit/logs?page=1&page_size=25

Returns paginated query audit log entries. Restricted to owner role only.
"""
from fastapi import APIRouter, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from api.models.schemas import AuditLogResponse, AuditEntry
from api.auth.jwt_handler import decode_token
from api.auth.rbac import require_role
from api.db.connection import get_conn

router = APIRouter(prefix="/api/audit", tags=["audit"])
_bearer = HTTPBearer()


def _get_payload(creds: HTTPAuthorizationCredentials = Depends(_bearer)) -> dict:
    return decode_token(creds.credentials)


@router.get("/logs", response_model=AuditLogResponse)
def get_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    payload: dict = Depends(_get_payload),
):
    require_role("owner")(payload)

    offset = (page - 1) * page_size

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS total FROM query_audit")
            total = cur.fetchone()["total"]

            cur.execute(
                """
                SELECT id, user_id, user_role, question, generated_sql,
                       row_count, execution_ms, chart_type,
                       created_at::text AS created_at
                FROM query_audit
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
                """,
                (page_size, offset),
            )
            rows = cur.fetchall()

    entries = [AuditEntry(**dict(row)) for row in rows]
    return AuditLogResponse(
        entries=entries,
        total=total,
        page=page,
        page_size=page_size,
    )
