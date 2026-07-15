"""
POST /repos/{repo_id}/impact — Change Impact Simulator

Traverses DEPENDS_ON and CALLS edges from a target file,
builds a dependency chain, and feeds it to GPT to predict
what breaks and suggest tests.
"""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_openai_client, get_prompt_engine, get_data_provider, get_cache
from app.models.impact import ImpactRequest, ImpactResult, AffectedFile
from app.mock.data_provider import DataProvider
from app.services.openai_client import OpenAIClient
from app.services.prompt_engine import PromptEngine
from app.services.cache import ResponseCache

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/repos/{repo_id}", tags=["impact"])


def _compute_risk_score(affected: list[AffectedFile]) -> float:
    """Compute an overall risk score from the affected files."""
    if not affected:
        return 0.0
    weights = {"high": 1.0, "medium": 0.5, "low": 0.2}
    total = sum(weights.get(f.risk_level, 0.1) for f in affected)
    return min(1.0, total / max(len(affected), 1))


@router.post("/impact", response_model=ImpactResult)
async def impact_analysis(
    repo_id: str,
    request: ImpactRequest,
    openai: OpenAIClient = Depends(get_openai_client),
    prompts: PromptEngine = Depends(get_prompt_engine),
    data: DataProvider = Depends(get_data_provider),
    cache: ResponseCache = Depends(get_cache),
):
    """
    Simulate the impact of changing or removing a file.
    Traverses dependency edges and asks GPT for breakage analysis.
    """
    repo = await data.get_repository(repo_id)
    if not repo:
        raise HTTPException(status_code=404, detail=f"Repository '{repo_id}' not found")

    target_file = await data.get_file_by_path(repo_id, request.target)
    all_files = await data.get_files(repo_id)
    all_edges = await data.get_edges(repo_id)
    files_map = {f.id: f for f in all_files}
    path_to_id = {f.path: f.id for f in all_files}

    if not target_file:
        raise HTTPException(status_code=404, detail=f"File '{request.target}' not found")

    target_id = target_file.id

    # ── Find all dependents (files that depend on or call the target) ──
    dependents: list[dict] = []
    for edge in all_edges:
        if edge.target_id == target_id and edge.edge_type.value in ("DEPENDS_ON", "CALLS", "IMPORTED_BY"):
            source_file = files_map.get(edge.source_id)
            if source_file:
                fns = await data.get_functions(repo_id, file_path=source_file.path)
                dependents.append({
                    "path": source_file.path,
                    "relationship": edge.edge_type.value,
                    "functions": [fn.name for fn in fns],
                })

    # Also find what the target depends on (reverse deps)
    reverse_deps: list[dict] = []
    for edge in all_edges:
        if edge.source_id == target_id and edge.edge_type.value in ("DEPENDS_ON", "CALLS"):
            dep_file = files_map.get(edge.target_id)
            if dep_file:
                reverse_deps.append({
                    "path": dep_file.path,
                    "relationship": edge.edge_type.value,
                })

    # Get recent commits touching the target
    recent_commits = await data.get_commits(repo_id, file_path=request.target)

    # ── Build affected files list from edge traversal ──
    affected_files: list[AffectedFile] = []
    for dep in dependents:
        risk = "high" if dep["relationship"] == "DEPENDS_ON" else "medium"
        affected_files.append(AffectedFile(
            path=dep["path"],
            relationship=dep["relationship"],
            risk_level=risk,
            reason=f"This file has a {dep['relationship']} relationship with {request.target}",
        ))

    # ── Check cache ──
    cache_key = [repo_id, "impact", request.target, request.change_type]
    cached = cache.get(*cache_key)

    if cached:
        return ImpactResult(
            target=request.target,
            change_type=request.change_type,
            risk_score=_compute_risk_score(affected_files),
            affected_files=affected_files,
            suggested_tests=[],
            ai_explanation=cached,
            total_affected=len(affected_files),
        )

    # ── Ask GPT for detailed analysis ──
    system_prompt = prompts.render("system.j2")
    impact_prompt = prompts.render(
        "impact_analysis.j2",
        repo=repo,
        target_path=request.target,
        target_file=target_file,
        change_type=request.change_type,
        description=request.description,
        dependencies=dependents,
        reverse_deps=reverse_deps,
        recent_commits=recent_commits[:5],
    )

    ai_explanation = await openai.complete([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": impact_prompt},
    ])

    cache.set(*cache_key, value=ai_explanation)

    # Extract suggested tests from AI response (simple heuristic)
    suggested_tests = []
    for line in ai_explanation.split("\n"):
        line_lower = line.lower().strip()
        if any(kw in line_lower for kw in ["test_", "pytest", "should test", "write a test", "unit test"]):
            clean = line.strip().lstrip("-•*").strip()
            if clean:
                suggested_tests.append(clean)

    return ImpactResult(
        target=request.target,
        change_type=request.change_type,
        risk_score=_compute_risk_score(affected_files),
        affected_files=affected_files,
        suggested_tests=suggested_tests[:10],
        ai_explanation=ai_explanation,
        total_affected=len(affected_files),
    )
