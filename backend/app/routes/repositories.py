import logging
import re
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query

from app.dependencies import get_db
from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    GraphEdge,
    GraphNode,
    GraphResponse,
    RepositoryCompleted,
    RepositoryError,
    RepositoryListItem,
    RepositoryListResponse,
    RepositoryPending,
    RepositoryProcessing,
    RepositoryResponse,
    RepositoryStatus,
    RepositorySubmitRequest,
    TimelineEvent,
    TimelineResponse,
    TimelineStats,
)
from app.services.repo_analyzer import RepoAnalyzer
from app.services.repo_cloner import RepoCloner
from app.services.chat_service import ChatService
from app.utils import parse_github_url

logger = logging.getLogger(__name__)

_FIX_PATTERN = re.compile(r"\b(fix|bug|patch|hotfix|resolve|close)\b", re.IGNORECASE)
_MERGE_PATTERN = re.compile(r"^merge", re.IGNORECASE)
_IMPORT_PY = re.compile(r"(?:from\s+(\S+)\s+import|import\s+(\S+))")
_IMPORT_JS = re.compile(r"""(?:import\s+.*?\s+from\s+['"]([^'"]+)['"]|require\s*\(\s*['"]([^'"]+)['"]\s*\))""")

router = APIRouter(prefix="/repositories", tags=["repositories"])


def _get_demo_user_id() -> str:
    supabase = get_db()
    existing = supabase.table("users").select("id").eq("github_id", 0).limit(1).execute()
    if existing.data:
        return existing.data[0]["id"]
    response = supabase.table("users").insert({
        "github_id": 0,
        "username": "demo",
    }).execute()
    if not response.data:
        raise HTTPException(status_code=500, detail="Failed to create demo user")
    return response.data[0]["id"]


def _run_analysis(repository_id: str, github_url: str) -> None:
    try:
        analyzer = RepoAnalyzer(repository_id, github_url)
        result = analyzer.analyze()
        logger.info(f"Analysis complete for {repository_id}: {result}")
    except Exception as e:
        logger.error(f"Background analysis failed for {repository_id}: {e}")
        try:
            supabase = get_db()
            supabase.table("analyses").update({
                "status": RepositoryStatus.ERROR.value,
                "error_message": str(e)[:500],
            }).eq("repository_id", repository_id).execute()
        except Exception as db_err:
            logger.error(f"Failed to update error status for {repository_id}: {db_err}")


@router.post("/", response_model=RepositoryResponse, status_code=202,
    summary="Submit a repository for analysis",
    description="Creates a repository record and triggers background analysis: clone, parse files, extract commits, and store in Supabase.",
    tags=["repositories"],
)
def submit_repository(body: RepositorySubmitRequest, background_tasks: BackgroundTasks, supabase = Depends(get_db)):

    if not RepoCloner.validate_url(body.github_url):
        raise HTTPException(status_code=400, detail="Invalid GitHub URL. Must be https://github.com/<owner>/<repo>")

    user_id = _get_demo_user_id()
    owner, name = parse_github_url(body.github_url)

    repo_response = (
        supabase.table("repositories")
        .insert({
            "github_url": body.github_url,
            "user_id": user_id,
            "name": name,
            "owner": owner,
        })
        .execute()
    )
    if not repo_response.data:
        raise HTTPException(status_code=500, detail="Failed to create repository")

    repo = repo_response.data[0]

    supabase.table("analyses").insert({
        "repository_id": repo["id"],
        "status": RepositoryStatus.PENDING.value,
    }).execute()

    background_tasks.add_task(_run_analysis, repo["id"], body.github_url)

    return RepositoryPending(
        id=repo["id"],
        github_url=repo["github_url"],
        created_at=datetime.fromisoformat(repo["created_at"]),
    )


@router.post("/{repo_id}/analyze", response_model=RepositoryResponse, summary="Manually trigger analysis", tags=["repositories"])
def trigger_analysis(repo_id: UUID, background_tasks: BackgroundTasks, supabase = Depends(get_db)):
    repo_response = supabase.table("repositories").select("*").eq("id", str(repo_id)).execute()
    if not repo_response.data:
        raise HTTPException(status_code=404, detail="Repository not found")

    repo = repo_response.data[0]
    background_tasks.add_task(_run_analysis, str(repo_id), repo["github_url"])

    return RepositoryProcessing(
        id=repo["id"],
        github_url=repo["github_url"],
        started_at=datetime.now(timezone.utc),
        created_at=datetime.fromisoformat(repo["created_at"]),
    )


