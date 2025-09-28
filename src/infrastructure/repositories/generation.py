from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.models.code_generation import CodeGenerationResult
from ...domain.services.ports import GenerationRepository
from ...domain.models.language import ProgrammingLanguage
from ..db.models import GenerationRecord


class SqlAlchemyGenerationRepository(GenerationRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, result: CodeGenerationResult) -> None:
        record = GenerationRecord(
            user_id=result.request.user_id,
            prompt=result.request.prompt,
            language=result.request.language.value,
            model=result.model,
            code=result.code,
            token_usage=result.token_usage,
            created_at=result.created_at,
        )
        self._session.add(record)
        await self._session.flush()
        result.record_id = record.id
        await self._session.commit()

    async def list_recent(self, limit: int = 20) -> list[CodeGenerationResult]:
        stmt = (
            select(GenerationRecord)
            .order_by(GenerationRecord.created_at.desc())
            .limit(limit)
        )
        rows = (await self._session.execute(stmt)).scalars().all()
        results: list[CodeGenerationResult] = []
        for row in rows:
            request = result_request_from_record(row)
            results.append(
                CodeGenerationResult(
                    request=request,
                    code=row.code,
                    model=row.model,
                    token_usage=row.token_usage,
                    created_at=row.created_at,
                    record_id=row.id,
                )
            )
        return results


def result_request_from_record(record: GenerationRecord):
    from ...domain.models.code_generation import CodeGenerationRequest

    return CodeGenerationRequest(
        prompt=record.prompt,
        language=ProgrammingLanguage.from_str(record.language),
        max_tokens=record.token_usage,
        user_id=record.user_id,
    )
