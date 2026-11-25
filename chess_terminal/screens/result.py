"""The game-over popup: a pulsing result card with a CRT waveform."""

from __future__ import annotations

from collections.abc import Callable

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Static

from .. import theme

WAVE = "▁▂▃▄▅▆▇█▇▆▅▄▃▂"
WAVE_WIDTH = 26


class ResultScreen(ModalScreen[str]):
    """Dismisses with ``"again"``, ``"coach"`` or ``"menu"``."""

    BINDINGS = [
        Binding("enter", "again", "Rematch"),
        Binding("n", "again", "Rematch"),
        Binding("a", "coach", "Coach"),
        Binding("s", "save", "PGN"),
        Binding("escape", "menu", "Menu"),
    ]

    def __init__(
        self,
        result: str,
        lines: tuple[str, ...],
        *,
        can_rematch: bool = True,
        can_coach: bool = False,
        on_save: Callable[[], object] | None = None,
    ) -> None:
        super().__init__()
        self.result = result
        self.lines = lines
        self.can_rematch = can_rematch
        self.can_coach = can_coach
        self.on_save = on_save
        self._phase = 0
        self._saved = ""

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static("", id="result-title", markup=False),
            Static("", id="result-wave", markup=False),
            Static("", id="result-detail", markup=False),
            Static("", id="result-keys", markup=False),
            classes="result-card",
        )

    def on_mount(self) -> None:
        self._paint()
        self.set_interval(0.16, self._tick)

    def _tick(self) -> None:
        self._phase = (self._phase + 1) % len(WAVE)
        self._paint()

    def _paint(self) -> None:
        title = Text()
        glow = self._phase % 2 == 0
        title.append(
            f" {self.result} ",
            style=f"{theme.BG} on {theme.BRIGHT} bold" if glow else f"{theme.BRIGHT} bold",
        )
        self.query_one("#result-title", Static).update(title)

        wave = Text()
        wave.append(
            "".join(WAVE[(index + self._phase) % len(WAVE)] for index in range(WAVE_WIDTH)),
            style=theme.AMBER if glow else theme.BRIGHT,
        )
        self.query_one("#result-wave", Static).update(wave)

        detail = Text()
        for number, line in enumerate(self.lines):
            if number:
                detail.append("\n")
            detail.append(line, style=theme.AMBER if number == 0 else theme.DIM)
        self.query_one("#result-detail", Static).update(detail)

        keys = []
        if self.can_rematch:
            keys.append("N REMATCH")
        keys.append("A COACH")
        keys.append("S PGN")
        keys.append("ESC MENU")
        self.query_one("#result-keys", Static).update(
            Text(" // ".join(keys) if not self._saved else self._saved)
        )

    def action_again(self) -> None:
        self.dismiss("again" if self.can_rematch else "menu")

    def action_coach(self) -> None:
        if self.can_coach:
            self.dismiss("coach")

    def action_save(self) -> None:
        if self.on_save is None:
            self._saved = "PGN EXPORT UNAVAILABLE"
        else:
            try:
                path = self.on_save()
                self._saved = f"PGN SAVED // {path}"
            except Exception as exc:  # a disk problem must not kill the card
                self._saved = f"PGN FAILED // {type(exc).__name__}"
        self._paint()

    def action_menu(self) -> None:
        self.dismiss("menu")


__all__ = ["ResultScreen"]
