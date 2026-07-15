from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class FileEmbedding(BaseModel):
    id: UUID
    repository_id: UUID
    file_path: str
    content: str
    language: Optional[str] = None
    embedding: Optional[list[float]] = None


class CodeChunk(BaseModel):
    file_path: str
    chunk_index: int
    content: str
    language: Optional[str] = None
    embedding: Optional[list[float]] = None
