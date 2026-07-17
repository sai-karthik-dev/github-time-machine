from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import CORS_ORIGINS
from app.routes.health import router as health_router
from app.routes.repositories import router as repositories_router
from app.routes.repos import router as repos_router

app = FastAPI(title="GitHub Time Machine API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in CORS_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(repositories_router)
app.include_router(repos_router)
