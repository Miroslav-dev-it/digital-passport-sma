"""Domain ports (interfaces) for infrastructure adapters."""
from __future__ import annotations

from typing import Protocol


class CodeGenPort(Protocol):
    """Port for LLM-based code generation."""

    async def generate(
        self, prompt: str, language: str, max_tokens: int, temperature: float
    ) -> dict:
        """Generate code from a natural language prompt."""


class HistoryRepositoryPort(Protocol):
    """Port for persisting and querying generation history."""

    async def save_generation(self, gid: str, req, res, rb_flags: list[str]) -> None:  # pragma: no cover - structural
        ...

    async def list_history(self, limit: int = 20, language: str | None = None) -> list[dict]:  # pragma: no cover - structural
        ...


class PluginPort(Protocol):
    """Port for post-processing plugins."""

    name: str

    async def run(self, code: str, language: str) -> str:
        """Run the plugin on generated code."""
