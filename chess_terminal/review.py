"""Whole-game review: Stockfish evaluations turned into blunders and brilliants.

Every position of the game is searched once. The evaluation of position ``i``
(best play for the side to move) minus the evaluation after the move actually
played gives that move's centipawn loss, which is what the tags are built from.
One search per position keeps a normal 40-move game to a few seconds, and the
numbers are the same ones a reviewer would quote.
"""

from __future__ import annotations

import asyncio
import io
import math
from collections import Counter
from dataclasses import dataclass, field

import chess
import chess.pgn

DEFAULT_DEPTH = 12
MATE_SCORE = 10_000
# Below this the game is already decided, so nothing counts as a blunder.
LOST_CP = 700

PIECE_VALUE = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0,
}

TAGS = ("BRILLIANT", "BEST", "GOOD", "INACCURACY", "MISTAKE", "BLUNDER")


@dataclass(frozen=True)
class MoveReview:
    """One played move, scored from the point of view of the player who made it."""

    ply: int
    number: int
    side: str  # "white" / "black"
    san: str
    tag: str
    loss: int
    best_san: str = ""
    eval_text: str = "0.00"
    sacrifice: bool = False

    @property
    def label(self) -> str:
        prefix = f"{self.number}." if self.side == "white" else f"{self.number}..."
        return f"{prefix} {self.san}"


@dataclass
class GameReview:
    """A finished review, or a friendly error."""

    moves: tuple[MoveReview, ...] = ()
    counts: dict[str, int] = field(default_factory=dict)
    accuracy: dict[str, int] = field(default_factory=lambda: {"white": 0, "black": 0})
    depth: int = 0
    error: str = ""

    @property
    def highlights(self) -> tuple[MoveReview, ...]:
        """Only the moves worth looking at, worst first."""
        order = {"BRILLIANT": 0, "BLUNDER": 1, "MISTAKE": 2, "INACCURACY": 3}
        picked = [move for move in self.moves if move.tag in order]
        return tuple(
            sorted(picked, key=lambda move: (order[move.tag], -move.loss, move.ply))
        )


# ------------------------------------------------------------------ scoring
def centipawns(score, colour: chess.Color) -> int:
    """A score as centipawns from ``colour``'s point of view, mates flattened."""
    pov = score.pov(colour)
    if pov.is_mate():
        mate = pov.mate() or 0
        return MATE_SCORE if mate > 0 else -MATE_SCORE
    return int(pov.score() or 0)


def eval_text(cp: int) -> str:
    """``+0.42``-style text, or the mate distance when the score is a mate."""
    if abs(cp) >= MATE_SCORE:
        return "MATE" if cp > 0 else "-MATE"
    return f"{cp / 100:+.2f}"


def classify(
    loss: int,
    *,
    best: bool,
    sacrifice: bool = False,
    winning: bool = False,
    already_lost: bool = False,
) -> str:
    """Turn a centipawn loss into one of ``TAGS``."""
    if already_lost:
        return "BEST" if best else "GOOD"
    if best:
        return "BRILLIANT" if sacrifice and winning else "BEST"
    if loss <= 25:
        return "GOOD"
    if loss <= 70:
        return "INACCURACY"
    if loss <= 150:
        return "MISTAKE"
    return "BLUNDER"


def accuracy(losses: list[int]) -> int:
    """Lichess-style accuracy percentage from a list of centipawn losses."""
    if not losses:
        return 0
    average = sum(losses) / len(losses)
    value = 103.1668 * math.exp(-0.04354 * average) - 3.1669
    return max(0, min(100, round(value)))


def _see(board: chess.Board, move: chess.Move) -> int:
    """A shallow static exchange evaluation of ``move`` for the side to move."""
    victim = board.piece_at(move.to_square)
    gain = PIECE_VALUE[victim.piece_type] if victim is not None else 0
    board.push(move)
    replies = [
        answer
        for answer in board.legal_moves
        if answer.to_square == move.to_square and board.is_capture(answer)
    ]
    best_reply = 0
    for answer in replies:
        best_reply = max(best_reply, _see(board, answer))
    board.pop()
    return gain - best_reply


