from __future__ import annotations
import logging

from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_data_provider, get_cache
from app.mock.data_provider import DataProvider
from app.services.cache import ResponseCache
from app.models.health import FileHealthScore
from app.services.health_analyzer import compute_file_health

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/repos/{repo_id}", tags=["health"])

@router.get("/file_health", response_model=FileHealthScore)
async def get_file_health(
    repo_id: str,
    path: str,
    data: DataProvider = Depends(get_data_provider),
    cache: ResponseCache = Depends(get_cache),
):
    """
    Returns the Software DNA health badge data (complexity, churn, debt) for a specific file.
    """
    # Verify repo exists
    repo = await data.get_repository(repo_id)
    if not repo:
        raise HTTPException(status_code=404, detail=f"Repository '{repo_id}' not found")
        
    file_obj = await data.get_file_by_path(repo_id, path)
    if not file_obj:
        raise HTTPException(status_code=404, detail=f"File '{path}' not found")

    cache_key = [repo_id, "file_health", path]
    cached = cache.get(*cache_key)
    if cached:
        # We cached it as a dict, we can parse it back
        return FileHealthScore.parse_raw(cached) if isinstance(cached, str) else FileHealthScore(**cached)
        
    score = await compute_file_health(repo_id, path, data)
    
    cache.set(*cache_key, value=score.json())
    return score
