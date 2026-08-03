"""
Translates a natural-language business question into a safe, read-only SQL query
using the OpenAI chat completion API with full schema context injection.
"""
from __future__ import annotations
import os
import re
from openai import OpenAI
from api.services.schema_inspector import build_schema_context

_client: OpenAI | None = None


def _openai() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    return _client


SYSTEM_PROMPT_TEMPLATE = """
You are an expert business intelligence SQL analyst for an SMB retail company.
Your job is to translate plain-English business questions into accurate PostgreSQL queries.

{schema_context}

RULES — follow these precisely:
1. Output ONLY the SQL query. No explanation, no markdown fences, no commentary.
2. Only use SELECT statements. Never write INSERT, UPDATE, DELETE, DROP, CREATE, TRUNCATE, or any DDL/DML.
3. Always filter orders to status = 'completed' unless the user explicitly asks about refunds or pending orders.
4. Use CTEs (WITH ...) for clarity when the query has multiple steps.
5. Prefer the pre-built views (vw_order_revenue, vw_product_sales, vw_customer_last_order) when they satisfy the question.
6. Always include human-readable column aliases (e.g. AS "Customer Name").
7. Limit results to 100 rows unless the user specifies otherwise.
8. If you cannot answer the question from the available schema, respond with exactly: CANNOT_ANSWER
""".strip()

# Regex to strip accidental markdown fences from the model response
_FENCE_RE = re.compile(r"^```(?:sql)?\s*|\s*```$", re.MULTILINE | re.IGNORECASE)

# Disallow any mutation keywords
_UNSAFE_RE = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|CREATE|TRUNCATE|ALTER|GRANT|REVOKE|EXEC|EXECUTE)\b",
    re.IGNORECASE,
)


def translate(question: str) -> str:
    """
    Returns a safe SELECT SQL string, or raises ValueError if the question
    cannot be answered from the schema.
    """
    schema_context = build_schema_context()
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(schema_context=schema_context)

    response = _openai().chat.completions.create(
        model="gpt-4o",
        temperature=0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
    )

    sql = response.choices[0].message.content.strip()

    # Strip accidental markdown fences
    sql = _FENCE_RE.sub("", sql).strip()

    if sql.upper() == "CANNOT_ANSWER":
        raise ValueError(f"This question cannot be answered from the available data: {question!r}")

    # Safety check — never execute mutation queries
    if _UNSAFE_RE.search(sql):
        raise ValueError("Generated SQL contains disallowed keywords and was rejected")

    return sql
