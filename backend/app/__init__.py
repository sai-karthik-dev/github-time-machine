"""GitHub Time Machine — Core Backend API.

Architecture:
    app/
    ├── core/       — infra: Supabase client, env config
    ├── models/     — Pydantic schemas (tables.py) and API contracts (schemas.py)
    ├── routes/     — FastAPI routers (health, repositories, repos/connect, graph, timeline)
    └── services/   — business logic (RepoAnalyzer, CommitAnalyzer)

Patterns used:
    - Facade: RepoAnalyzer.analyze() wraps the full analysis pipeline
    - Singleton: supabase client via get_supabase()
    - Strategy: tree-sitter extraction methods per language
    - Dependency Injection: Depends(get_db) in all routes
    - Template Method: analyze() skeleton with overridable steps
"""
