"""Service settings using Pydantic."""
from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuration for the CodeGen service."""

    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field("gpt-4.1-mini", env="OPENAI_MODEL")
    db_url: str = Field("sqlite+aiosqlite:///./dev.db", env="DB_URL")
    max_tokens_out: int = Field(2048, ge=64, le=8192)
    rb_secret_patterns: list[str] = Field(
        default=[
            "AKIA[0-9A-Z]{16}",
            "AIza[0-9A-Za-z\\-_]{35}",
            "sk-[A-Za-z0-9]{20,}",
        ]
    )

    class Config:
        env_file = ".env"
