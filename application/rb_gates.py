"""Red Button gates for security and drift detection."""
from __future__ import annotations

import re
from collections.abc import Iterable


class RBGates:
    """Security and quality guardrails."""

    def __init__(self, secret_patterns: Iterable[str], model_expected: str) -> None:
        self._secret_regexes = [re.compile(pattern) for pattern in secret_patterns]
        self._model_expected = model_expected

    def check_secret_leak(self, text: str) -> bool:
        """Return True if a secret pattern is detected in the text."""
        return any(regex.search(text) for regex in self._secret_regexes)

    def check_drift(self, model_used: str) -> bool:
        """Return True if the actual model differs from the expected one."""
        return model_used != self._model_expected
