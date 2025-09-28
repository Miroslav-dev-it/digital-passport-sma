from __future__ import annotations

from dataclasses import dataclass

import pytest

from src.application.use_cases.generate_code import GenerateCodeUseCase
from src.application.use_cases.get_history import GetHistoryUseCase
from src.domain.models.code_generation import CodeGenerationRequest, CodeGenerationResult
from src.domain.models.language import ProgrammingLanguage
from src.domain.services.postprocessing import PostProcessor
from src.domain.services.safety import SafetyGate, SafetyOrchestrator, SafetyViolation
from src.domain.services.token_policy import TokenLimitExceeded, TokenPolicy
from src.domain.services.ports import GenerationRepository, CodeGenerationProvider


@dataclass
class InMemoryRepo(GenerationRepository):
    stored: list[CodeGenerationResult]

    async def save(self, result: CodeGenerationResult) -> None:
        self.stored.append(result)

    async def list_recent(self, limit: int = 20):
        return self.stored[-limit:]


class DummyProvider(CodeGenerationProvider):
    async def generate(self, request: CodeGenerationRequest) -> CodeGenerationResult:
        return CodeGenerationResult.new(
            request=request,
            code=f"print('hello {request.language.value}')",
            model="dummy",
            token_usage=request.max_tokens,
        )


class TaggingPlugin(PostProcessor):
    name = "tag"

    async def run(self, result: CodeGenerationResult) -> CodeGenerationResult:
        result.code += "\n# tagged"
        return result


@pytest.mark.asyncio
async def test_generate_use_case_success():
    request = CodeGenerationRequest(
        prompt="write hello",
        language=ProgrammingLanguage.PYTHON,
        max_tokens=128,
    )
    repo = InMemoryRepo([])
    use_case = GenerateCodeUseCase(
        provider=DummyProvider(),
        repository=repo,
        safety=SafetyOrchestrator([SafetyGate("RB-SECRET")]),
        token_policy=TokenPolicy(256),
        post_processors=[TaggingPlugin()],
    )

    result = await use_case.execute(request)

    assert result.code.endswith("# tagged")
    assert repo.stored[0].code == result.code


@pytest.mark.asyncio
async def test_generate_use_case_token_limit():
    request = CodeGenerationRequest(
        prompt="write hello",
        language=ProgrammingLanguage.GO,
        max_tokens=999,
    )
    repo = InMemoryRepo([])
    use_case = GenerateCodeUseCase(
        provider=DummyProvider(),
        repository=repo,
        safety=SafetyOrchestrator([]),
        token_policy=TokenPolicy(100),
        post_processors=[],
    )

    with pytest.raises(TokenLimitExceeded):
        await use_case.execute(request)


@pytest.mark.asyncio
async def test_generate_use_case_safety_violation():
    request = CodeGenerationRequest(
        prompt="hack the planet",
        language=ProgrammingLanguage.JAVASCRIPT,
        max_tokens=128,
    )
    repo = InMemoryRepo([])
    use_case = GenerateCodeUseCase(
        provider=DummyProvider(),
        repository=repo,
        safety=SafetyOrchestrator([SafetyGate("RB-DRIFT")]),
        token_policy=TokenPolicy(256),
        post_processors=[],
    )

    with pytest.raises(SafetyViolation):
        await use_case.execute(request)


@pytest.mark.asyncio
async def test_get_history_use_case_reads_from_repo():
    repo = InMemoryRepo([])
    request = CodeGenerationRequest(
        prompt="demo",
        language=ProgrammingLanguage.PYTHON,
        max_tokens=16,
    )
    repo.stored.append(
        CodeGenerationResult.new(
            request=request,
            code="print('x')",
            model="stub",
            token_usage=16,
        )
    )
    history = await GetHistoryUseCase(repo).execute(limit=5)
    assert len(history) == 1
