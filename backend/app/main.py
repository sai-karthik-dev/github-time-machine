from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import CORS_ORIGINS
from app.core.rate_limit import rate_limit_middleware
from app.routes.health import router as health_router
from app.routes.repositories import router as repositories_router
from app.routes.repos import router as repos_router
from app.routes.ai_endpoints import router as ai_endpoints_router

app = FastAPI(title="GitHub Time Machine API", version="0.2.0")

_cors_origins = [o.strip() for o in CORS_ORIGINS.split(",")]
# Browsers reject credentialed requests against a wildcard origin, and CORS
# middleware that advertises both is a common misconfiguration (OWASP).
_allow_credentials = "*" not in _cors_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.middleware("http")(rate_limit_middleware())

app.include_router(health_router)
app.include_router(repositories_router)
app.include_router(repos_router)
app.include_router(ai_endpoints_router)
