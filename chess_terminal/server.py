"""Chess.Terminal relay server.

A tiny in-memory WebSocket relay: rooms, seats, and a validated move log. It is
free to run, needs no accounts, and works through any HTTP tunnel.

    chessterminal-server --host 0.0.0.0 --port 8765
"""

from __future__ import annotations

import argparse
import asyncio
import json
import random
import signal
import time
from typing import Any

import chess
from websockets.asyncio.server import serve
from websockets.exceptions import ConnectionClosed

from . import clock

PROTOCOL_VERSION = 1
DEFAULT_PORT = 8765


def _make_room_id(existing: set[str]) -> str:
    for _ in range(200):
        candidate = f"CT-{random.randint(100, 999)}"
        if candidate not in existing:
            return candidate
    raise RuntimeError("Could not allocate a room id")  # pragma: no cover


class Room:
    def __init__(self, room_id: str) -> None:
        self.id = room_id
        self.board = chess.Board()
        self.moves: list[str] = []
        self.seats: dict[str, Any] = {}  # "white"/"black" -> websocket
        self.clock: dict | None = None
        self.clock_label: str | None = None
        self.clock_task: asyncio.Task | None = None
        self.flagged = False

    def set_clock(self, label: object) -> None:
        spec = clock.spec_for(str(label) if label else None)
        if spec is None:
            return
        self.clock = clock.new_clock(spec, time.monotonic())
        # Do not burn the host's time while the room waits for a friend.
        self.clock["running"] = None
        self.clock_label = spec.label

    def seat_of(self, websocket: Any) -> str | None:
        for colour, occupant in self.seats.items():
            if occupant is websocket:
                return colour
        return None

    def is_full(self) -> bool:
        return "white" in self.seats and "black" in self.seats


class RelayHub:
    def __init__(self) -> None:
        self.rooms: dict[str, Room] = {}

    async def _send(self, websocket: Any, payload: dict) -> None:
        try:
            await websocket.send(json.dumps(payload))
        except ConnectionClosed:
            pass
        except Exception:
            pass

    async def _broadcast(self, room: Room, payload: dict, *, exclude: Any = None) -> None:
        for occupant in list(room.seats.values()):
            if occupant is not exclude:
                await self._send(occupant, payload)

    async def _send_state(self, websocket: Any, room: Room) -> None:
        await self._send(
            websocket,
            {
                "type": "state",
                "room": room.id,
                "moves": list(room.moves),
                "turn": "white" if room.board.turn == chess.WHITE else "black",
                "protocol": PROTOCOL_VERSION,
                "clock": clock.snapshot(room.clock, time.monotonic()),
            },
        )

    async def _watch_clock(self, room: Room) -> None:
        """Broadcast a flag as soon as the running side runs out."""
        try:
            while room.clock and not room.flagged:
                if not room.clock.get("running"):
                    await asyncio.sleep(0.2)
                    continue
                loser = clock.flag(room.clock, time.monotonic())
                if loser:
                    now = time.monotonic()
                    room.clock = clock.settle(room.clock, now)
                    room.flagged = True
                    await self._broadcast(
                        room,
                        {
                            "type": "flag",
                            "colour": loser,
                            "clock": clock.snapshot(room.clock, now),
                        },
                    )
                    return
                await asyncio.sleep(0.2)
        except asyncio.CancelledError:
            raise
        except Exception:
            pass

    @staticmethod
    def _stop_clock(room: Room) -> None:
        if room.clock_task is not None and not room.clock_task.done():
            room.clock_task.cancel()
        room.clock_task = None

    async def handler(self, websocket: Any) -> None:
        room: Room | None = None
        try:
            async for raw in websocket:
                try:
                    message = json.loads(raw)
                except (json.JSONDecodeError, TypeError):
                    await self._send(websocket, {"type": "error", "code": "bad_json", "message": "Unreadable message."})
                    continue
                if not isinstance(message, dict):
                    continue
                kind = message.get("type")

                if kind == "create":
                    if room is not None:
                        await self._send(websocket, {"type": "error", "code": "already_in_room", "message": "You are already hosting."})
                        continue
                    room_id = _make_room_id(set(self.rooms))
                    room = Room(room_id)
                    room.seats["white"] = websocket
                    room.set_clock(message.get("clock"))
                    self.rooms[room_id] = room
                    if room.clock is not None:
                        room.clock_task = asyncio.create_task(self._watch_clock(room))
                    await self._send(
                        websocket,
                        {
                            "type": "created",
                            "room": room.id,
                            "colour": "white",
                            "moves": [],
                            "protocol": PROTOCOL_VERSION,
                            "clock": room.clock_label,
                            "clock_state": clock.snapshot(room.clock, time.monotonic()),
                        },
                    )

                elif kind == "join":
                    if room is not None:
                        await self._send(websocket, {"type": "error", "code": "already_in_room", "message": "You are already in a room."})
                        continue
                    room_id = str(message.get("room", "")).strip().upper()
                    target = self.rooms.get(room_id)
                    if target is None:
                        await self._send(websocket, {"type": "error", "code": "room_not_found", "message": f"Room {room_id or '(none)'} is not open on this relay."})
                        continue
                    if target.is_full():
                        await self._send(websocket, {"type": "error", "code": "room_full", "message": f"Room {room_id} already has two players."})
                        continue
                    target.seats["black"] = websocket
                    room = target
                    await self._send(
                        websocket,
                        {
                            "type": "joined",
                            "room": room.id,
                            "colour": "black",
                            "moves": list(room.moves),
                            "protocol": PROTOCOL_VERSION,
                            "clock": room.clock_label,
                            "clock_state": clock.snapshot(room.clock, time.monotonic()),
                        },
                    )
                    await self._send_state(websocket, room)
                    await self._broadcast(room, {"type": "peer_joined", "colour": "black"}, exclude=websocket)

                elif kind == "move":
                    if room is None:
                        continue
                    colour = room.seat_of(websocket)
                    if colour is None:
                        continue
                    expected = "white" if room.board.turn == chess.WHITE else "black"
                    if colour != expected:
                        await self._send(websocket, {"type": "error", "code": "not_your_turn", "message": "It is not your turn."})
                        continue
                    uci = str(message.get("uci", "")).strip().lower()
                    try:
                        move = chess.Move.from_uci(uci)
                    except ValueError:
                        await self._send(websocket, {"type": "error", "code": "bad_move", "message": "Unreadable move."})
                        continue
                    if move not in room.board.legal_moves:
                        await self._send(websocket, {"type": "error", "code": "illegal_move", "message": f"{uci} is not legal."})
                        await self._send_state(websocket, room)
                        continue
                    ply = room.board.ply()
                    room.board.push(move)
                    room.moves.append(uci)
                    if room.clock is not None and not room.flagged:
                        room.clock = clock.after_move(room.clock, colour, time.monotonic())
                    await self._broadcast(
                        room,
                        {
                            "type": "move",
                            "uci": uci,
                            "ply": ply,
                            "colour": colour,
                            "clock": clock.snapshot(room.clock, time.monotonic()),
                        },
                    )

                elif kind == "resign":
                    if room is None:
                        continue
                    colour = room.seat_of(websocket)
                    if colour is None:
                        continue
                    self._stop_clock(room)
                    await self._broadcast(room, {"type": "resign", "colour": colour})

                elif kind == "resync":
                    if room is not None:
                        await self._send_state(websocket, room)

                elif kind == "ping":
                    await self._send(websocket, {"type": "pong"})

        except ConnectionClosed:
            pass
        finally:
            if room is not None:
                colour = room.seat_of(websocket)
                if colour is not None:
                    del room.seats[colour]
                await self._broadcast(
                    room,
                    {"type": "peer_left", "colour": colour},
                    exclude=websocket,
                )
                if not room.seats:
                    self._stop_clock(room)
                    self.rooms.pop(room.id, None)


