"""FastAPI interface layer for the CodeGen Service."""
from __future__ import annotations

from functools import lru_cache
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from application.plugins import PluginManager, PythonBlackFormat, TrimTrailingSpaces
from application.rb_gates import RBGates
from application.use_cases import GenerateCodeUseCase, GetHistoryUseCase
from domain.entities import GenerationRequest
from infrastructure.config import Settings
from infrastructure.db.repository import HistoryRepository, make_session_factory
from infrastructure.openai_adapter import OpenAIAdapter

app = FastAPI(title="CodeGen Service", version="1.0.0")


class GenerateIn(BaseModel):
    prompt: str = Field(min_length=1, max_length=8000)
    language: str = Field(pattern="^(python|javascript|go)$")
    max_tokens: int = Field(default=1024, ge=64, le=8192)
    temperature: float = Field(default=0.2, ge=0, le=2)
    plugins: list[str] = Field(default_factory=list)


class GenerateOut(BaseModel):
    id: str
    code: str
    language: str
    metadata: dict


@lru_cache()
def get_settings() -> Settings:
    return Settings()


@lru_cache()
def get_db_components():
    settings = get_settings()
    return make_session_factory(settings.db_url)


@lru_cache()
def get_repository() -> HistoryRepository:
    session_factory, engine = get_db_components()
    return HistoryRepository(session_factory, engine)


@lru_cache()
def get_plugin_manager() -> PluginManager:
    return PluginManager([TrimTrailingSpaces(), PythonBlackFormat()])


@lru_cache()
def get_generate_use_case() -> GenerateCodeUseCase:
    settings = get_settings()
    repository = get_repository()
    plugin_manager = get_plugin_manager()
    rb_gates = RBGates(settings.rb_secret_patterns, model_expected=settings.openai_model)
    llm = OpenAIAdapter(settings.openai_api_key, settings.openai_model)
    return GenerateCodeUseCase(llm, rb_gates, repository, plugin_manager)


@lru_cache()
def get_history_use_case() -> GetHistoryUseCase:
    return GetHistoryUseCase(get_repository())


def get_di():
    """Expose dependencies for testing convenience."""
    settings = get_settings()
    repository = get_repository()
    generate_use_case = get_generate_use_case()
    return settings, repository, generate_use_case


def reset_dependency_cache() -> None:
    """Clear cached singletons (useful for tests)."""
    get_generate_use_case.cache_clear()
    get_history_use_case.cache_clear()
    get_plugin_manager.cache_clear()
    get_repository.cache_clear()
    get_db_components.cache_clear()
    get_settings.cache_clear()


@app.on_event("startup")
async def on_startup() -> None:
    repository = get_repository()
    await repository.init_db()
    app.state.model = get_settings().openai_model


@app.get("/health")
async def health():
    return {"status": "ok", "model": getattr(app.state, "model", "unknown")}


@app.post("/generate", response_model=GenerateOut)
async def generate(payload: GenerateIn):
    _, _, use_case = get_di()
    request = GenerationRequest(
        prompt=payload.prompt,
        language=payload.language,
        max_tokens=payload.max_tokens,
        temperature=payload.temperature,
        plugin_names=tuple(payload.plugins),
    )
    try:
        generation_id, result = await use_case.execute(request)
    except ValueError as exc:  # domain validation errors
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "id": generation_id,
        "code": result.code,
        "language": result.language,
        "metadata": {
            "tokens_in": result.tokens_in,
            "tokens_out": result.tokens_out,
            "model": result.model,
            "rb_flags": list(result.rb_flags),
        },
    }


@app.get("/history")
async def history(
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    language: Annotated[str | None, Query(pattern="^(python|javascript|go)$")] = None,
):
    use_case = get_history_use_case()
    try:
        items = await use_case.execute(limit=limit, language=language)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"items": items}
