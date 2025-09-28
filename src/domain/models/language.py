from __future__ import annotations

from enum import Enum


class ProgrammingLanguage(str, Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    GO = "go"

    @classmethod
    def from_str(cls, value: str) -> "ProgrammingLanguage":
        normalized = value.lower()
        try:
            return cls(normalized)
        except ValueError as exc:
            raise ValueError(f"Unsupported language: {value}") from exc