async def start_relay(host: str = "127.0.0.1", port: int = DEFAULT_PORT) -> Any:
    """Start a relay and return the websockets Server object."""
    hub = RelayHub()
    server = await serve(
        hub.handler,
        host,
        port,
        ping_interval=20,
        ping_timeout=20,
        max_size=2**20,
    )
    setattr(server, "hub", hub)
    return server


def _print_banner(host: str, port: int) -> None:
    print("=" * 62)
    print("  CHESS.TERMINAL // RELAY NODE")
    print("=" * 62)
    print(f"  listening : ws://{host}:{port}")
    print("  rooms     : ephemeral, two players each, no accounts")
    print()
    print("  On this machine, use:  ws://localhost:" + str(port))
    print("  Over the internet, expose this port with a free tunnel:")
    print(f"      cloudflared tunnel --url http://localhost:{port}")
    print(f"      ngrok http {port}")
    print("  Then paste the tunnel's wss:// URL into PLAY VS FRIEND.")
    print("=" * 62)
    print("  Ctrl+C to stop.")
    print(flush=True)


async def _serve_forever(host: str, port: int) -> None:
    server = await start_relay(host, port)
    _print_banner(host, port)
    stop = asyncio.Event()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, stop.set)
        except (NotImplementedError, RuntimeError):
            pass

    try:
        await stop.wait()
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass
    finally:
        server.close()
        await server.wait_closed()
        print("\nrelay stopped.")


def run(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="chessterminal-server",
        description="Relay server for Chess.Terminal friend games.",
    )
    parser.add_argument("--host", default="0.0.0.0", help="Interface to bind (default 0.0.0.0)")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Port to bind (default {DEFAULT_PORT})")
    args = parser.parse_args(argv)
    try:
        asyncio.run(_serve_forever(args.host, args.port))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":  # pragma: no cover
    run()


__all__ = ["RelayHub", "Room", "start_relay", "run", "DEFAULT_PORT"]
