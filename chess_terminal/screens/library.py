"""The Opening Book & Chess Library screen."""

from __future__ import annotations

import chess
from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Input, Static

from .. import persist, theme
from ..data import ENTRIES, LibraryEntry
from ..widgets import BoardView, KeyboardList

FILTERS: tuple[tuple[str | None, str], ...] = (
    (None, "ALL"),
    ("opening", "OPENINGS"),
    ("trap", "TRAPS"),
    ("game", "GAMES"),
    ("note", "REFERENCE"),
)

FILTER_KEYS = {"0": None, "1": "opening", "2": "trap", "3": "game", "4": "note"}

KIND_LABEL = {
    "opening": "OPENING",
    "trap": "TRAP",
    "game": "GAME",
    "note": "REFERENCE",
}


class LibraryScreen(Screen):
    """Searchable opening book, trap archive and famous-game collection."""

    def __init__(self) -> None:
        super().__init__()
        self.entries: tuple[LibraryEntry, ...] = ENTRIES
        self.view: list[LibraryEntry] = list(ENTRIES)
        self.step = 0
        self.kind: str | None = None
        self.side: str | None = None
        self.needle = ""
        self.last_pgn = ""

    def compose(self) -> ComposeResult:
        yield Static("CHESS.TERMINAL // OPENING BOOK & LIBRARY", classes="telemetry")
        yield Static("", id="lib-telemetry", classes="telemetry-dim")
        yield Static("", id="lib-pgn", classes="hint")
        yield Horizontal(
            Vertical(
                Input(placeholder="search openings, traps, games, notes...", id="search"),
                KeyboardList(
                    [entry.label for entry in self.view],
                    on_change=self._selection_changed,
                    on_select=self._selection_changed,
                    id="library-list",
                    numbers=False,
                    pad_width=44,
                    max_visible=14,
                ),
                id="library-left",
            ),
            Vertical(
                Static("", id="lib-title", classes="panel-title"),
                Vertical(
                    BoardView(interactive=False, id="lib-board"),
                    id="lib-stage",
                ),
                VerticalScroll(Static("", id="lib-body"), classes="scroll-log"),
                id="library-right",
            ),
            id="screen-body",
        )
        yield Static(
            "[0] ALL [1] OPENINGS [2] TRAPS [3] GAMES [4] REFERENCE // "
            "W/B TRAPS BY SIDE // S PGN // ↑↓ SELECT // ←→ STEP // / SEARCH // ESC MENU",
            classes="footer",
        )

    def on_mount(self) -> None:
        self.query_one("#library-list", KeyboardList).focus()
        self._recompute()

    # ------------------------------------------------------------- filtering
    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "search":
            self.needle = event.value
            self._recompute()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "search":
            self.query_one("#library-list", KeyboardList).focus()

    def _recompute(self) -> None:
        needle = self.needle.strip().lower()
        entries = [entry for entry in self.entries if self.kind is None or entry.kind == self.kind]
        if self.side:
            entries = [entry for entry in entries if entry.side == self.side]
        if needle:
            entries = [entry for entry in entries if needle in entry.search_text()]
        self.view = entries
        listing = self.query_one("#library-list", KeyboardList)
        listing.set_options([entry.label for entry in self.view], index=0)
        self.step = 0
        self._telemetry()
        self._show()

    def _telemetry(self) -> None:
        if self.kind is None:
            scope = "ALL ARCHIVE"
        else:
            scope = next(label for kind, label in FILTERS if kind == self.kind)
        counts = []
        for kind, label in FILTERS[1:]:
            total = sum(1 for entry in self.entries if entry.kind == kind)
            counts.append(f"{label} {total}")
        text = Text()
        text.append(f"PHOSPHOR ARCHIVE // {len(self.view)}/{len(self.entries)} SHOWN // ", style=theme.DIM)
        text.append(scope, style=theme.BRIGHT)
        if self.side:
            text.append(f" // {self.side.upper()} ONLY", style=theme.BRIGHT)
        text.append(" // " + " · ".join(counts), style=theme.DIM)
        self.query_one("#lib-telemetry", Static).update(text)
        self.query_one("#lib-pgn", Static).update(Text(self.last_pgn, style=theme.DIM))

    # -------------------------------------------------------------- stepping
    def _current(self) -> LibraryEntry | None:
        listing = self.query_one("#library-list", KeyboardList)
        if not self.view:
            return None
        return self.view[min(listing.index, len(self.view) - 1)]

    def _selection_changed(self, _index: int) -> None:
        self.step = 0
        self._show()

    def _step(self, delta: int) -> None:
        entry = self._current()
        if entry is None or not entry.moves:
            return
        new_step = max(0, min(len(entry.moves), self.step + delta))
        if new_step != self.step:
            self.step = new_step
            self._show()

    def on_key(self, event) -> None:
        search = self.query_one("#search", Input)
        listing = self.query_one("#library-list", KeyboardList)
        if event.key in ("/", "slash"):
            search.focus()
            event.stop()
        elif event.key == "escape":
            if search.has_focus:
                search.value = ""
                self.needle = ""
                self._recompute()
                listing.focus()
            else:
                self.app.go_menu()
            event.stop()
        elif event.key in FILTER_KEYS and not search.has_focus:
            self.kind = FILTER_KEYS[event.key]
            self.side = None
            self._recompute()
            listing.focus()
            event.stop()
        elif event.key in ("w", "b") and not search.has_focus:
            self.kind = "trap"
            self.side = "white" if event.key == "w" else "black"
            self._recompute()
            listing.focus()
            event.stop()
        elif event.key == "s" and not search.has_focus:
            self._export_pgn()
            event.stop()
        elif event.key in ("left", "right") and not search.has_focus:
            self._step(-1 if event.key == "left" else 1)
            event.stop()

    # ---------------------------------------------------------------- export
    def _export_pgn(self) -> None:
        entry = self._current()
        if entry is None or not entry.moves:
            self.last_pgn = "PGN // NOTHING TO EXPORT"
            self._telemetry()
            return
        white, black, event_name = "LIBRARY", "LINE", entry.title
        parts = entry.summary.split(" // ")
        if entry.kind == "game" and " vs " in parts[0]:
            white, black = parts[0].split(" vs ", 1)
            event_name = f"{entry.title} // {parts[1] if len(parts) > 1 else ''}"
        try:
            path = persist.export_san(entry.moves, event=event_name, white=white, black=black)
        except OSError as exc:
            self.last_pgn = f"PGN FAILED // {exc}"
        else:
            self.last_pgn = f"PGN SAVED // {path}"
        self._telemetry()

    # ------------------------------------------------------------- rendering
    def _show(self) -> None:
        entry = self._current()
        title = self.query_one("#lib-title", Static)
        body = self.query_one("#lib-body", Static)
        board_view = self.query_one("#lib-board", BoardView)

        if entry is None:
            title.update(Text("NO MATCH", style=f"{theme.BRIGHT} bold"))
            board_view.set_board(chess.Board(), last_move=None)
            body.update(Text("NO ENTRY MATCHES THAT SEARCH.\n\nPRESS ESC TO CLEAR.", style=theme.DIM))
            return

        if self.step > len(entry.moves):
            self.step = len(entry.moves)
        board = entry.position_at(self.step)
        board_view.set_board(board, last_move=board.peek() if board.move_stack else None)

        header = Text()
        if entry.kind == "note":
            header.append("REFERENCE // ", style=theme.DIM)
        else:
            header.append(
                f"[{entry.eco}] // {KIND_LABEL.get(entry.kind, entry.kind.upper())} // ",
                style=theme.DIM,
            )
        header.append(entry.title.upper(), style=f"{theme.BRIGHT} bold")
        if entry.moves:
            header.append(f"  PLY {self.step}/{len(entry.moves)}", style=theme.AMBER)
        title.update(header)

        body.update(self._commentary(entry))

    def _commentary(self, entry: LibraryEntry) -> Text:
        text = Text()
        text.append(entry.summary + "\n\n", style=theme.AMBER)

        if entry.moves:
            text.append("MAIN LINE\n", style=f"{theme.BRIGHT} bold")
            for index, san in enumerate(entry.moves):
                if index % 2 == 0:
                    text.append(f"{index // 2 + 1:>3}. ", style=theme.DIM)
                current = index == self.step - 1
                text.append(san, style=f"{theme.BG} on {theme.AMBER}" if current else theme.AMBER)
                if index % 2 == 1 or index == len(entry.moves) - 1:
                    text.append("\n")
                else:
                    text.append("   ")
            text.append("\n")

        for heading, content in entry.sections:
            text.append(heading + "\n", style=f"{theme.BRIGHT} bold")
            text.append(content.strip() + "\n\n", style=theme.AMBER)

        if entry.moves:
            text.append("←/→ REPLAYS THE LINE // SHOWN POSITION IS AFTER ", style=theme.DIM)
            if self.step == 0:
                text.append("THE START.", style=theme.DIM)
            else:
                text.append(f"{self.step} PLY.", style=theme.DIM)
        return text


__all__ = ["LibraryScreen", "FILTERS"]
