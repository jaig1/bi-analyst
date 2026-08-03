"""
JWT encode/decode helpers.
Token payload: { sub: user_id, role: "owner"|"manager"|"staff", region: str | None }
"""
from __future__ import annotations
import os
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from fastapi import HTTPException, status

ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 8


def _secret() -> str:
    secret = os.environ.get("JWT_SECRET")
    if not secret:
        raise RuntimeError("JWT_SECRET environment variable is not set")
    return secret


def create_token(user_id: str, role: str, region: str | None = None) -> str:
    payload = {
        "sub": user_id,
        "role": role,
        "region": region,
        "exp": datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRE_HOURS),
    }
    return jwt.encode(payload, _secret(), algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, _secret(), algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
