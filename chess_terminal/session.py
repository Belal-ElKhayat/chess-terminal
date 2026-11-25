"""In-memory session state.

The API key lives here for the lifetime of the process only. Nothing in this
module writes to disk; the optional keychain is handled by ``secrets_store``
and only when the user presses the save button.
"""

from __future__ import annotations

from dataclasses import dataclass

from .ai import PROVIDERS


@dataclass
class Session:
    provider_key: str = PROVIDERS[0].key
    model: str = PROVIDERS[0].default_model
    api_key: str = ""
    stockfish_path: str = ""
    puzzle_streak: int = 0
    puzzle_best_streak: int = 0
    puzzle_solved: int = 0
    puzzle_seen: int = 0

    def clear_key(self) -> None:
        self.api_key = ""

    def wipe(self) -> None:
        self.api_key = ""
        self.provider_key = PROVIDERS[0].key
        self.model = PROVIDERS[0].default_model


__all__ = ["Session"]
