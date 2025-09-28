"""Async repository implementation for generation history."""
from __future__ import annotations

from hashlib import sha256

from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from domain.entities import GenerationRequest, GenerationResult
from infrastructure.db.models import Base, GenerationArtifact, GenerationLog


class HistoryRepository:
    """Async SQLAlchemy repository."""

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        engine: AsyncEngine,
    ) -> None:
        self._session_factory = session_factory
        self._engine = engine

    async def init_db(self) -> None:
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def save_generation(
        self,
        gid: str,
        request: GenerationRequest,
        result: GenerationResult,
        rb_flags: list[str],
    ) -> None:
        prompt_hash = sha256(request.prompt.encode("utf-8")).hexdigest()
        async with self._session_factory() as session:
            session.add(
                GenerationLog(
                    id=gid,
                    prompt_hash=prompt_hash,
                    language=request.language,
                    model=result.model,
                    tokens_in=result.tokens_in,
                    tokens_out=result.tokens_out,
                    rb_flags=";".join(rb_flags) if rb_flags else None,
                    meta={
                        "temperature": request.temperature,
                        "max_tokens": request.max_tokens,
                    },
                )
            )
            session.add(
                GenerationArtifact(
                    id=gid,
                    log_id=gid,
                    language=request.language,
                    code=result.code,
                )
            )
            await session.commit()

    async def list_history(self, limit: int = 20, language: str | None = None) -> list[dict]:
        async with self._session_factory() as session:
            stmt = select(GenerationLog).order_by(GenerationLog.created_at.desc()).limit(limit)
            if language:
                stmt = stmt.where(GenerationLog.language == language)
            rows = (await session.execute(stmt)).scalars().all()
            return [
                {
                    "id": row.id,
                    "prompt_hash": row.prompt_hash,
                    "language": row.language,
                    "created_at": row.created_at.isoformat(),
                }
                for row in rows
            ]


def make_session_factory(db_url: str) -> tuple[async_sessionmaker[AsyncSession], AsyncEngine]:
    engine = create_async_engine(db_url, pool_pre_ping=True)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    return session_factory, engine
