"""Puzzle trainer over the library's authored mating lines."""

from __future__ import annotations

import random

import chess
from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Static

from .. import theme
from ..puzzles import PUZZLES, Puzzle
from ..widgets import BoardView


class PuzzlesScreen(Screen):
    """Solve mate and tactic puzzles, with a session streak."""

    BINDINGS = [
        Binding("h", "hint", "Hint"),
        Binding("n", "next", "Next"),
        Binding("u", "retry", "Retry"),
        Binding("escape", "back", "Back"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.order = list(PUZZLES)
        random.Random().shuffle(self.order)
        self.index = 0
        self.puzzle: Puzzle | None = None
        self.board = chess.Board()
        self.queue: list[str] = []
        self.selected: int | None = None
        self.feedback = ""
        self.feedback_style = theme.DIM
        self.solved = False
        self.failed = False
        self._ready = False

    def compose(self) -> ComposeResult:
        yield Static("CHESS.TERMINAL // PUZZLE TRAINER", classes="telemetry")
        yield Static("LINES MINED FROM THE VALIDATED LIBRARY // NO ENGINE", classes="telemetry-dim")
        yield Horizontal(
            Vertical(
                Vertical(
                    BoardView(
                        self.board,
                        cell_width=4,
                        cell_height=2,
                        on_activate=self._activate,
                        id="puzzle-board",
                    ),
                    id="puzzle-stage",
                ),
                id="puzzle-board-col",
            ),
            Vertical(
                Static("", id="puzzle-head", classes="panel-title"),
                Static("", id="puzzle-prompt"),
                Static("", id="puzzle-feedback"),
                Static("", id="puzzle-hint"),
                Static("", id="puzzle-score"),
                Static(
                    "ENTER MOVE // H HINT // U RETRY // N NEXT",
                    classes="hint",
                ),
                id="puzzle-side",
            ),
            id="screen-body",
        )
        yield Static("", id="puzzle-footer", classes="footer")

    def on_mount(self) -> None:
        self._ready = True
        self.query_one("#puzzle-board", BoardView).focus()
        self._load(0)

    # --------------------------------------------------------------- loading
    def _load(self, index: int) -> None:
        if not self.order:
            return
        self.index = index % len(self.order)
        puzzle = self.order[self.index]
        self.puzzle = puzzle
        self.board = chess.Board(puzzle.fen)
        self.queue = list(puzzle.solution)
        self.selected = None
        self.solved = False
        self.failed = False
        self.feedback = ""
        self.feedback_style = theme.DIM
        self.query_one("#puzzle-hint", Static).update("")
        self.app.session.puzzle_seen += 1
        view = self.query_one("#puzzle-board", BoardView)
        view.flipped = self.board.turn == chess.BLACK
        view.cursor = chess.E4
        self._refresh()

    def _refresh(self) -> None:
        if not self._ready:
            return
        puzzle = self.puzzle
        if puzzle is None:
            return
        view = self.query_one("#puzzle-board", BoardView)
        view.set_board(self.board, last_move=self.board.peek() if self.board.move_stack else None)
        view.set_highlights(selected=self.selected)

        head = Text()
        head.append(f"PUZZLE {self.index + 1}/{len(self.order)}", style=f"{theme.BRIGHT} bold")
        head.append(f" // {puzzle.difficulty.upper()}", style=theme.DIM)
        self.query_one("#puzzle-head", Static).update(head)
        self.query_one("#puzzle-prompt", Static).update(
            Text(puzzle.prompt, style=f"{theme.AMBER} bold")
        )
        self.query_one("#puzzle-feedback", Static).update(
            Text(self.feedback, style=self.feedback_style)
        )
        self.query_one("#puzzle-hint", Static).update(
            Text(f"SOURCE // {puzzle.source}", style=theme.DIM)
        )
        session = self.app.session
        self.query_one("#puzzle-score", Static).update(
            Text(
                f"STREAK {session.puzzle_streak} // BEST {session.puzzle_best_streak} // "
                f"SOLVED {session.puzzle_solved}",
                style=theme.AMBER,
            )
        )
        self.query_one("#puzzle-footer", Static).update(
            "ENTER MOVE // H HINT // N NEXT // ESC BACK // "
            f"SESSION {session.puzzle_solved}/{session.puzzle_seen}"
        )

    # ----------------------------------------------------------------- input
    def _activate(self, square: int) -> None:
        if self.solved or self.failed or self.puzzle is None:
            return
        piece = self.board.piece_at(square)
        if self.selected is None:
            if piece is not None and piece.color == self.board.turn:
                self.selected = square
                self._refresh()
            return
        if square == self.selected:
            self.selected = None
            self._refresh()
            return
        if piece is not None and piece.color == self.board.turn:
            self.selected = square
            self._refresh()
            return

        moves = [
            move
            for move in self.board.legal_moves
            if move.from_square == self.selected and move.to_square == square
        ]
        if not moves:
            self.selected = None
            self._refresh()
            return
        chosen = moves[0]
        expected = self._expected()
        if expected is None or chosen != expected:
            self._fail()
            return
        self._play_solution()

    def _expected(self) -> chess.Move | None:
        if not self.queue:
            return None
        try:
            return self.board.parse_san(self.queue[0])
        except ValueError:
            return None

    def _play_solution(self) -> None:
        move = self._expected()
        if move is None:
            self._fail()
            return
        self.queue.pop(0)
        self.board.push(move)
        self.selected = None
        if self.queue:
            reply_san = self.queue.pop(0)
            try:
                reply = self.board.parse_san(reply_san)
            except ValueError:
                self._fail()
                return
            self.board.push(reply)
        if not self.queue:
            self._win()
        self._refresh()

    def _win(self) -> None:
        self.solved = True
        session = self.app.session
        session.puzzle_solved += 1
        session.puzzle_streak += 1
        session.puzzle_best_streak = max(session.puzzle_best_streak, session.puzzle_streak)
        self.feedback = "SOLVED // N NEXT // U RETRY"
        self.feedback_style = f"{theme.BRIGHT} bold"

    def _fail(self) -> None:
        self.failed = True
        self.app.session.puzzle_streak = 0
        solution = self.puzzle.solution if self.puzzle else ()
        first = self.board.san(self._expected()) if self._expected() is not None else "?"
        self.feedback = f"NOT THE LINE // TRY {first} // U RETRY"
        self.feedback_style = theme.BRIGHT
        self.selected = None
        self._refresh()

    def action_hint(self) -> None:
        if self.puzzle is None:
            return
        if self.solved or self.failed:
            self.query_one("#puzzle-hint", Static).update(
                Text(f"SOLUTION // {' '.join(self.puzzle.solution)}", style=theme.AMBER)
            )
            return
        expected = self._expected()
        hint = self.puzzle.hint
        if expected is not None:
            self.query_one("#puzzle-hint", Static).update(
                Text(f"TRY {self.board.san(expected)} // {hint}", style=theme.AMBER)
            )
        else:
            self.query_one("#puzzle-hint", Static).update(Text(hint, style=theme.AMBER))

    def action_retry(self) -> None:
        self._load(self.index)

    def action_next(self) -> None:
        self._load(self.index + 1)

    def action_back(self) -> None:
        self.app.go_menu()


__all__ = ["PuzzlesScreen"]
