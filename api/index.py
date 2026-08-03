"""
FastAPI entry point for Vercel Python Serverless Functions.

Vercel routes /api/* here via vercel.json rewrites.
Mangum wraps the ASGI app as an AWS Lambda-compatible handler,
which is the interface Vercel's Python runtime expects.
"""
from dotenv import load_dotenv
load_dotenv(".env.local")  # no-op in Vercel (vars come from dashboard)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from api.routes.auth import router as auth_router
from api.routes.query import router as query_router
from api.routes.audit import router as audit_router

app = FastAPI(
    title="AI Business Intelligence Analyst",
    description="Natural language → SQL → charts for SMB owners",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Tighten to your Vercel domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(query_router)
app.include_router(audit_router)


@app.get("/api/health")
def health():
    return {"status": "ok"}


# Vercel invokes this handler
handler = Mangum(app, lifespan="off")
