"""BYOK AI opponents: provider table, prompt building, reply parsing, retries.

Privacy rules enforced here:
* the key is used only to build request headers and is never logged;
* transport errors are scrubbed of the key before they reach the UI;
* replies are validated with ``python-chess`` before they are played.

The module is transport-agnostic: ``request_move`` calls ``_call_provider`` and
the tests patch that function, so no network access is needed for the suite.
"""

from __future__ import annotations

import asyncio
import json
import re
from dataclasses import dataclass, field
from typing import Any

import chess
import httpx

MAX_ATTEMPTS = 3


@dataclass(frozen=True)
class Provider:
    """One BYOK provider and its model suggestions."""

    key: str
    label: str
    default_model: str
    models: tuple[str, ...]
    requires_key: bool
    key_hint: str
    kind: str
    base_url: str


PROVIDERS: tuple[Provider, ...] = (
    Provider(
        key="openai",
        label="OpenAI",
        default_model="gpt-4o-mini",
        models=("gpt-4o-mini", "gpt-4o", "gpt-4.1", "o4-mini"),
        requires_key=True,
        key_hint="Create a key at platform.openai.com/api-keys",
        kind="openai",
        base_url="https://api.openai.com/v1/chat/completions",
    ),
    Provider(
        key="anthropic",
        label="Anthropic",
        default_model="claude-3-5-sonnet-latest",
        models=("claude-3-5-sonnet-latest", "claude-3-7-sonnet-latest", "claude-sonnet-4-5"),
        requires_key=True,
        key_hint="Create a key at console.anthropic.com",
        kind="anthropic",
        base_url="https://api.anthropic.com/v1/messages",
    ),
    Provider(
        key="gemini",
        label="Google Gemini",
        default_model="gemini-3.5-flash-lite",
        models=("gemini-3.5-flash-lite", "gemini-2.5-flash", "gemini-2.5-pro"),
        requires_key=True,
        key_hint="Create a key at aistudio.google.com/apikey",
        kind="gemini",
        base_url="https://generativelanguage.googleapis.com/v1beta",
    ),
    Provider(
        key="openrouter",
        label="OpenRouter",
        default_model="openai/gpt-4o-mini",
        models=(
            "openai/gpt-4o-mini",
            "anthropic/claude-3.5-sonnet",
            "google/gemini-2.5-pro",
            "meta-llama/llama-3.3-70b-instruct",
        ),
        requires_key=True,
        key_hint="Create a key at openrouter.ai/keys",
        kind="openai",
        base_url="https://openrouter.ai/api/v1/chat/completions",
    ),
    Provider(
        key="ollama",
        label="Ollama (local)",
        default_model="llama3.1",
        models=("llama3.1", "qwen2.5", "mistral"),
        requires_key=False,
        key_hint="Run 'ollama serve' and pull the model. No key is needed.",
        kind="openai",
        base_url="http://localhost:11434/v1/chat/completions",
    ),
)


def get_provider(key: str) -> Provider:
    """Return the provider for ``key``, falling back to the first one."""
    for provider in PROVIDERS:
        if provider.key == key:
            return provider
    return PROVIDERS[0]


SYSTEM_PROMPT = (
    "You are a chess engine playing through a terminal interface. "
    "Choose exactly one legal move for the side to move. "
    "Reply with the move only, using UCI (e2e4) or SAN (Nf3). "
    "Never explain, never add move numbers, never repeat the position."
)

ADVICE_PROMPT = (
    "You are a chess engine helping a human study a position. "
    "Give the best move for the side to move in UCI (e2e4), then one short reason "
    "of at most 25 words. Do not repeat the position or the legal-move list."
)

REVIEW_PROMPT = (
    "You are a patient chess coach reviewing a finished game for the player. "
    "Find three to five concrete turning points. For each one give the move number, "
    "what went wrong, and the better idea. Use plain text, no markdown, no lists of "
    "every move, at most 220 words. If the game is short, say what the decisive "
    "mistake was."
)


# --------------------------------------------------------------------- prompts
def format_history(history: list[str]) -> str:
    """Format SAN history as numbered move pairs, e.g. ``1. e4 e5 2. Nf3``."""
    parts: list[str] = []
    for index in range(0, len(history), 2):
        pair = history[index : index + 2]
        parts.append(f"{index // 2 + 1}. " + " ".join(pair))
    return " ".join(parts)


def build_prompt(board: chess.Board, history: list[str]) -> str:
    """The user prompt: FEN, move history and the full legal-move list."""
    history_text = format_history(history) or "(no moves yet)"
    legal = ", ".join(sorted(move.uci() for move in board.legal_moves))
    return (
        f"Position (FEN): {board.fen()}\n"
        f"Move history: {history_text}\n"
        f"Side to move: {'White' if board.turn == chess.WHITE else 'Black'}\n"
        f"Legal moves ({board.legal_moves.count()}): {legal}\n"
        "Reply with one legal move only."
    )


