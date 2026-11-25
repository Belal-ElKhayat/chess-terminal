"""chess.com and lichess scouting: public games in, opening advice out.

Only public, keyless endpoints are used. The chess.com single-game callback
(``/callback/{live|daily}/game/{id}``) is undocumented, so a failed link
resolution asks the player to fall back to the username scan, which uses the
official monthly archive.
"""

from __future__ import annotations

import io
import json
import re
from dataclasses import dataclass
from urllib.parse import quote, unquote

import chess
import chess.pgn
import httpx

from .data import ENTRIES, LibraryEntry

CHESSCOM_API = "https://api.chess.com/pub"
CHESSCOM_WEB = "https://www.chess.com"
LICHESS = "https://lichess.org"
HEADERS = {
    "User-Agent": "Chess.Terminal/1.0 (terminal chess study tool)",
    "Accept": "application/json, text/plain;q=0.9",
}

DRAW_RESULTS = {
    "agreed",
    "repetition",
    "stalemate",
    "insufficient",
    "50move",
    "timevsinsufficient",
}
LEVEL_ORDER = {"beginner": 0, "club": 1, "advanced": 2}

CHESSCOM_LINK_RE = re.compile(
    r"chess\.com/(?:analysis/game|game|live/game)/(live|daily)?/?(\d{5,})", re.IGNORECASE
)
LICHESS_LINK_RE = re.compile(r"lichess\.org/(?:game/)?([A-Za-z0-9]{8}(?:[A-Za-z0-9]{4})?)")


class ScoutError(Exception):
    """A scouting problem that should be shown to the player as one line."""


@dataclass(frozen=True)
class PlayedGame:
    """One game from the tracked player's point of view."""

    colour: str
    result: str  # "win", "loss" or "draw"
    opening: str
    eco: str = ""
    rating: int = 0


@dataclass(frozen=True)
class OpeningStat:
    name: str
    eco: str
    games: int
    score_pct: int


@dataclass(frozen=True)
class Recommendation:
    entry: LibraryEntry
    reason: str


@dataclass(frozen=True)
class ScoutReport:
    games: int
    wins: int
    losses: int
    draws: int
    score_pct: int
    rating: int
    openings: tuple[OpeningStat, ...]

    @property
    def record(self) -> str:
        return f"+{self.wins} ={self.draws} -{self.losses}"


# --------------------------------------------------------------------- http
async def _fetch_text(url: str, **kwargs) -> str:
    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(20.0, connect=10.0),
            headers=HEADERS,
            follow_redirects=True,
        ) as client:
            response = await client.get(url, **kwargs)
    except httpx.HTTPError as exc:
        raise ScoutError(f"NETWORK ERROR // {type(exc).__name__}") from exc

    if response.status_code == 404:
        raise ScoutError("NOT FOUND // CHECK THE USERNAME OR LINK.")
    if response.status_code == 429:
        raise ScoutError("RATE LIMITED // WAIT A MINUTE AND TRY AGAIN.")
    if response.status_code >= 400:
        raise ScoutError(f"REQUEST FAILED // HTTP {response.status_code}")
    return response.text


async def _fetch_json(url: str, **kwargs) -> dict:
    text = await _fetch_text(url, **kwargs)
    try:
        payload = json.loads(text)
    except ValueError as exc:
        raise ScoutError("BAD RESPONSE // COULD NOT READ THE JSON.") from exc
    if not isinstance(payload, dict):
        raise ScoutError("BAD RESPONSE // UNEXPECTED SHAPE.")
    return payload


# ------------------------------------------------------------------ parsing
def _family(name: str) -> str:
    """The opening family used to match games against the library."""
    value = (name or "").strip()
    value = value.split(":", 1)[0]
    value = re.sub(r"\bvariation\b.*$", "", value, flags=re.IGNORECASE)
    return " ".join(value.split()).lower()


def _chesscom_result(result: str) -> str:
    value = (result or "").strip().lower()
    if value == "win":
        return "win"
    if value in DRAW_RESULTS:
        return "draw"
    return "loss"


