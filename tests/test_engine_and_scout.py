import asyncio

import chess

from chess_terminal import ai, engine, scout


def test_find_stockfish_honours_the_environment(monkeypatch, tmp_path):
    binary = tmp_path / "stockfish.exe"
    binary.write_bytes(b"fake")
    monkeypatch.setenv("STOCKFISH_PATH", str(binary))
    assert engine.find_stockfish() == str(binary)


def test_find_stockfish_reports_nothing_for_a_missing_path(monkeypatch, tmp_path):
    monkeypatch.delenv("STOCKFISH_PATH", raising=False)
    monkeypatch.setattr(engine.shutil, "which", lambda name: None)
    assert engine.find_stockfish(str(tmp_path / "nope")) is None
    empty = tmp_path / "empty"
    empty.mkdir()
    assert engine.find_stockfish(str(empty)) is None


def test_analyse_without_a_binary_is_a_friendly_error(tmp_path):
    report = asyncio.run(engine.analyse(chess.Board(), str(tmp_path / "missing")))
    assert report.move is None
    assert "STOCKFISH" in report.error


def test_find_stockfish_ignores_directories(tmp_path):
    directory = tmp_path / "Stockfish"
    directory.mkdir()
    assert engine.find_stockfish(str(directory)) != str(directory)


def test_scout_parses_game_links():
    assert scout.parse_game_link("https://www.chess.com/game/live/168842570216") == (
        "chesscom",
        ("live", "168842570216"),
    )
    assert scout.parse_game_link("https://www.chess.com/game/daily/947761777") == (
        "chesscom",
        ("daily", "947761777"),
    )
    assert scout.parse_game_link("https://lichess.org/AbCd1234") == ("lichess", "AbCd1234")
    assert scout.parse_game_link("https://lichess.org/game/abcd1234/white") == (
        "lichess",
        "abcd1234",
    )
    assert scout.parse_game_link("1. e4 e5 2. Nf3")[0] == "pgn"
    assert scout.parse_game_link("not a game") is None


def test_lichess_ndjson_is_parsed(monkeypatch):
    payload = "\n".join(
        [
            '{"winner": "white", "status": "mate", "opening": {"eco": "B90", "name": "Sicilian Defense: Najdorf Variation"}, "players": {"white": {"rating": 1500}, "black": {"rating": 1510}}}',
            '{"winner": "black", "status": "resign", "opening": {"eco": "C50", "name": "Italian Game"}, "players": {"white": {"rating": 1490}, "black": {"rating": 1500}}}',
            '{"status": "draw", "opening": {"eco": "A00", "name": "Van Geet Opening"}, "players": {"white": {"rating": 1495}, "black": {"rating": 1495}}}',
        ]
    )

    async def fake_text(url, **kwargs):
        assert "lichess.org/api/games/user/" in url
        return payload

    monkeypatch.setattr(scout, "_fetch_text", fake_text)
    games = asyncio.run(scout.fetch_lichess("tester", "white"))
    assert len(games) == 3
    assert games[0].result == "win"
    assert games[1].result == "loss"
    assert games[2].result == "draw"
    assert games[0].eco == "B90"
    report = scout.summarise(games)
    assert report.games == 3
    assert report.score_pct == 50


def test_chesscom_archives_are_parsed(monkeypatch):
    pgn = '[ECO "B90"]\n[ECOUrl "https://www.chess.com/openings/Sicilian-Defense-Najdorf-Variation"]\n\n1. e4 c5 *'

    async def fake_json(url, **kwargs):
        if url.endswith("/games/archives"):
            return {"archives": ["https://api.chess.com/pub/player/x/games/2026/10"]}
        return {
            "games": [
                {
                    "rules": "chess",
                    "white": {"username": "X", "result": "win", "rating": 1500},
                    "black": {"username": "Y", "result": "resigned", "rating": 1510},
                    "pgn": pgn,
                    "url": "https://www.chess.com/game/live/123456",
                },
                {
                    "rules": "chess960",
                    "white": {"username": "X", "result": "win", "rating": 1500},
                    "black": {"username": "Y", "result": "resigned", "rating": 1510},
                    "pgn": pgn,
                },
            ]
        }

    monkeypatch.setattr(scout, "_fetch_json", fake_json)
    games = asyncio.run(scout.fetch_chesscom("x", "white"))
    assert len(games) == 1
    assert games[0].rating == 1500
    assert games[0].eco == "B90"
    assert "Sicilian" in games[0].opening


