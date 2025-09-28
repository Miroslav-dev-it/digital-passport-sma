from __future__ import annotations

from datetime import datetime, timezone

import pytest
from httpx import AsyncClient

from src.domain.models.code_generation import CodeGenerationRequest, CodeGenerationResult
from src.domain.models.language import ProgrammingLanguage
from src.interfaces.api.dependencies import (
    get_generate_use_case,
    get_history_use_case,
)
from src.main import create_app


class StubGenerateUseCase:
    async def execute(self, request: CodeGenerationRequest) -> CodeGenerationResult:
        return CodeGenerationResult.new(
            request=request,
            code="print('ok')",
            model="stub",
            token_usage=12,
            created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
            record_id=99,
        )


class StubHistoryUseCase:
    async def execute(self, limit: int = 20):
        request = CodeGenerationRequest(
            prompt="demo",
            language=ProgrammingLanguage.GO,
            max_tokens=64,
            user_id="morpheus",
        )
        return [
            CodeGenerationResult.new(
                request=request,
                code="fmt.Println('demo')",
                model="stub",
                token_usage=64,
                created_at=datetime(2024, 1, 2, tzinfo=timezone.utc),
                record_id=7,
            )
        ]


@pytest.mark.asyncio
async def test_generate_endpoint():
    app = create_app()

    async def override_generate():
        return StubGenerateUseCase()

    async def override_history():
        return StubHistoryUseCase()

    app.dependency_overrides[get_generate_use_case] = override_generate
    app.dependency_overrides[get_history_use_case] = override_history

    payload = {
        "prompt": "write hello world",
        "language": "python",
        "max_tokens": 32,
    }

    async with AsyncClient(app=app, base_url="http://test") as client:
        resp = await client.post("/generate", json=payload)
        assert resp.status_code == 201
        body = resp.json()
        assert body["code"].startswith("print")

        history_resp = await client.get("/history")
        assert history_resp.status_code == 200
        history_body = history_resp.json()
        assert history_body["items"][0]["id"] == 7
