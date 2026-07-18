# GitHub Time Machine Core Backend

The `backend` service is the core application API for GitHub Time Machine. It handles repository submission, analysis pipeline, graph/timeline endpoints, OAuth, and Supabase access.

## Responsibilities

- Create repository records and trigger background analysis (clone → walk → store files → extract functions/classes/import-edges via Tree-sitter → extract commits → update metadata)
- Serve graph data (file nodes + import edges, read from the `edges` table populated during analysis) and commit timelines
- Answer repository questions via OpenAI chat, with prompt-injection filtering and the Moderation API as a second guard
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
| **Facade** | `RepoAnalyzer.analyze()` | Orchestrates the collaborators below behind one call; doesn't implement their logic itself |
| **Extract Class collaborators** | `RepoCloner`, `FileWalker`, `SymbolExtractor`, `EmbeddingGenerator` | Each owns one pipeline stage (clone, walk, parse, embed) — `RepoAnalyzer` only coordinates + persists |
| **Singleton** | `get_supabase()` | Single DB client for the whole process |
| **Strategy** | `SymbolExtractor._get_lang` + per-language tree-sitter queries | Different parsing grammar/queries per language |
| **Dependency Injection** | `Depends(get_db)` | Routes receive the DB client, don't create it |
| **Template Method** | `analyze()` → clone → walk → store files → extract symbols/edges → extract commits → update metadata | Fixed sequence, each step delegated to a collaborator |

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
│       ├── repo_analyzer.py         # RepoAnalyzer: Facade — orchestrates the pipeline below, persists to Supabase
│       ├── repo_cloner.py           # RepoCloner: validate URL, git clone to temp dir, cleanup
│       ├── file_walker.py           # FileWalker: walk working tree, filter vendored/binary files
│       ├── symbol_extractor.py      # SymbolExtractor: Tree-sitter parsing (functions/classes/imports)
│       ├── embedding_generator.py   # EmbeddingGenerator: OpenAI embeddings, one client reused per job
│       ├── commit_analyzer.py       # CommitAnalyzer: GitPython extraction + Supabase upsert
│       └── chat_service.py          # ChatService: OpenAI chat with prompt-injection + moderation guards
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
| `CORS_ORIGINS` | No | `*` | Comma-separated allowed origins (`*` implies `allow_credentials=False`) |
| `OPENAI_API_KEY` | No | — | OpenAI key for embeddings + chat (both degrade gracefully without it) |
| `OPENAI_EMBEDDING_MODEL` | No | `text-embedding-3-small` | Embedding model name |
| `CHAT_MODEL` | No | `gpt-4o-mini` | Chat completion model for `/repositories/{id}/chat` |
| `CHAT_MAX_TOKENS` | No | `1024` | Max tokens per chat response |
| `CHAT_TEMPERATURE` | No | `0.4` | Chat completion temperature |
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
| `POST` | `/repositories/{id}/chat` | chat | Chat with a repository via OpenAI, grounded in stored README/files/commits |
| `GET` | `/repositories/{id}/chat` | chat | Get chat history |
| `GET` | `/repositories/{id}/timeline` | timeline | Commit timeline + fix/merge detection + stats |
| `GET` | `/repositories/{id}/graph` | graph | Knowledge graph — files as nodes, import edges read from the `edges` table (populated by analysis, not re-parsed per request) |
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
- Routes that only make synchronous Supabase calls are declared as plain `def`, not `async def` — FastAPI runs those in a threadpool automatically instead of blocking the event loop. `/repos/connect` stays `async def` (it does real async I/O against the GitHub API via `httpx`) and wraps its own synchronous Supabase calls in `run_in_threadpool`.
- Without an `OPENAI_API_KEY`, embedding generation and chat both fail gracefully (embeddings are skipped per-batch and logged as non-fatal; chat returns an error message) — the rest of the pipeline still completes.
- Background analysis via `BackgroundTasks` may timeout on Railway for large repos (>30s). Use `pre_seed.py` locally for large repos.
- `RepoCloner.validate_url` validates GitHub URLs before cloning to prevent SSRF (`^https://github\\.com/...`).
- `CORS_ORIGINS=*` (the default) disables `allow_credentials` automatically — browsers reject credentialed requests against a wildcard origin, so don't rely on cookies/auth headers across origins unless `CORS_ORIGINS` is set to explicit origins.
- Row Level Security is configured on all Supabase tables; the backend uses `service_role` key to bypass it.
