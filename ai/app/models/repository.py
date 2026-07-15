"""
Core domain models matching the Postgres schema agreed in the roadmap:
  repositories, files, functions, commits, edges
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ── Enums ───────────────────────────────────────────────────────────────


class EdgeType(str, Enum):
    CALLS = "CALLS"
    DEPENDS_ON = "DEPENDS_ON"
    MODIFIES = "MODIFIES"
    AUTHORED_BY = "AUTHORED_BY"
    IMPORTED_BY = "IMPORTED_BY"


class Language(str, Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    GO = "go"
    RUST = "rust"
    OTHER = "other"


# ── Models ──────────────────────────────────────────────────────────────


class Repository(BaseModel):
    id: str
    name: str
    full_name: str  # e.g. "owner/repo"
    description: Optional[str] = None
    default_branch: str = "main"
    language: Optional[str] = None
    total_commits: int = 0
    total_files: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    analyzed_at: Optional[datetime] = None


class File(BaseModel):
    id: str
    repo_id: str
    path: str  # e.g. "src/auth/oauth.py"
    language: Language = Language.OTHER
    size_bytes: int = 0
    line_count: int = 0
    last_modified: datetime = Field(default_factory=datetime.utcnow)
    complexity_score: float = 0.0  # 0-100


class Function(BaseModel):
    id: str
    file_id: str
    repo_id: str
    name: str
    signature: str = ""  # e.g. "def authenticate(token: str) -> User"
    start_line: int = 1
    end_line: int = 1
    complexity: float = 0.0
    is_exported: bool = True


class Commit(BaseModel):
    id: str
    repo_id: str
    sha: str
    message: str
    author_name: str
    author_email: str = ""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    files_changed: int = 0
    additions: int = 0
    deletions: int = 0
    is_fix_commit: bool = False  # heuristic: message matches fix/bug/patch


class Edge(BaseModel):
    id: str
    repo_id: str
    source_id: str
    target_id: str
    edge_type: EdgeType
    weight: float = 1.0  # strength of relationship
    metadata: Optional[dict] = None
