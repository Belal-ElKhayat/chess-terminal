"""Clock arithmetic shared by local games and the relay.

Times are integer milliseconds. A live clock is a plain dict so it can be
snapshotted over the relay:

    {"white_ms": 300000, "black_ms": 300000,
     "increment_ms": 0, "running": "white", "at": 1234.5}

``at`` is a monotonic timestamp that belongs to the machine holding the clock.
Snapshots sent over the wire omit it, and the receiver stamps it with its own
monotonic clock.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

NO_CLOCK = "none"


@dataclass(frozen=True)
class ClockSpec:
    label: str
    initial_ms: int
    increment_ms: int = 0


PRESETS: tuple[ClockSpec, ...] = (
    ClockSpec("5|0", 5 * 60_000, 0),
    ClockSpec("10|5", 10 * 60_000, 5_000),
)
PRESET_LABELS = tuple(preset.label for preset in PRESETS)


def spec_for(label: str | None) -> ClockSpec | None:
    """Return the preset for a label such as ``5|0``, or ``None``."""
    if not label:
        return None
    wanted = str(label).strip()
    for preset in PRESETS:
        if preset.label == wanted:
            return preset
    return None


def new_clock(spec: ClockSpec, now: float | None = None) -> dict:
    """A fresh clock with White to move and White's time running."""
    at = time.monotonic() if now is None else now
    return {
        "white_ms": spec.initial_ms,
        "black_ms": spec.initial_ms,
        "increment_ms": spec.increment_ms,
        "running": "white",
        "at": at,
    }


def format_ms(ms: int | float) -> str:
    """``m:ss``, never negative."""
    seconds = max(0, int(ms)) // 1000
    minutes, seconds = divmod(seconds, 60)
    return f"{minutes}:{seconds:02d}"


def remaining(clock: dict, colour: str, now: float | None = None) -> int:
    """Milliseconds left for ``colour`` at ``now``."""
    at = time.monotonic() if now is None else now
    value = int(clock.get(f"{colour}_ms", 0))
    if clock.get("running") == colour:
        value -= int(max(0.0, at - float(clock.get("at", at))) * 1000)
    return max(0, value)


def settle(clock: dict, now: float | None = None) -> dict:
    """Freeze the running side's remaining time and stop the clock."""
    at = time.monotonic() if now is None else now
    running = clock.get("running")
    if running in ("white", "black"):
        clock[f"{running}_ms"] = remaining(clock, running, at)
    clock["running"] = None
    clock["at"] = at
    return clock


def after_move(clock: dict, mover: str, now: float | None = None) -> dict:
    """Charge the mover's elapsed time, add the increment, pass the clock on."""
    at = time.monotonic() if now is None else now
    running = clock.get("running")
    if running == mover:
        clock[f"{mover}_ms"] = remaining(clock, mover, at) + int(clock.get("increment_ms", 0))
    elif running is None:
        # The clock starts with the first move: no elapsed time, no increment.
        clock[f"{mover}_ms"] = remaining(clock, mover, at)
    clock["running"] = "black" if mover == "white" else "white"
    clock["at"] = at
    return clock


def flag(clock: dict, now: float | None = None) -> str | None:
    """Return the colour whose flag has fallen, if any."""
    running = clock.get("running")
    if running in ("white", "black") and remaining(clock, running, now) <= 0:
        return running
    return None


def snapshot(clock: dict | None, now: float | None = None) -> dict | None:
    """Wire format: whole milliseconds and no monotonic timestamp."""
    if not clock:
        return None
    at = time.monotonic() if now is None else now
    return {
        "white_ms": remaining(clock, "white", at),
        "black_ms": remaining(clock, "black", at),
        "increment_ms": int(clock.get("increment_ms", 0)),
        "running": clock.get("running"),
    }


def from_snapshot(payload: dict | None, now: float | None = None) -> dict | None:
    """Rebuild a local ticking clock from a relay snapshot."""
    if not isinstance(payload, dict):
        return None
    at = time.monotonic() if now is None else now
    return {
        "white_ms": max(0, int(payload.get("white_ms", 0))),
        "black_ms": max(0, int(payload.get("black_ms", 0))),
        "increment_ms": max(0, int(payload.get("increment_ms", 0))),
        "running": payload.get("running"),
        "at": at,
    }


__all__ = [
    "ClockSpec",
    "PRESETS",
    "PRESET_LABELS",
    "NO_CLOCK",
    "spec_for",
    "new_clock",
    "format_ms",
    "remaining",
    "settle",
    "after_move",
    "flag",
    "snapshot",
    "from_snapshot",
]
