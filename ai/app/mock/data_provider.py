"""
DataProvider interface and mock implementation.

The interface defines how AI services access repo data.
MockDataProvider returns realistic sample data so the AI layer
can be developed and demoed without a live database.

When the real Supabase DB is ready, create a SupabaseDataProvider
implementing the same interface — zero changes to AI logic.
"""

from __future__ import annotations

from typing import Optional, Protocol, runtime_checkable

from app.models.repository import Repository, File, Function, Commit, Edge
from app.models.heatmap import DebtScore


# ── Interface ───────────────────────────────────────────────────────────


@runtime_checkable
class DataProvider(Protocol):
    """
    Contract for accessing repository analysis data.
    Implement this for each storage backend.
    """

    async def get_repository(self, repo_id: str) -> Optional[Repository]: ...

    async def get_files(self, repo_id: str) -> list[File]: ...

    async def get_file_by_path(self, repo_id: str, path: str) -> Optional[File]: ...

    async def get_functions(
        self, repo_id: str, file_path: Optional[str] = None
    ) -> list[Function]: ...

    async def get_commits(
        self, repo_id: str, file_path: Optional[str] = None
    ) -> list[Commit]: ...

    async def get_edges(
        self, repo_id: str, source_id: Optional[str] = None
    ) -> list[Edge]: ...

    async def get_debt_scores(self, repo_id: str) -> list[DebtScore]: ...


# ── Mock Implementation ────────────────────────────────────────────────


class MockDataProvider:
    """
    In-memory mock that returns realistic sample data.
    Supports a single demo repo with id "demo".
    """

    def __init__(self):
        from app.mock.sample_repo import MOCK_REPO, MOCK_FILES, MOCK_FUNCTIONS, MOCK_COMMITS, MOCK_EDGES, MOCK_DEBT_SCORES
        self._repo = MOCK_REPO
        self._files = MOCK_FILES
        self._functions = MOCK_FUNCTIONS
        self._commits = MOCK_COMMITS
        self._edges = MOCK_EDGES
        self._debt_scores = MOCK_DEBT_SCORES

    async def get_repository(self, repo_id: str) -> Optional[Repository]:
        if repo_id == "demo" or repo_id == self._repo.id:
            return self._repo
        return None

    async def get_files(self, repo_id: str) -> list[File]:
        return [f for f in self._files if f.repo_id == repo_id or repo_id == "demo"]

    async def get_file_by_path(self, repo_id: str, path: str) -> Optional[File]:
        for f in self._files:
            if f.path == path and (f.repo_id == repo_id or repo_id == "demo"):
                return f
        return None

    async def get_functions(
        self, repo_id: str, file_path: Optional[str] = None
    ) -> list[Function]:
        results = [
            fn for fn in self._functions
            if fn.repo_id == repo_id or repo_id == "demo"
        ]
        if file_path:
            # Find file id for this path
            file_ids = {f.id for f in self._files if f.path == file_path}
            results = [fn for fn in results if fn.file_id in file_ids]
        return results

    async def get_commits(
        self, repo_id: str, file_path: Optional[str] = None
    ) -> list[Commit]:
        commits = [
            c for c in self._commits
            if c.repo_id == repo_id or repo_id == "demo"
        ]
        if file_path:
            # In a real implementation, this would filter by commits touching the file.
            # For mock purposes, we return commits that mention the file path or
            # a subset based on the file's apparent module.
            module = file_path.split("/")[0] if "/" in file_path else ""
            if module:
                # Return commits whose message or changed files relate to the module
                filtered = [
                    c for c in commits
                    if module.lower() in c.message.lower()
                ]
                if filtered:
                    return sorted(filtered, key=lambda c: c.timestamp, reverse=True)
        return sorted(commits, key=lambda c: c.timestamp, reverse=True)

    async def get_edges(
        self, repo_id: str, source_id: Optional[str] = None
    ) -> list[Edge]:
        edges = [
            e for e in self._edges
            if e.repo_id == repo_id or repo_id == "demo"
        ]
        if source_id:
            edges = [e for e in edges if e.source_id == source_id]
        return edges

    async def get_debt_scores(self, repo_id: str) -> list[DebtScore]:
        return list(self._debt_scores)
