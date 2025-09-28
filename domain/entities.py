"""Domain entities for the CodeGen Service."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GenerationRequest:
    """Immutable input for a generation job."""

    prompt: str
    language: str
    max_tokens: int
    temperature: float
    plugin_names: tuple[str, ...] = ()


@dataclass(frozen=True)
class GenerationResult:
    """Output of an LLM generation enriched with RB flags."""

    code: str
    language: str
    tokens_in: int
    tokens_out: int
    model: str
    rb_flags: tuple[str, ...] = ()
