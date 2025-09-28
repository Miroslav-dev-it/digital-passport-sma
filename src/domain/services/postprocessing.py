from __future__ import annotations

from typing import Protocol

from ..models.code_generation import CodeGenerationResult


class PostProcessor(Protocol):
    name: str

    async def run(self, result: CodeGenerationResult) -> CodeGenerationResult:
        ...
