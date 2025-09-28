from __future__ import annotations

from typing import Protocol

from ..models.code_generation import CodeGenerationRequest, CodeGenerationResult


class CodeGenerationProvider(Protocol):
    async def generate(self, request: CodeGenerationRequest) -> CodeGenerationResult:
        ...


class GenerationRepository(Protocol):
    async def save(self, result: CodeGenerationResult) -> None:
        ...

    async def list_recent(self, limit: int = 20) -> list[CodeGenerationResult]:
        ...
