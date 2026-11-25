"""Clock selection for local (AI) games."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Static

from .. import clock, theme
from ..widgets import KeyboardList

OPTIONS = (
    "5|0   BLITZ",
    "10|5  RAPID + 5s",
    "NO CLOCK",
)


class ClockPickerScreen(ModalScreen[object]):
    """Dismisses with a ``ClockSpec``, ``"off"``, or ``None`` on cancel."""

    BINDINGS = [Binding("escape", "cancel", "Cancel")]

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static("GAME CLOCK", id="clock-title"),
            Static("", id="clock-note"),
            KeyboardList(OPTIONS, on_select=self._pick, id="clock-options", pad_width=30),
            Static("1-3 CHOOSE // ESC KEEP CURRENT", id="clock-keys"),
            classes="clock-card",
        )

    def on_mount(self) -> None:
        self.query_one("#clock-note", Static).update(
            "The clock starts on White's first move. 10|5 adds five seconds after every move."
        )
        self.query_one("#clock-options", KeyboardList).focus()

    def _pick(self, index: int) -> None:
        mapping: tuple[object, ...] = (clock.PRESETS[0], clock.PRESETS[1], "off")
        self.dismiss(mapping[index])

    def action_cancel(self) -> None:
        self.dismiss(None)


__all__ = ["ClockPickerScreen", "OPTIONS"]
