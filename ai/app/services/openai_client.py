"""
Async OpenAI client wrapper with streaming, retries, and token tracking.
"""

from __future__ import annotations

import logging
from typing import AsyncGenerator

from openai import AsyncOpenAI, APIError, RateLimitError

logger = logging.getLogger(__name__)


class OpenAIClient:
    """Thin wrapper around the OpenAI async SDK."""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        max_tokens: int = 2048,
        temperature: float = 0.4,
    ):
        self._client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self._total_tokens_used = 0

    # ── One-shot completion ─────────────────────────────────────────────

    async def complete(
        self,
        messages: list[dict[str, str]],
        *,
        model: str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> str:
        """Send messages and return the full assistant response."""
        retries = 3
        for attempt in range(retries):
            try:
                response = await self._client.chat.completions.create(
                    model=model or self.model,
                    messages=messages,
                    max_tokens=max_tokens or self.max_tokens,
                    temperature=temperature if temperature is not None else self.temperature,
                )
                usage = response.usage
                if usage:
                    self._total_tokens_used += usage.total_tokens
                    logger.debug(
                        "OpenAI usage: prompt=%d completion=%d total=%d",
                        usage.prompt_tokens,
                        usage.completion_tokens,
                        usage.total_tokens,
                    )
                return response.choices[0].message.content or ""

            except RateLimitError:
                if attempt < retries - 1:
                    import asyncio
                    wait = 2 ** (attempt + 1)
                    logger.warning("Rate limited, retrying in %ds…", wait)
                    await asyncio.sleep(wait)
                else:
                    raise
            except APIError as e:
                logger.error("OpenAI API error: %s", e)
                raise

    # ── Streaming completion ────────────────────────────────────────────

    async def stream(
        self,
        messages: list[dict[str, str]],
        *,
        model: str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> AsyncGenerator[str, None]:
        """Stream tokens one chunk at a time for SSE."""
        try:
            response = await self._client.chat.completions.create(
                model=model or self.model,
                messages=messages,
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature if temperature is not None else self.temperature,
                stream=True,
            )
            async for chunk in response:
                delta = chunk.choices[0].delta
                if delta.content:
                    yield delta.content

        except APIError as e:
            logger.error("OpenAI streaming error: %s", e)
            yield f"\n\n[Error: {e.message}]"

    # ── Stats ───────────────────────────────────────────────────────────

    @property
    def total_tokens_used(self) -> int:
        return self._total_tokens_used

    async def health_check(self) -> bool:
        """Quick check that the API key is valid."""
        try:
            await self._client.models.list()
            return True
        except Exception:
            return False