# --------------------------------------------------------------------- parsing
_UCI_RE = re.compile(r"\b([a-h][1-8][a-h][1-8][qrbn]?)\b", re.IGNORECASE)
_BESTMOVE_RE = re.compile(r"bestmove\s+([a-h][1-8][a-h][1-8][qrbn]?)", re.IGNORECASE)


def _strip_annotations(token: str) -> str:
    token = token.strip().strip(".!?,;:\"'`*_[](){}")
    token = token.replace("0-0-0", "O-O-O").replace("0-0", "O-O")
    token = token.rstrip("+#!?")
    return token


def _as_legal_uci(text: str, board: chess.Board) -> chess.Move | None:
    for match in _UCI_RE.findall(text):
        try:
            move = chess.Move.from_uci(match.lower())
        except ValueError:
            continue
        if move in board.legal_moves:
            return move
    return None


def parse_move(reply: str, board: chess.Board) -> chess.Move | None:
    """Extract one legal move from a provider reply, or ``None``.

    Understands a bare UCI move, SAN, fenced JSON such as ``{"move": "e2e4"}``,
    engine output such as ``bestmove g1f3 ponder ...`` and prose that mentions a
    move. Everything is validated against ``board.legal_moves``.
    """
    if not reply or not reply.strip():
        return None
    text = reply.strip()

    # 1. A JSON object with a "move" field, fenced or not.
    for candidate in re.findall(r"\{[^{}]*\}", text):
        try:
            payload = json.loads(candidate)
        except ValueError:
            continue
        if isinstance(payload, dict):
            value = payload.get("move")
            if isinstance(value, str):
                move = parse_move(value, board)
                if move is not None:
                    return move

    # 2. Engine-style "bestmove X".
    best = _BESTMOVE_RE.search(text)
    if best is not None:
        move = _as_legal_uci(best.group(1), board)
        if move is not None:
            return move

    # 3. Any UCI square pair in the text.
    move = _as_legal_uci(text, board)
    if move is not None:
        return move

    # 4. SAN tokens, including castling written with zeroes.
    tokens = re.split(r"[\s,;]+", text)
    for token in reversed(tokens):
        san = _strip_annotations(token)
        san = re.sub(r"^\d+\.+", "", san).lstrip(".")
        if not san or san.lower() in ("move", "bestmove", "moves"):
            continue
        for variant in (san, san.replace("x", "x"), san.capitalize(), san.upper()):
            try:
                candidate = board.parse_san(variant)
            except ValueError:
                continue
            if candidate in board.legal_moves:
                return candidate
    return None


# ------------------------------------------------------------------- results
@dataclass
class Attempt:
    """One provider reply and whether it produced a legal move."""

    reply: str
    accepted: bool


@dataclass
class AIResult:
    """The outcome of asking a provider for a move."""

    move: chess.Move | None
    attempts: list[Attempt] = field(default_factory=list)
    transcript: str = ""
    error: str = ""


def _scrub(text: str, api_key: str, limit: int = 600) -> str:
    """Remove the API key from any text that could reach the screen."""
    value = (text or "").strip()
    if api_key:
        value = value.replace(api_key, "[redacted]")
    return value[:limit]


