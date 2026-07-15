"""
POST /repos/{repo_id}/chat — Architecture Explanation (Architect's Memory)

Supports both SSE streaming and one-shot JSON responses.
Builds context from the repo's graph, commits, and file data,
then sends it to OpenAI for a rich architectural explanation.
"""

from __future__ import annotations

import json
import uuid
import logging
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException
from sse_starlette.sse import EventSourceResponse

from app.dependencies import get_openai_client, get_prompt_engine, get_data_provider, get_cache
from app.models.chat import ChatRequest, ChatResponse
from app.mock.data_provider import DataProvider
from app.services.openai_client import OpenAIClient
from app.services.prompt_engine import PromptEngine
from app.services.cache import ResponseCache

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/repos/{repo_id}", tags=["chat"])

# In-memory chat sessions (swap for DB table later)
_sessions: dict[str, list[dict]] = {}


async def _build_context(
    repo_id: str,
    request: ChatRequest,
    data: DataProvider,
    prompts: PromptEngine,
) -> list[dict[str, str]]:
    """Build the message list with system prompt + graph context + user question."""

    repo = await data.get_repository(repo_id)
    if not repo:
        raise HTTPException(status_code=404, detail=f"Repository '{repo_id}' not found")

    # Gather context
    target_file = None
    functions = []
    commits = await data.get_commits(repo_id, file_path=request.file_path)
    edges = await data.get_edges(repo_id)

    if request.file_path:
        target_file = await data.get_file_by_path(repo_id, request.file_path)
        functions = await data.get_functions(repo_id, file_path=request.file_path)

    target_function = None
    if request.function_name:
        all_fns = await data.get_functions(repo_id)
        for fn in all_fns:
            if fn.name == request.function_name:
                target_function = fn
                break

    # System prompt
    system_prompt = prompts.render("system.j2")

    # Context prompt
    context_prompt = prompts.render(
        "architecture_explain.j2",
        repo=repo,
        target_file=target_file,
        target_function=target_function,
        functions=functions,
        commits=commits[:20],
        edges=edges[:30],
        question=request.message,
    )

    messages = [
        {"role": "system", "content": system_prompt},
    ]

    # Add conversation history if session exists
    session_id = request.session_id
    if session_id and session_id in _sessions:
        messages.extend(_sessions[session_id])

    messages.append({"role": "user", "content": context_prompt})

    return messages


@router.post("/chat")
async def chat(
    repo_id: str,
    request: ChatRequest,
    openai: OpenAIClient = Depends(get_openai_client),
    prompts: PromptEngine = Depends(get_prompt_engine),
    data: DataProvider = Depends(get_data_provider),
    cache: ResponseCache = Depends(get_cache),
):
    """
    Architecture explanation endpoint.
    - stream=true (default): returns SSE event stream
    - stream=false: returns JSON response
    """
    messages = await _build_context(repo_id, request, data, prompts)
    session_id = request.session_id or str(uuid.uuid4())

    # ── Non-streaming response ──────────────────────────────────────
    if not request.stream:
        # Check cache
        cache_key_parts = [repo_id, request.message, request.file_path or "", request.function_name or ""]
        cached = cache.get(*cache_key_parts)
        if cached:
            return ChatResponse(
                answer=cached,
                session_id=session_id,
                sources=[request.file_path] if request.file_path else [],
                tokens_used=0,
            )

        answer = await openai.complete(messages)

        # Cache the response
        cache.set(*cache_key_parts, value=answer)

        # Store in session
        if session_id not in _sessions:
            _sessions[session_id] = []
        _sessions[session_id].append({"role": "user", "content": request.message})
        _sessions[session_id].append({"role": "assistant", "content": answer})

        return ChatResponse(
            answer=answer,
            session_id=session_id,
            sources=[request.file_path] if request.file_path else [],
            tokens_used=openai.total_tokens_used,
        )

    # ── SSE streaming response ──────────────────────────────────────
    async def event_generator() -> AsyncGenerator[dict, None]:
        full_response = ""
        try:
            # Send session_id first
            yield {"event": "session", "data": json.dumps({"session_id": session_id})}

            async for token in openai.stream(messages):
                full_response += token
                yield {"event": "token", "data": json.dumps({"token": token})}

            # Store in session
            if session_id not in _sessions:
                _sessions[session_id] = []
            _sessions[session_id].append({"role": "user", "content": request.message})
            _sessions[session_id].append({"role": "assistant", "content": full_response})

            yield {"event": "done", "data": json.dumps({"session_id": session_id, "total_length": len(full_response)})}

        except Exception as e:
            logger.error("Streaming error: %s", e)
            yield {"event": "error", "data": json.dumps({"error": str(e)})}

    return EventSourceResponse(event_generator())