def leaves_material(board: chess.Board, mover: chess.Color) -> bool:
    """True when the opponent has a capture that wins at least a piece.

    ``board`` is the position *after* the move, with the opponent to move.
    """
    captures = [
        move
        for move in board.legal_moves
        if board.is_capture(move) and not board.is_en_passant(move)
    ]
    for move in captures:
        if _see(board, move) >= 2:
            return True
    return False


def _best_san(board: chess.Board, move: chess.Move | None) -> str:
    if move is None:
        return ""
    try:
        return board.san(move)
    except (ValueError, AssertionError):
        return move.uci()


# ------------------------------------------------------------------ review
def _review_sync(pgn: str, path: str, depth: int) -> GameReview:
    import chess.engine

    game = chess.pgn.read_game(io.StringIO(pgn or ""))
    if game is None:
        return GameReview(error="COULD NOT READ THAT PGN.", depth=depth)

    positions = [game.board()]
    played: list[chess.Move] = []
    san: list[str] = []
    for move in game.mainline_moves():
        board = positions[-1].copy()
        if move not in board.legal_moves:
            break
        san.append(board.san(move))
        board.push(move)
        positions.append(board)
        played.append(move)

    if not played:
        return GameReview(error="THAT GAME HAS NO MOVES TO REVIEW.", depth=depth)

    engine = chess.engine.SimpleEngine.popen_uci(path)
    try:
        scores: list[int] = []
        bests: list[chess.Move | None] = []
        for board in positions:
            info = engine.analyse(board.copy(stack=False), chess.engine.Limit(depth=depth))
            score = info.get("score")
            scores.append(centipawns(score, board.turn) if score is not None else 0)
            line = info.get("pv") or []
            bests.append(line[0] if line else None)
    finally:
        engine.quit()

    records: list[MoveReview] = []
    losses: dict[str, list[int]] = {"white": [], "black": []}
    for index, move in enumerate(played):
        before = positions[index]
        after = positions[index + 1]
        side = "white" if before.turn == chess.WHITE else "black"
        best_eval = scores[index]
        played_eval = -scores[index + 1]
        already_lost = best_eval <= -LOST_CP
        is_best = bests[index] is not None and bests[index] == move
        sacrifice = leaves_material(after, before.turn) if is_best else False
        loss = max(0, best_eval - played_eval)
        tag = classify(
            loss,
            best=is_best,
            sacrifice=sacrifice,
            winning=best_eval >= 50,
            already_lost=already_lost,
        )
        records.append(
            MoveReview(
                ply=index + 1,
                number=index // 2 + 1,
                side=side,
                san=san[index],
                tag=tag,
                loss=loss,
                best_san=_best_san(before, bests[index]),
                eval_text=eval_text(played_eval),
                sacrifice=sacrifice,
            )
        )
        losses[side].append(0 if already_lost else loss)

    counts = Counter(record.tag for record in records)
    return GameReview(
        moves=tuple(records),
        counts={tag: counts.get(tag, 0) for tag in TAGS},
        accuracy={side: accuracy(values) for side, values in losses.items()},
        depth=depth,
    )


async def review_pgn(pgn: str, path: str, *, depth: int = DEFAULT_DEPTH) -> GameReview:
    """Review ``pgn`` with Stockfish without blocking the UI."""
    if not path:
        return GameReview(
            error="GAME REVIEW NEEDS STOCKFISH // INSTALL IT OR POINT THE PATH FIELD AT THE BINARY."
        )
    try:
        return await asyncio.to_thread(_review_sync, pgn, path, depth)
    except FileNotFoundError:
        return GameReview(error="STOCKFISH NOT FOUND // CHECK THE PATH.")
    except Exception as exc:  # engine protocol, timeouts, bad binary
        detail = str(exc).strip().replace("\n", " ")[:160]
        return GameReview(error=f"REVIEW FAILED // {type(exc).__name__}: {detail}")


__all__ = [
    "DEFAULT_DEPTH",
    "GameReview",
    "MoveReview",
    "TAGS",
    "accuracy",
    "centipawns",
    "classify",
    "eval_text",
    "leaves_material",
    "review_pgn",
]
