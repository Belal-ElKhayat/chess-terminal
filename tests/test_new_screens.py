import asyncio

import chess
from textual.widgets import Static

from chess_terminal import persist
from chess_terminal.main import ChessTerminalApp
from chess_terminal.screens.game import GameScreen


async def _engine_and_puzzles() -> None:
    app = ChessTerminalApp()
    async with app.run_test(size=(120, 42)) as pilot:
        await pilot.pause()
        assert type(app.screen).__name__ == "SplashScreen"

        await pilot.press("4")
        await pilot.pause()
        assert type(app.screen).__name__ == "EngineRoomScreen"
        assert "STOCKFISH" in str(app.screen.query_one("#stockfish-status", Static).content)

        await pilot.press("1")
        await pilot.pause()
        assert type(app.screen).__name__ == "AnalysisScreen"

        await pilot.press("escape")
        await pilot.pause()
        assert type(app.screen).__name__ == "EngineRoomScreen"

        await pilot.press("2")
        await pilot.pause()
        assert type(app.screen).__name__ == "ReviewScreen"
        await pilot.press("enter")
        await pilot.pause()
        assert "PASTE" in str(app.screen.query_one("#review-head", Static).content)
        await pilot.press("escape")
        await pilot.pause()

        await pilot.press("3")
        await pilot.pause()
        assert type(app.screen).__name__ == "ScoutScreen"
        await pilot.press("escape")
        await pilot.pause()
        await pilot.press("escape")
        await pilot.pause()
        assert type(app.screen).__name__ == "SplashScreen"

        await pilot.press("5")
        await pilot.pause()
        assert type(app.screen).__name__ == "PuzzlesScreen"
        assert app.screen.puzzle is not None
        assert "TO MOVE" in app.screen.puzzle.prompt
        # Mate-in-3 puzzles take two correct attacking moves; play the line out.
        for _ in range(4):
            if app.screen.solved:
                break
            app.screen._play_solution()
            await pilot.pause()
        assert app.screen.solved is True
        assert app.session.puzzle_solved == 1
        assert app.session.puzzle_streak == 1
        await pilot.press("h")
        await pilot.pause()
        await pilot.press("n")
        await pilot.pause()
        assert app.screen.solved is False
        await pilot.press("escape")
        await pilot.pause()
        assert type(app.screen).__name__ == "SplashScreen"


def test_engine_room_and_puzzle_trainer():
    asyncio.run(_engine_and_puzzles())


async def _trap_sides() -> None:
    app = ChessTerminalApp()
    async with app.run_test(size=(120, 42)) as pilot:
        await pilot.pause()
        await pilot.press("3")
        await pilot.pause()

        await pilot.press("w")
        await pilot.pause()
        assert app.screen.kind == "trap"
        assert app.screen.side == "white"
        assert app.screen.view and all(
            entry.kind == "trap" and entry.side == "white" for entry in app.screen.view
        )
        assert len(app.screen.view) == 4

        await pilot.press("b")
        await pilot.pause()
        assert app.screen.side == "black"
        assert app.screen.view and all(entry.side == "black" for entry in app.screen.view)
        assert len(app.screen.view) == 8

        await pilot.press("2")
        await pilot.pause()
        assert app.screen.kind == "trap"
        assert app.screen.side is None
        assert len(app.screen.view) == 12

        await pilot.press("0")
        await pilot.pause()
        assert app.screen.kind is None
        assert len(app.screen.view) == len(app.screen.entries)

        await pilot.press("escape")
        await pilot.pause()


def test_trap_side_filters():
    asyncio.run(_trap_sides())


