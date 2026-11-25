"""Post-game coach: send the finished PGN to the BYOK model for review."""

from __future__ import annotations

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Static

from .. import ai, theme
from ..ai import get_provider


class CoachScreen(Screen):
    """One review per request, retryable with R."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("r", "retry", "Retry"),
    ]

    def __init__(self, pgn: str, outcome: str = "") -> None:
        super().__init__()
        self.pgn = pgn
        self.outcome = outcome
        self._busy = False

    def compose(self) -> ComposeResult:
        yield Static("CHESS.TERMINAL // POST-GAME COACH // BYOK", classes="telemetry")
        yield Static("", id="coach-head", classes="telemetry-dim")
        yield VerticalScroll(Static("", id="coach-body"), classes="scroll-log")
        yield Static("R RETRY // ESC BACK // NOTHING LEAVES THIS MACHINE EXCEPT THE PGN", classes="footer")

    def on_mount(self) -> None:
        self._start()

    def _start(self) -> None:
        session = self.app.session
        provider = get_provider(session.provider_key)
        head = self.query_one("#coach-head", Static)
        body = self.query_one("#coach-body", Static)
        head.update(
            Text(
                f"{provider.label.upper()} · {session.model} // {self.outcome or 'REVIEW'}",
                style=theme.DIM,
            )
        )
        if provider.requires_key and not session.api_key.strip():
            self._busy = False
            body.update(
                Text(
                    "NO KEY IN RAM // OPEN [1] PLAY VS AI, PASTE A KEY, THEN COME BACK.\n\n"
                    "The PGN is kept locally until you leave this screen.",
                    style=theme.BRIGHT,
                )
            )
            return
        if self._busy:
            return
        self._busy = True
        body.update(Text("READING THE GAME...", style=theme.BRIGHT))
        self.run_worker(self._review(provider), group="coach", exclusive=True)

    async def _review(self, provider) -> None:
        session = self.app.session
        review = await ai.request_review(
            provider.key, session.model, session.api_key, self.pgn
        )
        if not self.is_mounted:
            return
        self._busy = False
        body = self.query_one("#coach-body", Static)
        if review.error:
            body.update(Text(review.error + "\n\nR RETRY // ESC BACK", style=theme.BRIGHT))
            return
        text = Text()
        text.append(review.text + "\n", style=theme.AMBER)
        text.append("\nR RETRY // ESC BACK", style=theme.DIM)
        body.update(text)

    def action_retry(self) -> None:
        self._busy = False
        self._start()

    def action_back(self) -> None:
        self.app.pop_screen()


__all__ = ["CoachScreen"]
