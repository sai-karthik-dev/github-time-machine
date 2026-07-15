from __future__ import annotations
import logging

from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_openai_client, get_prompt_engine, get_data_provider, get_cache
from app.mock.data_provider import DataProvider
from app.services.openai_client import OpenAIClient
from app.services.prompt_engine import PromptEngine
from app.services.cache import ResponseCache
from app.models.refactor_plan import RefactorPlanRequest, RefactorPlanResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/repos/{repo_id}", tags=["refactor_plan"])

@router.post("/refactor_plan", response_model=RefactorPlanResponse)
async def generate_refactor_plan(
    repo_id: str,
    request: RefactorPlanRequest,
    openai: OpenAIClient = Depends(get_openai_client),
    prompts: PromptEngine = Depends(get_prompt_engine),
    data: DataProvider = Depends(get_data_provider),
    cache: ResponseCache = Depends(get_cache),
):
    """
    Generates a step-by-step refactoring plan based on recent refactor commits.
    """
    repo = await data.get_repository(repo_id)
    if not repo:
        raise HTTPException(status_code=404, detail=f"Repository '{repo_id}' not found")
        
    cache_key = [repo_id, "refactor_plan", str(request.since_days)]
    cached = cache.get(*cache_key)
    if cached:
        return RefactorPlanResponse.parse_raw(cached) if isinstance(cached, str) else RefactorPlanResponse(**cached)
        
    commits = await data.get_commits(repo_id)
    # The timeline endpoint uses a heuristic or the data provider sets event_type.
    # For this endpoint, we'll use a simple heuristic to find refactor commits.
    refactor_commits = [c for c in commits if "refactor" in c.message.lower() or "cleanup" in c.message.lower()]
    
    system_prompt = prompts.render("system.j2")
    refactor_plan_prompt = prompts.render(
        "refactor_plan.j2",
        repo=repo,
        refactor_commits=refactor_commits[:20]
    )
    
    ai_plan = await openai.complete([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": refactor_plan_prompt},
    ])
    
    response = RefactorPlanResponse(plan=ai_plan)
    
    cache.set(*cache_key, value=response.json())
    return response
