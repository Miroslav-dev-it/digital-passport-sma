from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from ...domain.models.language import ProgrammingLanguage


class GenerateCodePayload(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=4096)
    language: ProgrammingLanguage = Field(default=ProgrammingLanguage.PYTHON)
    max_tokens: int = Field(default=512, gt=0, le=4096)
    user_id: Optional[str] = Field(default=None, max_length=128)


class GeneratedCode(BaseModel):
    request: GenerateCodePayload
    code: str
    model: str
    token_usage: int
    created_at: datetime


class HistoryItem(BaseModel):
    id: int
    user_id: Optional[str]
    language: ProgrammingLanguage
    model: str
    token_usage: int
    created_at: datetime


class HistoryResponse(BaseModel):
    items: list[HistoryItem]
