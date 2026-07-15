"""
Timeline event models for the commit timeline visualization.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TimelineEvent(BaseModel):
    id: str
    sha: str
    message: str
    author: str
    timestamp: datetime
    files_changed: int = 0
    additions: int = 0
    deletions: int = 0
    is_significant: bool = False  # large diff, fix commit, refactor
    event_type: str = "commit"  # "commit" | "fix" | "refactor" | "feature"
    tags: list[str] = []  # e.g. ["bugfix", "auth", "breaking"]
    affected_paths: list[str] = []


class TimelineResponse(BaseModel):
    repo_id: str
    events: list[TimelineEvent] = []
    total_events: int = 0
    date_range: Optional[dict] = None  # {"from": ..., "to": ...}
