"""Hand-drawn block lettering and ASCII piece art for the splash screen."""

from __future__ import annotations

import chess
from rich.text import Text

from . import theme
from .widgets import UNICODE_PIECES

# A 6-row shadow block font, just the glyphs needed for CHESS and TERMINAL.
# Ragged right edges are padded by ``banner_lines``.
_GLYPHS: dict[str, tuple[str, ...]] = {
    "C": (
        " ██████╗",
        "██╔════╝",
        "██║     ",
        "██║     ",
        "╚██████╗",
        " ╚═════╝",
    ),
    "H": (
        "██╗  ██╗",
        "██║  ██║",
        "███████║",
        "██╔══██║",
        "██║  ██║",
        "╚═╝  ╚═╝",
    ),
    "E": (
        "███████╗",
        "██╔════╝",
        "█████╗  ",
        "██╔══╝  ",
        "███████╗",
        "╚══════╝",
    ),
    "S": (
        "███████╗",
        "██╔════╝",
        "███████╗",
        "╚════██║",
        "███████║",
        "╚══════╝",
    ),
    "T": (
        "████████╗",
        "╚══██╔══╝",
        "   ██║   ",
        "   ██║   ",
        "   ██║   ",
        "   ╚═╝   ",
    ),
    "R": (
        "██████╗ ",
        "██╔══██╗",
        "██████╔╝",
        "██╔══██╗",
        "██║  ██║",
        "╚═╝  ╚═╝",
    ),
    "M": (
        "███╗   ███╗",
        "████╗ ████║",
        "██╔████╔██║",
        "██║╚██╔╝██║",
        "██║ ╚═╝ ██║",
        "╚═╝     ╚═╝",
    ),
    "I": (
        "██╗",
        "██║",
        "██║",
        "██║",
        "██║",
        "╚═╝",
    ),
    "N": (
        "███╗   ██╗",
        "████╗  ██║",
        "██╔██╗ ██║",
        "██║╚██╗██║",
        "██║ ╚████║",
        "╚═╝  ╚═══╝",
    ),
    "A": (
        " █████╗ ",
        "██╔══██╗",
        "███████║",
        "██╔══██║",
        "██║  ██║",
        "╚═╝  ╚═╝",
    ),
    "L": (
        "██╗     ",
        "██║     ",
        "██║     ",
        "██║     ",
        "███████╗",
        "╚══════╝",
    ),
    " ": (
        "   ",
        "   ",
        "   ",
        "   ",
        "   ",
        "   ",
    ),
    ".": (
        "   ",
        "   ",
        "   ",
        "   ",
        "██╗",
        "╚═╝",
    ),
}

TITLE = "CHESS.TERMINAL"


def banner_lines(text: str = TITLE) -> list[str]:
    """Render ``text`` in the built-in shadow font, one entry per screen row."""
    letters = [_GLYPHS[ch] for ch in text if ch in _GLYPHS]
    if not letters:
        letters = [_GLYPHS[" "]]
    widths = [max(len(row) for row in glyph) for glyph in letters]
    rows: list[str] = []
    for row in range(6):
        rows.append(" ".join(glyph[row].ljust(width) for glyph, width in zip(letters, widths)))
    return rows


# A real position, drawn with the actual pieces: the splash sides are genuine
# boards rather than hand-drawn block art, so every glyph is unmistakable.
ITALIAN = "r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/2N2N2/PPPP1PPP/R1BQK2R w KQkq - 6 5"


def mini_board(fen: str | None = None) -> Text:
    """A framed 8x8 board of Unicode pieces on amber squares."""
    board = chess.Board(fen) if fen else chess.Board()
    text = Text(no_wrap=True)
    text.append("┌" + "─" * 16 + "┐\n", style=theme.DIM)
    for rank in range(7, -1, -1):
        text.append("│", style=theme.DIM)
        for file in range(8):
            square = chess.square(file, rank)
            piece = board.piece_at(square)
            light = (file + rank) % 2 == 1
            background = theme.SQ_LIGHT if light else theme.SQ_DARK
            if piece is None:
                text.append("  ", style=f"on {background}")
                continue
            glyph = UNICODE_PIECES[(piece.color, piece.piece_type)]
            foreground = theme.BRIGHT if piece.color == chess.WHITE else theme.AMBER
            text.append(f" {glyph}", style=f"{foreground} on {background} bold")
        text.append("│\n", style=theme.DIM)
    text.append("└" + "─" * 16 + "┘", style=theme.DIM)
    return text


def title_block(first: str = "CHESS", second: str = "TERMINAL") -> str:
    """The two stacked shadow words used in the splash centre."""
    return "\n".join(banner_lines(first) + [""] + banner_lines(second))


PIECES_TOP = "  ♜  ♞  ♝  ♛  ♚  ♝  ♞  ♜   ── 9600 BAUD ──   ── 8-N-1 ──   ♜  ♞  ♝  ♛  ♚  ♝  ♞  ♜  "
PIECES_BOTTOM = "  ── CARRIER DETECT ──   CHESS.TERMINAL 1.2   ── LINK READY ──  "

TAGLINE = "PHOSPHOR CHESS WORKSTATION // REV 1.2 // 0 DISTRACTIONS"

__all__ = [
    "ITALIAN",
    "PIECES_BOTTOM",
    "PIECES_TOP",
    "TAGLINE",
    "banner_lines",
    "mini_board",
    "title_block",
]
