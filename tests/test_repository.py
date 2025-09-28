from __future__ import annotations

from datetime import datetime, timezone

import pytest

from src.domain.models.code_generation import CodeGenerationRequest, CodeGenerationResult
from src.domain.models.language import ProgrammingLanguage
from src.infrastructure.repositories.generation import SqlAlchemyGenerationRepository


@pytest.mark.asyncio
async def test_repository_persists_and_lists(session):
    repository = SqlAlchemyGenerationRepository(session)
    request = CodeGenerationRequest(
        prompt="write hello",
        language=ProgrammingLanguage.PYTHON,
        max_tokens=128,
        user_id="neo",
    )
    result = CodeGenerationResult.new(
        request=request,
        code="print('hi')",
        model="dummy",
        token_usage=42,
        created_at=datetime.now(timezone.utc),
    )

    await repository.save(result)
    await session.commit()

    history = await repository.list_recent(limit=5)

    assert len(history) == 1
    stored = history[0]
    assert stored.request.prompt == request.prompt
    assert stored.record_id is not None
