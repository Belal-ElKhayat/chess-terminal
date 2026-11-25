"""Famous traps, swindles and opening tricks for the Chess.Terminal library."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Trap:
    """A named trap: the line, the sting, and how to defend against it."""

    name: str
    eco: str
    moves: tuple[str, ...]
    claim: str
    explanation: str
    defence: str
    side: str  # "white" or "black": the side that springs the trap


TRAPS: tuple[Trap, ...] = (
    Trap(
        name="Fool's Mate",
        eco="A00",
        side="black",
        moves=("f3", "e5", "g4", "Qh4#"),
        claim="The fastest possible mate: two moves.",
        explanation=(
            "White weakens the e1-h4 diagonal with f3 and g4. Black's queen lands "
            "on h4 and mates at once: the king has no flight square, no piece can "
            "block the diagonal, and nothing can capture the queen."
        ),
        defence=(
            "Do not push the f- and g-pawns before castling. Against any early queen "
            "sortie, ask which diagonal it points at."
        ),
    ),
    Trap(
        name="Scholar's Mate",
        eco="C20",
        side="white",
        moves=("e4", "e5", "Qh5", "Nc6", "Bc4", "Nf6", "Qxf7#"),
        claim="Mate in four moves against a careless defender.",
        explanation=(
            "White aims the queen at f7, the weakest square in Black's camp, and adds "
            "the bishop's fire. Black's natural ...Nf6 develops but ignores the threat. "
            "Qxf7 is mate because the king is boxed in by its own pieces and the f7 "
            "square is defended by the bishop on c4."
        ),
        defence=(
            "After 1.e4 e5 2.Qh5, play 2...Nc6 3.Bc4 g6 4.Qf3 Nf6, or simply 2...Nc6 "
            "and 3...g6. Develop the g8 knight only after the queen's threats are met."
        ),
    ),
    Trap(
        name="Legal's Mate",
        eco="C41",
        side="white",
        moves=("e4", "e5", "Nf3", "d6", "Bc4", "Bg4", "Nc3", "g6", "Nxe5", "Bxd1", "Bxf7+", "Ke7", "Nd5#"),
        claim="A queen sacrifice that mates with three minor pieces.",
        explanation=(
            "Black pins the f3 knight and thinks the e5 pawn is safe. White crashes "
            "through with Nxe5, allowing ...Bxd1, because the discovered battery on "
            "f7 is decisive. After Bxf7+ Ke7, Nd5 is mate: the knight covers e7's "
            "escape squares and the bishop controls the diagonals."
        ),
        defence=(
            "Do not play ...Bg4 before ...Be7 in this order, and meet Nxe5 with ...dxe5 "
            "only when the pin is real. After 4...g6, Black has weakened the dark squares "
            "and must be precise."
        ),
    ),
    Trap(
        name="Fried Liver Attack",
        eco="C57",
        side="white",
        moves=("e4", "e5", "Nf3", "Nc6", "Bc4", "Nf6", "Ng5", "d5", "exd5", "Nxd5", "Nxf7", "Kxf7", "Qf3+", "Ke6", "Nc3"),
        claim="A knight sacrifice that drags the king into the open.",
        explanation=(
            "The knight on g5 hits f7 twice and Black's ...Nxd5 walks into Nxf7. "
            "White gives up a knight for a raging attack: Qf3+ forces the king to e6, "
            "where it blocks its own pieces. Nc3 adds a third attacker and Black must "
            "defend with ...Nb4 or ...Ne7 while walking a tightrope."
        ),
        defence=(
            "Avoid 5...Nxd5. Play 5...Na5, hitting the c4 bishop, or 5...b5!? and "
            "6...h6. The Fried Liver is only dangerous if Black allows Nxf7."
        ),
    ),
    Trap(
        name="Blackburne Shilling Gambit",
        eco="C50",
        side="black",
        moves=("e4", "e5", "Nf3", "Nc6", "Bc4", "Nd4", "Nxe5", "Qg5", "Nxf7", "Qxg2", "Rf1", "Qxe4+", "Be2", "Nf3#"),
        claim="A knight on the rim and a queen that mates from the middle of the board.",
        explanation=(
            "Black offers the e5 pawn with ...Nd4, hoping White grabs it. After "
            "Nxe5 Qg5! White's f7 grab loses to ...Qxg2, and the queen then swings to "
            "e4 with check. When White blocks with Be2, ...Nf3 is mate: the knight "
            "covers the king's escape and delivers check while the queen seals the "
            "diagonal."
        ),
        defence=(
            "Do not take on e5. Play 4.Nxd4 exd4 5.O-O, or 4.d3, keeping a healthy "
            "position. Against ...Nd4, ask what happens to your f-pawn before grabbing pawns."
        ),
    ),
    Trap(
        name="Lasker Trap",
        eco="D08",
        side="black",
        moves=("d4", "d5", "c4", "e5", "dxe5", "d4", "e3", "Bb4+", "Bd2", "dxe3", "Bxb4", "exf2+", "Ke2", "fxg1=N+"),
        claim="An underpromotion to a knight delivers the check.",
        explanation=(
            "In the Albin Countergambit Black gives a pawn for a wedge on d4, then "
            "offers the bishop on b4 to open lines. After Bxb4, ...exf2+ forces the "
            "king to e2 and ...fxg1=N+ promotes to a knight with check, winning the "
            "corner rook while the queen still hangs on d1."
        ),
        defence=(
            "Meet the Albin with 3.dxe5 or 3.Nf3 and avoid grabbing the b4 bishop "
            "before castling. If the pawn reaches f2, calculate the underpromotion "
            "before allowing it."
        ),
    ),
    Trap(
        name="Noah's Ark Trap",
        eco="C61",
        side="black",
        moves=("e4", "e5", "Nf3", "Nc6", "Bb5", "a6", "Ba4", "d6", "d4", "b5", "Bb3", "Nxd4", "Nxd4", "exd4", "Qxd4", "c5", "Qd5", "Be6", "Qc6+", "Bd7", "Qd5", "c4"),
        claim="The bishop on b3 is walled in and lost.",
        explanation=(
            "Black lures the Spanish bishop to b3, then plays ...c5-c4 at the right "
            "moment. The b3 bishop has no squares: c2 and d5 are covered, a2 and c4 "
            "are blocked or attacked, and the queenside pawns take away the rest. A "
            "whole piece disappears from the game."
        ),
        defence=(
            "Do not allow the bishop to be sealed in. Play c3 and Be3 early, or retreat "
            "to c2 before ...c4 lands. Count the bishop's squares whenever ...c5 is available."
        ),
    ),
    Trap(
        name="Budapest Trap",
        eco="A52",
        side="black",
        moves=("d4", "Nf6", "c4", "e5", "dxe5", "Ng4", "Bf4", "Nc6", "Nf3", "Bb4+", "Nbd2", "Qe7", "a3", "Ngxe5", "axb4", "Nd3#"),
        claim="A knight fork on d3 mates the uncastled king.",
        explanation=(
            "Black's Budapest Gambit aims at the d3 square from the start. White's "
            "a3 attacks the b4 bishop, but ...Ngxe5 ignores it: the knight lands on "
            "d3 with check and mate, covering e1, e2 and f2 while the other knight "
            "and queen cut off the rest."
        ),
        defence=(
            "After 4.Bf4, meet ...Bb4+ with 5.Nbd2 but keep the king's squares in "
            "mind. Do not grab on b4 while the d3 fork is available; play e3 or Nf3 "
            "to cover d3 first."
        ),
    ),
    Trap(
        name="Elephant Trap",
        eco="D30",
        side="black",
        moves=("d4", "d5", "c4", "e6", "Nc3", "Nf6", "Bg5", "Nbd7", "cxd5", "exd5", "Nxd5", "Nxd5", "Bxd8", "Bb4+", "Qd2", "Bxd2+", "Kxd2", "Kxd8"),
        claim="A queen grab loses the queen and the right to castle.",
        explanation=(
            "The pin on f6 looks strong, so White takes on d5 twice. Black answers "
            "with ...Bb4+, and the only block, Qd2, drops the queen to ...Bxd2+. "
            "White must recapture with the king, which loses castling and leaves Black "
            "a piece down for nothing."
        ),
        defence=(
            "Do not take on d5 while the c3 knight is pinned. After 6.cxd5, develop "
            "with e3 and Nf3, and only capture when the tactics work for you."
        ),
    ),
    Trap(
        name="Damiano Trap",
        eco="C40",
        side="white",
        moves=("e4", "e5", "Nf3", "f6", "Nxe5", "fxe5", "Qh5+", "g6", "Qxe5+", "Qe7", "Qxh8"),
        claim="A defensive pawn move loses the rook in the corner.",
        explanation=(
            "After ...f6, White's knight sacrifice opens the e-file and the h5 "
            "diagonal. Qh5+ and Qxe5+ win the rook on h8 because Black's queen is "
            "pinned on e7 and the h8 corner has no escape."
        ),
        defence=(
            "Never play ...f6 before developing. If you have, meet Nxe5 with ...Qe7 "
            "rather than ...fxe5, and accept a small disadvantage instead of a lost rook."
        ),
    ),
    Trap(
        name="Stafford Gambit",
        eco="C42",
        side="black",
        moves=("e4", "e5", "Nf3", "Nf6", "Nxe5", "Nc6", "Nxc6", "dxc6", "d3", "Bc5", "Bg5", "Nxe4", "Bxd8", "Bxf2+", "Ke2", "Bg4#"),
        claim="The 'Oh No My Queen' line: a queen sacrifice that mates with two bishops and a knight.",
        explanation=(
            "Black gives a pawn for open lines, then offers the queen. The natural 6.Bg5 "
            "pins the f6 knight and looks strong, but the knight moves anyway: 6...Nxe4! "
            "If White accepts with 7.Bxd8, then 7...Bxf2+ 8.Ke2 Bg4 is mate. The knight on "
            "e4 covers d2, the bishop on f2 covers e1 and e3, and White's own queen, bishop "
            "and pawns block every other escape. If White declines with 7.dxe4, then "
            "7...Bxf2+ wins the queen instead."
        ),
        defence=(
            "Do not play Bg5 here. After 4...dxc6, cover the g4 square with 6.Be2 or 6.h3; "
            "then White keeps the extra pawn. If you have already played Bg5, meet ...Nxe4 "
            "with 7.Be3 or 7.Qe2 rather than grabbing the queen."
        ),
    ),
    Trap(
        name="Englund Gambit Trap",
        eco="A40",
        side="black",
        moves=("d4", "e5", "dxe5", "Nc6", "Nf3", "Qe7", "Bg5", "Qb4+", "Bd2", "Qxb2", "Bc3", "Bb4", "Qd2", "Bxc3", "Qxc3", "Qc1#"),
        claim="A queen raid that ends in a back-rank mate.",
        explanation=(
            "Black invests a pawn for open lines and a queenside raid. The check on "
            "b4 forces the bishop to d2, where it blocks the queen's defence. After "
            "Qxb2 and ...Bb4, White's queen is overloaded; Qxc3 walks into Qc1 mate, "
            "with the king trapped by its own bishop on f1 and pawns on e2 and f2."
        ),
        defence=(
            "Decline the gift: after 1.d4 e5, play 2.c4 or 2.Nf3 and meet ...Qe7 with "
            "Nc3. If you do take on e5, develop calmly and never allow ...Qb4+ to win a tempo."
        ),
    ),
)


__all__ = ["Trap", "TRAPS"]