def _eco_from_pgn(pgn: str) -> str:
    match = re.search(r'\[ECO "([^"]+)"\]', pgn or "")
    return match.group(1) if match else ""


def _opening_from_pgn(pgn: str) -> str:
    match = re.search(r'\[ECOUrl "([^"]+)"\]', pgn or "")
    if not match:
        return ""
    slug = unquote(match.group(1)).rstrip("/").split("/")[-1]
    return slug.replace("-", " ").strip()


def looks_like_fen(text: str) -> bool:
    """True when ``text`` is a bare FEN position."""
    value = (text or "").strip()
    if not value or " " not in value or "/" not in value:
        return False
    if "\n" in value or len(value) > 120:
        return False
    try:
        chess.Board(value)
    except ValueError:
        return False
    return True


def parse_game_link(text: str) -> tuple[str, object] | None:
    """Classify pasted text as ``("pgn"|"fen"|"lichess"|"chesscom", payload)``."""
    value = (text or "").strip()
    if not value:
        return None
    if "[Event" in value or "[FEN" in value or "\n1." in value or value.startswith("1."):
        return ("pgn", value)
    if looks_like_fen(value):
        return ("fen", value)

    match = LICHESS_LINK_RE.search(value)
    if match:
        return ("lichess", match.group(1))

    match = CHESSCOM_LINK_RE.search(value)
    if match:
        return ("chesscom", ((match.group(1) or "live").lower(), match.group(2)))
    return None


def _fen_pgn(fen: str) -> str:
    """Wrap a bare FEN as a one-position PGN so the analyser can load it."""
    board = chess.Board(fen)
    return (
        '[Event "Analysis"]\n[Site "Chess.Terminal"]\n'
        f'[SetUp "1"]\n[FEN "{board.fen()}"]\n[Result "*"]\n\n*\n'
    )


def detect_colour(pgn: str, username: str) -> str:
    """Which side ``username`` played in ``pgn``: ``white``, ``black`` or ``""``."""
    name = (username or "").strip().lstrip("@").lower()
    if not name:
        return ""
    try:
        game = chess.pgn.read_game(io.StringIO(pgn or ""))
    except Exception:
        return ""
    if game is None:
        return ""
    for colour in ("white", "black"):
        player = str(game.headers.get(colour.capitalize(), "")).strip().lower()
        if player and player == name:
            return colour
    return ""


def level_for_elo(elo: int | None) -> str:
    if not elo:
        return "club"
    if elo < 1200:
        return "beginner"
    if elo < 1800:
        return "club"
    return "advanced"


# ------------------------------------------------------------------ fetches
async def fetch_chesscom(username: str, colour: str, *, months: int = 2) -> list[PlayedGame]:
    """Recent public chess.com games for ``colour`` (``white``/``black``)."""
    name = username.strip().lstrip("@")
    if not name:
        raise ScoutError("ENTER A CHESS.COM USERNAME.")
    index = await _fetch_json(f"{CHESSCOM_API}/player/{quote(name)}/games/archives")
    archives = [str(url) for url in index.get("archives") or []]
    if not archives:
        raise ScoutError(f"NO PUBLIC GAMES FOUND FOR {name.upper()}.")

    games: list[PlayedGame] = []
    for archive_url in archives[-max(1, months) :]:
        payload = await _fetch_json(archive_url)
        for raw in payload.get("games") or []:
            if not isinstance(raw, dict):
                continue
            if raw.get("rules") not in (None, "chess"):
                continue
            side = raw.get(colour) or {}
            if str(side.get("username", "")).lower() != name.lower():
                continue
            pgn = str(raw.get("pgn") or "")
            games.append(
                PlayedGame(
                    colour=colour,
                    result=_chesscom_result(str(side.get("result", ""))),
                    opening=_opening_from_pgn(pgn),
                    eco=_eco_from_pgn(pgn),
                    rating=int(side.get("rating") or 0),
                )
            )

    if not games:
        raise ScoutError(
            f"NO PUBLIC {colour.upper()} CHESS GAMES FOR {name.upper()} IN THE LAST {months} MONTHS."
        )
    return games


