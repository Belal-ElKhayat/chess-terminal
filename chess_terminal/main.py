"""Chess.Terminal application entry point."""

from __future__ import annotations

from textual.app import App

from . import theme
from .screens import SplashScreen
from .session import Session


class ChessTerminalApp(App):
    """The phosphor chess workstation."""

    CSS = theme.CSS
    TITLE = "CHESS.TERMINAL"

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.session = Session()
        self.local_relay = None

    def on_mount(self) -> None:
        self.push_screen(SplashScreen())

    def go_menu(self) -> None:
        """Unwind back to the splash screen without leaving a screen behind."""
        while len(self.screen_stack) > 1 and not isinstance(self.screen, SplashScreen):
            self.pop_screen()

    def action_quit(self) -> None:
        self.exit()


def run() -> None:
    """Console script entry point: ``chessterminal``."""
    ChessTerminalApp().run()


__all__ = ["ChessTerminalApp", "run"]
