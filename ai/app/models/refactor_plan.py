from pydantic import BaseModel
from typing import Optional

class RefactorPlanRequest(BaseModel):
    since_days: int = 30

class RefactorPlanResponse(BaseModel):
    plan: str
