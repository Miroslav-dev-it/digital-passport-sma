from __future__ import annotations

from datetime import datetime, timezone

from openai import AsyncOpenAI

from ...config.settings import get_settings
from ...domain.models.code_generation import CodeGenerationRequest, CodeGenerationResult
from ...domain.services.ports import CodeGenerationProvider


class OpenAICodeGenerationProvider(CodeGenerationProvider):
    def __init__(self, client: AsyncOpenAI | None = None, model: str | None = None) -> None:
        settings = get_settings()
        self._client = client or AsyncOpenAI(api_key=settings.openai_api_key)
        self._model = model or settings.openai_model

    async def generate(self, request: CodeGenerationRequest) -> CodeGenerationResult:
        response = await self._client.responses.create(
            model=self._model,
            input=request.prompt,
            max_output_tokens=request.max_tokens,
            metadata={"language": request.language.value, "user_id": request.user_id},
        )
        output_text = response.output[0].content[0].text  # type: ignore[index]
        token_usage = response.usage.output_tokens  # type: ignore[attr-defined]
        created = datetime.now(timezone.utc)
        return CodeGenerationResult.new(
            request=request,
            code=output_text,
            model=self._model,
            token_usage=token_usage,
            created_at=created,
        )
