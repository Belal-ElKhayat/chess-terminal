"""Host / join screen for free relayed friend games."""

from __future__ import annotations

import asyncio
from urllib.parse import urlparse

import chess
from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Input, Static

from .. import theme
from ..net import DEFAULT_SERVER_URL, RelayClient, normalise_url
from ..server import DEFAULT_PORT, start_relay
from ..widgets import KeyboardList
from .game import GameScreen

CLOCK_OPTIONS = ("NO CLOCK", "5|0  BLITZ", "10|5  RAPID + 5s")
CLOCK_LABELS = (None, "5|0", "10|5")


class FriendScreen(Screen):
    """Create a room, or join one through any relay URL or tunnel."""

    BINDINGS = [Binding("escape", "back", "Back")]

    def __init__(self) -> None:
        super().__init__()
        self._client: RelayClient | None = None
        self._transferred = False
        self._busy = False
        self._url = DEFAULT_SERVER_URL

    def compose(self) -> ComposeResult:
        yield Static("CHESS.TERMINAL // FRIEND LINK // FREE ROOM ID", classes="telemetry")
        yield Static("NO ACCOUNT // NO SIGN-IN // JUST A ROOM ID AND A RELAY", classes="telemetry-dim")
        yield Horizontal(
            Vertical(
                Static("RELAY / TUNNEL URL", classes="panel-title"),
                Input(value=DEFAULT_SERVER_URL, id="server-url"),
                Static(
                    "Local: ws://localhost:8765  ·  Tunnel: paste the https:// URL "
                    "from cloudflared or ngrok — it is converted automatically.",
                    classes="hint",
                ),
                Static("ROOM ID // TO JOIN AN EXISTING ROOM", classes="panel-title"),
                Input(placeholder="CT-492", id="room-id"),
                Static("", id="friend-status"),
                classes="form-col",
            ),
            Vertical(
                Static("HOST", classes="panel-title"),
                Static(
                    "Creates a short room ID such as CT-492 and waits for one friend. "
                    "If the local relay is not running, Chess.Terminal starts one for you.",
                    classes="hint",
                ),
                Static("CLOCK // HOST SETS IT", classes="panel-title"),
                KeyboardList(CLOCK_OPTIONS, id="clock", pad_width=24),
                Button("HOST A ROOM", id="host", variant="primary"),
                Static("JOIN", classes="panel-title"),
                Static("Paste a relay URL and the room ID your friend gave you.", classes="hint"),
                Button("JOIN ROOM", id="join"),
                Button("BACK TO MENU", id="back"),
                classes="form-col-tight",
            ),
            id="screen-body",
        )
        yield Static(
            "ENTER A ROOM // HOST STARTS A LOCAL RELAY IF NEEDED // ESC BACK",
            classes="footer",
        )

    def on_mount(self) -> None:
        self.query_one("#server-url", Input).focus()

    def _set_status(self, message: str, colour: str = theme.BRIGHT) -> None:
        self.query_one("#friend-status", Static).update(Text(message, style=colour))

    def _set_busy(self, busy: bool) -> None:
        self._busy = busy
        for button_id in ("#host", "#join"):
            self.query_one(button_id, Button).disabled = busy

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if self._busy:
            return
        if event.button.id == "host":
            self.run_worker(self._host(), group="friend", exclusive=True)
        elif event.button.id == "join":
            self.run_worker(self._join(), group="friend", exclusive=True)
        elif event.button.id == "back":
            self.action_back()

    def _server_url(self) -> str:
        return normalise_url(self.query_one("#server-url", Input).value)

    async def _host(self) -> None:
        self._set_busy(True)
        url = self._server_url()
        self._url = url
        self._set_status("DIALING RELAY...", theme.DIM)
        client = RelayClient()
        try:
            await client.connect(url)
        except Exception:
            if not self._is_loopback(url):
                self._set_busy(False)
                self._set_status("RELAY UNREACHABLE. CHECK THE URL OR START THE TUNNEL.", theme.BRIGHT)
                return
            port = self._port(url)
            self._set_status(f"NO RELAY ON {url} // STARTING LOCAL NODE ON PORT {port}...", theme.DIM)
            try:
                server = await start_relay("127.0.0.1", port)
                self.app.local_relay = server
            except Exception:
                self._set_busy(False)
                self._set_status(
                    f"COULD NOT START A LOCAL RELAY ON PORT {port}. RUN: chessterminal-server",
                    theme.BRIGHT,
                )
                return
            try:
                await client.connect(url)
            except Exception:
                self._set_busy(False)
                self._set_status("LOCAL RELAY STARTED BUT THE LINK FAILED.", theme.BRIGHT)
                return

        client.on_message = self._lobby_message
        client.on_disconnect = self._lobby_disconnect
        self._client = client
        self._set_status("LINK UP // REQUESTING A FREE ROOM...", theme.DIM)
        await client.send({"type": "create", "clock": self._clock_label()})

    async def _join(self) -> None:
        room = self.query_one("#room-id", Input).value.strip().upper()
        if not room:
            self._set_status("ENTER A ROOM ID SUCH AS CT-492.")
            self.query_one("#room-id", Input).focus()
            return
        self._set_busy(True)
        url = self._server_url()
        self._url = url
        self._set_status(f"JOINING {room} AT {url}...", theme.DIM)
        client = RelayClient()
        try:
            await client.connect(url)
        except Exception:
            self._set_busy(False)
            self._set_status("RELAY UNREACHABLE. CHECK THE URL AND THE TUNNEL.", theme.BRIGHT)
            return
        client.on_message = self._lobby_message
        client.on_disconnect = self._lobby_disconnect
        self._client = client
        await client.send({"type": "join", "room": room})

    def _clock_label(self) -> str | None:
        try:
            index = self.query_one("#clock", KeyboardList).index
        except Exception:
            return None
        return CLOCK_LABELS[min(index, len(CLOCK_LABELS) - 1)]

    def _lobby_message(self, message: dict) -> None:
        kind = message.get("type")
        client = self._client
        if client is None:
            return
        if kind == "created":
            room = str(message.get("room", "CT-???"))
            self._start_game(
                room,
                chess.WHITE,
                message.get("moves") or [],
                peer_present=False,
                clock_label=message.get("clock"),
            )
        elif kind == "joined":
            self._start_game(
                str(message.get("room", "")),
                chess.BLACK,
                message.get("moves") or [],
                peer_present=True,
                clock_label=message.get("clock"),
            )
        elif kind == "error":
            self._set_busy(False)
            self._set_status(str(message.get("message", "RELAY ERROR")).upper(), theme.BRIGHT)
            asyncio.create_task(client.close())
            self._client = None

    def _start_game(
        self,
        room: str,
        colour: chess.Color,
        moves: list[str],
        *,
        peer_present: bool,
        clock_label: str | None = None,
    ) -> None:
        client = self._client
        if client is None:
            return
        game = GameScreen(
            mode="net",
            client=client,
            room=room,
            colour=colour,
            server_url=self._url,
            initial_moves=tuple(moves),
            peer_present=peer_present,
            clock_label=clock_label,
        )
        client.on_message = game.handle_message
        client.on_disconnect = game.handle_disconnect
        self._transferred = True
        self._set_busy(False)
        self.app.push_screen(game)

    def _lobby_disconnect(self, reason: str) -> None:
        self._set_busy(False)
        self._set_status(reason, theme.BRIGHT)
        self._client = None

    @staticmethod
    def _is_loopback(url: str) -> bool:
        host = urlparse(url).hostname or ""
        return host in ("localhost", "127.0.0.1", "::1")

    @staticmethod
    def _port(url: str) -> int:
        return urlparse(url).port or DEFAULT_PORT

    def action_back(self) -> None:
        client = self._client
        if client is not None and not self._transferred:
            asyncio.create_task(client.close())
            self._client = None
        self.app.pop_screen()

    def on_unmount(self) -> None:
        if self._client is not None and not self._transferred:
            asyncio.create_task(self._client.close())
            self._client = None


__all__ = ["FriendScreen"]