@router.get("/", response_model=RepositoryListResponse, summary="List all repositories", tags=["repositories"])
def list_repositories(user_id: Optional[str] = Query(None, description="Filter by user ID"),
    limit: int = Query(20, le=100),
    offset: int = 0,
    supabase = Depends(get_db),
):

    query = supabase.table("repositories").select("*")
    if user_id:
        query = query.eq("user_id", user_id)

    response = query.order("created_at", desc=True).range(offset, offset + limit - 1).execute()

    repo_ids = [r["id"] for r in (response.data or [])]
    latest_statuses: dict[str, str] = {}

    if repo_ids:
        analyses_response = (
            supabase.table("analyses")
            .select("repository_id, status")
            .in_("repository_id", repo_ids)
            .order("created_at", desc=True)
            .execute()
        )
        seen = set()
        for a in (analyses_response.data or []):
            if a["repository_id"] not in seen:
                seen.add(a["repository_id"])
                latest_statuses[a["repository_id"]] = a["status"]

    repos = [
        RepositoryListItem(
            id=r["id"],
            name=r.get("name", ""),
            owner=r.get("owner", ""),
            github_url=r.get("github_url", ""),
            language=r.get("language"),
            status=latest_statuses.get(r["id"]),
            created_at=datetime.fromisoformat(r["created_at"]) if r.get("created_at") else None,
            last_analyzed=datetime.fromisoformat(r["last_analyzed"]) if r.get("last_analyzed") else None,
        )
        for r in (response.data or [])
    ]

    return RepositoryListResponse(repositories=repos)


@router.get("/{repo_id}", response_model=RepositoryResponse, summary="Get repository analysis status", tags=["repositories"])
def get_repository_status(repo_id: UUID, supabase = Depends(get_db)):

    repo_response = supabase.table("repositories").select("*").eq("id", str(repo_id)).execute()
    if not repo_response.data:
        raise HTTPException(status_code=404, detail="Repository not found")
    repo = repo_response.data[0]

    analysis_response = (
        supabase.table("analyses")
        .select("*")
        .eq("repository_id", str(repo_id))
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )

    status = RepositoryStatus.PENDING.value
    analysis_data = None
    if analysis_response.data:
        analysis_data = analysis_response.data[0]
        status = analysis_data.get("status", RepositoryStatus.PENDING.value)

    files_count = (
        supabase.table("files").select("id", count="exact").eq("repository_id", str(repo_id)).execute()
    ).count or 0

    commits_count = (
        supabase.table("commits").select("id", count="exact").eq("repository_id", str(repo_id)).execute()
    ).count or 0

    if status == RepositoryStatus.COMPLETED.value:
        from app.models.tables import Analysis

        return RepositoryCompleted(
            id=repo["id"],
            github_url=repo["github_url"],
            name=repo.get("name") or "",
            owner=repo.get("owner") or "",
            language=repo.get("language"),
            files_indexed=files_count,
            commits_analyzed=commits_count,
            analysis=Analysis(**analysis_data) if analysis_data else None,
            created_at=datetime.fromisoformat(repo["created_at"]),
            completed_at=datetime.fromisoformat(analysis_data["completed_at"])
                if analysis_data and analysis_data.get("completed_at") else None,
        )

    if status == RepositoryStatus.PROCESSING.value:
        return RepositoryProcessing(
            id=repo["id"],
            github_url=repo["github_url"],
            started_at=datetime.fromisoformat(analysis_data["started_at"])
                if analysis_data and analysis_data.get("started_at") else None,
            created_at=datetime.fromisoformat(repo["created_at"]),
        )

    if status == RepositoryStatus.ERROR.value:
        return RepositoryError(
            id=repo["id"],
            github_url=repo["github_url"],
            error_message=analysis_data.get("error_message", "Unknown error") if analysis_data else "Unknown error",
            created_at=datetime.fromisoformat(repo["created_at"]),
        )

    return RepositoryPending(
        id=repo["id"],
        github_url=repo["github_url"],
        created_at=datetime.fromisoformat(repo["created_at"]),
    )


