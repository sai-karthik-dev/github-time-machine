# GitHub Time Machine Core Backend

The `backend` service is the core application API for GitHub Time Machine. It handles repository submission, analysis pipeline, graph/timeline endpoints, OAuth, and Supabase access.

## Responsibilities

- Create repository records and trigger background analysis (clone → parse → store)
- Serve graph data (nodes + edges from file imports) and commit timelines
- Store and retrieve chat history
- Centralize Supabase client configuration and dependency injection
- Pre-seed demo repositories for the hackathon

## Technologies

- **FastAPI** + Uvicorn — async API server
- **Pydantic** — request/response schemas with Field validators and StrEnum
- **Supabase Python client** — Postgres + pgvector access via service_role key
- **GitPython** — commit history extraction
- **Tree-sitter** — AST parsing for Python and JavaScript/TypeScript
- **OpenAI SDK** — text-embedding-3-small for vector embeddings (optional)
- **python-dotenv** — local environment configuration

## Design Patterns

| Pattern | Where | Why |
|---------|-------|-----|
| **Facade** | `RepoAnalyzer.analyze()` | One method orchestrates 6 internal steps |
| **Singleton** | `get_supabase()` | Single DB client for the whole process |
| **Strategy** | `_extract_functions / _extract_classes / _extract_imports` | Different parsing per language |
| **Dependency Injection** | `Depends(get_db)` | Routes receive the DB client, don't create it |
| **Template Method** | `analyze()` → `_clone → _walk → _store → _update` | Fixed sequence, overridable steps |

## Folder Structure

```text
backend/
├── app/
│   ├── __init__.py              # Package docs
│   ├── main.py                  # FastAPI app, CORS, router mounting
│   ├── dependencies.py          # FastAPI DI: get_db()
│   ├── utils.py                 # Shared: parse_github_url()
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py            # All env vars + analysis constants
│   │   └── supabase.py          # Singleton Supabase client (service_role)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── schemas.py           # API request/response (RepositoryStatus StrEnum, Field validators)
│   │   ├── tables.py            # DB table models (User, Repository, Commit, FileRecord, etc.)
│   │   └── embeddings.py        # FileEmbedding, CodeChunk
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── health.py            # GET /health, GET /
│   │   ├── repositories.py      # Repo CRUD, chat, timeline, graph
│   │   └── repos.py             # POST /repos/connect (OAuth)
│   └── services/
│       ├── __init__.py
│       ├── repo_analyzer.py      # RepoAnalyzer: clone, walk, Tree-sitter, file storage, embeddings
│       └── commit_analyzer.py    # CommitAnalyzer: GitPython extraction + Supabase upsert
├── database/
│   ├── schema_v2.sql            # functions + edges tables (optional, for Knowledge Graph v2)
│   └── complete_schema.sql      # Full DDL snapshot
├── main.py                      # Entry: from app.main import app
├── pre_seed.py                  # Pre-seed a demo repo into Supabase
├── Procfile                     # Railway start command
├── railway.json                 # Railway deploy config (Nixpacks)
├── nixpacks.toml                # apt packages for Railway (git)
├── requirements.txt
├── .env.example
└── .gitignore
```

## How To Run

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

Open http://localhost:8000/docs for Swagger UI.

## Environment

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SUPABASE_URL` | Yes | — | Supabase project URL |
| `SUPABASE_SERVICE_KEY` | Yes | — | Service role key (bypasses RLS) |
| `SUPABASE_ANON_KEY` | No | — | Anon key (not used by backend) |
| `CORS_ORIGINS` | No | `*` | Comma-separated allowed origins |
| `OPENAI_API_KEY` | No | — | OpenAI key for embeddings (pipeline runs without it) |
| `OPENAI_EMBEDDING_MODEL` | No | `text-embedding-3-small` | Embedding model name |
| `EMBEDDING_DIMENSION` | No | `1536` | Vector dimension for pgvector |
| `ANALYSIS_MAX_FILE_SIZE` | No | `1000000` | Skip files larger than this (bytes) |
| `ANALYSIS_EMBED_BATCH_SIZE` | No | `20` | Files per embedding API call |
| `ANALYSIS_CLONE_DEPTH` | No | `1` | Git clone depth |
| `ANALYSIS_EMBED_CHUNK_SIZE` | No | `8000` | Chars per embedding chunk |

## API Endpoints

| Method | Endpoint | Tags | Purpose |
|--------|----------|------|---------|
| `GET` | `/health` | health | Health check |
| `GET` | `/` | health | API info |
| `POST` | `/repositories/` | repositories | Submit a repo URL — triggers background analysis |
| `GET` | `/repositories/` | repositories | List all repositories with status |
| `GET` | `/repositories/{id}` | repositories | Get analysis status + file/commit counts |
| `POST` | `/repositories/{id}/analyze` | repositories | Manually re-trigger analysis |
| `POST` | `/repositories/{id}/chat` | chat | Chat with a repository (placeholder, needs OpenAI) |
| `GET` | `/repositories/{id}/chat` | chat | Get chat history |
| `GET` | `/repositories/{id}/timeline` | timeline | Commit timeline + fix/merge detection + stats |
| `GET` | `/repositories/{id}/graph` | graph | Knowledge graph — files as nodes, imports as edges |
| `POST` | `/repos/connect` | auth | OAuth — validate JWT + sync GitHub user |

## Deployment (Railway)

The backend is deployed on Railway using Nixpacks. Configuration:

- **Root Directory**: `backend/`
- **Builder**: Nixpacks (auto-detects Python via `requirements.txt`)
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Procfile** and **railway.json** are provided in the repo

See the [Railway FastAPI guide](https://docs.railway.com/guides/fastapi) for more details.

## Pre-Seeding a Demo Repo

```bash
cd backend
source venv/bin/activate
python pre_seed.py
```

This clones a repo (default: `tiangolo/typer`), runs the full analysis pipeline locally, and uploads the results to Supabase. The Railway API then serves this data instantly without background task timeouts.

## Important Notes

- The backend uses `Depends(get_db)` for Supabase access — all route handlers receive the client via FastAPI's dependency injection.
- Chat responses are placeholders until an `OPENAI_API_KEY` is configured and the AI service (#15, #16) is wired.
- Background analysis via `BackgroundTasks` may timeout on Railway for large repos (>30s). Use `pre_seed.py` locally for large repos.
- The `RepoAnalyzer` validates GitHub URLs before cloning to prevent SSRF (`^https://github\\.com/...`).
- Row Level Security is configured on all Supabase tables; the backend uses `service_role` key to bypass it.
