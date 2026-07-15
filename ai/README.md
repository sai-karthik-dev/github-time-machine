# GitHub Time Machine — AI Orchestration Service

AI-powered engineering intelligence backend for the GitHub Time Machine platform.

## Quick Start

```bash
# 1. Create virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate # macOS/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
copy .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 4. Run the server
uvicorn app.main:app --reload --port 8001
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/repos/{id}/chat` | Architecture explanation (SSE streaming) |
| `GET` | `/repos/{id}/graph` | Knowledge graph slice |
| `POST` | `/repos/{id}/impact` | Change impact simulator |
| `GET` | `/repos/{id}/timeline` | Commit timeline events |
| `GET` | `/repos/{id}/heatmap` | Technical debt heatmap |

## Demo Mode

A pre-built demo repo (`repo_id = "demo"`) is available with realistic mock data.
No database needed — works completely standalone.

```bash
# Try it out
curl http://localhost:8001/repos/demo/graph?depth=2
curl http://localhost:8001/repos/demo/timeline
curl http://localhost:8001/repos/demo/heatmap

# Chat (requires OpenAI key)
curl -X POST http://localhost:8001/repos/demo/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Explain the auth module", "stream": false}'
```

## Architecture

```
app/
├── main.py              # FastAPI app entry point
├── config.py            # Pydantic settings
├── dependencies.py      # Dependency injection
├── models/              # Pydantic schemas
├── services/            # Business logic (OpenAI, prompts, cache)
├── prompts/             # Jinja2 prompt templates
├── mock/                # Mock data layer (swap for DB later)
└── routers/             # API endpoints
```

## Integration with Backend

The `DataProvider` interface in `app/mock/data_provider.py` defines the contract.
When the real Supabase DB is ready, implement `SupabaseDataProvider` with the same
methods and swap it in `app/dependencies.py`. Zero changes to AI logic needed.
