"""Reference notes: tactics, endgames and notation for the library screen."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ReferenceNote:
    """A compact reference card with no move sequence."""

    title: str
    category: str
    body: str
    drills: tuple[str, ...] = ()


REFERENCE_NOTES: tuple[ReferenceNote, ...] = (
    ReferenceNote(
        title="Forks & Double Attacks",
        category="TACTICS",
        body=(
            "A fork attacks two or more targets at once. Knights are the classic "
            "forksmiths because their attacks cannot be blocked, but queens, bishops, "
            "rooks and pawns all fork. A double attack is the general idea: one move, "
            "two threats. Look for loose pieces, undefended queens and kings on the "
            "same colour complex as your knight."
        ),
        drills=(
            "Before every move, scan for your opponent's undefended pieces.",
            "Knights love c7, f7, e6 and d6 in the opening; aim them at king and rook.",
            "A fork is only good if both targets are worth more than the forking piece.",
        ),
    ),
    ReferenceNote(
        title="Pins, Skewers & Discovered Attacks",
        category="TACTICS",
        body=(
            "A pin freezes a piece because moving it exposes something more valuable "
            "behind it. An absolute pin is against the king; a relative pin can be "
            "broken at a cost. A skewer is a pin in reverse: the valuable piece is in "
            "front and must move, exposing the piece behind. Discovered attacks move "
            "one piece to unleash another's line; discovered checks are especially "
            "strong because the moving piece gets a free tempo."
        ),
        drills=(
            "Pile up on a pinned piece with pawns and minor pieces; it cannot run.",
            "When pinned, look for a zwischenzug that creates a bigger threat.",
            "A discovered check plus a capture is often decisive; calculate forcing lines first.",
        ),
    ),
    ReferenceNote(
        title="King Activity in the Endgame",
        category="ENDGAME",
        body=(
            "Once the queens are gone, the king becomes a fighting piece. Centralise it "
            "before pushing pawns. The king's value is roughly four pawns in the "
            "endgame, so losing a tempo with a passive king can decide the game. "
            "Opposition - placing kings on the same file with one square between them "
            "and the opponent to move - is the core mechanism of pawn endings."
        ),
        drills=(
            "Ask which king reaches the centre first; that side usually dictates.",
            "In king-and-pawn endings, calculate the pawn race before trading.",
            "Keep the king in front of its pawns when marching up the board.",
        ),
    ),
    ReferenceNote(
        title="Rook Endgame Essentials",
        category="ENDGAME",
        body=(
            "Rook endings are the most common endgame and the most drawish. Two rules "
            "carry most of the weight: place your rook behind a passed pawn (yours or "
            "the opponent's), and activate the rook before defending passively. The "
            "Lucena position shows how to build a bridge to shelter the king; the "
            "Philidor position shows how to hold a draw with the rook on the third rank."
        ),
        drills=(
            "Rooks belong on open files, behind passed pawns.",
            "Cut the enemy king off along a rank or file before escorting your pawn.",
            "In the Lucena, use the rook to block checks on the fourth rank, then walk out.",
        ),
    ),
    ReferenceNote(
        title="The Rule of the Square",
        category="ENDGAME",
        body=(
            "A lone king can catch a running pawn only if it is inside the square drawn "
            "from the pawn to its promotion square. Count the squares: a pawn on a5 needs "
            "five moves to promote, so a king within a 5x5 square of a5 can intercept. "
            "A pawn on the second rank is a special case because it may move two squares."
        ),
        drills=(
            "Draw the square from the pawn's current square to promotion.",
            "If your king is outside, try to blockade with your own pawn or rook.",
            "A rook pawn on the a- or h-file draws if the defender reaches the corner.",
        ),
    ),
    ReferenceNote(
        title="Algebraic Notation",
        category="NOTATION",
        body=(
            "Every move is written as piece letter + destination square, with file and "
            "rank. Pawn moves omit the piece letter: e4. Captures use x: Nxf3. Castling "
            "is O-O or O-O-O. Check is +, mate is #, promotion is =Q, and en passant is "
            "sometimes marked e.p. Disambiguation is added only when needed: Nbd2, R1e2. "
            "Annotation symbols: ! good, ? bad, !? interesting, ?! dubious, = equal."
        ),
        drills=(
            "Read coordinates from White's side: a1 is bottom-left, h8 top-right.",
            "Say the move out loud in coordinate form to avoid board-vision slips.",
            "In this app's move log, use Left/Right in the library to replay a main line.",
        ),
    ),
    ReferenceNote(
        title="Opening Principles",
        category="STRATEGY",
        body=(
            "Fight for the centre, develop your minor pieces toward it, castle early, "
            "and connect your rooks. Do not move the same piece twice without reason, "
            "and do not launch a wing attack before the centre is settled. A lead in "
            "development is only meaningful if you open lines; a pawn move that does "
            "not help development is usually a lost tempo."
        ),
        drills=(
            "Count developed pieces after move 6; the side with more usually stands better.",
            "Ask which side controls more central squares before choosing a plan.",
            "A queen sortie that can be hit by a developing move is usually a mistake.",
        ),
    ),
    ReferenceNote(
        title="Converting an Advantage",
        category="STRATEGY",
        body=(
            "When ahead in material, trade pieces, not pawns, and keep the position "
            "simple. When behind, keep pieces on, create counterplay and complicate. "
            "Pawn structure is the skeleton of the position: identify the backwards "
            "pawn, the isolated pawn and the passed pawn before choosing a plan. "
            "Prophylaxis - stopping the opponent's plan before advancing your own - is "
            "the mark of mature play."
        ),
        drills=(
            "Name both sides' worst-placed piece before every plan.",
            "Fix enemy pawn weaknesses on the colour of your bishop.",
            "With an extra pawn, activate the king and create a second front.",
        ),
    ),
)


__all__ = ["ReferenceNote", "REFERENCE_NOTES"]
