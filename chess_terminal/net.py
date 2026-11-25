"""WebSocket client for relayed friend games.

The client is deliberately thin: it connects, sends JSON, and hands received
messages to a callback owned by the active Textual screen.
"""

from __future__ import annotations

import asyncio
import json
from collections.abc import Callable
from typing import Any

try:  # websockets >= 13
    from websockets.asyncio.client import connect as ws_connect
    from websockets.exceptions import ConnectionClosed
except ImportError:  # pragma: no cover - very old websockets
    from websockets.client import connect as ws_connect  # type: ignore[no-redef]
    from websockets.exceptions import ConnectionClosed  # type: ignore[no-redef]

DEFAULT_SERVER_URL = "ws://localhost:8765"


def normalise_url(raw: str) -> str:
    """Accept localhost:8765, http(s)://... and ws(s)://... and return a ws URL."""
    url = (raw or "").strip()
    if not url:
        return DEFAULT_SERVER_URL
    if url.startswith("wss://") or url.startswith("ws://"):
        return url.rstrip("/")
    if url.startswith("https://"):
        return "wss://" + url[len("https://") :].rstrip("/")
    if url.startswith("http://"):
        return "ws://" + url[len("http://") :].rstrip("/")
    return "ws://" + url.rstrip("/")


class RelayClient:
    """A reconnecting-free, single-connection relay client."""

    def __init__(self) -> None:
        self._ws: Any = None
        self._reader: asyncio.Task | None = None
        self._closed = False
        self.on_message: Callable[[dict[str, Any]], None] | None = None
        self.on_disconnect: Callable[[str], None] | None = None
        self.url = ""

    @property
    def connected(self) -> bool:
        return self._ws is not None and not self._closed

    async def connect(self, url: str) -> None:
        self.url = normalise_url(url)
        self._ws = await ws_connect(self.url, open_timeout=12, max_size=2**20)
        self._closed = False
        self._reader = asyncio.create_task(self._read_loop())

    async def _read_loop(self) -> None:
        assert self._ws is not None
        try:
            async for raw in self._ws:
                try:
                    message = json.loads(raw)
                except (json.JSONDecodeError, TypeError):
                    continue
                if isinstance(message, dict) and self.on_message is not None:
                    self.on_message(message)
        except asyncio.CancelledError:
            raise
        except ConnectionClosed:
            pass
        except Exception:
            pass
        finally:
            was_closed = self._closed
            self._closed = True
            self._ws = None
            if not was_closed and self.on_disconnect is not None:
                self.on_disconnect("LINK LOST // RELAY CLOSED THE CONNECTION")

    async def send(self, payload: dict[str, Any]) -> bool:
        if self._ws is None:
            return False
        try:
            await self._ws.send(json.dumps(payload))
            return True
        except Exception:
            return False

    async def close(self) -> None:
        self._closed = True
        if self._reader is not None and not self._reader.done():
            self._reader.cancel()
        if self._ws is not None:
            try:
                await self._ws.close()
            except Exception:
                pass
        self._ws = None


__all__ = ["RelayClient", "normalise_url", "DEFAULT_SERVER_URL"]
