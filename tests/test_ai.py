import asyncio

import chess

from chess_terminal import ai


def test_parse_uci():
    board = chess.Board()
    assert ai.parse_move("e2e4", board) == chess.Move.from_uci("e2e4")


def test_parse_san():
    board = chess.Board()
    assert ai.parse_move("Nf3", board) == chess.Move.from_uci("g1f3")


def test_parse_fenced_json_reply():
    board = chess.Board()
    reply = '```json\n{"move": "e2e4"}\n```'
    assert ai.parse_move(reply, board) == chess.Move.from_uci("e2e4")


def test_parse_engine_line():
    board = chess.Board()
    assert ai.parse_move("bestmove g1f3 ponder e7e5", board) == chess.Move.from_uci("g1f3")


def test_parse_castling_variants():
    board = chess.Board("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
    assert ai.parse_move("O-O", board) == chess.Move.from_uci("e1g1")
    assert ai.parse_move("0-0-0", board) == chess.Move.from_uci("e1c1")


def test_parse_rejects_illegal_and_garbage():
    board = chess.Board()
    assert ai.parse_move("Qh5", board) is None  # blocked by the e2 pawn
    assert ai.parse_move("this is not chess", board) is None
    assert ai.parse_move("", board) is None


def test_prompt_contains_fen_history_and_legal_moves():
    board = chess.Board()
    prompt = ai.build_prompt(board, ["e4", "e5"])
    assert board.fen() in prompt
    assert "1. e4 e5" in prompt
    assert "g1f3" in prompt


def test_request_retries_with_feedback(monkeypatch):
    replies = iter(["nonsense", "also not a move", "Nf3"])
    seen_feedback = []

    async def fake_call(provider, model, key, board, history, feedback):
        seen_feedback.append(feedback)
        return next(replies)

    monkeypatch.setattr(ai, "_call_provider", fake_call)
    result = asyncio.run(ai.request_move("openai", "test-model", "sk-test", chess.Board(), []))

    assert result.move == chess.Move.from_uci("g1f3")
    assert len(result.attempts) == 3
    assert result.attempts[0].accepted is False
    assert result.attempts[-1].accepted is True
    assert seen_feedback[0] is None
    assert seen_feedback[1] is not None and "rejected" in seen_feedback[1]
    assert seen_feedback[2] is not None and "not a legal move" in seen_feedback[2]


def test_request_stops_after_three_bad_replies(monkeypatch):
    async def fake_call(*args, **kwargs):
        return "not a move"

    monkeypatch.setattr(ai, "_call_provider", fake_call)
    result = asyncio.run(ai.request_move("anthropic", "m", "sk-test", chess.Board(), []))
    assert result.move is None
    assert "3 attempts" in result.error
    assert len(result.attempts) == 3


def test_missing_key_returns_safe_error():
    result = asyncio.run(ai.request_move("openai", "gpt-4o-mini", "", chess.Board(), []))
    assert result.move is None
    assert "API key" in result.error


def test_models_and_providers_are_well_formed():
    keys = {provider.key for provider in ai.PROVIDERS}
    assert {"openai", "anthropic", "gemini", "openrouter", "ollama"} <= keys
    for provider in ai.PROVIDERS:
        assert provider.default_model in provider.models
        assert provider.label
        assert provider.requires_key is (provider.key != "ollama")
