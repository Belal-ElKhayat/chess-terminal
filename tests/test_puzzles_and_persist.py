import asyncio

import chess
import chess.pgn

from chess_terminal import persist
from chess_terminal.puzzles import PUZZLES


def test_puzzles_are_legal_and_labelled_honestly():
    assert len(PUZZLES) >= 15
    for puzzle in PUZZLES:
        board = chess.Board(puzzle.fen)
        assert board.outcome() is None, puzzle.source
        assert puzzle.solution, puzzle.source
        assert puzzle.hint
        assert puzzle.source
        for san in puzzle.solution:
            move = board.parse_san(san)
            assert move in board.legal_moves
            board.push(move)
        if "MATE" in puzzle.prompt:
            assert board.is_checkmate(), f"{puzzle.source} does not end in mate"
        assert puzzle.prompt.endswith(("MATE IN 2", "MATE IN 3", "FIND THE WINNING SHOT"))


def test_puzzles_start_with_the_side_that_moves():
    for puzzle in PUZZLES:
        board = chess.Board(puzzle.fen)
        side = "WHITE" if board.turn == chess.WHITE else "BLACK"
        assert puzzle.prompt.startswith(side)


def test_session_round_trip(monkeypatch, tmp_path):
    monkeypatch.setenv("CHESS_TERMINAL_HOME", str(tmp_path))
    assert persist.load_session() is None
    record = {"version": 1, "mode": "ai", "colour": "white", "moves": ["e2e4", "e7e5"]}
    path = persist.save_session(record)
    assert path is not None and path.exists()
    assert persist.load_session() == record
    persist.clear_session()
    assert persist.load_session() is None


def test_corrupt_session_is_ignored(monkeypatch, tmp_path):
    monkeypatch.setenv("CHESS_TERMINAL_HOME", str(tmp_path))
    persist.session_path().write_text("{not json", encoding="utf-8")
    assert persist.load_session() is None


def test_pgn_export_has_headers_and_the_moves(monkeypatch, tmp_path):
    monkeypatch.setenv("CHESS_TERMINAL_HOME", str(tmp_path))
    board = chess.Board()
    for san in ("e4", "e5", "Nf3"):
        board.push_san(san)
    path = persist.export_pgn(board, event="Chess.Terminal // Test", white="YOU", black="AI")
    text = path.read_text(encoding="utf-8")
    assert '[Event "Chess.Terminal // Test"]' in text
    assert '[White "YOU"]' in text
    assert '[Black "AI"]' in text
    assert "1. e4 e5 2. Nf3" in text
    assert path.parent == persist.games_dir()


def test_library_line_export_is_legal(monkeypatch, tmp_path):
    monkeypatch.setenv("CHESS_TERMINAL_HOME", str(tmp_path))
    path = persist.export_san(("e4", "e5", "Nf3", "Nc6"), event="Ruy Lopez")
    text = path.read_text(encoding="utf-8")
    assert '[Event "Ruy Lopez"]' in text
    assert "1. e4 e5 2. Nf3 Nc6" in text


def test_exported_pgn_can_be_read_back(monkeypatch, tmp_path):
    monkeypatch.setenv("CHESS_TERMINAL_HOME", str(tmp_path))
    board = chess.Board()
    for san in ("d4", "d5", "c4"):
        board.push_san(san)
    path = persist.export_pgn(board)
    game = chess.pgn.read_game((path).open(encoding="utf-8"))
    assert game is not None
    assert game.end().board().ply() == 3
