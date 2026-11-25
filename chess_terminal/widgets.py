"""Shared custom widgets: a keyboard list and the phosphor chess board."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

import chess
from rich.text import Text
from textual.widgets import Static

from . import theme

UNICODE_PIECES = {
    (chess.WHITE, chess.PAWN): "♙",
    (chess.WHITE, chess.KNIGHT): "♘",
    (chess.WHITE, chess.BISHOP): "♗",
    (chess.WHITE, chess.ROOK): "♖",
    (chess.WHITE, chess.QUEEN): "♕",
    (chess.WHITE, chess.KING): "♔",
    (chess.BLACK, chess.PAWN): "♟",
    (chess.BLACK, chess.KNIGHT): "♞",
    (chess.BLACK, chess.BISHOP): "♝",
    (chess.BLACK, chess.ROOK): "♜",
    (chess.BLACK, chess.QUEEN): "♛",
    (chess.BLACK, chess.KING): "♚",
}

PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0,
}


def captured_pieces(board: chess.Board) -> tuple[str, str]:
    """Return (white captures, black captures) as unicode strings."""
    counts = {chess.WHITE: {}, chess.BLACK: {}}
    for square, piece in board.piece_map().items():
        counts[piece.color][piece.piece_type] = counts[piece.color].get(piece.piece_type, 0) + 1
    starting = {
        chess.PAWN: 8,
        chess.KNIGHT: 2,
        chess.BISHOP: 2,
        chess.ROOK: 2,
        chess.QUEEN: 1,
        chess.KING: 1,
    }

    def lost(colour: chess.Color) -> str:
        glyphs = []
        for piece_type in (chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT, chess.PAWN):
            missing = starting[piece_type] - counts[colour].get(piece_type, 0)
            glyphs.extend(UNICODE_PIECES[(colour, piece_type)] * max(0, missing))
        return "".join(glyphs)

    # White's captured material = black pieces missing from the board.
    return lost(chess.BLACK), lost(chess.WHITE)


def material_balance(board: chess.Board) -> int:
    balance = 0
    for piece in board.piece_map().values():
        value = PIECE_VALUES[piece.piece_type]
        balance += value if piece.color == chess.WHITE else -value
    return balance


class KeyboardList(Static):
    """A focusable, arrow-key driven list rendered in the CRT palette."""

    can_focus = True

    def __init__(
        self,
        options: Sequence[str] = (),
        *,
        on_select: Callable[[int], None] | None = None,
        on_change: Callable[[int], None] | None = None,
        numbers: bool = True,
        pad_width: int = 46,
        max_visible: int | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__("", markup=False, **kwargs)
        self._options = list(options)
        self._index = 0
        self._on_select = on_select
        self._on_change = on_change
        self._numbers = numbers
        self._pad_width = pad_width
        self._max_visible = max_visible

    @property
    def options(self) -> list[str]:
        return list(self._options)

    @property
    def index(self) -> int:
        return self._index

    def set_options(self, options: Sequence[str], *, index: int | None = None) -> None:
        self._options = list(options)
        if index is not None:
            self._index = max(0, min(index, len(self._options) - 1))
        elif self._index >= len(self._options):
            self._index = max(0, len(self._options) - 1)
        self.refresh(layout=True)

    def set_index(self, index: int) -> None:
        if not self._options:
            return
        new_index = max(0, min(index, len(self._options) - 1))
        if new_index != self._index:
            self._index = new_index
            self.refresh()
            if self._on_change is not None:
                self._on_change(self._index)

    def choose(self, index: int | None = None) -> None:
        if index is not None:
            self.set_index(index)
        if not self._options:
            return
        if self._on_select is not None:
            self._on_select(self._index)

    def render(self) -> Text:
        text = Text(no_wrap=True, overflow="crop")
        if not self._options:
            text.append("  (no entries)", style=theme.DIM)
            return text

        # Window long lists around the cursor so the widget keeps a fixed height.
        start, end = 0, len(self._options)
        if self._max_visible is not None and len(self._options) > self._max_visible:
            start = self._index - self._max_visible // 2
            start = max(0, min(start, len(self._options) - self._max_visible))
            end = start + self._max_visible

        # One entry per row: never let a long name wrap onto a second line.
        room = max(12, (self.size.width or self._pad_width) - 2)

        for position in range(start, end):
            option = self._options[position]
            if len(option) > room:
                option = option[: max(1, room - 1)].rstrip() + "…"
            selected = position == self._index
            if selected and self.has_focus:
                style = f"{theme.BG} on {theme.AMBER} bold"
            elif selected:
                style = f"{theme.BRIGHT} on {theme.SQ_LAST}"
            else:
                style = theme.AMBER if self.has_focus else theme.DIM
            marker = "▌" if selected else " "
            line = f" {marker}{option}"
            if len(line) < room + 2:
                line = line.ljust(room + 2)
            text.append(line, style=style)
            if position != end - 1:
                text.append("\n")
        return text

    async def on_key(self, event: Any) -> None:
        key = event.key
        if key in ("up", "k"):
            self.set_index(self._index - 1)
            event.stop()
        elif key in ("down", "j"):
            self.set_index(self._index + 1)
            event.stop()
        elif key in ("home",):
            self.set_index(0)
            event.stop()
        elif key in ("end",):
            self.set_index(len(self._options) - 1)
            event.stop()
        elif key == "enter":
            self.choose()
            event.stop()
        elif self._numbers and key.isdigit() and key != "0":
            position = int(key) - 1
            if position < len(self._options):
                self.choose(position)
                event.stop()


class BoardView(Static):
    """A Unicode chess board rendered with inverted phosphor highlights."""

    can_focus = True

    def __init__(
        self,
        board: chess.Board | None = None,
        *,
        flipped: bool = False,
        interactive: bool = True,
        cell_width: int = 2,
        cell_height: int = 1,
        on_activate: Callable[[int], None] | None = None,
        on_cursor: Callable[[int], None] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__("", markup=False, **kwargs)
        self.board = board if board is not None else chess.Board()
        self.flipped = flipped
        self.interactive = interactive
        self.cell_width = max(2, cell_width)
        self.cell_height = max(1, cell_height)
        self.can_focus = interactive
        self.cursor: int = chess.E4
        self.selected: int | None = None
        self.last_move: chess.Move | None = None
        self.on_activate = on_activate
        self.on_cursor = on_cursor

    def set_board(self, board: chess.Board, *, last_move: chess.Move | None = None) -> None:
        self.board = board
        self.last_move = last_move
        self.refresh()

    def set_highlights(self, *, cursor: int | None = None, selected: int | None = None) -> None:
        if cursor is not None:
            self.cursor = cursor
        self.selected = selected
        self.refresh()

    def _move_cursor(self, delta_file: int, delta_rank: int) -> None:
        file = chess.square_file(self.cursor) + delta_file
        rank = chess.square_rank(self.cursor) + delta_rank
        if self.flipped:
            file = chess.square_file(self.cursor) - delta_file
            rank = chess.square_rank(self.cursor) - delta_rank
        file = max(0, min(7, file))
        rank = max(0, min(7, rank))
        self.cursor = chess.square(file, rank)
        self.refresh()
        if self.on_cursor is not None:
            self.on_cursor(self.cursor)

    async def on_key(self, event: Any) -> None:
        if not self.interactive:
            return
        key = event.key
        if key == "left":
            self._move_cursor(-1, 0)
            event.stop()
        elif key == "right":
            self._move_cursor(1, 0)
            event.stop()
        elif key == "up":
            self._move_cursor(0, 1)
            event.stop()
        elif key == "down":
            self._move_cursor(0, -1)
            event.stop()
        elif key in ("enter", "space"):
            if self.on_activate is not None:
                self.on_activate(self.cursor)
            event.stop()

    def render(self) -> Text:
        board = self.board
        text = Text(no_wrap=True, overflow="crop")
        files = list(range(7, -1, -1)) if self.flipped else list(range(8))
        ranks = list(range(8)) if self.flipped else list(range(7, -1, -1))

        label_style = theme.DIM
        width = self.cell_width
        height = self.cell_height

        def centred(symbol: str) -> tuple[str, str]:
            padding = max(0, width - len(symbol))
            left = padding // 2
            return " " * left, " " * (padding - left)

        def emit(symbol: str, foreground: str, background: str, *, bold: bool = False) -> None:
            """Write one cell of ``width`` columns with ``symbol`` in the middle."""
            left, right = centred(symbol)
            style = f"{foreground} on {background}" + (" bold" if bold else "")
            if left:
                text.append(left, style=f"on {background}")
            text.append(symbol, style=style)
            if right:
                text.append(right, style=f"on {background}")

        def file_labels() -> None:
            text.append("  ", style=label_style)
            for file in files:
                left, right = centred(chess.FILE_NAMES[file])
                text.append(left + chess.FILE_NAMES[file] + right, style=label_style)

        file_labels()
        text.append("\n")

        check_square = None
        if board.is_check():
            king = board.king(board.turn)
            if king is not None:
                check_square = king
        targets: set[int] = set()
        if self.selected is not None:
            for move in board.legal_moves:
                if move.from_square == self.selected:
                    targets.add(move.to_square)

        for rank in ranks:
            for row in range(height):
                text.append(f"{rank + 1} " if row == 0 else "  ", style=label_style)
                for file in files:
                    square = chess.square(file, rank)
                    piece = board.piece_at(square)
                    light = (file + rank) % 2 == 1
                    background = theme.SQ_LIGHT if light else theme.SQ_DARK
                    foreground = theme.AMBER

                    if self.last_move is not None and square in (
                        self.last_move.from_square,
                        self.last_move.to_square,
                    ):
                        background = theme.SQ_LAST
                    if square in targets:
                        background = theme.SQ_TARGET
                    if square == check_square:
                        background = theme.SQ_CHECK
                    if self.selected == square:
                        background = theme.BRIGHT
                        foreground = theme.BG
                    if square == self.cursor and self.interactive:
                        background = theme.AMBER
                        foreground = theme.BG

                    if row == 0 and piece is not None:
                        glyph = UNICODE_PIECES[(piece.color, piece.piece_type)]
                        if square != self.cursor and square != self.selected:
                            foreground = theme.BRIGHT if piece.color == chess.WHITE else theme.AMBER
                        emit(glyph, foreground, background, bold=True)
                    elif row == 0 and square in targets:
                        emit("·", theme.BRIGHT, background)
                    else:
                        text.append(" " * width, style=f"on {background}")
                if row == 0:
                    text.append(f" {rank + 1}", style=label_style)
                text.append("\n")

        file_labels()
        return text


__all__ = ["BoardView", "KeyboardList", "captured_pieces", "material_balance", "UNICODE_PIECES"]