async def _result_actions() -> None:
    app = ChessTerminalApp()
    async with app.run_test(size=(120, 42)) as pilot:
        await pilot.pause()
        game = GameScreen(mode="ai")
        app.push_screen(game)
        await pilot.pause()
        game.busy_ai = True
        for ply, uci in enumerate(("f2f3", "e7e5", "g2g4", "d8h4")):
            game.handle_message({"type": "move", "uci": uci, "ply": ply})
            await pilot.pause()
        assert game.board.is_checkmate()
        assert type(app.screen).__name__ == "ResultScreen"
        assert app.screen.can_coach is True

        await pilot.press("s")
        await pilot.pause()
        assert list(persist.games_dir().glob("*.pgn"))

        await pilot.press("a")
        await pilot.pause()
        assert type(app.screen).__name__ == "CoachScreen"
        body = str(app.screen.query_one("#coach-body", Static).content)
        assert "NO KEY" in body or "KEY" in body

        await pilot.press("escape")
        await pilot.pause()
        assert app.screen is game
        assert game.game_over is True


def test_result_card_saves_pgn_and_opens_coach():
    asyncio.run(_result_actions())


async def _save_and_resume() -> None:
    persist.save_session(
        {
            "version": 1,
            "mode": "ai",
            "colour": "white",
            "moves": ["e2e4", "e7e5"],
        }
    )
    app = ChessTerminalApp()
    async with app.run_test(size=(120, 42)) as pilot:
        await pilot.pause()
        hint = str(app.screen.query_one("#splash-hint", Static).content)
        assert "RESUME" in hint

        await pilot.press("r")
        await pilot.pause()
        assert type(app.screen).__name__ == "GameScreen"
        assert app.screen.mode == "ai"
        assert app.screen.board.ply() == 2
        assert app.screen.history == ["e4", "e5"]

        # Leave a live game and confirm it is still resumable.
        await pilot.press("escape")
        await pilot.pause()
        assert persist.load_session() is not None


def test_resume_saved_ai_game():
    asyncio.run(_save_and_resume())


async def _clock_picker() -> None:
    app = ChessTerminalApp()
    async with app.run_test(size=(120, 42)) as pilot:
        await pilot.pause()
        game = GameScreen(mode="ai")
        app.push_screen(game)
        await pilot.pause()
        game.busy_ai = True

        await pilot.press("q")
        await pilot.pause()
        assert type(app.screen).__name__ == "ClockPickerScreen"
        await pilot.press("1")
        await pilot.pause()
        assert game.clock is not None
        assert game.clock["white_ms"] == 5 * 60_000
        assert game.clock["running"] == "white"

        # Moving charges White and hands the clock to Black. The AI is kept
        # idle so the test never reaches the network.
        game.busy_ai = False
        board = game.query_one("#board")
        board.focus()
        board.cursor = chess.E2
        await pilot.press("enter")
        await pilot.press("up", "up", "enter")
        await pilot.pause()
        assert game.clock["running"] == "black"
        assert game.clock["white_ms"] <= 5 * 60_000
        game.busy_ai = True


def test_clock_picker_and_countdown():
    asyncio.run(_clock_picker())


async def _play_engine_line() -> None:
    from chess_terminal import engine
    from chess_terminal.screens.engine_room import AnalysisScreen

    app = ChessTerminalApp()
    async with app.run_test(size=(120, 42)) as pilot:
        await pilot.pause()
        app.push_screen(AnalysisScreen())
        await pilot.pause()
        screen = app.screen
        screen.last_report = engine.EngineReport(
            move=chess.Move.from_uci("e2e4"),
            san="e4",
            score="+0.31",
            pv=("e4", "e5"),
            depth=14,
            lines=(engine.EngineLine("+0.31", ("e4", "e5")),),
        )
        await pilot.press("p")
        await pilot.pause()
        assert screen.board.ply() == 1
        assert screen.board.peek() == chess.Move.from_uci("e2e4")

        await pilot.press("c")
        await pilot.pause()
        body = str(screen.query_one("#analysis-body", Static).content)
        assert "FEN" in body


def test_analyser_plays_the_engine_move():
    asyncio.run(_play_engine_line())
