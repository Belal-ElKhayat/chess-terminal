"""Splash screen and main menu."""

from __future__ import annotations

import chess
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Static

from .. import persist
from ..banner import ITALIAN, PIECES_BOTTOM, PIECES_TOP, TAGLINE, mini_board, title_block
from ..widgets import KeyboardList

MENU_ITEMS = (
    "[1]  PLAY VS AI (BYOK)",
    "[2]  PLAY VS FRIEND (FREE ROOM ID)",
    "[3]  THE OPENING BOOK & LIBRARY",
    "[4]  ENGINE ROOM // BEST MOVE & SCOUT",
    "[5]  PUZZLE TRAINER",
    "[6]  QUIT",
)



class SplashScreen(Screen):
    """The amber-CRT landing screen."""

    BINDINGS = [
        Binding("q", "quit_app", "Quit"),
        Binding("r", "resume", "Resume"),
    ]

    def compose(self) -> ComposeResult:
        yield Static("CHESS.TERMINAL // PHOSPHOR LINK // SYS 1.2", classes="telemetry")
        yield Static("LINK READY // 9600 BAUD // 8-N-1 // CARRIER DETECT", classes="telemetry-dim")
        yield Static(PIECES_TOP, classes="dim", markup=False)
        yield Horizontal(
            Static(mini_board(), id="pieces-left"),
            Vertical(
                Static(title_block(), id="banner", markup=False),
                Static(TAGLINE, classes="dim", markup=False),
                KeyboardList(MENU_ITEMS, on_select=self._menu_selected, id="menu", pad_width=48),
                id="splash-center",
            ),
            Static(mini_board(ITALIAN), id="pieces-right"),
            id="splash-mid",
        )
        yield Static("", id="splash-hint", classes="hint")
        yield Static(PIECES_BOTTOM, classes="telemetry", markup=False)

    def on_mount(self) -> None:
        self.query_one("#menu", KeyboardList).focus()
        self._refresh_hint()

    def _refresh_hint(self) -> None:
        record = persist.load_session()
        if record:
            moves = len(record.get("moves") or [])
            hint = (
                f"↑/↓ SELECT    ENTER EXECUTE    1-6 DIRECT    R RESUME AI GAME "
                f"({moves} PLIES)    Q QUIT"
            )
        else:
            hint = "↑/↓ SELECT    ENTER EXECUTE    1-6 DIRECT    Q QUIT"
        self.query_one("#splash-hint", Static).update(hint)

    def on_resize(self, event) -> None:
        # The piece art frames the menu on roomy terminals; hide it when there
        # is not enough space for the banner plus both galleries.
        roomy = event.size.width >= 100 and event.size.height >= 26
        for selector in ("#pieces-left", "#pieces-right"):
            try:
                self.query_one(selector).display = roomy
            except Exception:
                pass

    def _menu_selected(self, index: int) -> None:
        from .ai_setup import AISetupScreen
        from .engine_room import EngineRoomScreen
        from .friend import FriendScreen
        from .library import LibraryScreen
        from .puzzles import PuzzlesScreen

        if index == 0:
            self.app.push_screen(AISetupScreen())
        elif index == 1:
            self.app.push_screen(FriendScreen())
        elif index == 2:
            self.app.push_screen(LibraryScreen())
        elif index == 3:
            self.app.push_screen(EngineRoomScreen())
        elif index == 4:
            self.app.push_screen(PuzzlesScreen())
        else:
            self.app.exit()

    def action_resume(self) -> None:
        record = persist.load_session()
        if not record:
            self.query_one("#splash-hint", Static).update(
                "NO SAVED GAME // START AN AI GAME AND IT AUTOSAVES AFTER EVERY MOVE"
            )
            return
        from .game import GameScreen

        moves = tuple(str(item) for item in record.get("moves") or [])
        colour = chess.WHITE if record.get("colour") == "white" else chess.BLACK
        self.app.push_screen(
            GameScreen(mode="ai", colour=colour, initial_moves=moves, resume=True)
        )

    def action_quit_app(self) -> None:
        self.app.exit()


__all__ = ["SplashScreen", "MENU_ITEMS"]
