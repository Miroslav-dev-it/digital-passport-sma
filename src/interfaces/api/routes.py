from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from ...application.dto.generation import (
    GenerateCodePayload,
    GeneratedCode,
    HistoryItem,
    HistoryResponse,
)
from ...application.use_cases.generate_code import GenerateCodeUseCase
from ...application.use_cases.get_history import GetHistoryUseCase
from ...domain.models.code_generation import CodeGenerationRequest
from ...domain.services.safety import SafetyViolation
from ...domain.services.token_policy import TokenLimitExceeded
from .dependencies import get_generate_use_case, get_history_use_case

router = APIRouter()


@router.get("/health", tags=["ops"])
async def health() -> dict[str, str]:
    return {"status": "green"}


@router.post("/generate", response_model=GeneratedCode, tags=["codegen"], status_code=201)
async def generate_code(
    payload: GenerateCodePayload,
    use_case: GenerateCodeUseCase = Depends(get_generate_use_case),
) -> GeneratedCode:
    request = CodeGenerationRequest(
        prompt=payload.prompt,
        language=payload.language,
        max_tokens=payload.max_tokens,
        user_id=payload.user_id,
    )
    try:
        result = await use_case.execute(request)
    except TokenLimitExceeded as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except SafetyViolation as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return GeneratedCode(
        request=payload,
        code=result.code,
        model=result.model,
        token_usage=result.token_usage,
        created_at=result.created_at,
    )


@router.get("/history", response_model=HistoryResponse, tags=["codegen"])
async def get_history(
    use_case: GetHistoryUseCase = Depends(get_history_use_case),
) -> HistoryResponse:
    records = await use_case.execute()
    items = [
        HistoryItem(
            id=record.record_id or index + 1,
            user_id=record.request.user_id,
            language=record.request.language,
            model=record.model,
            token_usage=record.token_usage,
            created_at=record.created_at,
        )
        for index, record in enumerate(records)
    ]
    return HistoryResponse(items=items)
