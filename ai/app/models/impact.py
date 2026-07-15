"""
Change Impact Simulator models.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class ImpactRequest(BaseModel):
    target: str  # file path to simulate changing
    change_type: str = "modify"  # "remove" | "modify" | "refactor"
    description: Optional[str] = None  # optional: what the change does


class AffectedFile(BaseModel):
    path: str
    relationship: str  # e.g. "DEPENDS_ON", "CALLS"
    risk_level: str  # "high" | "medium" | "low"
    reason: str  # why this file is affected


class ImpactResult(BaseModel):
    target: str
    change_type: str
    risk_score: float  # 0.0 - 1.0
    affected_files: list[AffectedFile] = []
    suggested_tests: list[str] = []
    ai_explanation: str = ""
    total_affected: int = 0
