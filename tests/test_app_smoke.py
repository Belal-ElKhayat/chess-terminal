import asyncio

import chess

from chess_terminal.banner import ITALIAN, mini_board
from chess_terminal.main import ChessTerminalApp
from chess_terminal.screens.game import GameScreen
from chess_terminal.screens.result import ResultScreen
from chess_terminal.widgets import BoardView


async def _navigate() -> None:
    app = ChessTerminalApp()
    async with app.run_test(size=(120, 42)) as pilot:
        await pilot.pause()
        assert type(app.screen).__name__ == "SplashScreen"

        await pilot.press("1")
        await pilot.pause()
        assert type(app.screen).__name__ == "AISetupScreen"
        assert app.screen.query_one("#api-key").password is True

        await pilot.press("escape")
        await pilot.pause()
        assert type(app.screen).__name__ == "SplashScreen"

        await pilot.press("2")
        await pilot.pause()
        assert type(app.screen).__name__ == "FriendScreen"
        await pilot.press("escape")
        await pilot.pause()
        assert type(app.screen).__name__ == "SplashScreen"

        await pilot.press("3")
        await pilot.pause()
        assert type(app.screen).__name__ == "LibraryScreen"
        await pilot.press("right")
        await pilot.pause()
        await pilot.press("down")
        await pilot.pause()
        await pilot.press("escape")
        await pilot.pause()
        assert type(app.screen).__name__ == "SplashScreen"


def test_screen_navigation():
    asyncio.run(_navigate())


async def _library_and_board() -> None:
    app = ChessTerminalApp()
    async with app.run_test(size=(120, 42)) as pilot:
        await pilot.pause()

        await pilot.press("3")
        await pilot.pause()
        await pilot.press("/")
        await pilot.pause()
        search = app.screen.query_one("#search")
        assert search.has_focus
        await pilot.press(*"italian")
        await pilot.pause()
        assert search.value == "italian"
        titles = [entry.title for entry in app.screen.view]
        assert "Italian Game: Giuoco Piano" in titles
        assert all("italian" in entry.search_text() for entry in app.screen.view)

        # Escape clears the search and returns focus to the list, not the menu.
        await pilot.press("escape")
        await pilot.pause()
        assert type(app.screen).__name__ == "LibraryScreen"
        assert search.value == ""
        assert app.screen.query_one("#library-list").has_focus

        await pilot.press("escape")
        await pilot.pause()
        assert type(app.screen).__name__ == "SplashScreen"

        # Category filters narrow the archive and keep one entry selected.
        await pilot.press("3")
        await pilot.pause()
        await pilot.press("3")
        await pilot.pause()
        assert app.screen.kind == "game"
        assert app.screen.view and all(entry.kind == "game" for entry in app.screen.view)
        await pilot.press("1")
        await pilot.pause()
        assert app.screen.kind == "opening"
        await pilot.press("escape")
        await pilot.pause()
        assert type(app.screen).__name__ == "SplashScreen"

        # Enter / arrows move a pawn from e2 to e4 on the game board.
        app.push_screen(GameScreen(mode="net", peer_present=True))
        await pilot.pause()
        board = app.screen.query_one("#board", BoardView)
        board.cursor = chess.E2
        await pilot.press("enter")
        await pilot.pause()
        assert board.selected == chess.E2
        await pilot.press("up", "up", "enter")
        await pilot.pause()
        assert app.screen.history == ["e4"]
        assert app.screen.board.peek().uci() == "e2e4"


def test_library_search_and_board_input():
    asyncio.run(_library_and_board())


async def _victory_popup() -> None:
    app = ChessTerminalApp()
    async with app.run_test(size=(120, 42)) as pilot:
        await pilot.pause()
        game = GameScreen(mode="ai")
        app.push_screen(game)
        await pilot.pause()
        # Keep the AI idle so the test never reaches the network.
        game.busy_ai = True
        for ply, uci in enumerate(("f2f3", "e7e5", "g2g4", "d8h4")):
            game.handle_message({"type": "move", "uci": uci, "ply": ply})
            await pilot.pause()

        assert game.board.is_checkmate()
        assert type(app.screen).__name__ == "ResultScreen"
        assert isinstance(app.screen, ResultScreen)
        assert "BLACK WINS" in app.screen.result

        await pilot.press("n")
        await pilot.pause()
        assert app.screen is game
        assert game.board.ply() == 0
        assert game.result_text == ""
        assert game.busy_ai is False


def test_victory_popup_and_rematch():
    asyncio.run(_victory_popup())


def test_splash_boards_are_eight_squares_wide():
    for fen in (None, ITALIAN):
        art = mini_board(fen).plain
        rows = art.split("\n")
        assert len(rows) == 10
        assert all(len(row) == 18 for row in rows)
        assert 8 == art.count("│") // 2
