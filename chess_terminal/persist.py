"""Save/restore of the in-progress game and PGN export.

Everything lives under ``CHESS_TERMINAL_HOME`` when that is set, otherwise
``~/.chess_terminal``. Writes are atomic and never raise into the UI.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import chess
import chess.pgn

APP_DIR = ".chess_terminal"


def data_dir() -> Path:
    override = os.environ.get("CHESS_TERMINAL_HOME")
    if override:
        return Path(override).expanduser()
    return Path.home() / APP_DIR


def session_path() -> Path:
    return data_dir() / "session.json"


def games_dir() -> Path:
    return data_dir() / "games"


def save_session(record: dict) -> Path | None:
    """Atomically write the resume record; ``None`` when the disk says no."""
    path = session_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
        temporary.replace(path)
        return path
    except OSError:
        return None


def load_session() -> dict | None:
    try:
        raw = json.loads(session_path().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(raw, dict):
        return None
    if not isinstance(raw.get("moves"), list):
        return None
    return raw


def clear_session() -> None:
    try:
        session_path().unlink()
    except OSError:
        pass


def build_pgn(
    board: chess.Board,
    *,
    event: str = "Chess.Terminal",
    site: str = "Chess.Terminal",
    white: str = "YOU",
    black: str = "OPPONENT",
    date: datetime | None = None,
) -> str:
    """Full PGN for a board, with the headers this app sets."""
    game = chess.pgn.Game.from_board(board)
    game.headers["Event"] = event
    game.headers["Site"] = site
    game.headers["Date"] = (date or datetime.now(timezone.utc)).strftime("%Y.%m.%d")
    game.headers["White"] = white
    game.headers["Black"] = black
    game.headers["Creator"] = "Chess.Terminal"
    return str(game)


def export_pgn(
    board: chess.Board,
    *,
    event: str = "Chess.Terminal",
    white: str = "YOU",
    black: str = "OPPONENT",
    directory: Path | str | None = None,
) -> Path:
    """Write a timestamped PGN and return its path."""
    target = Path(directory) if directory else games_dir()
    target.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    path = target / f"{stamp}.pgn"
    counter = 2
    while path.exists():
        path = target / f"{stamp}-{counter}.pgn"
        counter += 1
    path.write_text(
        build_pgn(board, event=event, white=white, black=black),
        encoding="utf-8",
    )
    return path


def board_from_san(moves: tuple[str, ...] | list[str]) -> chess.Board:
    board = chess.Board()
    for san in moves:
        board.push_san(san)
    return board


def export_san(
    moves: tuple[str, ...] | list[str],
    *,
    event: str,
    white: str = "LIBRARY",
    black: str = "LINE",
    directory: Path | str | None = None,
) -> Path:
    """Export a library line as a PGN."""
    return export_pgn(board_from_san(moves), event=event, white=white, black=black, directory=directory)


__all__ = [
    "APP_DIR",
    "data_dir",
    "session_path",
    "games_dir",
    "save_session",
    "load_session",
    "clear_session",
    "build_pgn",
    "export_pgn",
    "board_from_san",
    "export_san",
]
