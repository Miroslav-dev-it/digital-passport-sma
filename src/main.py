from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from .infrastructure.db.base import Base
from .infrastructure.db.session import db
from .interfaces.api.routes import router


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with db.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


def create_app() -> FastAPI:
    tags_metadata = [
        {"name": "codegen", "description": "Code generation endpoints"},
        {"name": "ops", "description": "Ops and monitoring"},
    ]
    app = FastAPI(
        title="CodeGen Service",
        version="0.1.0",
        description="Enterprise-ready code generation service",
        openapi_url="/openapi.json",
        lifespan=lifespan,
        openapi_tags=tags_metadata,
    )
    app.include_router(router)
    return app


app = create_app()
