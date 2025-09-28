from __future__ import annotations

from collections.abc import AsyncIterator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ...application.use_cases.generate_code import GenerateCodeUseCase
from ...application.use_cases.get_history import GetHistoryUseCase
from ...config.settings import get_settings
from ...domain.services.safety import SafetyGate, SafetyOrchestrator
from ...domain.services.token_policy import TokenPolicy
from ...infrastructure.db.session import db
from ...infrastructure.openai.client import OpenAICodeGenerationProvider
from ...infrastructure.plugins.trim_plugin import TrimWhitespacePlugin
from ...infrastructure.repositories.generation import SqlAlchemyGenerationRepository


async def get_session() -> AsyncIterator[AsyncSession]:
    async for session in db.session():
        yield session


def get_generate_use_case(
    session: AsyncSession = Depends(get_session),
) -> GenerateCodeUseCase:
    settings = get_settings()
    repository = SqlAlchemyGenerationRepository(session)
    safety = SafetyOrchestrator([SafetyGate("RB-SECRET"), SafetyGate("RB-DRIFT")])
    token_policy = TokenPolicy(settings.max_tokens_limit)
    provider = OpenAICodeGenerationProvider()
    plugins = (TrimWhitespacePlugin(),)
    return GenerateCodeUseCase(provider, repository, safety, token_policy, plugins)


def get_history_use_case(
    session: AsyncSession = Depends(get_session),
) -> GetHistoryUseCase:
    repository = SqlAlchemyGenerationRepository(session)
    return GetHistoryUseCase(repository)
