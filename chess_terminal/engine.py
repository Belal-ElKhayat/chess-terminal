"""Stockfish integration for the best-move analyser.

The engine is optional. Detection looks at the session path, ``STOCKFISH_PATH``,
``PATH`` and the usual install locations. Analysis runs in a worker thread so
Textual stays responsive, and every failure comes back as an ``EngineReport``
error string rather than an exception.
"""

from __future__ import annotations

import asyncio
import os
import shutil
from dataclasses import dataclass
from pathlib import Path

import chess

DEFAULT_DEPTH = 14


@dataclass(frozen=True)
class EngineLine:
    """One principal variation with its evaluation."""

    score: str
    pv: tuple[str, ...] = ()


@dataclass
class EngineReport:
    """The analyser's answer, or a friendly error."""

    move: chess.Move | None = None
    san: str = ""
    score: str = ""
    pv: tuple[str, ...] = ()
    depth: int = 0
    lines: tuple[EngineLine, ...] = ()
    source: str = "STOCKFISH"
    error: str = ""


def candidate_paths(configured: str = "") -> list[Path]:
    """Every place worth checking for a Stockfish binary, best first."""
    candidates: list[Path] = []

    def add(value: str | Path | None) -> None:
        if not value:
            return
        path = Path(str(value).strip().strip('"')).expanduser()
        if path.is_dir():
            for pattern in ("stockfish*.exe", "stockfish*"):
                candidates.extend(sorted(path.glob(pattern)))
        else:
            candidates.append(path)

    add(configured)
    add(os.environ.get("STOCKFISH_PATH"))
    for name in ("stockfish", "stockfish.exe"):
        found = shutil.which(name)
        if found:
            add(found)

    roots = [
        os.environ.get("PROGRAMFILES"),
        os.environ.get("PROGRAMFILES(X86)"),
        os.environ.get("LOCALAPPDATA"),
        os.environ.get("USERPROFILE"),
        "/opt/homebrew/bin",
        "/usr/local/bin",
        "/usr/bin",
        "/usr/games",
        "/snap/bin",
    ]
    for root in roots:
        if not root:
            continue
        base = Path(root)
        for relative in ("Stockfish", "stockfish", "Programs/Stockfish", "Downloads/Stockfish"):
            add(base / relative)
        if base.name in ("bin", "games"):
            add(base / "stockfish")
    return [path for path in candidates if path.is_file()]


def find_stockfish(configured: str = "") -> str | None:
    """Return a usable Stockfish path, or ``None``."""
    for path in candidate_paths(configured):
        try:
            if path.is_file() and path.stat().st_size > 0:
                return str(path)
        except OSError:
            continue
    return None


def _probe_sync(path: str) -> str:
    """Start the binary, ping it over UCI and return its reported name."""
    import chess.engine

    engine = chess.engine.SimpleEngine.popen_uci(path, timeout=10.0)
    try:
        engine.ping()
        identity = engine.id or {}
        name = str(identity.get("name") or "").strip()
        author = str(identity.get("author") or "").strip()
        if name and author and author.lower() not in name.lower():
            return f"{name} // {author}"
        return name
    finally:
        engine.quit()


async def probe(path: str) -> tuple[str, str]:
    """Check that ``path`` really speaks UCI, returning ``(identity, error)``."""
    if not path:
        return "", "NO STOCKFISH PATH // INSTALL IT OR POINT THE PATH FIELD AT THE BINARY."
    try:
        name = await asyncio.to_thread(_probe_sync, path)
    except FileNotFoundError:
        return "", "STOCKFISH NOT FOUND // CHECK THE PATH."
    except Exception as exc:  # not an engine, wrong architecture, timeout
        detail = str(exc).strip().replace("\n", " ")[:140]
        message = f"NOT A UCI ENGINE // {type(exc).__name__}"
        return "", f"{message}: {detail}" if detail else message
    return (name or "UCI ENGINE"), ""


def _score_text(score, turn: chess.Color) -> str:
    pov = score.pov(turn)
    if pov.is_mate():
        mate = pov.mate()
        return f"M{mate}" if mate and mate > 0 else f"M-{abs(mate or 0)}"
    centipawns = pov.score()
    if centipawns is None:
        return "?"
    return f"{centipawns / 100:+.2f}"


def _san_line(board: chess.Board, moves: list[chess.Move]) -> tuple[str, ...]:
    sandbox = board.copy()
    parts: list[str] = []
    for move in moves:
        try:
            parts.append(sandbox.san(move))
        except (ValueError, AssertionError):
            break
        sandbox.push(move)
    return tuple(parts)


def _analyse_sync(board: chess.Board, path: str, depth: int, multipv: int) -> EngineReport:
    import chess.engine

    engine = chess.engine.SimpleEngine.popen_uci(path)
    try:
        infos = engine.analyse(board, chess.engine.Limit(depth=depth), multipv=max(1, multipv))
    finally:
        engine.quit()
    if isinstance(infos, dict):
        infos = [infos]

    lines: list[EngineLine] = []
    best: tuple[dict, list[chess.Move], str] | None = None
    for info in infos:
        pv = list(info.get("pv") or [])
        score = info.get("score")
        text = _score_text(score, board.turn) if score is not None else "?"
        lines.append(EngineLine(text, _san_line(board, pv)))
        if best is None and pv:
            best = (info, pv, text)

    if best is None:
        return EngineReport(error="STOCKFISH FOUND NO MOVE IN THIS POSITION.")
    info, pv, text = best
    return EngineReport(
        move=pv[0],
        san=_san_line(board, [pv[0]])[0],
        score=text,
        pv=_san_line(board, pv),
        depth=int(info.get("depth") or 0),
        lines=tuple(lines),
    )


async def analyse(
    board: chess.Board,
    path: str,
    *,
    depth: int = DEFAULT_DEPTH,
    multipv: int = 3,
) -> EngineReport:
    """Analyse ``board`` with Stockfish without blocking the UI."""
    if not path:
        return EngineReport(error="NO STOCKFISH PATH // INSTALL IT OR POINT THE PATH FIELD AT THE BINARY.")
    try:
        return await asyncio.to_thread(_analyse_sync, board.copy(stack=False), path, depth, multipv)
    except FileNotFoundError:
        return EngineReport(error="STOCKFISH NOT FOUND // CHECK THE PATH.")
    except Exception as exc:  # engine protocol, timeouts, bad binary
        detail = str(exc).strip().replace("\n", " ")[:200]
        return EngineReport(error=f"STOCKFISH FAILED // {type(exc).__name__}: {detail}")


__all__ = [
    "DEFAULT_DEPTH",
    "EngineLine",
    "EngineReport",
    "analyse",
    "candidate_paths",
    "find_stockfish",
    "probe",
]
