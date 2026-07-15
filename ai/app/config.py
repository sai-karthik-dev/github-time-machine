
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration — every value can be overridden via env vars."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── OpenAI ──────────────────────────────────────────────────────────
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_max_tokens: int = 2048
    openai_temperature: float = 0.4

    # ── Server ──────────────────────────────────────────────────────────
    cors_origins: str = "http://localhost:3000"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8001

    # ── Cache ───────────────────────────────────────────────────────────
    cache_max_size: int = 256
    cache_ttl_seconds: int = 3600

    @property
    def cors_origin_list(self) -> list[str]:
        """Parse comma-separated CORS origins into a list."""
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
