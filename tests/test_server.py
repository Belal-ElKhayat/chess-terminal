import asyncio
import socket

from chess_terminal.net import RelayClient
from chess_terminal.server import start_relay


def _free_port() -> int:
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


class Collector:
    """Queue-backed collector for relay messages."""

    def __init__(self) -> None:
        self.queue: asyncio.Queue = asyncio.Queue()

    def __call__(self, message: dict) -> None:
        self.queue.put_nowait(message)

    async def next(self, kind: str, timeout: float = 3.0) -> dict:
        while True:
            message = await asyncio.wait_for(self.queue.get(), timeout)
            if message.get("type") == kind:
                return message


async def _scenario() -> None:
    port = _free_port()
    server = await start_relay("127.0.0.1", port)
    url = f"ws://127.0.0.1:{port}"
    host, guest, third = RelayClient(), RelayClient(), RelayClient()
    host_box, guest_box, third_box = Collector(), Collector(), Collector()
    host.on_message = host_box
    guest.on_message = guest_box
    third.on_message = third_box
    try:
        await host.connect(url)
        await host.send({"type": "create"})
        created = await host_box.next("created")
        assert created["colour"] == "white"
        room = created["room"]
        assert room.startswith("CT-")

        await guest.connect(url)
        await guest.send({"type": "join", "room": room})
        joined = await guest_box.next("joined")
        state = await guest_box.next("state")
        assert joined["colour"] == "black"
        assert joined["room"] == room
        assert state["moves"] == []
        assert (await host_box.next("peer_joined"))["colour"] == "black"

        await host.send({"type": "move", "uci": "e2e4", "ply": 0})
        assert (await host_box.next("move"))["uci"] == "e2e4"
        assert (await guest_box.next("move"))["uci"] == "e2e4"

        # It is Black's turn; a White rook move is rejected and resynced.
        await guest.send({"type": "move", "uci": "e1e8", "ply": 1})
        error = await guest_box.next("error")
        assert error["code"] in ("illegal_move", "not_your_turn")
        assert (await guest_box.next("state"))["moves"] == ["e2e4"]

        await guest.send({"type": "move", "uci": "e7e5", "ply": 1})
        assert (await guest_box.next("move"))["uci"] == "e7e5"
        assert (await host_box.next("move"))["uci"] == "e7e5"

        # A third player cannot take a seat.
        await third.connect(url)
        await third.send({"type": "join", "room": room})
        assert (await third_box.next("error"))["code"] == "room_full"

        await guest.send({"type": "resign"})
        assert (await host_box.next("resign"))["colour"] == "black"
    finally:
        for client in (host, guest, third):
            await client.close()
        server.close()
        await server.wait_closed()


def test_relay_room_lifecycle_and_moves():
    asyncio.run(_scenario())


async def _clock_scenario() -> None:
    port = _free_port()
    server = await start_relay("127.0.0.1", port)
    url = f"ws://127.0.0.1:{port}"
    host, guest = RelayClient(), RelayClient()
    host_box, guest_box = Collector(), Collector()
    host.on_message = host_box
    guest.on_message = guest_box
    try:
        await host.connect(url)
        await host.send({"type": "create", "clock": "10|5"})
        created = await host_box.next("created")
        assert created["clock"] == "10|5"
        assert created["clock_state"]["white_ms"] == 600_000
        assert created["clock_state"]["running"] is None  # starts on the first move
        room = created["room"]

        await guest.connect(url)
        await guest.send({"type": "join", "room": room})
        joined = await guest_box.next("joined")
        assert joined["clock"] == "10|5"
        state = await guest_box.next("state")
        assert state["clock"]["running"] is None

        await host.send({"type": "move", "uci": "e2e4", "ply": 0})
        move = await guest_box.next("move")
        assert move["uci"] == "e2e4"
        assert move["clock"]["running"] == "black"
        assert move["clock"]["white_ms"] == 600_000  # first move: no increment yet
        assert move["clock"]["black_ms"] == 600_000
    finally:
        for client in (host, guest):
            await client.close()
        server.close()
        await server.wait_closed()


def test_relay_clock_is_authoritative():
    asyncio.run(_clock_scenario())


def test_join_unknown_room_is_rejected():
    async def scenario() -> None:
        port = _free_port()
        server = await start_relay("127.0.0.1", port)
        client = RelayClient()
        box = Collector()
        client.on_message = box
        try:
            await client.connect(f"ws://127.0.0.1:{port}")
            await client.send({"type": "join", "room": "CT-000"})
            error = await box.next("error")
            assert error["code"] == "room_not_found"
        finally:
            await client.close()
            server.close()
            await server.wait_closed()

    asyncio.run(scenario())