async def fetch_lichess(username: str, colour: str, *, limit: int = 50) -> list[PlayedGame]:
    """Recent rated lichess games for ``colour`` (``white``/``black``)."""
    name = username.strip().lstrip("@")
    if not name:
        raise ScoutError("ENTER A LICHESS USERNAME.")
    url = (
        f"{LICHESS}/api/games/user/{quote(name)}"
        f"?max={max(1, limit)}&color={colour}&opening=true&rated=true"
    )
    text = await _fetch_text(url, headers={**HEADERS, "Accept": "application/x-ndjson"})

    games: list[PlayedGame] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            raw = json.loads(line)
        except ValueError:
            continue
        if str(raw.get("status", "")) == "aborted":
            continue
        opening = raw.get("opening") or {}
        winner = raw.get("winner")
        if winner in ("white", "black"):
            result = "win" if winner == colour else "loss"
        else:
            result = "draw"
        players = raw.get("players") or {}
        rating = int(((players.get(colour) or {}).get("rating")) or 0)
        games.append(
            PlayedGame(
                colour=colour,
                result=result,
                opening=str(opening.get("name") or ""),
                eco=str(opening.get("eco") or ""),
                rating=rating,
            )
        )

    if not games:
        raise ScoutError(f"NO RATED {colour.upper()} GAMES FOUND FOR {name.upper()}.")
    return games


async def fetch_pgn_from_link(link: str) -> str:
    """Resolve a lichess link, chess.com link or raw PGN into PGN text."""
    parsed = parse_game_link(link)
    if parsed is None:
        raise ScoutError("THAT IS NOT A CHESS.COM / LICHESS LINK OR A PGN.")
    kind, payload = parsed
    if kind == "pgn":
        return str(payload)
    if kind == "fen":
        return _fen_pgn(str(payload))
    if kind == "lichess":
        return await _fetch_text(f"{LICHESS}/game/export/{payload}")

    game_type, game_id = payload  # type: ignore[misc]
    try:
        callback = await _fetch_json(f"{CHESSCOM_WEB}/callback/{game_type}/game/{game_id}")
    except ScoutError as exc:
        raise ScoutError(
            "CHESS.COM WOULD NOT RESOLVE THAT LINK // USE THE USERNAME SCOUT INSTEAD."
        ) from exc

    game = callback.get("game") if isinstance(callback, dict) else None
    headers = (game or {}).get("pgnHeaders") or {}
    white = str(headers.get("White") or "").strip()
    date = str(headers.get("Date") or "").split(".")
    if not white or len(date) < 2:
        raise ScoutError("CHESS.COM DID NOT RETURN THAT GAME'S HEADERS // USE THE USERNAME SCOUT.")

    archive = await _fetch_json(
        f"{CHESSCOM_API}/player/{quote(white.lower())}/games/{date[0]}/{date[1]}"
    )
    for raw in archive.get("games") or []:
        if not isinstance(raw, dict):
            continue
        if str(raw.get("url", "")).rstrip("/").endswith(f"/{game_id}"):
            pgn = str(raw.get("pgn") or "")
            if pgn:
                return pgn
    raise ScoutError("CHESS.COM DID NOT RETURN THE PGN // USE THE USERNAME SCOUT.")


