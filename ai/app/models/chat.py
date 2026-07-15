"""
Chat / Architecture Explanation models.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant" | "system"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatRequest(BaseModel):
    message: str
    file_path: Optional[str] = None  # optional focus on a specific file
    function_name: Optional[str] = None  # optional focus on a specific function
    session_id: Optional[str] = None  # for conversation continuity
    stream: bool = True  # whether to use SSE streaming


class ChatResponse(BaseModel):
    """Non-streaming response (used when stream=false)."""
    answer: str
    session_id: str
    sources: list[str] = []  # file paths / commit SHAs used as context
    tokens_used: int = 0