# ------------------------------------------------------------------ transport
async def _call_provider(
    provider_key: str,
    model: str,
    api_key: str,
    board: chess.Board,
    history: list[str],
    feedback: str | None,
    *,
    system_prompt: str | None = None,
    user_prompt: str | None = None,
    max_tokens: int = 64,
) -> str:
    """Send one request and return the raw text reply."""
    provider = get_provider(provider_key)
    prompt = user_prompt or build_prompt(board, history)
    if feedback:
        prompt = f"{prompt}\n\nCorrection from the referee:\n{feedback}"
    system = system_prompt or SYSTEM_PROMPT

    timeout = httpx.Timeout(60.0, connect=10.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        if provider.kind == "anthropic":
            response = await client.post(
                provider.base_url,
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": model,
                    "max_tokens": max_tokens,
                    "system": system,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            response.raise_for_status()
            payload = response.json()
            blocks = payload.get("content") or []
            return " ".join(
                str(block.get("text", "")) for block in blocks if isinstance(block, dict)
            )

        if provider.kind == "gemini":
            response = await client.post(
                f"{provider.base_url}/models/{model}:generateContent",
                headers={"x-goog-api-key": api_key, "content-type": "application/json"},
                json={
                    "systemInstruction": {"parts": [{"text": system}]},
                    "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                    "generationConfig": {"maxOutputTokens": max_tokens, "temperature": 0},
                },
            )
            response.raise_for_status()
            payload = response.json()
            candidates = payload.get("candidates") or []
            if not candidates:
                return ""
            parts = candidates[0].get("content", {}).get("parts") or []
            return " ".join(str(part.get("text", "")) for part in parts if isinstance(part, dict))

        headers = {"content-type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        response = await client.post(
            provider.base_url,
            headers=headers,
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0,
                "max_tokens": max_tokens,
            },
        )
        response.raise_for_status()
        payload: Any = response.json()
        choices = payload.get("choices") or []
        if not choices:
            return ""
        message = choices[0].get("message") or {}
        return str(message.get("content", ""))


@dataclass
class Advice:
    """A study suggestion (or its error) from a BYOK model."""

    text: str = ""
    error: str = ""


@dataclass
class Review:
    """A post-game coaching review (or its error)."""

    text: str = ""
    error: str = ""


async def request_advice(
    provider_key: str,
    model: str,
    api_key: str,
    board: chess.Board,
    history: list[str] | None = None,
) -> Advice:
    """Ask the provider for the best move and a one-line reason."""
    provider = get_provider(provider_key)
    if provider.requires_key and not (api_key or "").strip():
        return Advice(
            error=f"{provider.label.upper()} NEEDS A KEY // PASTE IT IN AI SETUP, OR INSTALL STOCKFISH."
        )
    legal = ", ".join(sorted(move.uci() for move in board.legal_moves))
    prompt = (
        f"Position (FEN): {board.fen()}\n"
        f"Side to move: {'White' if board.turn == chess.WHITE else 'Black'}\n"
        f"Legal moves: {legal}\n"
        f"Move history: {format_history(history or []) or '(none)'}\n"
        "Best move and one short reason."
    )
    try:
        reply = await _call_provider(
            provider.key,
            model,
            api_key,
            board,
            history or [],
            None,
            system_prompt=ADVICE_PROMPT,
            user_prompt=prompt,
            max_tokens=160,
        )
    except Exception as exc:
        return Advice(error=_scrub(f"{type(exc).__name__}: {exc}", api_key))
    text = _scrub(reply, api_key, limit=1200)
    return Advice(text=text or "", error="" if text else "THE MODEL RETURNED NOTHING.")


async def request_review(
    provider_key: str,
    model: str,
    api_key: str,
    pgn: str,
) -> Review:
    """Ask the provider for a blunder-by-blunder review of a PGN."""
    provider = get_provider(provider_key)
    if provider.requires_key and not (api_key or "").strip():
        return Review(error=f"{provider.label.upper()} NEEDS A KEY IN RAM TO COACH THIS GAME.")
    prompt = (
        "Review this game for the player. Point out the decisive mistakes and the "
        "better moves, with move numbers.\n\n"
        f"{pgn.strip()[:8000]}"
    )
    try:
        reply = await _call_provider(
            provider.key,
            model,
            api_key,
            chess.Board(),
            [],
            None,
            system_prompt=REVIEW_PROMPT,
            user_prompt=prompt,
            max_tokens=900,
        )
    except Exception as exc:
        return Review(error=_scrub(f"{type(exc).__name__}: {exc}", api_key))
    text = _scrub(reply, api_key, limit=6000)
    return Review(text=text, error="" if text else "THE MODEL RETURNED AN EMPTY REVIEW.")


# ------------------------------------------------------------------ public API
async def request_move(
    provider_key: str,
    model: str,
    api_key: str,
    board: chess.Board,
    history: list[str],
) -> AIResult:
    """Ask a provider for a move, retrying with referee feedback on rejection."""
    provider = get_provider(provider_key)
    if provider.requires_key and not (api_key or "").strip():
        return AIResult(
            None,
            [],
            "",
            f"{provider.label.upper()} needs an API key. Paste it in the AI screen; it stays in RAM.",
        )

    attempts: list[Attempt] = []
    transcript: list[str] = []
    feedback: str | None = None

    for number in range(1, MAX_ATTEMPTS + 1):
        try:
            reply = await _call_provider(provider.key, model, api_key, board, history, feedback)
        except Exception as exc:  # transport or HTTP failure: report, do not retry blindly
            detail = _scrub(f"{type(exc).__name__}: {exc}", api_key)
            return AIResult(
                None,
                attempts,
                "\n".join(transcript),
                f"Provider request failed. {detail}",
            )

        move = parse_move(reply, board)
        accepted = move is not None and move in board.legal_moves
        attempts.append(Attempt(reply, accepted))
        shown = _scrub(reply, api_key) or "(empty reply)"
        transcript.append(f"ATTEMPT {number}: {shown}")

        if accepted:
            return AIResult(move, attempts, "\n".join(transcript), "")

        legal = ", ".join(sorted(item.uci() for item in board.legal_moves))
        feedback = (
            f"Your previous reply was rejected: {shown!r} is not a legal move in this position. "
            f"Reply with exactly one move from this list: {legal}"
        )

    return AIResult(
        None,
        attempts,
        "\n".join(transcript),
        "Engine did not return a legal move after 3 attempts.",
    )


__all__ = [
    "PROVIDERS",
    "Provider",
    "get_provider",
    "build_prompt",
    "format_history",
    "parse_move",
    "request_move",
    "Attempt",
    "AIResult",
    "Advice",
    "Review",
    "request_advice",
    "request_review",
    "MAX_ATTEMPTS",
]
