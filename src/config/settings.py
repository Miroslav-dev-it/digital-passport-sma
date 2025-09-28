from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="CODEGEN_", case_sensitive=False)

    environment: Literal["dev", "prod"] = Field(default="dev")
    openai_api_key: str = Field(alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4.1-mini")
    database_url: str = Field(default="sqlite+aiosqlite:///./codegen.db")
    max_tokens_limit: int = Field(default=2048, gt=0)
    history_limit: int = Field(default=20, gt=0)


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
