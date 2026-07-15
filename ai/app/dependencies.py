from __future__ import annotations

from functools import lru_cache

from app.config import Settings, settings
from app.mock.data_provider import DataProvider, MockDataProvider
from app.services.openai_client import OpenAIClient
from app.services.prompt_engine import PromptEngine
from app.services.cache import ResponseCache


# ── Singletons ──────────────────────────────────────────────────────────


@lru_cache
def get_settings() -> Settings:
    return settings


@lru_cache
def get_openai_client() -> OpenAIClient:
    return OpenAIClient(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
        max_tokens=settings.openai_max_tokens,
        temperature=settings.openai_temperature,
    )


@lru_cache
def get_prompt_engine() -> PromptEngine:
    return PromptEngine()


@lru_cache
def get_data_provider() -> DataProvider:
    """
    Returns mock data for now.
    Swap to SupabaseDataProvider once the real DB is ready.
    """
    return MockDataProvider()


@lru_cache
def get_cache() -> ResponseCache:
    return ResponseCache(
        max_size=settings.cache_max_size,
        ttl_seconds=settings.cache_ttl_seconds,
    )
