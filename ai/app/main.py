"""
GitHub Time Machine — AI Orchestration Service

FastAPI application entry point.
Run with: uvicorn app.main:app --reload --port 8001
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import chat, graph, impact, timeline, heatmap, health, bug_origin, refactor_plan

# ── Logging ─────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s │ %(levelname)-7s │ %(name)s │ %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("github-time-machine")


# ── Lifespan ────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown events."""
    logger.info("🚀  GitHub Time Machine AI service starting…")

    if not settings.openai_api_key:
        logger.warning("⚠️  OPENAI_API_KEY not set — AI endpoints will fail")
    else:
        logger.info("✅  OpenAI key configured (model: %s)", settings.openai_model)

    logger.info("📡  CORS origins: %s", settings.cors_origin_list)
    logger.info("🧪  Using MockDataProvider (demo repo available at repo_id='demo')")

    yield

    logger.info("👋  Shutting down…")


# ── App ─────────────────────────────────────────────────────────────────

app = FastAPI(
    title="GitHub Time Machine — AI Service",
    description="AI-powered engineering intelligence: architecture explanation, "
                "impact simulation, knowledge graph, timeline, and debt heatmap.",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ─────────────────────────────────────────────────────────────

app.include_router(chat.router)
app.include_router(graph.router)
app.include_router(impact.router)
app.include_router(timeline.router)
app.include_router(heatmap.router)
app.include_router(health.router)
app.include_router(bug_origin.router)
app.include_router(refactor_plan.router)


# ── Health Check ────────────────────────────────────────────────────────

@app.get("/health", tags=["system"])
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "github-time-machine-ai",
        "version": "0.1.0",
        "openai_configured": bool(settings.openai_api_key),
        "model": settings.openai_model,
        "data_provider": "mock",
    }


@app.get("/", tags=["system"])
async def root():
    """Root endpoint with API info."""
    return {
        "service": "GitHub Time Machine — AI Orchestration",
        "version": "0.1.0",
        "docs": "/docs",
        "endpoints": {
            "chat": "POST /repos/{repo_id}/chat",
            "graph": "GET /repos/{repo_id}/graph",
            "impact": "POST /repos/{repo_id}/impact",
            "timeline": "GET /repos/{repo_id}/timeline",
            "heatmap": "GET /repos/{repo_id}/heatmap",
            "file_health": "GET /repos/{repo_id}/file_health",
            "bug_origin": "POST /repos/{repo_id}/bug_origin",
            "refactor_plan": "POST /repos/{repo_id}/refactor_plan",
            "health": "GET /health",
        },
    }

