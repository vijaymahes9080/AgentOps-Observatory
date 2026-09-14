"""
AgentOps Observatory - Main Application Entrypoint
FastAPI server with security headers, request ID tracing, CORS, and automated DB initialization.
"""

import logging
import time
from uuid import uuid4
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from backend.app.api.routes import router as api_router
from backend.app.core.config import settings
from backend.app.core.security import RedactedLogFilter
from backend.app.models.db import init_db

# Configure redacted logger
logger = logging.getLogger("agentops")
handler = logging.StreamHandler()
handler.addFilter(RedactedLogFilter())
handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"))
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adds hardened security headers and request-id tracing."""
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid4()))
        request.state.request_id = request_id
        
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time:.4f}"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
        
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB
    logger.info("Initializing AgentOps Observatory Database schema...")
    await init_db()
    logger.info("Observatory ready to ingest telemetry events.")
    yield
    # Shutdown
    logger.info("AgentOps Observatory shutting down.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Observability, Governance, and Audit Platform for AI Agents, MCP Servers, RAG Pipelines, and n8n Workflows.",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security Headers & Tracing Middleware
app.add_middleware(SecurityHeadersMiddleware)

# Mount API Routers
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(api_router)  # Also mount at root for /health, /version, /events convenience


@app.get("/")
async def root():
    return {
        "platform": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "api_v1": settings.API_V1_STR,
        "status": "operational"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
