"""Structured opening data for the Chess.Terminal library.

Every move line is written in Standard Algebraic Notation and is replayed with
``python-chess`` by the library screen. The commentary is intentionally written
in plain, teachable language: an idea, then the plans that follow from it.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Opening:
    """A major opening with its ECO code, main line, ideas and plans."""

    eco: str
    name: str
    family: str
    side: str  # "white" or "black": whose choice defines the line
    level: str  # "beginner", "club" or "advanced"
    moves: tuple[str, ...]
    ideas: str
    plans: tuple[str, ...]
    watch_out: str = ""


OPENINGS: tuple[Opening, ...] = (
    # ------------------------------------------------------------ 1.e4 e5
    Opening(
        eco="C88",
        name="Ruy Lopez: Closed",
        family="Ruy Lopez",
        side="white",
        level="club",
        moves=("e4", "e5", "Nf3", "Nc6", "Bb5", "a6", "Ba4", "Nf6", "O-O", "Be7", "Re1", "b5", "Bb3", "d6", "c3", "O-O"),
        ideas=(
            "The Spanish Game asks a simple question: can Black hold the e5 pawn? "
            "White pressures the c6 knight, the defender of e5, and builds a broad "
            "centre with c3 and d4. Black answers with ...b5 and ...d6, securing the "
            "queenside and preparing ...Na5 or ...Bg4."
        ),
        plans=(
            "White: build the d4 centre with c3, d4 and Nbd2, then reroute the knight to f1-g3.",
            "White: play h3 and Be3, keeping the option of a kingside pawn storm.",
            "Black: play ...Na5 and ...c5 to challenge the bishop and hit the centre.",
            "Black: use ...Bg4 and ...Nd7 to pressure d4 and untangle the pieces.",
        ),
        watch_out="The bishop on b3 can be trapped by ...Na5 and ...c5; keep an escape via c2 or d5.",
    ),
    Opening(
        eco="C67",
        name="Ruy Lopez: Berlin",
        family="Ruy Lopez",
        side="white",
        level="advanced",
        moves=("e4", "e5", "Nf3", "Nc6", "Bb5", "Nf6", "O-O", "Nxe4", "d4", "Nd6", "Bxc6", "dxc6", "dxe5", "Nf5", "Qxd8+", "Kxd8"),
        ideas=(
            "The Berlin Wall: Black grabs the e4 pawn and happily trades queens, "
            "accepting a slightly worse structure in return for an endgame that is "
            "very hard to lose. White gets the bishop pair and a queenside majority, "
            "Black gets the only open file and a active king."
        ),
        plans=(
            "White: use the bishop pair and push the queenside majority with b4 and c4.",
            "White: avoid unnecessary piece trades; the extra bishop is the long-term asset.",
            "Black: activate the king, put rooks on the d-file and blockade on light squares.",
            "Black: aim for ...Ke7, ...Be6 and ...c5 to open the position for the bishops.",
        ),
        watch_out="Do not treat the Berlin as a drawing line by default: passive rooks lose the endgame slowly.",
    ),
    Opening(
        eco="C54",
        name="Italian Game: Giuoco Piano",
        family="Italian Game",
        side="white",
        level="beginner",
        moves=("e4", "e5", "Nf3", "Nc6", "Bc4", "Bc5", "c3", "Nf6", "d3", "d6", "O-O", "O-O"),
        ideas=(
            "The oldest opening in the book. White develops the bishop to its most "
            "active diagonal and prepares d4 with c3. Black mirrors the setup, "
            "keeping a firm grip on e5 and waiting for the right moment to break."
        ),
        plans=(
            "White: prepare d4 with Re1, Nbd2 and Bb3, or play the slow d3 Italian.",
            "White: use the bishop pair and a later a4-a5 expansion on the queenside.",
            "Black: play ...a6, ...Ba7 and ...Be6, meeting d4 with ...exd4 and ...Bxd4.",
            "Black: free the position with ...Ne7 and ...Ng6 or ...d5 at the right moment.",
        ),
        watch_out="The d4 break needs preparation; premature d4 lets Black equalise with ...exd4 and ...d5.",
    ),
    Opening(
        eco="C51",
        name="Italian Game: Evans Gambit",
        family="Italian Game",
        side="white",
        level="club",
        moves=("e4", "e5", "Nf3", "Nc6", "Bc4", "Bc5", "b4", "Bxb4", "c3", "Ba5", "d4", "exd4", "O-O", "Nge7", "cxd4", "d5"),
        ideas=(
            "White throws a pawn at the bishop to gain time and build the ideal "
            "centre. The b4 pawn is a battering ram: after c3 and d4 White owns the "
            "middle, and the open b-file plus the a3-f8 diagonal give the attack "
            "real teeth."
        ),
        plans=(
            "White: open lines fast with d4, then hit f7 with e5 and Ng5 or Re1.",
            "White: use the b-file with Rb1 and the a3-f8 diagonal with Ba3.",
            "Black: return the pawn at the right moment with ...d5 to free the game.",
            "Black: develop with ...Nge7 and ...O-O, meeting e5 with ...d5.",
        ),
        watch_out="If White does not get open lines, the gambit pawn is simply gone; keep the tempi coming.",
    ),
    Opening(
        eco="C55",
        name="Two Knights Defense",
        family="Italian Game",
        side="black",
        level="club",
        moves=("e4", "e5", "Nf3", "Nc6", "Bc4", "Nf6", "d3", "Bc5", "c3", "d6", "O-O", "O-O", "Re1", "a6", "Bb3", "Ba7"),
        ideas=(
            "Black refuses the quiet Italian and develops actively, inviting White "
            "to grab e5. The modern main lines are positional: both sides build the "
            "same slow centre, and the small differences in piece placement decide "
            "who gets the first central break."
        ),
        plans=(
            "White: play Nbd2 and d4, or Re1 and Bb3 before the break.",
            "White: watch for the Ng5/Nxf7 tactics that give the opening its name.",
            "Black: play ...h6 and ...Re8, then meet d4 with ...exd4 and ...Bxd4.",
            "Black: use ...a6 and ...Ba7 to keep the bishop on the strong diagonal.",
        ),
        watch_out="The Fried Liver is only one move away if Black plays ...Nxd5 carelessly.",
    ),
    Opening(
        eco="C45",
        name="Scotch Game",
        family="Scotch",
        side="white",
        level="club",
        moves=("e4", "e5", "Nf3", "Nc6", "d4", "exd4", "Nxd4", "Bc5", "Be3", "Qf6", "c3", "Nge7", "Bc4", "Ne5", "Be2"),
        ideas=(
            "White opens the centre immediately instead of building slowly. The "
            "knight on d4 is strong but can be hit by ...c5 or ...Qb6, and Black's "
            "queen on f6 creates pressure on d4 and f2. Precise development matters "
            "more than memorisation."
        ),
        plans=(
            "White: castle quickly, then use the d4 knight and the e-file.",
            "White: meet ...Qf6 with Nb5 or Be3 and c3, keeping d4 defended.",
            "Black: pressure d4 with ...Qf6, ...Nge7 and ...c5.",
            "Black: trade the strong knight with ...Ne5 or ...Bxd4 when it helps.",
        ),
        watch_out="The queen on f6 is a target too: Be3 hits it, so Black must be ready to move it again.",
    ),
    Opening(
        eco="C39",
        name="King's Gambit",
        family="King's Gambit",
        side="white",
        level="advanced",
        moves=("e4", "e5", "f4", "exf4", "Nf3", "g5", "h4", "g4", "Ne5", "Nf6", "Bc4", "d5", "exd5", "Bd6", "d4"),
        ideas=(
            "White offers the f-pawn to deflect Black's e-pawn and open the f-file. "
            "The Kieseritzky line shows the modern treatment: Black holds the extra "
            "pawn with ...g5 and ...g4, White gets a strong knight on e5, and both "
            "sides race to finish development."
        ),
        plans=(
            "White: castle, pile up on f4 and use the e5 knight as a battering ram.",
            "White: open the f-file with Bxf4 and aim rooks at f7.",
            "Black: consolidate with ...Bg7, ...d6 and ...Ne7, then give back the pawn.",
            "Black: use ...Qe7 and ...Be6 to challenge the e5 knight.",
        ),
        watch_out="The g4 pawn can be a liability; if White breaks through with Bxf4, Black's king is the target.",
    ),
    Opening(
        eco="C41",
        name="Philidor Defense",
        family="Philidor",
        side="black",
        level="beginner",
        moves=("e4", "e5", "Nf3", "d6", "d4", "Nf6", "Nc3", "Nbd7", "Bc4", "Be7", "O-O", "O-O"),
        ideas=(
            "Black defends e5 with ...d6, accepting a cramped but resilient setup. "
            "The structure is passive but hard to crack: the idea is to hold the "
            "centre, then break with ...c5 or ...exd4 at the right moment."
        ),
        plans=(
            "White: build a big centre with dxe5, Bb5+ or Re1 and Bf1.",
            "White: avoid early piece trades that relieve Black's cramp.",
            "Black: play ...c5 or ...exd4 to get counterplay against d4.",
            "Black: reroute the f6 knight to e8 or h5 when the centre is closed.",
        ),
        watch_out="Passive is not the same as safe: without ...c5 or ...exd4 Black can be squeezed to death.",
    ),

    # ------------------------------------------------------------ Sicilian
    Opening(
        eco="B90",
        name="Sicilian Defense: Najdorf",
        family="Sicilian Defense",
        side="black",
        level="advanced",
        moves=("e4", "c5", "Nf3", "d6", "d4", "cxd4", "Nxd4", "Nf6", "Nc3", "a6"),
        ideas=(
            "Black refuses a symmetrical pawn structure. By trading the c-pawn for "
            "White's d-pawn, Black gains a half-open c-file and a central majority, "
            "at the cost of giving White more space. The Najdorf's ...a6 is a "
            "multi-purpose move: it controls b5, prepares ...e5 and ...b5, and gives "
            "the queen a future square on c7."
        ),
        plans=(
            "Black: fianchetto or develop the light bishop, castle, then strike with ...b5 and ...Bb7.",
            "Black: play ...e5 to contest d4, or ...e6 followed by ...Be7 and ...O-O for a hedgehog setup.",
            "White: castle queenside in the English Attack with Be3, f3, g4 and h4.",
            "White: play the positional 6.Be2 and 7.O-O, aiming at d5 and the e-file.",
        ),
        watch_out="The d5 square and the b6/g7 dark squares are the permanent tension points.",
    ),
    Opening(
        eco="B70",
        name="Sicilian Defense: Dragon",
        family="Sicilian Defense",
        side="black",
        level="club",
        moves=("e4", "c5", "Nf3", "d6", "d4", "cxd4", "Nxd4", "Nf6", "Nc3", "g6", "Be3", "Bg7", "f3", "O-O", "Qd2", "Nc6", "Bc4"),
        ideas=(
            "Black fianchettoes on the long diagonal and castles into the coming "
            "storm. White's Yugoslav Attack (Be3, f3, Qd2, O-O-O) is a race: White "
            "mates on the h-file, Black mates on the c-file. Both sides play for "
            "checkmate from move ten."
        ),
        plans=(
            "White: castle queenside, push h4-h5 and sac on h5 or g7.",
            "White: use Bh6 to trade the dragon bishop, the heart of Black's defence.",
            "Black: counter with ...Rc8, ...Ne5 and ...Nc4, hitting the white king.",
            "Black: play ...a6 and ...b5 to open the b-file for the rooks.",
        ),
        watch_out="Do not castle short as White; the whole point of the system is opposite-side castling.",
    ),
    Opening(
        eco="B33",
        name="Sicilian Defense: Sveshnikov",
        family="Sicilian Defense",
        side="black",
        level="advanced",
        moves=("e4", "c5", "Nf3", "Nc6", "d4", "cxd4", "Nxd4", "Nf6", "Nc3", "e5", "Ndb5", "d6", "Bg5", "a6", "Na3", "b5"),
        ideas=(
            "Black allows a hole on d5 in exchange for active piece play and the "
            "bishop pair. The knight is chased to a3, where it is misplaced, while "
            "Black expands with ...b5 and ...Be6. Modern theory treats this as one "
            "of Black's most reliable Sicilians."
        ),
        plans=(
            "White: occupy d5 with Nd5 and support it with c4 and Be3.",
            "White: exploit the d5 hole before Black finishes development.",
            "Black: develop with ...Be6, ...Be7 and ...O-O, then hit d5 with ...f5.",
            "Black: use the b-file and the bishop pair for long-term pressure.",
        ),
        watch_out="The d5 square is a permanent weakness; Black must keep pieces active enough to cover it.",
    ),

    # ------------------------------------------------------------ French
    Opening(
        eco="C11",
        name="French Defense: Classical Steinitz",
        family="French Defense",
        side="black",
        level="club",
        moves=("e4", "e6", "d4", "d5", "Nc3", "Nf6", "e5", "Nfd7", "f4", "c5", "Nf3", "Nc6"),
        ideas=(
            "Black accepts a space disadvantage in exchange for a granite pawn chain "
            "and a clear target on d4. White's e5 pawn cramps Black but takes pressure "
            "off the centre; the f4 advance supports a kingside push, while Black "
            "attacks the base of White's chain with ...c5."
        ),
        plans=(
            "White: attack on the kingside with Be3, Qd2, O-O-O and a pawn storm.",
            "White: reroute the knight to e2-g3 and play for f5 or a central break.",
            "Black: pressure d4 with ...cxd4, ...Nc6, ...Qb6 and ...Bd7-b5.",
            "Black: free the position with ...f6 at the right moment, or ...b5 and ...Bb7.",
        ),
        watch_out="Do not open the position while your king is uncastled; the French rewards patience.",
    ),
    Opening(
        eco="C18",
        name="French Defense: Winawer",
        family="French Defense",
        side="black",
        level="advanced",
        moves=("e4", "e6", "d4", "d5", "Nc3", "Bb4", "e5", "c5", "a3", "Bxc3+", "bxc3", "Ne7", "Qg4", "Qc7", "Qxg7", "Rg8", "Qxh7", "cxd4"),
        ideas=(
            "Black gives up the dark-squared bishop to wreck White's queenside, then "
            "attacks the doubled c-pawns. White grabs pawns on the kingside and walks "
            "a tightrope. The Winawer is a strategic bargain: structure for White, "
            "activity and targets for Black."
        ),
        plans=(
            "White: hold the centre and the extra kingside pawns, then consolidate.",
            "White: use the half-open b-file and the bishop pair after ...Bxc3+.",
            "Black: open lines against c3 and the white king with ...cxd4 and ...Qa5.",
            "Black: bring the rook to g8 and the knight to bc6 or d7 to hit e5.",
        ),
        watch_out="White's queen sortie can run out of squares; calculate the ...cxd4 breaks before grabbing more pawns.",
    ),
    Opening(
        eco="C02",
        name="French Defense: Advance",
        family="French Defense",
        side="black",
        level="club",
        moves=("e4", "e6", "d4", "d5", "e5", "c5", "c3", "Nc6", "Nf3", "Qb6", "a3", "c4"),
        ideas=(
            "White grabs space with e5 and defends d4 with c3, while Black attacks "
            "the base of the chain with ...c5 and ...Qb6. The structure is fixed "
            "early, so both sides play on the two wings: White on the kingside, "
            "Black on the queenside."
        ),
        plans=(
            "White: play Be3, Qd2 and O-O-O, then push f4-f5 or h4-h5.",
            "White: use the d4 pawn as a shield and attack the kingside.",
            "Black: play ...Bd7, ...Rc8 and ...Na5 to pressure c3 and b2.",
            "Black: clamp the queenside with ...c4 and ...Na5, then target b2.",
        ),
        watch_out="With the centre closed, the clocks matter: whoever breaks through first usually wins.",
    ),

    # ------------------------------------------------------------ Caro-Kann
    Opening(
        eco="B19",
        name="Caro-Kann: Classical",
        family="Caro-Kann Defense",
        side="black",
        level="club",
        moves=("e4", "c6", "d4", "d5", "Nc3", "dxe4", "Nxe4", "Bf5", "Ng3", "Bg6", "h4", "h6", "Nf3", "Nd7", "h5", "Bh7", "Bd3", "Bxd3", "Qxd3", "e6"),
        ideas=(
            "Black builds a fortress: the light-squared bishop develops outside the pawn "
            "chain, and ...e6 keeps the structure sound. White gains space and the "
            "bishop pair often follows, but Black's position is notoriously hard to break."
        ),
        plans=(
            "White: castle queenside and attack with h4-h5, Bd2 and Ne5.",
            "White: trade the last light-squared bishop with Bd3 and pressure the h7/b7 weaknesses.",
            "Black: develop with ...Ngf6, ...Be7 and ...O-O, then aim for ...c5.",
            "Black: use the c-file and ...Qa5 to create queenside counterplay.",
        ),
        watch_out="Black must solve the c8 bishop before closing the centre; that is the whole point of 3...dxe4.",
    ),
    Opening(
        eco="B12",
        name="Caro-Kann: Advance",
        family="Caro-Kann Defense",
        side="black",
        level="club",
        moves=("e4", "c6", "d4", "d5", "e5", "Bf5", "Nf3", "e6", "Be2", "c5", "Be3", "Nc6", "c3", "Qb6"),
        ideas=(
            "White closes the centre and Black develops the bishop outside the chain. "
            "Compared with the French, Black's light bishop is free, which is the "
            "whole point of the Caro-Kann. White gets space on the kingside; Black "
            "attacks d4 and the queenside."
        ),
        plans=(
            "White: play O-O, Nbd2 and a kingside expansion with Ne1-g3 or f4.",
            "White: meet ...cxd4 with cxd4 and use the open c-file.",
            "Black: pressure d4 with ...cxd4, ...Nge7 and ...Nf5.",
            "Black: use ...h5 or ...f6 to chip at the e5 pawn.",
        ),
        watch_out="Black's queen on b6 can be hit by a tempo; do not drift into a passive blockade.",
    ),

    # ------------------------------------------------------------ d4 systems
    Opening(
        eco="D37",
        name="Queen's Gambit: Orthodox",
        family="Queen's Gambit",
        side="white",
        level="club",
        moves=("d4", "d5", "c4", "e6", "Nc3", "Nf6", "Bg5", "Be7", "e3", "O-O", "Nf3"),
        ideas=(
            "White offers the c-pawn to deflect Black's d-pawn and win the centre. "
            "Black usually declines with ...e6, accepting a solid but cramped position. "
            "The pin with Bg5 pressures the f6 knight, the defender of d5 and h7, while "
            "e3 keeps the d4 pawn protected by the queen."
        ),
        plans=(
            "White: complete development with Bd3, O-O and Rc1, then play for e4 or cxd5.",
            "White: use the minority attack with b4-b5 on the queenside in Carlsbad structures.",
            "Black: free the game with ...dxc4 and ...c5, or ...Nbd7 and ...Re8 before ...e5.",
            "Black: trade dark-squared bishops with ...Ne4 and ...Bf5 to ease the cramp.",
        ),
        watch_out="Do not grab c4 too early unless you can hold it; the extra pawn is often a target.",
    ),
    Opening(
        eco="D35",
        name="Queen's Gambit: Exchange",
        family="Queen's Gambit",
        side="white",
        level="club",
        moves=("d4", "d5", "c4", "e6", "Nc3", "Nf6", "cxd5", "exd5", "Bg5", "Be7", "e3", "c6", "Bd3", "Nbd7", "Qc2", "O-O"),
        ideas=(
            "White resolves the tension at once, leaving Black with an isolated "
            "queenside structure and a symmetrical centre. The Carlsbad formation "
            "gives White a clear plan - the minority attack - and Black a clear "
            "counter-plan on the kingside."
        ),
        plans=(
            "White: play b4-b5 to create a weakness on c6, then pile on it.",
            "White: trade the light bishop with Bxf6 or use Ne5 to control the centre.",
            "Black: attack on the kingside with ...Ne4, ...f5 and ...Qf6.",
            "Black: use the e4 square for a knight and aim at the d4 pawn.",
        ),
        watch_out="Symmetry does not mean a draw: whoever executes their plan first is usually better.",
    ),
    Opening(
        eco="D10",
        name="Slav Defense",
        family="Queen's Gambit",
        side="black",
        level="club",
        moves=("d4", "d5", "c4", "c6", "Nf3", "Nf6", "Nc3", "dxc4", "a4", "Bf5", "e3", "e6", "Bxc4", "Bb4", "O-O"),
        ideas=(
            "Black defends d5 with ...c6 and develops the light bishop before closing "
            "the centre - the Caro-Kann idea against the Queen's Gambit. White regains "
            "the c4 pawn with a4 and Bxc4, and the game turns on the b4 pin and the "
            "fight for e4."
        ),
        plans=(
            "White: play Qe2 and e4 to seize the centre after development.",
            "White: use the a-file and the bishop pair against the b4 pin.",
            "Black: develop with ...Nbd7, ...O-O and ...Rc8, then play ...c5.",
            "Black: keep the bishop active with ...Bg4 or ...Bf5 and pressure e4.",
        ),
        watch_out="The c4 pawn cannot be held forever; returning it at the right moment is normal.",
    ),
    Opening(
        eco="E20",
        name="Nimzo-Indian Defense",
        family="Indian Defense",
        side="black",
        level="club",
        moves=("d4", "Nf6", "c4", "e6", "Nc3", "Bb4", "e3", "O-O", "Bd3", "d5", "Nf3", "c5", "O-O", "Nc6", "a3", "Bxc3", "bxc3"),
        ideas=(
            "Black pins the c3 knight to fight for e4 with pieces rather than pawns. "
            "The trade on c3 gives White doubled pawns and the bishop pair: White gets "
            "the two bishops, Black gets the squares. The Nimzo is the most reliable "
            "answer to 1.d4 for a reason."
        ),
        plans=(
            "White: use the bishop pair and play for e4 with Qe2 and Rd1.",
            "White: expand on the queenside with a3, bxc3 and c4-c5 or Rb1.",
            "Black: blockade c4 and e4 with ...d5, ...b6 and ...Bb7.",
            "Black: aim for ...c5 and ...Ne4, trading pieces to expose the doubled pawns.",
        ),
        watch_out="Do not release the pin too early unless the structure you get is what you want.",
    ),
    Opening(
        eco="D85",
        name="Grünfeld Defense: Exchange",
        family="Grünfeld Defense",
        side="black",
        level="advanced",
        moves=("d4", "Nf6", "c4", "g6", "Nc3", "d5", "cxd5", "Nxd5", "e4", "Nxc3", "bxc3", "Bg7", "Bc4", "c5", "Ne2", "Nc6", "Be3", "O-O", "O-O"),
        ideas=(
            "Black lets White build a huge pawn centre, then attacks it with pieces "
            "and the g7 bishop. The Exchange Variation is the main line: White gets "
            "space and the c4 bishop; Black gets pressure on d4 and the long diagonal."
        ),
        plans=(
            "White: defend d4 and expand with c4-c5 or e5 at the right moment.",
            "White: use the c4 bishop and the passed b-pawn potential.",
            "Black: pile on d4 with ...c5, ...Qa5 and ...Rd8.",
            "Black: trade the dark bishop or use ...Bg4 to increase the pressure.",
        ),
        watch_out="The d4 pawn is the whole position; if it falls, Black's structure problems vanish.",
    ),
    Opening(
        eco="A70",
        name="Benoni Defense",
        family="Benoni",
        side="black",
        level="advanced",
        moves=("d4", "Nf6", "c4", "e6", "Nf3", "c5", "d5", "exd5", "cxd5", "d6", "Nc3", "g6", "e4", "Bg7", "Be2", "O-O"),
        ideas=(
            "Black accepts a cramped, isolated d6 pawn in exchange for the g7 bishop, "
            "the e5 outpost and play on the queenside. White gets a passed d5 pawn and "
            "the centre. The Benoni is unbalanced by design."
        ),
        plans=(
            "White: defend d5 and push e5 or use the d5 pawn as a wedge.",
            "White: play on the kingside where Black has less space.",
            "Black: play ...Re8, ...Na6-c7 and ...b5 to attack d5 and queenside.",
            "Black: use the e5 square and the long diagonal for the bishop.",
        ),
        watch_out="The d6 pawn is weak; Black needs activity before White simplifies.",
    ),
    Opening(
        eco="A87",
        name="Dutch Defense: Leningrad",
        family="Dutch Defense",
        side="black",
        level="club",
        moves=("d4", "f5", "g3", "Nf6", "Bg2", "g6", "Nf3", "Bg7", "O-O", "O-O", "c4", "d6", "Nc3", "Qe8"),
        ideas=(
            "Black plays the Dutch against the grain of the centre: ...f5 grabs space "
            "and prepares a kingside attack, while the fianchetto covers the dark "
            "squares that ...f5 weakens. White gets the centre and the e4 square."
        ),
        plans=(
            "White: play d5 and e4 to open the centre while Black is committed kingside.",
            "White: use the e6 hole and the queenside for counterplay.",
            "Black: play ...e5 to challenge the centre and free the bishop.",
            "Black: attack with ...Qh5, ...Rf6 and ...g5 when the centre is closed.",
        ),
        watch_out="The e6 and e5 holes are real; if Black never plays ...e5, White's space tells.",
    ),
    Opening(
        eco="E01",
        name="Catalan Opening",
        family="Catalan",
        side="white",
        level="club",
        moves=("d4", "Nf6", "c4", "e6", "g3", "d5", "Bg2", "Be7", "Nf3", "O-O", "O-O", "Nbd7", "Qc2", "c6", "Nbd2", "b6"),
        ideas=(
            "White combines the Queen's Gambit with a fianchetto, so the g2 bishop "
            "pressures the queenside for the whole game. Black gets a solid centre but "
            "must solve the problem of the b7 and c6 squares. Positional pressure, not "
            "tactics, is the point."
        ),
        plans=(
            "White: play b3, Bb2 and Rc1, then cxd5 or e4.",
            "White: keep the light bishop and attack the b7/a8 diagonal.",
            "Black: free the game with ...dxc4 and ...b5, or ...c5 and ...Bb7.",
            "Black: trade the c4 bishop or block the diagonal with ...b6 and ...Bb7.",
        ),
        watch_out="White's edge is small and slow; without a queenside plan it can evaporate.",
    ),
    Opening(
        eco="D02",
        name="London System",
        family="Queen's Pawn",
        side="white",
        level="beginner",
        moves=("d4", "d5", "Nf3", "Nf6", "Bf4", "c5", "e3", "Nc6", "c3", "e6", "Nbd2", "Bd6", "Bg3", "O-O"),
        ideas=(
            "White develops the dark bishop outside the pawn chain and builds a "
            "compact, hard-to-break setup. The plan is simple and repeatable: e3, c3, "
            "Bd3, Nbd2, then a central or kingside push. Black's job is to find "
            "activity before White's space tells."
        ),
        plans=(
            "White: play Bd3, O-O and Ne5, then f4 or e4.",
            "White: use the c-file and the b1-h7 diagonal for a kingside attack.",
            "Black: hit the centre with ...cxd4 or ...Bf5 and ...Qb6.",
            "Black: trade the strong dark bishop with ...Bf5 and ...Bxd3.",
        ),
        watch_out="The London can drift into passivity; a plan without a pawn break is just decoration.",
    ),
    Opening(
        eco="A45",
        name="Trompowsky Attack",
        family="Queen's Pawn",
        side="white",
        level="beginner",
        moves=("d4", "Nf6", "Bg5", "e6", "e4", "h6", "Bxf6", "Qxf6", "Nc3", "d6", "Qd2", "g6"),
        ideas=(
            "White develops the bishop to g5 on move two, ready to double Black's "
            "pawns or disrupt the knight. Black usually takes on f6 and gets the "
            "bishop pair, while White gets a big centre and a space advantage."
        ),
        plans=(
            "White: play e4 and O-O-O, then attack on the kingside.",
            "White: use the half-open f-file and the space advantage.",
            "Black: use the bishop pair and hit the centre with ...c5.",
            "Black: keep the queen safe on f6, then play ...d6 and ...Nd7.",
        ),
        watch_out="Trading on f6 helps Black's structure; do it only when the doubled pawns really hurt.",
    ),

    # ------------------------------------------------------------ flank
    Opening(
        eco="A29",
        name="English Opening: Four Knights",
        family="English Opening",
        side="white",
        level="club",
        moves=("c4", "e5", "Nc3", "Nf6", "Nf3", "Nc6", "g3", "d5", "cxd5", "Nxd5", "Bg2", "Nb6", "O-O", "Be7"),
        ideas=(
            "A reversed Sicilian. White plays on the c-file and the long diagonal, "
            "treating the position as a Sicilian with an extra tempo. Black gets easy "
            "development but must find a way to use the e5 pawn actively."
        ),
        plans=(
            "White: play a3, Rb1 and b4 for a queenside bind, or d4 to open the centre.",
            "White: keep the tension with d3 and Nd2, then reroute toward e4.",
            "Black: play ...Be6, ...Qd7 and ...Rd8 to pressure the d-file.",
            "Black: strike with ...e4 or ...d4 when the timing favours a central break.",
        ),
        watch_out="The reversed-Sicilian comparison is a guide, not a rule: White is a tempo up, not a plan up.",
    ),
    Opening(
        eco="A30",
        name="English Opening: Symmetrical",
        family="English Opening",
        side="white",
        level="club",
        moves=("c4", "c5", "Nf3", "Nf6", "Nc3", "Nc6", "g3", "g6", "Bg2", "Bg7", "O-O", "O-O", "d4", "cxd4", "Nxd4"),
        ideas=(
            "Both sides fianchetto and fight for the d4/d5 squares. The symmetrical "
            "structure means small differences matter: the first player to occupy the "
            "long diagonal or the d-file usually gets the initiative."
        ),
        plans=(
            "White: play d4 at the right moment and use the d-file.",
            "White: use the extra tempo to pressure b7 or the queenside.",
            "Black: mirror White's setup, then break with ...d5 or ...b5.",
            "Black: use the ...Nd4 and ...Ne5 outposts after the structure opens.",
        ),
        watch_out="Mirroring for too long hands White the first useful break; Black needs a plan of their own.",
    ),
    Opening(
        eco="A09",
        name="Réti Opening",
        family="Réti",
        side="white",
        level="club",
        moves=("Nf3", "d5", "c4", "e6", "g3", "Nf6", "Bg2", "Be7", "O-O", "O-O", "b3", "c5", "Bb2", "Nc6"),
        ideas=(
            "White starts with a knight and a queenside fianchetto, treating the "
            "centre as something to control from a distance. The setup is flexible: "
            "it can become a Catalan, a Queen's Gambit or a kingside attack."
        ),
        plans=(
            "White: play cxd5 or d4 once Black commits, choosing the structure.",
            "White: use the b2 bishop and the e5/d4 squares for pressure.",
            "Black: occupy the centre with ...d5, ...c5 and ...Nc6.",
            "Black: avoid overextending; the hypermodern setup punishes targets.",
        ),
        watch_out="Flexibility cuts both ways: without a concrete plan White can end up passively placed.",
    ),
    Opening(
        eco="B01",
        name="Scandinavian Defense",
        family="Scandinavian",
        side="black",
        level="beginner",
        moves=("e4", "d5", "exd5", "Qxd5", "Nc3", "Qa5", "d4", "Nf6", "Nf3", "c6", "Bc4", "Bf5"),
        ideas=(
            "Black challenges the centre on move one and accepts a queen on the road. "
            "The queen on a5 is safe enough, but every White developing move comes "
            "with a tempo. Black gets a sound structure and a clear plan: ...c6, "
            "development, then ...e6 or ...e5."
        ),
        plans=(
            "White: develop with tempo and use the d4 pawn to gain space.",
            "White: play Bd2 and Rc1 to harass the queen on a5.",
            "Black: play ...c6 and ...Bf5, then ...e6 and ...Nbd7.",
            "Black: use the c8 bishop before ...e6 closes it in.",
        ),
        watch_out="The early queen can be a target; Black must not lose time moving it again and again.",
    ),

    # ------------------------------------------------------------ hypermodern
    Opening(
        eco="E97",
        name="King's Indian Defense: Mar del Plata",
        family="King's Indian Defense",
        side="black",
        level="advanced",
        moves=("d4", "Nf6", "c4", "g6", "Nc3", "Bg7", "e4", "d6", "Nf3", "O-O", "Be2", "e5", "O-O", "Nc6", "d5", "Ne7"),
        ideas=(
            "Black concedes the centre, then attacks it. The g7 bishop and the e5/f5 "
            "pawn duo are the heart of the system. White closes the centre with d5, "
            "which buys time for a queenside expansion but hands Black a clear "
            "kingside target."
        ),
        plans=(
            "Black: play ...f5, ...fxe4 and ...Nf6-g6-h4 to build a kingside attack.",
            "Black: use ...a5 and ...Na6-c5 to fight for the queenside dark squares.",
            "White: expand with c5 and b4 on the queenside, aiming at the d6/e5 chain.",
            "White: exchange the dark-squared bishop with Be3 and Bf2 or Bh6.",
        ),
        watch_out="Black's kingside attack can be faster than it looks; count tempi before opening the queenside.",
    ),
    Opening(
        eco="B04",
        name="Alekhine Defense",
        family="Alekhine Defense",
        side="black",
        level="club",
        moves=("e4", "Nf6", "e5", "Nd5", "d4", "d6", "Nf3", "g6", "Bc4", "Nb6", "Bb3", "Bg7", "O-O", "O-O"),
        ideas=(
            "Black invites White to overextend, then hits the pawn chain with ...d6 "
            "and piece pressure. The knights are mobile and the g7 bishop is strong, "
            "but White gets a big centre and a lead in space if Black is careless."
        ),
        plans=(
            "White: support the centre with c4 and Be3, then squeeze.",
            "White: avoid chasing the knight at the cost of development.",
            "Black: undermine e5 with ...d6, ...dxe5 and ...Nc6.",
            "Black: use the b6 knight and the c4 square for counterplay.",
        ),
        watch_out="The knight tour takes time; if White develops calmly, Black can end up cramped.",
    ),
    Opening(
        eco="B07",
        name="Pirc Defense",
        family="Pirc Defense",
        side="black",
        level="club",
        moves=("e4", "d6", "d4", "Nf6", "Nc3", "g6", "Be3", "Bg7", "Qd2", "O-O", "O-O-O", "c6", "f3", "b5"),
        ideas=(
            "Black lets White build the centre, then attacks it with the fianchetto "
            "bishop and pawn breaks. The Austrian Attack (f4) is White's sharpest "
            "try; the classical setup with Be3 and Qd2 is a slower race."
        ),
        plans=(
            "White: castle queenside and storm the kingside with h4-h5.",
            "White: use the e5/d5 breaks to open lines in the centre.",
            "Black: play ...c5 or ...e5 against the centre, then use the long diagonal.",
            "Black: develop with ...Nbd7, ...Re8 and ...c6, waiting for the right break.",
        ),
        watch_out="Black is passive until a break happens; without ...c5 or ...e5 the bishop on g7 stares at a wall.",
    ),
)


__all__ = ["Opening", "OPENINGS"]
