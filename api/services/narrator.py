"""
Generates a 2-3 sentence plain-English summary of the query results,
written for a non-technical business owner.
"""
from __future__ import annotations
import json
import os
from openai import OpenAI

_client: OpenAI | None = None


def _openai() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    return _client


SYSTEM_PROMPT = """
You are a business intelligence analyst summarising data for a non-technical SMB owner.

Write 2-3 short, plain-English sentences that:
1. Directly answer the question that was asked
2. Highlight the single most important insight from the data
3. Note any trend, anomaly, or action the business owner should consider

Tone: concise, professional, no jargon, no SQL.
Do NOT say "Based on the data..." or "The results show...". Just state the insight directly.
""".strip()


def summarise(question: str, rows: list[dict], row_count: int) -> str:
    """
    Returns a plain-English narrative summary.
    Truncates rows sent to OpenAI to avoid large token usage.
    """
    sample = rows[:20]  # send at most 20 rows to the model
    data_str = json.dumps(sample, indent=2, default=str)

    user_message = f"""
Question: {question}

Results ({row_count} total rows, showing up to 20):
{data_str}
""".strip()

    response = _openai().chat.completions.create(
        model="gpt-4o",
        temperature=0.3,
        max_tokens=200,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )

    return response.choices[0].message.content.strip()
