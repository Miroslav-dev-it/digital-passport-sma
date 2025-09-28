from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from .language import ProgrammingLanguage


@dataclass(slots=True)
class CodeGenerationRequest:
    prompt: str
    language: ProgrammingLanguage
    max_tokens: int
    user_id: Optional[str] = None

    def ensure_safe(self) -> None:
        if not self.prompt.strip():
            raise ValueError("Prompt must not be empty")
        if self.max_tokens <= 0:
            raise ValueError("max_tokens must be positive")


@dataclass(slots=True)
class CodeGenerationResult:
    request: CodeGenerationRequest
    code: str
    model: str
    token_usage: int
    created_at: datetime
    record_id: int | None = None

    @classmethod
    def new(
        cls,
        request: CodeGenerationRequest,
        code: str,
        model: str,
        token_usage: int,
        created_at: Optional[datetime] = None,
        record_id: int | None = None,
    ) -> "CodeGenerationResult":
        timestamp = created_at or datetime.now(timezone.utc)
        return cls(
            request=request,
            code=code,
            model=model,
            token_usage=token_usage,
            created_at=timestamp,
            record_id=record_id,
        )
