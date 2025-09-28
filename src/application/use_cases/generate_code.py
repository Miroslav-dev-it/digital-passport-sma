from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from ...domain.models.code_generation import (
    CodeGenerationRequest,
    CodeGenerationResult,
)
from ...domain.services.postprocessing import PostProcessor
from ...domain.services.safety import SafetyOrchestrator
from ...domain.services.token_policy import TokenPolicy
from ...domain.services.ports import CodeGenerationProvider, GenerationRepository


@dataclass(slots=True)
class GenerateCodeUseCase:
    provider: CodeGenerationProvider
    repository: GenerationRepository
    safety: SafetyOrchestrator
    token_policy: TokenPolicy
    post_processors: Sequence[PostProcessor] = field(default_factory=tuple)

    async def execute(self, request: CodeGenerationRequest) -> CodeGenerationResult:
        request.ensure_safe()
        self.token_policy.ensure_within_limit(request.max_tokens)
        self.safety.validate(request.prompt)

        result = await self.provider.generate(request)
        for plugin in self.post_processors:
            result = await plugin.run(result)

        await self.repository.save(result)
        return result
