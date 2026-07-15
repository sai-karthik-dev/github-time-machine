"""
Technical Debt Heatmap models.
"""

from __future__ import annotations

from pydantic import BaseModel


class DebtScore(BaseModel):
    path: str
    language: str = "other"
    churn: int = 0  # number of commits modifying this file
    complexity: float = 0.0  # cyclomatic complexity estimate (0-100)
    age_days: int = 0  # days since last modification
    line_count: int = 0
    debt_score: float = 0.0  # composite: churn × complexity × recency
    risk_level: str = "low"  # "high" | "medium" | "low"


class HeatmapResponse(BaseModel):
    repo_id: str
    scores: list[DebtScore] = []
    average_debt: float = 0.0
    hotspot_count: int = 0  # files with risk_level == "high"