def read_pgn(pgn: str, colour: str) -> tuple[PlayedGame, str, str, int]:
    """Turn one PGN into ``(game, username, opponent, rating)``."""
    try:
        game = chess.pgn.read_game(io.StringIO(pgn))
    except Exception as exc:
        raise ScoutError(f"COULD NOT READ THAT PGN // {type(exc).__name__}") from exc
    if game is None:
        raise ScoutError("COULD NOT READ THAT PGN.")

    headers = game.headers
    you = headers.get("White" if colour == "white" else "Black", "") or "UNKNOWN"
    opponent = headers.get("Black" if colour == "white" else "White", "") or "UNKNOWN"
    try:
        rating = int(headers.get("WhiteElo" if colour == "white" else "BlackElo", "0") or 0)
    except ValueError:
        rating = 0
    result_header = headers.get("Result", "*")
    if result_header == "1-0":
        winner = "white"
    elif result_header == "0-1":
        winner = "black"
    else:
        winner = None
    result = "draw" if winner is None else ("win" if winner == colour else "loss")
    return (
        PlayedGame(
            colour=colour,
            result=result,
            opening=headers.get("Opening", "") or _opening_from_pgn(pgn),
            eco=headers.get("ECO", "") or _eco_from_pgn(pgn),
            rating=rating,
        ),
        you,
        opponent,
        rating,
    )


# ----------------------------------------------------------------- analysis
def summarise(games: list[PlayedGame] | tuple[PlayedGame, ...]) -> ScoutReport:
    """Win/loss/draw totals plus opening-by-opening scoring."""
    if not games:
        return ScoutReport(0, 0, 0, 0, 0, 0, ())

    wins = sum(1 for game in games if game.result == "win")
    losses = sum(1 for game in games if game.result == "loss")
    draws = len(games) - wins - losses

    grouped: dict[str, list[PlayedGame]] = {}
    display: dict[str, str] = {}
    eco_by_family: dict[str, str] = {}
    for game in games:
        family = _family(game.opening) or "unknown"
        grouped.setdefault(family, []).append(game)
        display.setdefault(family, game.opening.strip() or "Unknown opening")
        eco_by_family.setdefault(family, game.eco)

    openings: list[OpeningStat] = []
    for family, bucket in grouped.items():
        points = sum(1.0 if game.result == "win" else 0.5 if game.result == "draw" else 0.0 for game in bucket)
        openings.append(
            OpeningStat(
                name=display[family],
                eco=eco_by_family[family],
                games=len(bucket),
                score_pct=round(100 * points / len(bucket)),
            )
        )
    openings.sort(key=lambda stat: (-stat.games, stat.name))

    ratings = [game.rating for game in games if game.rating]
    score = 100 * (wins + draws / 2) / len(games)
    return ScoutReport(
        games=len(games),
        wins=wins,
        losses=losses,
        draws=draws,
        score_pct=round(score),
        rating=max(ratings) if ratings else 0,
        openings=tuple(openings[:6]),
    )


def recommend(
    games: list[PlayedGame] | tuple[PlayedGame, ...],
    colour: str,
    elo: int | None = None,
    *,
    limit: int = 3,
) -> tuple[Recommendation, ...]:
    """Pick library openings for this colour, level and recent results."""
    band = level_for_elo(elo)
    stats = {_family(stat.name): stat for stat in summarise(games).openings}

    entries = [
        entry
        for entry in ENTRIES
        if entry.kind == "opening" and entry.side == colour
    ]

    def rank(entry: LibraryEntry) -> tuple:
        gap = abs(LEVEL_ORDER.get(entry.level, 1) - LEVEL_ORDER.get(band, 1))
        played = 0 if _family(entry.title) in stats else 1
        return (gap, played, entry.title)

    picked = sorted(entries, key=rank)[: max(1, limit)]
    out: list[Recommendation] = []
    for entry in picked:
        stat = stats.get(_family(entry.title))
        if stat:
            label = "GAME" if stat.games == 1 else "GAMES"
            reason = f"YOU ALREADY PLAY THIS // {stat.score_pct}% IN {stat.games} {label}"
        else:
            reason = f"NEW LINE FOR {band.upper()} // {entry.level.upper()}"
        out.append(Recommendation(entry, reason))
    return tuple(out)


__all__ = [
    "ScoutError",
    "PlayedGame",
    "OpeningStat",
    "Recommendation",
    "ScoutReport",
    "parse_game_link",
    "looks_like_fen",
    "detect_colour",
    "level_for_elo",
    "fetch_chesscom",
    "fetch_lichess",
    "fetch_pgn_from_link",
    "read_pgn",
    "summarise",
    "recommend",
]
