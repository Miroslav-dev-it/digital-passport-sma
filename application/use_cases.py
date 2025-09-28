"""Application use cases orchestrating domain ports and policies."""
from __future__ import annotations

import uuid

from domain.entities import GenerationRequest, GenerationResult
from domain.ports import CodeGenPort, HistoryRepositoryPort
from domain.policies import validate_language
from application.plugins import PluginManager
from application.rb_gates import RBGates


class GenerateCodeUseCase:
    """Use case for running the LLM generation pipeline."""

    def __init__(
        self,
        llm: CodeGenPort,
        rb_gates: RBGates,
        repository: HistoryRepositoryPort,
        plugin_manager: PluginManager,
    ) -> None:
        self._llm = llm
        self._rb_gates = rb_gates
        self._repository = repository
        self._plugin_manager = plugin_manager

    async def execute(self, request: GenerationRequest) -> tuple[str, GenerationResult]:
        """Execute generation, apply RB gates and post-processing."""
        validate_language(request.language)

        raw = await self._llm.generate(
            request.prompt,
            request.language,
            request.max_tokens,
            request.temperature,
        )
        code = raw.get("code", "")
        rb_flags: list[str] = []

        if self._rb_gates.check_secret_leak(code):
            rb_flags.append("RB-SECRET")
            code = self._sanitize(code)

        if self._rb_gates.check_drift(raw.get("model", "")):
            rb_flags.append("RB-DRIFT")

        plugins = self._plugin_manager.resolve(request.plugin_names)
        for plugin in plugins:
            code = await plugin.run(code, request.language)

        result = GenerationResult(
            code=code,
            language=request.language,
            tokens_in=int(raw.get("tokens_in", 0)),
            tokens_out=int(raw.get("tokens_out", 0)),
            model=raw.get("model", "unknown"),
            rb_flags=tuple(rb_flags),
        )

        generation_id = str(uuid.uuid4())
        await self._repository.save_generation(generation_id, request, result, rb_flags=rb_flags)
        return generation_id, result

    def _sanitize(self, code: str) -> str:
        import re

        replacements = {
            r"(sk-[A-Za-z0-9]{20,})": "sk-REDACTED",
            r"(AKIA[0-9A-Z]{16})": "AKIA-REDACTED",
            r"(AIza[0-9A-Za-z\-_]{35})": "AIza-REDACTED",
        }
        sanitized = code
        for pattern, replacement in replacements.items():
            sanitized = re.sub(pattern, replacement, sanitized)
        return sanitized


class GetHistoryUseCase:
    """Retrieve generation history."""

    def __init__(self, repository: HistoryRepositoryPort) -> None:
        self._repository = repository

    async def execute(self, limit: int = 20, language: str | None = None) -> list[dict]:
        validate_language(language) if language else None
        return await self._repository.list_history(limit=limit, language=language)
