"""Async OpenAI client adapter."""
from __future__ import annotations

import re
from typing import Any

from openai import AsyncOpenAI


class OpenAIAdapter:
    """Adapter implementing the CodeGenPort via OpenAI's async client."""

    def __init__(self, api_key: str, model: str) -> None:
        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model

    async def generate(
        self, prompt: str, language: str, max_tokens: int, temperature: float
    ) -> dict[str, Any]:
        system_prompt = (
            "You are a code generator. Respond with code only, no explanations. "
            "Wrap code in triple backticks. Language: "
            + language
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        choice = response.choices[0].message.content or ""
        code = _extract_code_block(choice)
        tokens_in = response.usage.prompt_tokens if response.usage else 0
        tokens_out = response.usage.completion_tokens if response.usage else len(code) // 4
        return {
            "code": code,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "model": self._model,
        }


def _extract_code_block(content: str) -> str:
    """Extract code from triple backticks."""
    match = re.search(r"```[\w+-]*\n(.*?)```", content, re.DOTALL)
    return match.group(1).strip() if match else content.strip()
