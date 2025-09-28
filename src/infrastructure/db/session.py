from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from ...config.settings import get_settings


class Database:
    def __init__(self) -> None:
        settings = get_settings()
        self._engine: AsyncEngine = create_async_engine(settings.database_url, echo=False, future=True)
        self._session_factory = async_sessionmaker(self._engine, expire_on_commit=False)

    @property
    def engine(self) -> AsyncEngine:
        return self._engine

    async def session(self) -> AsyncIterator[AsyncSession]:
        async with self._session_factory() as session:
            yield session


db = Database()
