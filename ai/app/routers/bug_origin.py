from __future__ import annotations
import logging
import re

from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_openai_client, get_prompt_engine, get_data_provider, get_cache
from app.mock.data_provider import DataProvider
from app.services.openai_client import OpenAIClient
from app.services.prompt_engine import PromptEngine
from app.services.cache import ResponseCache
from app.models.bug_origin import BugOriginRequest, BugOriginResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/repos/{repo_id}", tags=["bug_origin"])

@router.post("/bug_origin", response_model=BugOriginResponse)
async def analyze_bug_origin(
    repo_id: str,
    request: BugOriginRequest,
    openai: OpenAIClient = Depends(get_openai_client),
    prompts: PromptEngine = Depends(get_prompt_engine),
    data: DataProvider = Depends(get_data_provider),
    cache: ResponseCache = Depends(get_cache),
):
    """
    Analyzes the bug origin for a given file and identifies the culprit commit.
    """
    repo = await data.get_repository(repo_id)
    if not repo:
        raise HTTPException(status_code=404, detail=f"Repository '{repo_id}' not found")
        
    cache_key = [repo_id, "bug_origin", request.file_path]
    cached = cache.get(*cache_key)
    if cached:
        return BugOriginResponse.parse_raw(cached) if isinstance(cached, str) else BugOriginResponse(**cached)
        
    commits = await data.get_commits(repo_id, file_path=request.file_path)
    fix_commits = [c for c in commits if c.is_fix_commit]
    
    # Simple heuristic to get surrounding commits
    surrounding_commits = []
    if fix_commits:
        # just get some of the regular commits as surrounding context
        surrounding_commits = [c for c in commits if not c.is_fix_commit][:10]
        
    edges = await data.get_edges(repo_id)
    
    system_prompt = prompts.render("system.j2")
    bug_origin_prompt = prompts.render(
        "bug_origin.j2",
        repo=repo,
        file_path=request.file_path,
        fix_commits=fix_commits,
        surrounding_commits=surrounding_commits,
        edges=edges[:20]
    )
    
    ai_explanation = await openai.complete([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": bug_origin_prompt},
    ])
    
    # Try to extract a commit SHA from the first few lines of the response
    culprit_commit_sha = None
    match = re.search(r'\b([a-f0-9]{7,40})\b', ai_explanation.split('\n')[0].lower())
    if match:
        culprit_commit_sha = match.group(1)
        
    response = BugOriginResponse(
        file_path=request.file_path,
        culprit_commit_sha=culprit_commit_sha,
        ai_explanation=ai_explanation
    )
    
    cache.set(*cache_key, value=response.json())
    return response
