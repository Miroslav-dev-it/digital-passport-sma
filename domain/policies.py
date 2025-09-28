"""Domain policies for validation and business rules."""
from __future__ import annotations

from typing import Final

SUPPORTED_LANGUAGES: Final[set[str]] = {"python", "javascript", "go"}


def validate_language(language: str) -> None:
    """Ensure language is supported."""
    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported language: {language}")
