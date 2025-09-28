from __future__ import annotations

from dataclasses import dataclass

from ...domain.services.ports import GenerationRepository


@dataclass(slots=True)
class GetHistoryUseCase:
    repository: GenerationRepository

    async def execute(self, limit: int = 20):
        return await self.repository.list_recent(limit=limit)
