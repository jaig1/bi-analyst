"""
Pydantic request/response models for all API routes.
"""
from __future__ import annotations
from typing import Any, Optional
from pydantic import BaseModel


# ── Auth ────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: str


# ── Query pipeline ───────────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    question: str
    sql: str
    chart_type: str          # "bar" | "line" | "pie" | "kpi" | "table"
    chart_data: list[dict[str, Any]]
    x_key: Optional[str]     # column name for the X-axis / label
    y_keys: list[str]        # column name(s) for numeric series
    narrative: str           # plain-English summary
    rows: list[dict[str, Any]]
    row_count: int
    execution_ms: int


# ── Audit log ────────────────────────────────────────────────────────────────

class AuditEntry(BaseModel):
    id: int
    user_id: str
    user_role: str
    question: str
    generated_sql: str
    row_count: Optional[int]
    execution_ms: Optional[int]
    chart_type: Optional[str]
    created_at: str


class AuditLogResponse(BaseModel):
    entries: list[AuditEntry]
    total: int
    page: int
    page_size: int
