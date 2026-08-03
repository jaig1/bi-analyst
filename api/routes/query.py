"""
POST /api/query

The core NL → SQL → chart → narrative pipeline.

Flow:
  1. Validate JWT, extract role + region
  2. Translate question to SQL via OpenAI (schema context injected)
  3. Apply RBAC row filter if role == manager
  4. Execute SQL against Neon Postgres
  5. Select chart type from result shape
  6. Generate plain-English narrative via OpenAI
  7. Write audit log entry
  8. Return structured response
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from api.models.schemas import QueryRequest, QueryResponse
from api.auth.jwt_handler import decode_token
from api.auth.rbac import require_role, apply_row_filter
from api.services import text_to_sql, query_executor, chart_selector, narrator
from api.db.audit_log import log_query

router = APIRouter(prefix="/api", tags=["query"])
_bearer = HTTPBearer()


def _get_payload(creds: HTTPAuthorizationCredentials = Depends(_bearer)) -> dict:
    return decode_token(creds.credentials)


@router.post("/query", response_model=QueryResponse)
def run_query(
    body: QueryRequest,
    payload: dict = Depends(_get_payload),
):
    # Block staff from ad-hoc queries
    require_role("owner", "manager")(payload)

    role = payload["role"]
    region = payload.get("region")
    user_id = payload["sub"]

    # Step 1: NL → SQL
    try:
        sql = text_to_sql.translate(body.question)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    # Step 2: Apply row-level filter for managers
    if role == "manager":
        sql = apply_row_filter(sql, role, region)

    # Step 3: Execute
    try:
        rows, execution_ms = query_executor.run(sql)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Query execution failed: {exc}")

    row_count = len(rows)

    # Step 4: Pick chart type
    chart_type, x_key, y_keys = chart_selector.select(rows)

    # Step 5: Narrative summary
    summary = narrator.summarise(body.question, rows, row_count)

    # Step 6: Audit log (fire and forget — don't fail the request if logging fails)
    try:
        log_query(
            user_id=user_id,
            user_role=role,
            question=body.question,
            generated_sql=sql,
            row_count=row_count,
            execution_ms=execution_ms,
            chart_type=chart_type,
        )
    except Exception:
        pass  # Logging failure must never break the user response

    return QueryResponse(
        question=body.question,
        sql=sql,
        chart_type=chart_type,
        chart_data=rows,
        x_key=x_key,
        y_keys=y_keys,
        narrative=summary,
        rows=rows,
        row_count=row_count,
        execution_ms=execution_ms,
    )
