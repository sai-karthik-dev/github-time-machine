from pydantic import BaseModel
from typing import Optional


class ImpactRequest(BaseModel):
    target: str
    change_type: str = "modify"
    description: Optional[str] = None


class AffectedFile(BaseModel):
    path: str
    relationship: str
    risk_level: str
    reason: str


class ImpactResult(BaseModel):
    target: str
    change_type: str
    risk_score: float
    affected_files: list[AffectedFile] = []
    suggested_tests: list[str] = []