def test_link_resolution_uses_callback_and_archive(monkeypatch):
    pgn = '[Event "Live Chess"]\n[White "Hikaru"]\n[Black "Magnus"]\n[Result "1-0"]\n\n1. e4 *'
    calls = []

    async def fake_json(url, **kwargs):
        calls.append(url)
        if "/callback/live/game/123456" in url:
            return {"game": {"pgnHeaders": {"White": "Hikaru", "Date": "2026.10.01"}}}
        return {"games": [{"url": "https://www.chess.com/game/live/123456", "pgn": pgn}]}

    monkeypatch.setattr(scout, "_fetch_json", fake_json)
    result = asyncio.run(scout.fetch_pgn_from_link("https://www.chess.com/game/live/123456"))
    assert result == pgn
    assert any("/games/2026/10" in url for url in calls)


def test_read_pgn_and_recommend():
    pgn = (
        '[Event "Live Chess"]\n[White "Rookie"]\n[Black "Veteran"]\n'
        '[Result "1-0"]\n[WhiteElo "1450"]\n[ECO "B90"]\n'
        '[Opening "Sicilian Defense: Najdorf Variation"]\n\n'
        "1. e4 c5 2. Nf3 d6 3. d4 cxd4 4. Nxd4 Nf6 5. Nc3 a6 1-0\n"
    )
    game, username, opponent, rating = scout.read_pgn(pgn, "white")
    assert username == "Rookie"
    assert opponent == "Veteran"
    assert rating == 1450
    assert game.result == "win"
    recommendations = scout.recommend([game], "white", 1450)
    assert recommendations and all(item.entry.side == "white" for item in recommendations)
    assert all(item.reason for item in recommendations)


def test_recommend_uses_level_when_there_are_no_games():
    beginner = scout.recommend([], "black", 900)
    assert beginner
    assert all(item.entry.side == "black" for item in beginner)
    assert any(item.entry.level == "beginner" for item in beginner)


def test_ai_advice_and_review_use_the_transport(monkeypatch):
    seen = {}

    async def fake_call(provider, model, key, board, history, feedback, **kwargs):
        seen["system"] = kwargs.get("system_prompt")
        return "e2e4 because it claims the centre."

    monkeypatch.setattr(ai, "_call_provider", fake_call)
    advice = asyncio.run(ai.request_advice("openai", "m", "sk-test", chess.Board()))
    assert "e2e4" in advice.text
    assert seen["system"] == ai.ADVICE_PROMPT

    review = asyncio.run(ai.request_review("openai", "m", "sk-test", "1. e4 e5"))
    assert "e2e4" in review.text


def test_ai_review_without_a_key_is_safe():
    review = asyncio.run(ai.request_review("openai", "m", "", "1. e4 e5"))
    assert review.text == ""
    assert "KEY" in review.error


def test_clock_formatting_and_arithmetic():
    from chess_terminal import clock

    assert clock.format_ms(300_000) == "5:00"
    assert clock.format_ms(-20) == "0:00"
    live = clock.new_clock(clock.spec_for("10|5"), now=100.0)
    assert live["running"] == "white"
    clock.after_move(live, "white", now=101.0)
    assert live["running"] == "black"
    assert 604_000 <= live["white_ms"] <= 605_000
    assert live["black_ms"] == 600_000
    assert clock.flag(live, now=105.0) is None
    # A clock that has not started yet begins with the first move, no increment.
    pending = clock.new_clock(clock.spec_for("10|5"), now=200.0)
    pending["running"] = None
    clock.after_move(pending, "white", now=260.0)
    assert pending["white_ms"] == 600_000
    assert pending["running"] == "black"

    live["black_ms"] = 0
    assert clock.flag(live, now=105.5) == "black"
    frozen = clock.settle(live, now=106.0)
    assert frozen["running"] is None
    assert frozen["black_ms"] == 0


def test_opening_metadata_is_complete():
    from chess_terminal.data import OPENINGS, TRAPS

    assert {trap.side for trap in TRAPS} == {"white", "black"}
    assert sum(1 for trap in TRAPS if trap.side == "white") == 4
    for opening in OPENINGS:
        assert opening.side in ("white", "black")
        assert opening.level in ("beginner", "club", "advanced")
    assert sum(1 for opening in OPENINGS if opening.side == "white") >= 10
    assert sum(1 for opening in OPENINGS if opening.side == "black") >= 10
