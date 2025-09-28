from __future__ import annotations

from ...domain.models.code_generation import CodeGenerationResult
from ...domain.services.postprocessing import PostProcessor


class TrimWhitespacePlugin(PostProcessor):
    name = "trim-whitespace"

    async def run(self, result: CodeGenerationResult) -> CodeGenerationResult:
        result.code = result.code.strip() + "\n"
        return result
