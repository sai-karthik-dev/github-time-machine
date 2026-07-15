"""
GET /repos/{repo_id}/heatmap — Technical Debt Heatmap

Returns per-file debt scores shaped for treemap visualization.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_data_provider
from app.mock.data_provider import DataProvider
from app.models.heatmap import HeatmapResponse

router = APIRouter(prefix="/repos/{repo_id}", tags=["heatmap"])


@router.get("/heatmap", response_model=HeatmapResponse)
async def get_heatmap(
    repo_id: str,
    data: DataProvider = Depends(get_data_provider),
):
    """
    Return technical debt heatmap data for the repository.
    Each file gets a composite debt score based on churn, complexity, and recency.
    """
    repo = await data.get_repository(repo_id)
    if not repo:
        raise HTTPException(status_code=404, detail=f"Repository '{repo_id}' not found")

    scores = await data.get_debt_scores(repo_id)

    # Sort by debt score descending (hottest files first)
    scores.sort(key=lambda s: s.debt_score, reverse=True)

    # Compute aggregate stats
    avg_debt = sum(s.debt_score for s in scores) / len(scores) if scores else 0.0
    hotspot_count = sum(1 for s in scores if s.risk_level == "high")

    return HeatmapResponse(
        repo_id=repo_id,
        scores=scores,
        average_debt=round(avg_debt, 2),
        hotspot_count=hotspot_count,
    )
