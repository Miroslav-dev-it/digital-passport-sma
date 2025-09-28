from __future__ import annotations

from dataclasses import dataclass


class TokenLimitExceeded(Exception):
    pass


@dataclass(slots=True)
class TokenPolicy:
    hard_limit: int

    def ensure_within_limit(self, requested: int) -> None:
        if requested > self.hard_limit:
            raise TokenLimitExceeded(
                f"Requested tokens {requested} exceed hard limit {self.hard_limit}"
            )