@router.post("/{repo_id}/chat", response_model=ChatResponse, summary="Chat with a repository", tags=["chat"])
def chat_with_repository(repo_id: UUID, body: ChatRequest, supabase = Depends(get_db)):

    repo_response = supabase.table("repositories").select("id").eq("id", str(repo_id)).execute()
    if not repo_response.data:
        raise HTTPException(status_code=404, detail="Repository not found")

    chat_service = ChatService(supabase, str(repo_id))
    answer = chat_service.answer(body.question)

    chat_response = (
        supabase.table("chat_history")
        .insert({
            "repository_id": str(repo_id),
            "question": body.question,
            "answer": answer,
        })
        .execute()
    )

    if chat_response.data:
        row = chat_response.data[0]
        return ChatResponse(
            id=row["id"],
            repository_id=row["repository_id"],
            question=row["question"],
            answer=row["answer"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    raise HTTPException(status_code=500, detail="Failed to store chat message")


@router.get("/{repo_id}/chat", response_model=list[ChatResponse], summary="Get chat history", tags=["chat"])
def get_chat_history(repo_id: UUID, limit: int = Query(50, le=100), supabase = Depends(get_db)):

    response = (
        supabase.table("chat_history")
        .select("*")
        .eq("repository_id", str(repo_id))
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )

    return [
        ChatResponse(
            id=r["id"],
            repository_id=r["repository_id"],
            question=r["question"],
            answer=r.get("answer") or "",
            created_at=datetime.fromisoformat(r["created_at"]),
        )
        for r in (response.data or [])
    ]


@router.get("/{repo_id}/timeline", response_model=TimelineResponse, summary="Get commit timeline", tags=["timeline"])
def get_repository_timeline(repo_id: UUID,
    limit: int = Query(100, le=500),
    offset: int = 0,
    supabase = Depends(get_db),
):

    repo_response = supabase.table("repositories").select("id").eq("id", str(repo_id)).execute()
    if not repo_response.data:
        raise HTTPException(status_code=404, detail="Repository not found")

    commits_response = (
        supabase.table("commits")
        .select("*", count="exact")
        .eq("repository_id", str(repo_id))
        .order("commit_date", desc=True)
        .range(offset, offset + limit - 1)
        .execute()
    )

    total = commits_response.count or 0

    if total == 0:
        return TimelineResponse(events=[], stats=None)

    events = []
    for c in commits_response.data or []:
        message = c.get("message") or ""
        events.append(TimelineEvent(
            sha=c.get("commit_sha", ""),
            date=datetime.fromisoformat(c["commit_date"]) if c.get("commit_date") else None,
            author=c.get("author"),
            message=message[:200],
            is_fix=bool(_FIX_PATTERN.search(message)),
            is_merge=bool(_MERGE_PATTERN.search(message)),
        ))

    dates = sorted([
        c["commit_date"] for c in commits_response.data
        if c.get("commit_date")
    ]) if commits_response.data else []

    author_counts: dict[str, int] = {}
    for c in commits_response.data or []:
        author = c.get("author")
        if author:
            author_counts[author] = author_counts.get(author, 0) + 1

    stats = TimelineStats(
        total_commits=total,
        date_range={
            "start": dates[0] if dates else None,
            "end": dates[-1] if dates else None,
        },
        top_authors=sorted(author_counts, key=author_counts.get, reverse=True)[:5],
    )

    return TimelineResponse(events=events, stats=stats)


@router.get("/{repo_id}/graph", response_model=GraphResponse, summary="Get knowledge graph (nodes + edges)", tags=["graph"])
def get_repository_graph(repo_id: UUID,
    depth: int = Query(0, ge=0, le=5),
    focus: Optional[str] = Query(None),
    supabase = Depends(get_db),
):

    repo_response = supabase.table("repositories").select("id").eq("id", str(repo_id)).execute()
    if not repo_response.data:
        raise HTTPException(status_code=404, detail="Repository not found")

    files_response = (
        supabase.table("files")
        .select("id, file_path, language, size, content")
        .eq("repository_id", str(repo_id))
        .execute()
    )

    if not files_response.data:
        return GraphResponse()

    nodes = [
        GraphNode(
            id=f"file:{f['id']}",
            label=f["file_path"],
            type="file",
            language=f.get("language"),
            size=f.get("size"),
        )
        for f in files_response.data
    ]

    edges_response = (
        supabase.table("edges")
        .select("source_id, target_id, target_name")
        .eq("repository_id", str(repo_id))
        .eq("edge_type", "imports")
        .execute()
    )

    if edges_response.data:
        edges = [
            GraphEdge(
                source=f"file:{e['source_id']}",
                target=f"file:{e['target_id']}",
                type="imports",
                label=f"imports {e.get('target_name', '')}",
            )
            for e in edges_response.data
        ]
    else:
        edges = _build_edges_from_content(files_response.data, nodes)

    return GraphResponse(nodes=nodes, edges=edges)


def _extract_imports(content: str) -> list[str]:
    modules: list[str] = []
    for m in _IMPORT_PY.finditer(content):
        module = m.group(1) or m.group(2)
        if module:
            modules.append(module.split(".")[0])
    for m in _IMPORT_JS.finditer(content):
        module = m.group(1) or m.group(2)
        if module and not module.startswith("."):
            parts = module.split("/")
            modules.append(parts[0] if parts[0] else parts[1] if len(parts) > 1 else module)
    return list(dict.fromkeys(modules))


def _build_edges_from_content(files_data: list[dict], nodes: list[GraphNode]) -> list[GraphEdge]:
    """Fallback: parse imports from file content when edges table is empty."""
    file_index = {}
    for i, f in enumerate(files_data):
        file_index[f["file_path"]] = i

    edges = []
    for f in files_data:
        content = f.get("content") or ""
        if not content:
            continue

        source_id = f"file:{f['id']}"
        imports = _extract_imports(content)

        for module in imports:
            target_path = None
            for path in file_index:
                path_clean = path.replace("/", ".").replace(".py", "").replace(".ts", "").replace(".tsx", "").replace(".js", "").replace(".jsx", "")
                if module in path_clean or path_clean.endswith(module):
                    target_path = path
                    break

            if target_path and target_path != f["file_path"]:
                target_id = nodes[file_index[target_path]].id
                if target_id != source_id:
                    edges.append(GraphEdge(
                        source=source_id,
                        target=target_id,
                        type="imports",
                        label=f"imports {module}",
                    ))

    return edges
