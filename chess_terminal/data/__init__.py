"""Unified, validated library entries for the opening book screen."""

from __future__ import annotations

from dataclasses import dataclass, field

import chess

from .games import FAMOUS_GAMES, FamousGame
from .openings import OPENINGS, Opening
from .reference import REFERENCE_NOTES, ReferenceNote
from .traps import TRAPS, Trap


@dataclass(frozen=True)
class LibraryEntry:
    """One selectable item in the library: opening, trap or reference note."""

    kind: str
    title: str
    eco: str
    moves: tuple[str, ...]
    summary: str
    sections: tuple[tuple[str, str], ...] = field(default_factory=tuple)
    side: str = ""
    level: str = ""

    @property
    def label(self) -> str:
        if self.kind == "note":
            return f"[NOTE] {self.title.upper()}"
        if self.kind == "game":
            return f"[{self.eco}] {self.title.upper()}"
        tag = f"[{self.eco}]" if self.eco else "[----]"
        return f"{tag} {self.title.upper()}"

    def search_text(self) -> str:
        parts = [self.kind, self.title, self.eco, self.summary, self.side, self.level]
        parts.extend(text for _, text in self.sections)
        return " ".join(parts).lower()

    def position_at(self, index: int) -> chess.Board:
        """Replay the stored SAN moves up to ``index`` plies."""
        board = chess.Board()
        for san in self.moves[: max(0, min(index, len(self.moves)))]:
            board.push_san(san)
        return board

    def validate(self) -> None:
        """Raise ``ValueError`` if any stored move is not legal."""
        board = chess.Board()
        for number, san in enumerate(self.moves, start=1):
            try:
                board.push_san(san)
            except ValueError as exc:  # pragma: no cover - data guard
                raise ValueError(f"{self.title}: ply {number} ({san}) is illegal") from exc


def _opening_entry(opening: Opening) -> LibraryEntry:
    plans = "\n".join(f"  {number}. {plan}" for number, plan in enumerate(opening.plans, 1))
    sections = [
        ("KEY IDEA", opening.ideas),
        ("PLANS", plans),
    ]
    if opening.watch_out:
        sections.append(("WATCH OUT", opening.watch_out))
    return LibraryEntry(
        kind="opening",
        title=f"{opening.name}",
        eco=opening.eco,
        moves=opening.moves,
        summary=f"{opening.family} // {len(opening.moves) // 2} moves deep.",
        sections=tuple(sections),
        side=opening.side,
        level=opening.level,
    )


def _trap_entry(trap: Trap) -> LibraryEntry:
    return LibraryEntry(
        kind="trap",
        title=trap.name,
        eco=trap.eco,
        moves=trap.moves,
        summary=trap.claim,
        sections=(
            ("THE STING", trap.explanation),
            ("DEFENCE", trap.defence),
        ),
        side=trap.side,
    )


def _note_entry(note: ReferenceNote) -> LibraryEntry:
    drills = "\n".join(f"  - {drill}" for drill in note.drills)
    return LibraryEntry(
        kind="note",
        title=note.title,
        eco="",
        moves=(),
        summary=f"{note.category} // reference card.",
        sections=(("NOTES", note.body), ("DRILLS", drills or "  - Rehearse the idea in a slow game.")),
    )


def _game_entry(game: FamousGame) -> LibraryEntry:
    plies = len(game.moves)
    sections = [
        ("THE STORY", game.story),
        ("WHY IT MATTERS", game.why),
        ("THE MOMENT", game.moment),
    ]
    if game.line_note:
        sections.append(("LINE", game.line_note))
    return LibraryEntry(
        kind="game",
        title=game.title,
        eco=str(game.year),
        moves=game.moves,
        summary=(
            f"{game.white} vs {game.black} // {game.event} // {game.result} // "
            f"{plies // 2} moves."
        ),
        sections=tuple(sections),
    )


def build_entries() -> tuple[LibraryEntry, ...]:
    entries: list[LibraryEntry] = []
    entries.extend(_opening_entry(opening) for opening in OPENINGS)
    entries.extend(_trap_entry(trap) for trap in TRAPS)
    entries.extend(_game_entry(game) for game in FAMOUS_GAMES)
    entries.extend(_note_entry(note) for note in REFERENCE_NOTES)
    for entry in entries:
        entry.validate()
    return tuple(entries)


ENTRIES: tuple[LibraryEntry, ...] = build_entries()


__all__ = [
    "LibraryEntry",
    "ENTRIES",
    "build_entries",
    "OPENINGS",
    "TRAPS",
    "FAMOUS_GAMES",
    "REFERENCE_NOTES",
]
