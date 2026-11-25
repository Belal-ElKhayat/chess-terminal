import asyncio

import chess

from chess_terminal import engine, review, scout


def test_fen_input_becomes_a_loadable_game():
    fen = "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 4 3"
    assert scout.looks_like_fen(fen) is True
    assert scout.looks_like_fen("not a position") is False
    assert scout.parse_game_link(fen) == ("fen", fen)

    pgn = asyncio.run(scout.fetch_pgn_from_link(fen))
    game = chess.pgn.read_game(__import__("io").StringIO(pgn))
    assert game is not None
    assert game.board().fen() == chess.Board(fen).fen()
    assert list(game.mainline_moves()) == []


def test_detect_colour_reads_the_players():
    pgn = (
        '[Event "Live Chess"]\n[White "Rookie"]\n[Black "Veteran"]\n'
        '[Result "1-0"]\n\n1. e4 e5 1-0\n'
    )
    assert scout.detect_colour(pgn, "rookie") == "white"
    assert scout.detect_colour(pgn, "@Veteran") == "black"
    assert scout.detect_colour(pgn, "someone-else") == ""
    assert scout.detect_colour("1. e4 e5", "rookie") == ""


def test_classify_turns_losses_into_tags():
    assert review.classify(0, best=True) == "BEST"
    assert review.classify(0, best=False) == "GOOD"
    assert review.classify(40, best=False) == "INACCURACY"
    assert review.classify(120, best=False) == "MISTAKE"
    assert review.classify(400, best=False) == "BLUNDER"
    assert review.classify(0, best=True, sacrifice=True, winning=True) == "BRILLIANT"
    assert review.classify(0, best=True, sacrifice=True, winning=False) == "BEST"
    # Nothing is a blunder once the position is already lost.
    assert review.classify(900, best=False, already_lost=True) == "GOOD"


def test_accuracy_and_eval_text():
    assert review.accuracy([]) == 0
    assert review.accuracy([0, 0, 0]) >= 99
    assert review.accuracy([300, 300]) < review.accuracy([20, 20])
    assert review.eval_text(42) == "+0.42"
    assert review.eval_text(-15) == "-0.15"
    assert review.eval_text(review.MATE_SCORE) == "MATE"


def test_brilliant_detection_needs_a_real_sacrifice():
    # 1. e4 e5 2. Qh5 Nc6 3. Qxf7+: the queen can be taken, so White gave it up.
    board = chess.Board()
    for san in ("e4", "e5", "Qh5", "Nc6", "Qxf7+"):
        board.push_san(san)
    assert review.leaves_material(board, chess.WHITE) is True

    quiet = chess.Board()
    quiet.push_san("e4")
    assert review.leaves_material(quiet, chess.WHITE) is False


def test_highlights_put_blunders_first():
    moves = (
        review.MoveReview(1, 1, "white", "e4", "BEST", 0),
        review.MoveReview(2, 1, "black", "Nf6", "INACCURACY", 50),
        review.MoveReview(3, 2, "white", "Qh5", "BLUNDER", 400),
        review.MoveReview(4, 2, "black", "Nxh5", "BRILLIANT", 0),
    )
    result = review.GameReview(moves=moves, counts={"BLUNDER": 1})
    assert [move.tag for move in result.highlights] == [
        "BRILLIANT",
        "BLUNDER",
        "INACCURACY",
    ]


def test_review_without_stockfish_explains_itself():
    result = asyncio.run(review.review_pgn("1. e4 e5", ""))
    assert result.moves == ()
    assert "STOCKFISH" in result.error

    missing = asyncio.run(engine.probe(""))
    assert missing[0] == "" and "STOCKFISH" in missing[1]
