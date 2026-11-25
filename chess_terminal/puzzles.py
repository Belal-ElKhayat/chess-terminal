"""Puzzles mined from the already-validated library lines.

No engine is needed: the authored continuation *is* the solution. Positions
two and three attacking moves before a mating finish become mate-in-2 and
mate-in-3 puzzles; traps that end in a winning shot become one-move puzzles.
"""

from __future__ import annotations

from dataclasses import dataclass

import chess

from .data import ENTRIES, LibraryEntry

DIFFICULTY_ORDER = {"beginner": 0, "club": 1, "advanced": 2}


@dataclass(frozen=True)
class Puzzle:
    source: str
    prompt: str
    fen: str
    solution: tuple[str, ...]
    hint: str
    difficulty: str
    kind: str = "mate"


def _boards(moves: tuple[str, ...]) -> list[chess.Board]:
    board = chess.Board()
    boards = [board.copy()]
    for san in moves:
        board.push_san(san)
        boards.append(board.copy())
    return boards


def _hint(entry: LibraryEntry) -> str:
    preferred = ("THE STING", "THE MOMENT", "THE STORY", "WHY IT MATTERS")
    text = ""
    for heading, content in entry.sections:
        if heading in preferred and content.strip():
            text = content.strip()
            break
    if not text and entry.sections:
        text = entry.sections[0][1].strip()
    first = text.replace("\n", " ").split(". ")[0].strip()
    if len(first) > 150:
        first = first[:147].rstrip() + "..."
    return first or entry.summary


def _entry_puzzles(entry: LibraryEntry) -> list[Puzzle]:
    if not entry.moves:
        return []
    boards = _boards(entry.moves)
    total = len(entry.moves)
    puzzles: list[Puzzle] = []

    if boards[-1].is_checkmate():
        for plies, label, difficulty in (
            (3, "MATE IN 2", "club"),
            (5, "MATE IN 3", "advanced"),
        ):
            start = total - plies
            if start < 0:
                continue
            board = boards[start]
            if board.outcome() is not None:
                continue
            side = "WHITE" if board.turn == chess.WHITE else "BLACK"
            puzzles.append(
                Puzzle(
                    source=entry.title,
                    prompt=f"{side} TO MOVE // {label}",
                    fen=board.fen(),
                    solution=tuple(entry.moves[start:total]),
                    hint=_hint(entry),
                    difficulty=difficulty,
                )
            )
    elif entry.kind == "trap" and total >= 2:
        # Find the sting: the latest check or big capture in the line, not just
        # the last quiet move recorded in the archive.
        for index in range(total - 1, max(-1, total - 9), -1):
            board = boards[index]
            if board.outcome() is not None:
                continue
            try:
                move = board.parse_san(entry.moves[index])
            except ValueError:
                continue
            target = board.piece_at(move.to_square)
            value = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9}.get(
                target.piece_type if target is not None else chess.PAWN, 0
            )
            if not board.gives_check(move) and value < 5:
                continue
            side = "WHITE" if board.turn == chess.WHITE else "BLACK"
            puzzles.append(
                Puzzle(
                    source=entry.title,
                    prompt=f"{side} TO MOVE // FIND THE WINNING SHOT",
                    fen=board.fen(),
                    solution=(entry.moves[index],),
                    hint=_hint(entry),
                    difficulty="beginner",
                    kind="best",
                )
            )
            break
    return puzzles


def build_puzzles(entries: tuple[LibraryEntry, ...] = ENTRIES) -> tuple[Puzzle, ...]:
    """Every distinct puzzle in the archive, easy first."""
    seen: set[tuple[str, tuple[str, ...]]] = set()
    puzzles: list[Puzzle] = []
    for entry in entries:
        for puzzle in _entry_puzzles(entry):
            key = (puzzle.fen, puzzle.solution)
            if key in seen:
                continue
            seen.add(key)
            puzzles.append(puzzle)
    puzzles.sort(key=lambda puzzle: (DIFFICULTY_ORDER.get(puzzle.difficulty, 1), puzzle.source))
    return tuple(puzzles)


PUZZLES: tuple[Puzzle, ...] = build_puzzles()


__all__ = ["Puzzle", "PUZZLES", "build_puzzles"]
