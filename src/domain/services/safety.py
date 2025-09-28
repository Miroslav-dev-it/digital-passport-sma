from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


class SafetyViolation(Exception):
    """Raised when a safety gate blocks the request."""


@dataclass(slots=True)
class SafetyGate:
    name: str

    def check(self, text: str) -> None:
        if self.name == "RB-SECRET" and "sk-" in text.lower():
            raise SafetyViolation("Potential secret detected by RB-SECRET gate")
        if self.name == "RB-DRIFT" and "hack" in text.lower():
            raise SafetyViolation("Prompt drift detected by RB-DRIFT gate")


@dataclass(slots=True)
class SafetyOrchestrator:
    gates: Iterable[SafetyGate]

    def validate(self, prompt: str) -> None:
        for gate in self.gates:
            gate.check(prompt)
