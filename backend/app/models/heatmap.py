"""
Technical Debt Heatmap models.
"""

from __future__ import annotations

from pydantic import BaseModel


class DebtScore(BaseModel):
    path: str
    language: str = "other"
    churn: int = 0
    complexity: float = 0.0
    age_days: int = 0
    line_count: int = 0
    debt_score: float = 0.0
    risk_level: str = "low"


class HeatmapResponse(BaseModel):
    repo_id: str
    scores: list[DebtScore] = []
    average_debt: float = 0.0
    hotspot_count: int = 0
