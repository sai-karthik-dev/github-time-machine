from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from app.core.supabase import get_supabase
from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    RepositoryCompleted,
    RepositoryError,
    RepositoryListItem,
    RepositoryListResponse,
    RepositoryPending,
    RepositoryProcessing,
    RepositoryResponse,
    RepositorySubmitRequest,
)

router = APIRouter(prefix="/repositories", tags=["repositories"])


@router.post("/", response_model=RepositoryResponse, status_code=202)
async def submit_repository(body: RepositorySubmitRequest):
    supabase = get_supabase()

    repo_response = (
        supabase.table("repositories")
        .insert({"github_url": body.github_url})
        .execute()
    )
    if not repo_response.data:
        raise HTTPException(status_code=500, detail="Failed to create repository")

    repo = repo_response.data[0]

    supabase.table("analyses").insert({
        "repository_id": repo["id"],
        "status": "pending",
    }).execute()

    return RepositoryPending(
        id=repo["id"],
        github_url=repo["github_url"],
        created_at=datetime.fromisoformat(repo["created_at"]),
    )


@router.get("/", response_model=RepositoryListResponse)
async def list_repositories(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    limit: int = Query(20, le=100),
    offset: int = 0,
):
    supabase = get_supabase()

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


@router.get("/{repo_id}", response_model=RepositoryResponse)
async def get_repository_status(repo_id: UUID):
    supabase = get_supabase()

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

    status = "pending"
    analysis_data = None
    if analysis_response.data:
        analysis_data = analysis_response.data[0]
        status = analysis_data.get("status", "pending")

    files_count = (
        supabase.table("files").select("id", count="exact").eq("repository_id", str(repo_id)).execute()
    ).count or 0

    commits_count = (
        supabase.table("commits").select("id", count="exact").eq("repository_id", str(repo_id)).execute()
    ).count or 0

    if status == "completed":
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

    if status == "processing":
        return RepositoryProcessing(
            id=repo["id"],
            github_url=repo["github_url"],
            started_at=datetime.fromisoformat(analysis_data["started_at"])
                if analysis_data and analysis_data.get("started_at") else None,
            created_at=datetime.fromisoformat(repo["created_at"]),
        )

    if status == "error":
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


@router.post("/{repo_id}/chat", response_model=ChatResponse)
async def chat_with_repository(repo_id: UUID, body: ChatRequest):
    supabase = get_supabase()

    repo_response = supabase.table("repositories").select("id").eq("id", str(repo_id)).execute()
    if not repo_response.data:
        raise HTTPException(status_code=404, detail="Repository not found")

    answer = f"[placeholder] RAG response for: {body.question}"

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


@router.get("/{repo_id}/chat", response_model=list[ChatResponse])
async def get_chat_history(repo_id: UUID, limit: int = Query(50, le=100)):
    supabase = get_supabase()

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
