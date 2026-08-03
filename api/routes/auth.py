"""
POST /api/auth/login

Demo-mode: a hardcoded user registry so the illustrative codebase works
without an external identity provider. In production, replace _USERS with
a real database lookup + bcrypt verification.

Demo credentials
  owner@demo.com   / demo1234  → role: owner
  manager@demo.com / demo1234  → role: manager, region: North
  staff@demo.com   / demo1234  → role: staff
"""
from fastapi import APIRouter, HTTPException, status
from api.models.schemas import LoginRequest, LoginResponse
from api.auth.jwt_handler import create_token

router = APIRouter(prefix="/api/auth", tags=["auth"])

# In production: query the users table + bcrypt.verify
_USERS = {
    "owner@demo.com":   {"password": "demo1234", "role": "owner",   "region": None},
    "manager@demo.com": {"password": "demo1234", "role": "manager", "region": "North"},
    "staff@demo.com":   {"password": "demo1234", "role": "staff",   "region": None},
}


@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest):
    user = _USERS.get(body.username)
    if not user or user["password"] != body.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    token = create_token(
        user_id=body.username,
        role=user["role"],
        region=user["region"],
    )
    return LoginResponse(
        access_token=token,
        role=user["role"],
        user_id=body.username,
    )
