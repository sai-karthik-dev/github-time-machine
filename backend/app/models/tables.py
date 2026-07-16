from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class User(BaseModel):
    id: UUID
    github_id: int
    username: str
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: Optional[datetime] = None


class Repository(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    owner: str
    github_url: str
    default_branch: Optional[str] = "main"
    language: Optional[str] = None
    created_at: Optional[datetime] = None
    last_analyzed: Optional[datetime] = None


class Commit(BaseModel):
    id: UUID
    repository_id: UUID
    commit_sha: str
    author: Optional[str] = None
    author_email: Optional[str] = None
    committer_name: Optional[str] = None
    committer_email: Optional[str] = None
    message: Optional[str] = None
    summary: Optional[str] = None
    commit_date: Optional[datetime] = None


class FileRecord(BaseModel):
    id: UUID
    repository_id: UUID
    file_path: str
    language: Optional[str] = None
    size: Optional[int] = None
    content: Optional[str] = None
    embedding: Optional[list[float]] = None


class Analysis(BaseModel):
    id: UUID
    repository_id: UUID
    status: str = "pending"
    summary: Optional[str] = None
    risk_score: Optional[int] = None
    technical_debt: Optional[str] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None


class ChatMessage(BaseModel):
    id: UUID
    repository_id: UUID
    question: str
    answer: Optional[str] = None
    created_at: Optional[datetime] = None


class Function(BaseModel):
    id: UUID
    file_id: UUID
    repository_id: UUID
    name: str
    signature: Optional[str] = None
    start_line: int
    end_line: int
    is_exported: bool = False
    created_at: Optional[datetime] = None


class Edge(BaseModel):
    id: UUID
    repository_id: UUID
    source_id: UUID
    target_id: UUID
    edge_type: str
    source_name: Optional[str] = None
    target_name: Optional[str] = None
    metadata: Optional[dict] = None
    created_at: Optional[datetime] = None
