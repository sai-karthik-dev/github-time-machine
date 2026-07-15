"""
GET /repos/{repo_id}/timeline — Timeline Events

Returns commits grouped by time period with significance flags.
Uses bug-origin heuristic to flag fix commits.
"""

from __future__ import annotations

import re
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.dependencies import get_data_provider
from app.mock.data_provider import DataProvider
from app.models.timeline import TimelineEvent, TimelineResponse

router = APIRouter(prefix="/repos/{repo_id}", tags=["timeline"])

# Patterns for classifying commit types
_FIX_PATTERNS = re.compile(
    r"\b(fix|bug|patch|hotfix|resolve|repair|correct)\b", re.IGNORECASE
)
_REFACTOR_PATTERNS = re.compile(
    r"\b(refactor|restructure|reorganize|cleanup|clean up|simplify)\b", re.IGNORECASE
)
_FEATURE_PATTERNS = re.compile(
    r"\b(add|implement|introduce|create|new|feature)\b", re.IGNORECASE
)
_SECURITY_PATTERNS = re.compile(
    r"\b(security|csrf|xss|injection|auth|vulnerability|cve)\b", re.IGNORECASE
)


def _classify_commit(message: str, files_changed: int, additions: int, deletions: int) -> tuple[str, list[str], bool]:
    """Classify a commit by type, tags, and significance."""
    tags: list[str] = []
    event_type = "commit"

    if _FIX_PATTERNS.search(message):
        event_type = "fix"
        tags.append("bugfix")

    if _REFACTOR_PATTERNS.search(message):
        event_type = "refactor"
        tags.append("refactor")

    if _FEATURE_PATTERNS.search(message):
        if event_type == "commit":
            event_type = "feature"
        tags.append("feature")

    if _SECURITY_PATTERNS.search(message):
        tags.append("security")

    # Detect module from message
    for module in ["auth", "billing", "api", "team", "notification", "config"]:
        if module in message.lower():
            tags.append(module)

    # Significance: large diffs, fix commits, or refactors
    is_significant = (
        files_changed >= 4
        or additions + deletions >= 100
        or event_type in ("fix", "refactor")
    )

    return event_type, tags, is_significant


@router.get("/timeline", response_model=TimelineResponse)
async def get_timeline(
    repo_id: str,
    from_date: Optional[str] = Query(None, alias="from", description="Start date (YYYY-MM-DD)"),
    to_date: Optional[str] = Query(None, alias="to", description="End date (YYYY-MM-DD)"),
    limit: int = Query(100, ge=1, le=500),
    data: DataProvider = Depends(get_data_provider),
):
    """
    Return timeline events (commits) for the repository.
    Optionally filter by date range.
    """
    repo = await data.get_repository(repo_id)
    if not repo:
        raise HTTPException(status_code=404, detail=f"Repository '{repo_id}' not found")

    commits = await data.get_commits(repo_id)

    # Date filtering
    if from_date:
        from datetime import datetime
        try:
            from_dt = datetime.strptime(from_date, "%Y-%m-%d")
            commits = [c for c in commits if c.timestamp >= from_dt]
        except ValueError:
            pass

    if to_date:
        from datetime import datetime
        try:
            to_dt = datetime.strptime(to_date, "%Y-%m-%d")
            commits = [c for c in commits if c.timestamp <= to_dt]
        except ValueError:
            pass

    # Build timeline events
    events: list[TimelineEvent] = []
    for commit in commits[:limit]:
        event_type, tags, is_significant = _classify_commit(
            commit.message, commit.files_changed, commit.additions, commit.deletions
        )
        events.append(TimelineEvent(
            id=commit.id,
            sha=commit.sha,
            message=commit.message,
            author=commit.author_name,
            timestamp=commit.timestamp,
            files_changed=commit.files_changed,
            additions=commit.additions,
            deletions=commit.deletions,
            is_significant=is_significant,
            event_type=event_type,
            tags=tags,
            affected_paths=[],  # Would be populated from real git data
        ))

    date_range = None
    if events:
        timestamps = [e.timestamp for e in events]
        date_range = {
            "from": min(timestamps).isoformat(),
            "to": max(timestamps).isoformat(),
        }

    return TimelineResponse(
        repo_id=repo_id,
        events=events,
        total_events=len(events),
        date_range=date_range,
    )
