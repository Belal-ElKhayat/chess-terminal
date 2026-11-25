"""Engine room: analyser, game review and opening scout."""

from __future__ import annotations

import asyncio
import io

import chess
import chess.pgn
from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Input, Static

from .. import ai, engine, review, scout, theme
from ..widgets import BoardView, KeyboardList
from .coach import CoachScreen


class EngineRoomScreen(Screen):
    """The two analysis tools, plus Stockfish configuration."""

    BINDINGS = [Binding("escape", "back", "Back")]

    def compose(self) -> ComposeResult:
        yield Static("CHESS.TERMINAL // ENGINE ROOM", classes="telemetry")
        yield Static("STOCKFISH OR BYOK AI // CHESS.COM & LICHESS SCOUT", classes="telemetry-dim")
        yield Horizontal(
            Vertical(
                Static("TOOLS // ↑↓ ENTER", classes="panel-title"),
                KeyboardList(
                    ("BEST MOVE ANALYSER", "GAME REVIEW", "OPENING SCOUT"),
                    on_select=self._choose,
                    id="engine-menu",
                    pad_width=30,
                ),
                classes="form-col-tight",
            ),
            Vertical(
                Static("STOCKFISH BINARY", classes="panel-title"),
                Static("", id="stockfish-status"),
                Input(
                    value=self.app.session.stockfish_path,
                    placeholder="path to stockfish.exe (optional)",
                    id="stockfish-path",
                ),
                Static("", id="stockfish-hint", classes="hint"),
                Static(
                    "Without Stockfish, the analyser asks the AI provider already "
                    "configured in PLAY VS AI. Nothing is downloaded automatically.",
                    id="engine-note",
                ),
                classes="form-col",
            ),
            id="screen-body",
        )
        yield Static("ESC BACK // PATH STAYS IN RAM FOR THIS SESSION", classes="footer")

    def on_mount(self) -> None:
        self.query_one("#engine-menu", KeyboardList).focus()
        self._refresh_status()
        self.query_one("#stockfish-path", Input).value = self.app.session.stockfish_path

    def _refresh_status(self) -> None:
        """Find a binary, then prove it answers UCI before calling it ready."""
        path = engine.find_stockfish(self.app.session.stockfish_path)
        status = self.query_one("#stockfish-status", Static)
        hint = self.query_one("#stockfish-hint", Static)
        if not path:
            status.update(Text("STOCKFISH // NOT FOUND", style=theme.BRIGHT))
            hint.update(
                Text(
                    "Install Stockfish, set STOCKFISH_PATH, or paste its path above.",
                    style=theme.DIM,
                )
            )
            return
        status.update(Text("STOCKFISH // CHECKING...", style=theme.DIM))
        hint.update(Text(path, style=theme.DIM))
        self.run_worker(self._probe(path), group="probe", exclusive=True)

    async def _probe(self, path: str) -> None:
        # Debounce: typing a path fires Changed once per key.
        await asyncio.sleep(0.25)
        identity, error = await engine.probe(path)
        if not self.is_mounted:
            return
        status = self.query_one("#stockfish-status", Static)
        hint = self.query_one("#stockfish-hint", Static)
        if error:
            status.update(Text("STOCKFISH // NOT USABLE", style=theme.BRIGHT))
            hint.update(Text(f"{path} // {error}", style=theme.DIM))
            return
        status.update(Text(f"{identity.upper()} // READY"[:52], style=f"{theme.BRIGHT} bold"))
        hint.update(Text(path, style=theme.DIM))

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "stockfish-path":
            self.app.session.stockfish_path = event.value.strip()
            self._refresh_status()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "stockfish-path":
            self.query_one("#engine-menu", KeyboardList).focus()

    def _choose(self, index: int) -> None:
        if index == 0:
            self.app.push_screen(AnalysisScreen())
        elif index == 1:
            self.app.push_screen(ReviewScreen())
        else:
            self.app.push_screen(ScoutScreen())

    def action_back(self) -> None:
        self.app.pop_screen()


