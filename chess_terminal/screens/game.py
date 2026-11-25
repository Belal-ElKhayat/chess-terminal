"""The game screen: local vs AI, or relayed vs a friend."""

from __future__ import annotations

import asyncio
import time

import chess
from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Static

from .. import ai, clock, persist, theme
from ..ai import get_provider
from ..net import RelayClient
from ..widgets import BoardView, captured_pieces, material_balance
from .clock_picker import ClockPickerScreen
from .coach import CoachScreen
from .result import ResultScreen


class GameScreen(Screen):
    """One game session. Board input is validated by python-chess."""

    BINDINGS = [
        Binding("escape", "leave", "Menu"),
        Binding("u", "undo", "Undo"),
        Binding("r", "resign", "Resign"),
        Binding("a", "retry_ai", "AI move"),
        Binding("s", "export_pgn_binding", "PGN"),
    ]

    def __init__(
        self,
        *,
        mode: str = "ai",
        client: RelayClient | None = None,
        room: str | None = None,
        colour: chess.Color = chess.WHITE,
        server_url: str | None = None,
        initial_moves: tuple[str, ...] = (),
        peer_present: bool = True,
        clock_label: str | None = None,
        resume: bool = False,
    ) -> None:
        super().__init__()
        self.mode = mode
        self.client = client
        self.room = room
        self.server_url = server_url
        self.player_colour = colour
        self.peer_connected = (mode == "ai") or peer_present
        self.board = chess.Board()
        self.history: list[str] = []
        self.last_move: chess.Move | None = None
        self.selected: int | None = None
        self.pending_promotion: tuple[int, int] | None = None
        self.game_over = False
        self.disconnected = False
        self._result_shown = False
        self.result_text = ""
        self.busy_ai = False
        self.ai_transcript = ""
        self.ai_error = ""
        self.pgn_path = ""
        self.clock_spec = clock.spec_for(clock_label)
        self.clock: dict | None = None
        self._clock_timer = None
        self.resume = resume
        self._ready = False
        self._pending_messages: list[dict] = []
        self._pending_disconnect: str | None = None
        self._replay_uci(initial_moves)

    # ---------------------------------------------------------------- layout
    def compose(self) -> ComposeResult:
        yield Static("CHESS.TERMINAL // GAME LINK", classes="telemetry")
        yield Horizontal(
            Vertical(
                Vertical(
                    BoardView(
                        self.board,
                        flipped=self.player_colour == chess.BLACK,
                        cell_width=4,
                        cell_height=2,
                        on_activate=self._activate,
                        id="board",
                    ),
                    id="board-stage",
                ),
                Static("", id="board-hint", classes="hint"),
                id="game-board-col",
            ),
            Vertical(
                Static("", id="game-head", classes="panel-title"),
                Static("", id="players"),
                Static("", id="captured"),
                VerticalScroll(Static("", id="move-log"), classes="scroll-log"),
                Static("", id="ai-panel", classes="hint"),
                id="game-side",
            ),
            id="screen-body",
        )
        yield Static("", id="game-footer", classes="footer")

    def on_mount(self) -> None:
        self._ready = True
        self.query_one("#board", BoardView).focus()
        if self.mode == "net" and self.client is not None:
            self.client.on_message = self.handle_message
            self.client.on_disconnect = self.handle_disconnect
            if not self.client.connected:
                self.disconnected = True
        for message in self._pending_messages:
            self._dispatch(message)
        self._pending_messages.clear()
        if self._pending_disconnect:
            self.disconnected = True
            self._pending_disconnect = None
        if self.clock_spec is not None:
            self.clock = clock.new_clock(self.clock_spec, time.monotonic())
            if self.mode == "net":
                # The relay starts the clock on the first move.
                self.clock["running"] = None
            self._ensure_timer()
        self._refresh()
        if (
            self.resume
            and self.mode == "ai"
            and not self.game_over
            and self.board.turn != self.player_colour
        ):
            self._start_ai()

    # ---------------------------------------------------------------- clocks
    def _ensure_timer(self) -> None:
        if self._clock_timer is None and self.is_mounted:
            self._clock_timer = self.set_interval(0.2, self._clock_tick)

    def _clock_tick(self) -> None:
        if not self.clock or self.game_over:
            return
        running = self.clock.get("running")
        if running not in ("white", "black"):
            return
        if clock.remaining(self.clock, running, time.monotonic()) <= 0:
            self._flag(running)
            return
        self.query_one("#players", Static).update(self._players())

    def _flag(self, loser: str) -> None:
        self.clock = clock.settle(self.clock, time.monotonic())
        self.game_over = True
        winner = "BLACK" if loser == "white" else "WHITE"
        self.result_text = f"{winner} WINS // {loser.upper()} FLAGGED"
        if self.mode == "ai":
            persist.clear_session()
        self._refresh()
        self._show_result()

    def _pick_clock(self) -> None:
        if self.mode != "ai" or self.game_over:
            return
        self.app.push_screen(ClockPickerScreen(), self._clock_chosen)

    def _clock_chosen(self, choice: object) -> None:
        if choice is None:
            return
        if choice == "off":
            self.clock_spec = None
            self.clock = None
        elif isinstance(choice, clock.ClockSpec):
            self.clock_spec = choice
            self.clock = clock.new_clock(choice, time.monotonic())
            self._ensure_timer()
        self._refresh()

    # ------------------------------------------------------------- rendering
    def _turn_name(self) -> str:
        return "WHITE" if self.board.turn == chess.WHITE else "BLACK"

    def _head(self) -> Text:
        text = Text()
        if self.mode == "ai":
            provider = get_provider(self.app.session.provider_key)
            text.append("MODE // AI UPLINK\n", style=f"{theme.BRIGHT} bold")
            text.append(f"{provider.label.upper()} · {self.app.session.model}\n", style=theme.AMBER)
        else:
            text.append(f"ROOM // {self.room}\n", style=f"{theme.BRIGHT} bold")
            text.append(f"LINK // {self.server_url}\n", style=theme.DIM)

        if self.result_text:
            status = self.result_text
            style = f"{theme.BG} on {theme.AMBER} bold"
        elif self.disconnected:
            status = "LINK LOST // GAME HALTED"
            style = theme.BRIGHT
        elif self.mode == "net" and not self.peer_connected:
            status = "AWAITING PEER // SHARE ROOM ID + RELAY URL"
            style = theme.BRIGHT
        elif self.pending_promotion is not None:
            status = "PROMOTION // PRESS Q R B N"
            style = f"{theme.BG} on {theme.BRIGHT} bold"
        elif self.busy_ai:
            status = "ENGINE THINKING // UPLINK BUSY"
            style = theme.BRIGHT
        else:
            status = f"{self._turn_name()} TO MOVE"
            if self.mode == "net" and self.board.turn == self.player_colour:
                status += " // YOUR TURN"
            elif self.mode == "ai" and self.board.turn == self.player_colour:
                status += " // YOUR TURN"
            if self.board.is_check():
                status += " // CHECK"
            style = theme.AMBER
        text.append("\n" + status, style=style)
        return text

    def _players(self) -> Text:
        text = Text()
        session = self.app.session
        if self.mode == "ai":
            opponent = f"{get_provider(session.provider_key).label.upper()} // {session.model}"
        else:
            opponent = "FRIEND"
        active = self.board.turn
        if self.clock and self.clock.get("running") in ("white", "black"):
            active = chess.WHITE if self.clock["running"] == "white" else chess.BLACK
        for colour, name in ((chess.WHITE, "WHITE"), (chess.BLACK, "BLACK")):
            marker = "▶ " if active == colour else "  "
            mine = "YOU" if colour == self.player_colour else opponent
            label = f"{marker}{name}"
            if self.clock:
                side = "white" if colour == chess.WHITE else "black"
                label += f" {clock.format_ms(clock.remaining(self.clock, side, time.monotonic()))}"
            style = theme.BRIGHT if active == colour else theme.AMBER
            text.append(f"{label} // {mine}\n", style=style)
        text.append(
            "FOCUS // BOARD" if self.mode == "ai" or self.peer_connected else "FOCUS // WAITING",
            style=theme.DIM,
        )
        return text

    def _captured(self) -> Text:
        white_took, black_took = captured_pieces(self.board)
        balance = material_balance(self.board)
        text = Text()
        text.append("WHITE TOOK  ", style=theme.DIM)
        text.append((white_took or "—") + "\n", style=theme.BRIGHT)
        text.append("BLACK TOOK  ", style=theme.DIM)
        text.append((black_took or "—") + "\n", style=theme.AMBER)
        if balance > 0:
            text.append(f"MATERIAL // +{balance} WHITE", style=theme.BRIGHT)
        elif balance < 0:
            text.append(f"MATERIAL // +{-balance} BLACK", style=theme.BRIGHT)
        else:
            text.append("MATERIAL // LEVEL", style=theme.DIM)
        return text

    def _log(self) -> Text:
        text = Text()
        if not self.history:
            text.append("NO MOVES YET.\n", style=theme.DIM)
            text.append("ARROWS MOVE CURSOR // ENTER PICKS UP AND DROPS.", style=theme.DIM)
            return text
        for index in range(0, len(self.history), 2):
            number = index // 2 + 1
            text.append(f"{number:>3}.  ", style=theme.DIM)
            for offset in range(2):
                if index + offset >= len(self.history):
                    break
                san = self.history[index + offset]
                current = index + offset == len(self.history) - 1
                text.append(san, style=f"{theme.BG} on {theme.AMBER}" if current else theme.AMBER)
                text.append("   ")
            text.append("\n")
        return text

    def _ai_panel(self) -> Text:
        text = Text()
        if self.mode == "ai":
            if self.ai_error:
                text.append(self.ai_error + "\n", style=theme.BRIGHT)
            if self.ai_transcript:
                for line in self.ai_transcript.strip().splitlines():
                    text.append(line + "\n", style=theme.DIM)
            if self.pgn_path:
                text.append(f"PGN // {self.pgn_path}\n", style=theme.DIM)
            text.append("A // ASK ENGINE AGAIN // S // PGN EXPORT", style=theme.DIM)
        else:
            text.append("RELAY V1 // MOVES VALIDATED TWICE", style=theme.DIM)
        return text

    def _hint(self) -> str:
        if self.mode == "net":
            return "ARROWS CURSOR // ENTER MOVE // U UNDO (LOCAL) // R RESIGN // ESC MENU"
        return "ARROWS CURSOR // ENTER PICK-MOVE // U UNDO // R RESIGN // A RETRY AI // ESC MENU"

    def _refresh(self) -> None:
        if not self._ready:
            return
        view = self.query_one("#board", BoardView)
        view.set_board(self.board, last_move=self.last_move)
        view.set_highlights(selected=self.selected)
        self.query_one("#game-head", Static).update(self._head())
        self.query_one("#players", Static).update(self._players())
        self.query_one("#captured", Static).update(self._captured())
        self.query_one("#move-log", Static).update(self._log())
        self.query_one("#ai-panel", Static).update(self._ai_panel())
        self.query_one("#board-hint", Static).update(
            "SELECT A PIECE, THEN ITS DESTINATION." if self.selected is not None else ""
        )
        self.query_one("#game-footer", Static).update(self._hint())

    # ----------------------------------------------------------------- input
    def _activate(self, square: int) -> None:
        if self.game_over or self.busy_ai or self.disconnected or self.pending_promotion:
            return
        if self.mode == "net" and (not self.peer_connected or self.board.turn != self.player_colour):
            return
        if self.mode == "ai" and self.board.turn != self.player_colour:
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
            self._refresh()
            return
        self._complete_move(moves[0], broadcast=True)

    def on_key(self, event) -> None:
        if event.key == "q" and self.pending_promotion is None:
            self._pick_clock()
            event.stop()
            return
        if self.pending_promotion is not None:
            promotion = {"q": chess.QUEEN, "r": chess.ROOK, "b": chess.BISHOP, "n": chess.KNIGHT}.get(
                event.key.lower()
            )
            if promotion is not None:
                start, end = self.pending_promotion
                self.pending_promotion = None
                move = chess.Move(start, end, promotion=promotion)
                if move in self.board.legal_moves:
                    self._complete_move(move, broadcast=True)
                else:
                    self._refresh()
                event.stop()

    def _complete_move(self, move: chess.Move, *, broadcast: bool) -> None:
        mover = "white" if self.board.turn == chess.WHITE else "black"
        san = self.board.san(move)
        self.board.push(move)
        self.history.append(san)
        self.last_move = move
        self.selected = None
        self.pending_promotion = None
        self.ai_error = ""

        if broadcast and self.mode == "net" and self.client is not None:
            asyncio.create_task(
                self.client.send({"type": "move", "uci": move.uci(), "ply": self.board.ply() - 1})
            )

        if self.clock is not None and self.mode == "ai":
            self.clock = clock.after_move(self.clock, mover, time.monotonic())

        if self._check_outcome():
            if self.clock is not None:
                self.clock = clock.settle(self.clock, time.monotonic())
            if self.mode == "ai":
                persist.clear_session()
            self._refresh()
            self._show_result()
            return
        if self.mode == "ai":
            self._auto_save()
        self._refresh()
        if self.mode == "ai" and self.board.turn != self.player_colour:
            self._start_ai()

    def _check_outcome(self) -> bool:
        outcome = self.board.outcome(claim_draw=True)
        if outcome is None:
            return False
        self.game_over = True
        if outcome.winner is None:
            self.result_text = f"DRAW // {outcome.termination.name.replace('_', ' ')}"
        else:
            winner = "WHITE" if outcome.winner == chess.WHITE else "BLACK"
            self.result_text = f"{winner} WINS // {outcome.termination.name.replace('_', ' ')}"
        return True

    # --------------------------------------------------------------- result
    def _result_lines(self) -> tuple[str, ...]:
        lines = [f"{len(self.history) // 2} MOVES // {len(self.history)} PLIES"]
        balance = material_balance(self.board)
        if balance:
            lines.append(f"MATERIAL +{abs(balance)} {'WHITE' if balance > 0 else 'BLACK'}")
        if self.mode == "ai":
            lines.append(f"OPPONENT // {get_provider(self.app.session.provider_key).label.upper()}")
        elif self.room:
            lines.append(f"ROOM // {self.room}")
        return tuple(lines)

    def _show_result(self) -> None:
        """Raise the victory card once per finished game."""
        if self._result_shown or not self.result_text or not self.is_mounted:
            return
        self._result_shown = True
        self.app.push_screen(
            ResultScreen(
                self.result_text,
                self._result_lines(),
                can_rematch=self.mode == "ai",
                can_coach=bool(self.history),
                on_save=self._export_pgn,
            ),
            self._result_dismissed,
        )

    def _result_dismissed(self, action: str | None) -> None:
        if action == "again":
            self._reset_game()
        elif action == "coach":
            self.app.push_screen(CoachScreen(self._pgn_text(), self.result_text))

    # ------------------------------------------------------------ save/export
    def _names(self) -> tuple[str, str]:
        if self.mode == "ai":
            provider = get_provider(self.app.session.provider_key)
            opponent = f"{provider.label.upper()} {self.app.session.model}"
        else:
            opponent = "FRIEND"
        if self.player_colour == chess.WHITE:
            return "YOU", opponent
        return opponent, "YOU"

    def _pgn_text(self) -> str:
        white, black = self._names()
        event = "Chess.Terminal // AI" if self.mode == "ai" else f"Chess.Terminal // {self.room}"
        return persist.build_pgn(self.board, event=event, white=white, black=black)

    def _export_pgn(self) -> str:
        white, black = self._names()
        event = "Chess.Terminal // AI" if self.mode == "ai" else f"Chess.Terminal // {self.room}"
        path = persist.export_pgn(self.board, event=event, white=white, black=black)
        self.pgn_path = str(path)
        self._refresh()
        return self.pgn_path

    def _auto_save(self) -> None:
        if self.mode != "ai" or self.game_over:
            return
        persist.save_session(
            {
                "version": 1,
                "mode": "ai",
                "colour": "white" if self.player_colour == chess.WHITE else "black",
                "moves": [move.uci() for move in self.board.move_stack],
                "provider": self.app.session.provider_key,
                "saved": time.time(),
            }
        )

    def _reset_game(self) -> None:
        self.board = chess.Board()
        self.history = []
        self.last_move = None
        self.selected = None
        self.pending_promotion = None
        self.game_over = False
        self.result_text = ""
        self.ai_error = ""
        self.ai_transcript = ""
        self.pgn_path = ""
        self.busy_ai = False
        self._result_shown = False
        self.clock = clock.new_clock(self.clock_spec, time.monotonic()) if self.clock_spec else None
        persist.clear_session()
        self.query_one("#board", BoardView).cursor = chess.E4
        self._refresh()
        self.query_one("#board", BoardView).focus()

    # -------------------------------------------------------------------- AI
    def _start_ai(self) -> None:
        if self.game_over or self.busy_ai or self.mode != "ai":
            return
        self.busy_ai = True
        self.ai_error = ""
        self.ai_transcript = ""
        self._refresh()
        self.run_worker(self._ai_turn(), group="ai", exclusive=True)

    async def _ai_turn(self) -> None:
        session = self.app.session
        provider = get_provider(session.provider_key)
        snapshot = self.board.copy(stack=False)
        history = list(self.history)
        result = await ai.request_move(
            provider.key,
            session.model,
            session.api_key,
            snapshot,
            history,
        )
        if not self.is_mounted:
            return
        self.busy_ai = False
        self.ai_transcript = result.transcript
        if result.move is not None and not self.game_over:
            if result.move in self.board.legal_moves:
                self._complete_move(result.move, broadcast=False)
                return
            self.ai_error = "ENGINE RETURNED A MOVE THAT IS NO LONGER LEGAL."
        else:
            self.ai_error = result.error or "ENGINE DID NOT RETURN A USABLE MOVE."
        self._refresh()

    # ------------------------------------------------------------------ undo
    def action_undo(self) -> None:
        if self.mode == "net" or self.busy_ai or not self.history:
            return
        self.board.pop()
        self.history.pop()
        if self.mode == "ai" and self.board.turn != self.player_colour and self.history:
            self.board.pop()
            self.history.pop()
        self.last_move = self.board.peek() if self.board.move_stack else None
        self.selected = None
        self.pending_promotion = None
        self.game_over = False
        self.result_text = ""
        self.ai_error = ""
        self._result_shown = False
        self._refresh()

    def action_export_pgn_binding(self) -> None:
        self._export_pgn()

    def action_retry_ai(self) -> None:
        if self.mode != "ai" or self.busy_ai or self.game_over:
            return
        if self.board.turn != self.player_colour:
            self._start_ai()

    def action_resign(self) -> None:
        if self.game_over:
            return
        if self.mode == "net" and self.client is not None:
            asyncio.create_task(self.client.send({"type": "resign"}))
        self.game_over = True
        if self.clock is not None:
            self.clock = clock.settle(self.clock, time.monotonic())
        if self.mode == "ai":
            persist.clear_session()
        self.result_text = "GAME OVER // YOU RESIGNED"
        self._refresh()
        self._show_result()

    def action_leave(self) -> None:
        if self.pending_promotion is not None:
            self.pending_promotion = None
            self._refresh()
            return
        if self.client is not None:
            asyncio.create_task(self.client.close())
        if self.mode == "ai" and self.game_over:
            persist.clear_session()
        self.app.go_menu()

    # -------------------------------------------------------------- net sync
    def handle_message(self, message: dict) -> None:
        if not self._ready:
            self._pending_messages.append(message)
            return
        self._dispatch(message)

    def handle_disconnect(self, reason: str) -> None:
        if not self._ready:
            self._pending_disconnect = reason
            return
        self.disconnected = True
        self.peer_connected = False
        self.ai_error = reason
        self._refresh()

    def _dispatch(self, message: dict) -> None:
        kind = message.get("type")
        if kind == "move":
            ply = message.get("ply")
            uci = str(message.get("uci", ""))
            if ply == self.board.ply():
                try:
                    move = chess.Move.from_uci(uci)
                except ValueError:
                    move = None
                if move is not None and move in self.board.legal_moves:
                    if isinstance(message.get("clock"), dict):
                        self._apply_clock(message.get("clock"))
                    self._complete_move(move, broadcast=False)
                else:
                    self._request_resync()
            elif isinstance(ply, int) and ply > self.board.ply():
                self._request_resync()
        elif kind == "state":
            moves = message.get("moves")
            if isinstance(moves, list):
                self._sync_uci([str(item) for item in moves])
            self._apply_clock(message.get("clock"))
        elif kind == "clock":
            self._apply_clock(message.get("clock"))
        elif kind == "flag":
            loser = str(message.get("colour", ""))
            self._apply_clock(message.get("clock"))
            if loser in ("white", "black") and not self.game_over:
                winner = "BLACK" if loser == "white" else "WHITE"
                self.game_over = True
                self.result_text = f"{winner} WINS // {loser.upper()} FLAGGED"
                self._refresh()
                self._show_result()
        elif kind == "peer_joined":
            self.peer_connected = True
            self._refresh()
        elif kind == "peer_left":
            self.peer_connected = False
            self.ai_error = "OPPONENT LEFT THE ROOM."
            self._refresh()
        elif kind == "resign":
            colour = message.get("colour")
            winner = "BLACK" if colour == "white" else "WHITE"
            self.game_over = True
            self.result_text = f"{winner} WINS // OPPONENT RESIGNED"
            self._refresh()
            self._show_result()
        elif kind == "error":
            self.ai_error = str(message.get("message", "RELAY ERROR")).upper()
            if message.get("code") in ("illegal_move", "not_your_turn"):
                self._request_resync()
            self._refresh()

    def _apply_clock(self, payload: object) -> None:
        if not isinstance(payload, dict):
            return
        self.clock = clock.from_snapshot(payload)
        self._ensure_timer()
        if self._ready:
            self.query_one("#players", Static).update(self._players())

    def _request_resync(self) -> None:
        if self.client is not None:
            asyncio.create_task(self.client.send({"type": "resync"}))

    def _replay_uci(self, moves: tuple[str, ...] | list[str]) -> None:
        for uci in moves:
            try:
                move = chess.Move.from_uci(str(uci))
            except ValueError:
                continue
            if move not in self.board.legal_moves:
                break
            self.history.append(self.board.san(move))
            self.board.push(move)
            self.last_move = move

    def _sync_uci(self, moves: list[str]) -> None:
        if len(moves) == self.board.ply():
            return
        self.board = chess.Board()
        self.history = []
        self.last_move = None
        self.selected = None
        self.pending_promotion = None
        self.game_over = False
        self.result_text = ""
        self._result_shown = False
        self._replay_uci(moves)
        self._check_outcome()
        self._refresh()
        self._show_result()


__all__ = ["GameScreen"]
