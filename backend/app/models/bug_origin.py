from pydantic import BaseModel
from typing import Optional


class BugOriginRequest(BaseModel):
    file_path: str


class BugOriginResponse(BaseModel):
    file_path: str
    culprit_commit_sha: Optional[str] = None
    ai_explanation: str