class AnalysisScreen(Screen):
    """A free board that can be analysed, or loaded from a game link."""

    BINDINGS = [
        Binding("a", "analyse", "Analyse"),
        Binding("p", "play_engine(0)", "Play best"),
        Binding("1", "play_engine(0)", "Line 1"),
        Binding("2", "play_engine(1)", "Line 2"),
        Binding("3", "play_engine(2)", "Line 3"),
        Binding("c", "copy_fen", "Copy FEN"),
        Binding("u", "undo", "Undo"),
        Binding("f", "flip", "Flip"),
        Binding("r", "reset", "Reset"),
        Binding("escape", "back", "Back"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.board = chess.Board()
        self.last_move: chess.Move | None = None
        self.selected: int | None = None
        self.pending_promotion: tuple[int, int] | None = None
        self.busy = False
        self.review: list[chess.Board] | None = None
        self.review_index = 0
        self.last_report: engine.EngineReport | None = None
        self._ready = False

    def compose(self) -> ComposeResult:
        yield Static("CHESS.TERMINAL // BEST MOVE ANALYSER", classes="telemetry")
        yield Static(
            "MOVE BOTH SIDES // A ANALYSE // PASTE A GAME TO REVIEW IT",
            classes="telemetry-dim",
        )
        yield Horizontal(
            Vertical(
                Vertical(
                    BoardView(
                        self.board,
                        cell_width=4,
                        cell_height=2,
                        on_activate=self._activate,
                        id="analysis-board",
                    ),
                    id="analysis-stage",
                ),
                Static("", id="analysis-board-hint", classes="hint"),
                id="analysis-board-col",
            ),
            Vertical(
                Static("PASTE GAME LINK / PGN", classes="panel-title"),
                Input(
                    placeholder="chess.com/game/live/... or lichess.org/...",
                    id="pgn",
                ),
                Static("", id="analysis-head", classes="panel-title"),
                VerticalScroll(Static("", id="analysis-body"), classes="scroll-log"),
                id="analysis-side",
            ),
            id="screen-body",
        )
        yield Static(
            "ENTER LOADS // A ANALYSE // P PLAY BEST // C FEN // U UNDO // F FLIP // R RESET // [ ] STEP",
            classes="footer",
        )

    def on_mount(self) -> None:
        self._ready = True
        self.query_one("#analysis-board", BoardView).focus()
        self._refresh()

    # ----------------------------------------------------------------- board
    def _refresh(self) -> None:
        if not self._ready:
            return
        view = self.query_one("#analysis-board", BoardView)
        view.set_board(self.board, last_move=self.last_move)
        view.set_highlights(selected=self.selected)
        side = "WHITE" if self.board.turn == chess.WHITE else "BLACK"
        head = Text()
        head.append(f"POSITION // {side} TO MOVE", style=f"{theme.BRIGHT} bold")
        head.append(f" // PLY {self.board.ply()}", style=theme.DIM)
        if self.review is not None:
            head.append(f" // REVIEW {self.review_index}/{len(self.review) - 1}", style=theme.AMBER)
        self.query_one("#analysis-head", Static).update(head)
        self.query_one("#analysis-board-hint", Static).update(
            "SELECT A PIECE, THEN ITS DESTINATION." if self.selected is not None else ""
        )

    def _activate(self, square: int) -> None:
        if self.busy or self.pending_promotion or self.review is not None:
            return
        piece = self.board.piece_at(square)
        if self.selected is None:
            if piece is not None and piece.color == self.board.turn:
                self.selected = square
                self._refresh()
            return
        if square == self.selected:
            self.selected = None
            self._refresh()
            return
        if piece is not None and piece.color == self.board.turn:
            self.selected = square
            self._refresh()
            return

        moves = [
            move
            for move in self.board.legal_moves
            if move.from_square == self.selected and move.to_square == square
        ]
        if not moves:
            self.selected = None
            self._refresh()
            return
        if any(move.promotion for move in moves):
            self.pending_promotion = (self.selected, square)
            self.query_one("#analysis-board-hint", Static).update("PROMOTION // PRESS Q R B N")
            return
        self._push(moves[0])

    def on_key(self, event) -> None:
        if self.pending_promotion is not None:
            promotion = {
                "q": chess.QUEEN,
                "r": chess.ROOK,
                "b": chess.BISHOP,
                "n": chess.KNIGHT,
            }.get(event.key.lower())
            if promotion is not None:
                start, end = self.pending_promotion
                self.pending_promotion = None
                move = chess.Move(start, end, promotion=promotion)
                if move in self.board.legal_moves:
                    self._push(move)
                else:
                    self._refresh()
                event.stop()
            return
        if event.key in ("left_square_bracket", "["):
            self._step(-1)
            event.stop()
        elif event.key in ("right_square_bracket", "]"):
            self._step(1)
            event.stop()

    def _note(self, message: str) -> None:
        self.query_one("#analysis-body", Static).update(Text(message, style=theme.BRIGHT))

    def _push(self, move: chess.Move) -> None:
        self.board.push(move)
        self.last_move = move
        self.selected = None
        self.last_report = None
        self._refresh()

    def _step(self, delta: int) -> None:
        if self.review is None:
            return
        index = max(0, min(len(self.review) - 1, self.review_index + delta))
        if index == self.review_index:
            return
        self.review_index = index
        self.board = self.review[index].copy()
        self.last_move = self.board.peek() if self.board.move_stack else None
        self.selected = None
        self.last_report = None
        self._refresh()

    def action_undo(self) -> None:
        if self.review is not None or not self.board.move_stack:
            return
        self.board.pop()
        self.last_move = self.board.peek() if self.board.move_stack else None
        self.selected = None
        self.last_report = None
        self._refresh()

    def action_flip(self) -> None:
        view = self.query_one("#analysis-board", BoardView)
        view.flipped = not view.flipped
        view.refresh()

    def action_reset(self) -> None:
        self.board = chess.Board()
        self.last_move = None
        self.selected = None
        self.pending_promotion = None
        self.review = None
        self.review_index = 0
        self.last_report = None
        self.query_one("#analysis-body", Static).update("")
        self._refresh()

    # ------------------------------------------------------------- analysing
    def action_analyse(self) -> None:
        if self.busy:
            return
        self.busy = True
        self.query_one("#analysis-head", Static).update(
            Text("ANALYSING...", style=f"{theme.BRIGHT} bold")
        )
        self.run_worker(self._analyse(), group="analysis", exclusive=True)

    async def _analyse(self) -> None:
        session = self.app.session
        snapshot = self.board.copy(stack=False)
        path = engine.find_stockfish(session.stockfish_path)
        body = self.query_one("#analysis-body", Static)
        text = Text()

        if path:
            report = await engine.analyse(snapshot, path)
            if report.error:
                self.last_report = None
                text.append(report.error, style=theme.BRIGHT)
            else:
                self.last_report = report
                text.append("BEST MOVE // ", style=theme.DIM)
                text.append(f"{report.san} ({report.move.uci()})\n", style=f"{theme.BRIGHT} bold")
                text.append("EVAL // ", style=theme.DIM)
                text.append(f"{report.score}\n", style=theme.AMBER)
                text.append(f"DEPTH {report.depth} // SOURCE STOCKFISH\n\n", style=theme.DIM)
                for number, line in enumerate(report.lines, start=1):
                    text.append(f"LINE {number} {line.score} ", style=theme.BRIGHT)
                    text.append(" ".join(line.pv) + "\n", style=theme.AMBER)
                text.append("\nP OR 1-3 PLAYS A LINE'S FIRST MOVE\n", style=theme.DIM)
        else:
            advice = await ai.request_advice(
                session.provider_key,
                session.model,
                session.api_key,
                snapshot,
            )
            if advice.error:
                text.append(advice.error + "\n\n", style=theme.BRIGHT)
                text.append(
                    "Install Stockfish or set a path on the ENGINE ROOM screen for local analysis.",
                    style=theme.DIM,
                )
            else:
                move = ai.parse_move(advice.text, snapshot)
                if move is not None:
                    text.append("BEST MOVE // ", style=theme.DIM)
                    text.append(f"{snapshot.san(move)} ({move.uci()})\n", style=f"{theme.BRIGHT} bold")
                text.append("\n", style=theme.DIM)
                text.append(advice.text + "\n", style=theme.AMBER)
                text.append("\nSOURCE // BYOK AI", style=theme.DIM)

        if not self.is_mounted:
            return
        self.busy = False
        body.update(text)
        self._refresh()

    # -------------------------------------------------------------- loading
    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id != "pgn":
            return
        value = event.value.strip()
        if not value:
            return
        self.query_one("#analysis-body", Static).update(Text("FETCHING GAME...", style=theme.DIM))
        self.run_worker(self._load(value), group="analysis", exclusive=True)

    async def _load(self, value: str) -> None:
        try:
            pgn = await scout.fetch_pgn_from_link(value)
            game = chess.pgn.read_game(io.StringIO(pgn))
        except (scout.ScoutError, ValueError) as exc:
            if self.is_mounted:
                self.query_one("#analysis-body", Static).update(Text(str(exc), style=theme.BRIGHT))
            return
        if game is None:
            if self.is_mounted:
                self.query_one("#analysis-body", Static).update(
                    Text("COULD NOT READ THAT PGN.", style=theme.BRIGHT)
                )
            return

        board = chess.Board()
        review = [board.copy()]
        for move in game.mainline_moves():
            if move not in board.legal_moves:
                break
            board.push(move)
            review.append(board.copy())
        if not self.is_mounted:
            return

        self.review = review
        self.review_index = len(review) - 1
        self.board = review[-1].copy()
        self.last_move = self.board.peek() if self.board.move_stack else None
        self.selected = None
        headers = game.headers
        text = Text()
        text.append(
            f"{headers.get('White', '?')} vs {headers.get('Black', '?')}\n",
            style=f"{theme.BRIGHT} bold",
        )
        text.append(
            f"{headers.get('Event', 'GAME')} // {headers.get('Result', '*')} // "
            f"{len(review) - 1} PLIES\n",
            style=theme.DIM,
        )
        text.append("[ ] STEP THROUGH // A ANALYSE THIS POSITION", style=theme.AMBER)
        self.query_one("#analysis-body", Static).update(text)
        self._refresh()

    # -------------------------------------------------------------- playing
    def action_play_engine(self, index: int = 0) -> None:
        """Play the first move of line ``index`` from the last analysis."""
        if self.busy:
            return
        if self.review is not None:
            self._note("THAT GAME IS READ-ONLY // R RESETS TO AN EMPTY BOARD")
            return
        report = self.last_report
        if report is None or not report.lines:
            self._note("NOTHING TO PLAY // PRESS A TO ANALYSE THIS POSITION FIRST.")
            return
        line = report.lines[min(index, len(report.lines) - 1)]
        if not line.pv:
            self._note("THAT LINE HAS NO MOVES.")
            return
        try:
            move = self.board.parse_san(line.pv[0])
        except ValueError:
            self._note("THAT LINE NO LONGER FITS // ANALYSE AGAIN.")
            return
        self._push(move)
        self._note(f"PLAYED {line.pv[0]} // LINE {min(index, len(report.lines) - 1) + 1} {line.score}")

    def action_copy_fen(self) -> None:
        fen = self.board.fen()
        try:
            self.app.copy_to_clipboard(fen)
        except Exception:
            self._note(f"CLIPBOARD UNAVAILABLE // {fen}")
            return
        self._note(f"FEN COPIED // {fen}")

    def action_back(self) -> None:
        self.app.pop_screen()


TAG_STYLE = {
    "BRILLIANT": f"{theme.BRIGHT} bold",
    "BLUNDER": f"{theme.BRIGHT} bold",
    "MISTAKE": theme.BRIGHT,
    "INACCURACY": theme.AMBER,
    "GOOD": theme.DIM,
    "BEST": theme.DIM,
}


class ReviewScreen(Screen):
    """A Stockfish review of a whole game: blunders, mistakes and brilliants."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("r", "review", "Review"),
        Binding("a", "coach", "Coach"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.busy = False
        self.pgn = ""
        self.last_review: review.GameReview | None = None

    def compose(self) -> ComposeResult:
        yield Static("CHESS.TERMINAL // GAME REVIEW", classes="telemetry")
        yield Static(
            "STOCKFISH SEARCHES EVERY MOVE // BLUNDERS, MISTAKES, INACCURACIES, BRILLIANTS",
            classes="telemetry-dim",
        )
        yield Horizontal(
            Vertical(
                Static("GAME LINK / PGN", classes="panel-title"),
                Input(
                    placeholder="chess.com/game/live/... or a PGN",
                    id="review-pgn",
                ),
                Button("REVIEW", id="review-run", variant="primary"),
                Static(
                    "\nAccuracy is scored from every move's centipawn loss. "
                    "A brilliant is a sacrifice that is also the best move.",
                    id="engine-note",
                ),
                classes="form-col-tight",
            ),
            Vertical(
                Static("", id="review-head", classes="panel-title"),
                VerticalScroll(Static("", id="review-body"), classes="scroll-log"),
                id="review-side",
            ),
            id="screen-body",
        )
        yield Static(
            "ENTER REVIEWS // R AGAIN // A BYOK COACH // ESC BACK",
            classes="footer",
        )

    def on_mount(self) -> None:
        self.query_one("#review-pgn", Input).focus()

    def _head(self, message: str, colour: str = theme.BRIGHT) -> None:
        self.query_one("#review-head", Static).update(Text(message, style=colour))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "review-run":
            self._start()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "review-pgn":
            self._start()

    def _start(self) -> None:
        if self.busy:
            return
        value = self.query_one("#review-pgn", Input).value.strip()
        if not value:
            self._head("PASTE A GAME LINK OR PGN FIRST.")
            return
        path = engine.find_stockfish(self.app.session.stockfish_path)
        if not path:
            self._head("STOCKFISH NOT FOUND // SET ITS PATH IN THE ENGINE ROOM.")
            self.query_one("#review-body", Static).update(
                Text(
                    "The review needs a real engine: every move is scored by search, "
                    "not by a language model.\n\n"
                    "Install Stockfish or paste its path in ENGINE ROOM, then press R.",
                    style=theme.DIM,
                )
            )
            return
        self.busy = True
        self._head("LOADING THE GAME...", theme.DIM)
        self.run_worker(self._review(value, path), group="review", exclusive=True)

    async def _review(self, value: str, path: str) -> None:
        try:
            pgn = await scout.fetch_pgn_from_link(value)
        except scout.ScoutError as exc:
            if self.is_mounted:
                self.busy = False
                self._head(str(exc))
            return
        if not self.is_mounted:
            return
        self.pgn = pgn
        self._head("REVIEWING EVERY MOVE...", theme.DIM)
        self.query_one("#review-body", Static).update(
            Text("STOCKFISH IS SEARCHING EVERY POSITION // A FEW SECONDS.", style=theme.DIM)
        )
        result = await review.review_pgn(pgn, path)
        if not self.is_mounted:
            return
        self.busy = False
        self.last_review = result
        if result.error:
            self._head(result.error)
            return
        self._render_review(result)

    def _render_review(self, result: review.GameReview) -> None:
        self._head(f"REVIEW // {len(result.moves)} PLIES // DEPTH {result.depth}", theme.BRIGHT)
        text = Text()
        text.append(
            f"WHITE {result.accuracy.get('white', 0)}%   "
            f"BLACK {result.accuracy.get('black', 0)}%   ACCURACY\n\n",
            style=f"{theme.BRIGHT} bold",
        )
        counts = "   ".join(
            f"{tag} {result.counts.get(tag, 0)}"
            for tag in ("BRILLIANT", "BLUNDER", "MISTAKE", "INACCURACY")
        )
        text.append(counts + "\n\n", style=theme.AMBER)

        highlights = result.highlights
        if not highlights:
            text.append(
                "NO BLUNDERS, MISTAKES OR BRILLIANTS // A CLEAN GAME.\n", style=theme.DIM
            )
        for move in highlights:
            text.append(f"{move.label:<12}", style=f"{theme.BRIGHT} bold")
            text.append(f"{move.tag:<12}", style=TAG_STYLE.get(move.tag, theme.AMBER))
            text.append(f"{move.eval_text:>7}", style=theme.AMBER)
            if move.tag not in ("BEST", "BRILLIANT"):
                text.append(f"   BEST {move.best_san}", style=theme.DIM)
            text.append("\n")
        text.append(
            "\nEVAL IS FROM THE SIDE THAT JUST MOVED // A OPENS THE BYOK COACH",
            style=theme.DIM,
        )
        self.query_one("#review-body", Static).update(text)

    def action_review(self) -> None:
        self._start()

    def action_coach(self) -> None:
        if not self.pgn:
            self._head("REVIEW A GAME FIRST // THEN A OPENS THE BYOK COACH.")
            return
        self.app.push_screen(CoachScreen(self.pgn))

    def action_back(self) -> None:
        self.app.pop_screen()


class ScoutScreen(Screen):
    """Import public games and recommend openings for colour + Elo."""

    BINDINGS = [Binding("escape", "back", "Back")]

    def __init__(self) -> None:
        super().__init__()
        self.busy = False
        self.last_recommendations: tuple[scout.Recommendation, ...] = ()

    def compose(self) -> ComposeResult:
        yield Static("CHESS.TERMINAL // OPENING SCOUT", classes="telemetry")
        yield Static("CHESS.COM / LICHESS // COLOUR + ELO IN // REPERTOIRE OUT", classes="telemetry-dim")
        yield Horizontal(
            Vertical(
                Static("PLATFORM // 1-2", classes="panel-title"),
                KeyboardList(("CHESS.COM", "LICHESS"), id="scout-platform", pad_width=24),
                Static("COLOUR // 1-2", classes="panel-title"),
                KeyboardList(("WHITE", "BLACK"), id="scout-colour", pad_width=24),
                Static("USERNAME", classes="panel-title"),
                Input(placeholder="your public username", id="scout-user"),
                Static("ELO // OPTIONAL", classes="panel-title"),
                Input(placeholder="e.g. 1450", id="scout-elo"),
                Button("SCOUT", id="scout-run", variant="primary"),
                classes="form-col-tight",
            ),
            Vertical(
                Static("GAME LINK / PGN // OPTIONAL", classes="panel-title"),
                Input(placeholder="paste a chess.com or lichess game link", id="scout-link"),
                Static("", id="scout-head", classes="panel-title"),
                VerticalScroll(Static("", id="scout-body"), classes="scroll-log"),
                id="scout-side",
            ),
            id="screen-body",
        )
        yield Static(
            "USERNAME OR LINK // ENTER SCOUTS // ESC BACK // PUBLIC DATA ONLY",
            classes="footer",
        )

    def on_mount(self) -> None:
        self.query_one("#scout-user", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "scout-run" and not self.busy:
            self.busy = True
            self._head("SCOUTING...", theme.DIM)
            self.run_worker(self._scout(), group="scout", exclusive=True)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if self.busy:
            return
        self.busy = True
        self._head("SCOUTING...", theme.DIM)
        self.run_worker(self._scout(), group="scout", exclusive=True)

    def _head(self, message: str, colour: str = theme.BRIGHT) -> None:
        self.query_one("#scout-head", Static).update(Text(message, style=colour))

    def _values(self) -> tuple[str, str, str, str, int | None]:
        platform = "chesscom" if self.query_one("#scout-platform", KeyboardList).index == 0 else "lichess"
        colour = "white" if self.query_one("#scout-colour", KeyboardList).index == 0 else "black"
        username = self.query_one("#scout-user", Input).value.strip()
        link = self.query_one("#scout-link", Input).value.strip()
        raw_elo = self.query_one("#scout-elo", Input).value.strip()
        try:
            elo = int(raw_elo) if raw_elo else None
        except ValueError:
            elo = None
        return platform, colour, username, link, elo

    async def _scout(self) -> None:
        platform, colour, username, link, elo = self._values()
        try:
            if link:
                if scout.looks_like_fen(link):
                    raise scout.ScoutError(
                        "THAT IS A POSITION, NOT A GAME // PASTE IT IN THE BEST MOVE ANALYSER."
                    )
                pgn = await scout.fetch_pgn_from_link(link)
                detected = scout.detect_colour(pgn, username)
                if detected:
                    colour = detected
                game, you, opponent, rating = scout.read_pgn(pgn, colour)
                games = [game]
                if elo is None:
                    elo = rating
                label = f"{you.upper()} VS {opponent.upper()}"
                source = "LINK"
            else:
                if not username:
                    raise scout.ScoutError("ENTER A USERNAME OR PASTE A GAME LINK.")
                if platform == "chesscom":
                    games = await scout.fetch_chesscom(username, colour)
                else:
                    games = await scout.fetch_lichess(username, colour)
                label = username.upper()
                source = platform.upper()
                if elo is None:
                    elo = scout.summarise(games).rating
        except scout.ScoutError as exc:
            if self.is_mounted:
                self.busy = False
                self._head(str(exc), theme.BRIGHT)
            return
        except Exception as exc:
            if self.is_mounted:
                self.busy = False
                self._head(f"NETWORK ERROR // {type(exc).__name__}", theme.BRIGHT)
            return

        report = scout.summarise(games)
        recommendations = scout.recommend(games, colour, elo)
        if not self.is_mounted:
            return
        self.busy = False
        self.last_recommendations = recommendations
        self._render_report(source, label, colour, elo, report, recommendations)

    def _render_report(
        self, source: str, label: str, colour: str, elo, report, recommendations
    ) -> None:
        self._head(f"{source} // {label} // {report.games} GAMES // SCORE {report.score_pct}%")
        text = Text()
        text.append(
            f"RECORD {report.record} // RATING {report.rating or '—'} // "
            f"LEVEL {scout.level_for_elo(elo).upper()}\n\n",
            style=theme.DIM,
        )

        text.append("YOUR OPENINGS\n", style=f"{theme.BRIGHT} bold")
        if report.openings:
            for stat in report.openings:
                text.append(f"  {stat.name[:34]:<34}", style=theme.AMBER)
                text.append(f" {stat.games:>2} GAMES {stat.score_pct:>3}%\n", style=theme.DIM)
        else:
            text.append("  NO OPENING DATA IN THESE GAMES.\n", style=theme.DIM)

        text.append(f"\nRECOMMENDED FOR {colour.upper()}\n", style=f"{theme.BRIGHT} bold")
        for number, recommendation in enumerate(recommendations, start=1):
            entry = recommendation.entry
            text.append(
                f"  {number}. [{entry.eco}] {entry.title.upper()}\n",
                style=f"{theme.BRIGHT} bold",
            )
            text.append(f"     {recommendation.reason}\n", style=theme.AMBER)
            text.append(f"     {entry.summary}\n", style=theme.DIM)
        text.append("\nOPEN AN ENTRY IN [3] LIBRARY // S EXPORTS ITS PGN", style=theme.DIM)
        self.query_one("#scout-body", Static).update(text)

    def action_back(self) -> None:
        self.app.pop_screen()


__all__ = ["EngineRoomScreen", "AnalysisScreen", "ReviewScreen", "ScoutScreen"]
