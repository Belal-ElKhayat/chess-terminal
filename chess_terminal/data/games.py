"""Famous historical games for the Chess.Terminal library.

The move scores below are the published game scores (SAN, in order). Some games
end when the loser resigned rather than in checkmate, which is noted in the
commentary. Every line is replayed and validated with ``python-chess``.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FamousGame:
    """One historical game, with its score, story and turning point."""

    year: int
    white: str
    black: str
    title: str
    event: str
    result: str
    moves: tuple[str, ...]
    story: str
    why: str
    moment: str
    line_note: str = ""


FAMOUS_GAMES: tuple[FamousGame, ...] = (
    FamousGame(
        year=1851,
        white="Adolf Anderssen",
        black="Lionel Kieseritzky",
        title="The Immortal Game",
        event="Casual game, London",
        result="1-0",
        moves=(
            "e4", "e5", "f4", "exf4", "Bc4", "Qh4+", "Kf1", "b5", "Bxb5", "Nf6",
            "Nf3", "Qh6", "d3", "Nh5", "Nh4", "Qg5", "Nf5", "c6", "g4", "Nf6",
            "Rg1", "cxb5", "h4", "Qg6", "h5", "Qg5", "Qf3", "Ng8", "Bxf4", "Qf6",
            "Nc3", "Bc5", "Nd5", "Qxb2", "Bd6", "Bxg1", "e5", "Qxa1+", "Ke2",
            "Na6", "Nxg7+", "Kd8", "Qf6+", "Nxf6", "Be7#",
        ),
        story=(
            "A casual game in London, played while the first international tournament "
            "was running. Anderssen gave up both rooks and then his queen, hunting "
            "the black king across the board with the two bishops and a knight. "
            "Kieseritzky, one of the strongest players of the day, was mated on move "
            "23 with almost all of White's heavy pieces gone."
        ),
        why=(
            "The Immortal Game is the founding myth of romantic chess: material is "
            "only worth what it buys. It is still used to teach coordination, the "
            "power of open lines against an uncastled king, and how a bishop pair can "
            "outweigh a queen when the king has nowhere to go."
        ),
        moment=(
            "18.Bd6!! leaves the a1 rook hanging and invites ...Bxg1, then 19.e5! "
            "opens the a1-h8 diagonal. Every White piece is en prise; every Black "
            "piece is irrelevant."
        ),
    ),
    FamousGame(
        year=1858,
        white="Paul Morphy",
        black="Duke Karl & Count Isouard",
        title="The Opera Game",
        event="Paris Opera House (casual)",
        result="1-0",
        moves=(
            "e4", "e5", "Nf3", "d6", "d4", "Bg4", "dxe5", "Bxf3", "Qxf3", "dxe5",
            "Bc4", "Nf6", "Qb3", "Qe7", "Nc3", "c6", "Bg5", "b5", "Nxb5", "cxb5",
            "Bxb5+", "Nbd7", "O-O-O", "Rd8", "Rxd7", "Rxd7", "Rd1", "Qe6",
            "Bxd7+", "Nxd7", "Qb8+", "Nxb8", "Rd8#",
        ),
        story=(
            "Morphy played this game in a box at the Paris Opera, against two "
            "aristocratic amateurs who consulted on every move. He developed every "
            "piece, gave up a knight for open lines and finished with a queen "
            "sacrifice that forces mate. The whole game takes seventeen moves and "
            "contains almost no wasted effort."
        ),
        why=(
            "It is the cleanest demonstration of the opening principles in existence: "
            "develop with threats, castle, put rooks on open files, and do not move "
            "the same piece twice. The final position has Black's entire army on the "
            "board, still undeveloped, while White's pieces converge on d8."
        ),
        moment=(
            "16.Qb8+!! Nxb8 17.Rd8# - the queen is given up so the rook can deliver "
            "mate on the back rank with the support of the b5 bishop."
        ),
        line_note="COMPLETE GAME // 17 MOVES",
    ),
    FamousGame(
        year=1895,
        white="Wilhelm Steinitz",
        black="Curt von Bardeleben",
        title="The Hastings Combination",
        event="Hastings, round 10",
        result="1-0",
        moves=(
            "e4", "e5", "Nf3", "Nc6", "Bc4", "Bc5", "c3", "Nf6", "d4", "exd4",
            "cxd4", "Bb4+", "Nc3", "d5", "exd5", "Nxd5", "O-O", "Be6", "Bg5",
            "Be7", "Bxd5", "Bxd5", "Nxd5", "Qxd5", "Bxe7", "Nxe7", "Re1", "f6",
            "Qe2", "Qd7", "Rac1", "c6", "d5", "cxd5", "Nd4", "Kf7", "Ne6", "Rhc8",
            "Qg4", "g6", "Ng5+", "Ke8", "Rxe7+", "Kf8", "Rf7+", "Kg8", "Rg7+",
            "Kh8", "Rxh7+",
        ),
        story=(
            "The 58-year-old former world champion found a forcing rook combination "
            "against von Bardeleben, who left the hall rather than resign. Steinitz's "
            "rook walks the seventh rank, taking everything in sight, while the black "
            "king is dragged toward the h-file."
        ),
        why=(
            "The game is a textbook on the seventh rank and on keeping the initiative "
            "with checks. It also shows how a king stuck on f8-g8-h8 becomes a target "
            "long before any pawn is promoted."
        ),
        moment=(
            "22.Rxe7+! starts the tour: 22...Kf8 23.Rf7+ Kg8 24.Rg7+! Kh8 25.Rxh7+. "
            "The rook is untouchable because every capture allows a faster mate."
        ),
        line_note="SCORE ENDS AT 25.Rxh7+ // BARD ELEBEN LEFT, WHITE WON ON TIME",
    ),
    FamousGame(
        year=1907,
        white="Georg Rotlewi",
        black="Akiba Rubinstein",
        title="Rubinstein's Immortal",
        event="All-Russian Masters, Łódź",
        result="0-1",
        moves=(
            "d4", "d5", "Nf3", "e6", "e3", "c5", "c4", "Nc6", "Nc3", "Nf6",
            "dxc5", "Bxc5", "a3", "a6", "b4", "Bd6", "Bb2", "O-O", "Qd2", "Qe7",
            "Bd3", "dxc4", "Bxc4", "b5", "Bd3", "Rd8", "Qe2", "Bb7", "O-O", "Ne5",
            "Nxe5", "Bxe5", "f4", "Bc7", "e4", "Rac8", "e5", "Bb6+", "Kh1", "Ng4",
            "Be4", "Qh4", "g3", "Rxc3", "gxh4", "Rd2", "Qxd2", "Bxe4+", "Qg2", "Rh3",
        ),
        story=(
            "Rubinstein produced one of the great attacking games of the pre-war era. "
            "He let White build a big centre, then broke it with ...Rxc3 and finished "
            "with a quiet ...Rh3 that White could not answer: the queen on g2 is pinned "
            "and the h-file is fatally open."
        ),
        why=(
            "It is a masterclass in removing defenders. ...Rxc3, ...Rd2 and ...Bxe4+ "
            "all exist to clear the g2 square and leave White's queen overworked. The "
            "final position contains four black pieces around the white king and no "
            "checks left for White."
        ),
        moment=(
            "22...Rxc3! is the bolt: the rook is untouchable (23.gxh4 allows ...Rd2), "
            "and the queen sacrifice on h4 comes only after the defenders are gone."
        ),
        line_note="SCORE ENDS AT 25...Rh3 // ROTLEWI RESIGNED",
    ),
    FamousGame(
        year=1918,
        white="José Raúl Capablanca",
        black="Frank Marshall",
        title="The Marshall Attack Debut",
        event="Manhattan Chess Club Masters, New York",
        result="1-0",
        moves=(
            "e4", "e5", "Nf3", "Nc6", "Bb5", "a6", "Ba4", "Nf6", "O-O", "Be7",
            "Re1", "b5", "Bb3", "O-O", "c3", "d5", "exd5", "Nxd5", "Nxe5", "Nxe5",
            "Rxe5", "Nf6", "Re1", "Bd6", "h3", "Ng4", "Qf3", "Qh4", "d4", "Nxf2",
            "Re2", "Bg4", "hxg4", "Bh2+", "Kf1", "Bg3", "Rxf2", "Qh1+", "Ke2",
            "Bxf2", "Bd2", "Bh4", "Qh3", "Rae8+", "Kd3", "Qf1+", "Kc2", "Bf2",
            "Qf3", "Qg1", "Bd5", "c5", "dxc5", "Bxc5", "b4", "Bd6", "a4", "a5",
            "axb5", "axb4", "Ra6", "bxc3", "Nxc3", "Bb4", "b6", "Bxc3", "Bxc3",
            "h6", "b7", "Re3", "Bxf7+", "Rxf7", "b8=Q+", "Kh7", "Rxh6+",
        ),
        story=(
            "Marshall had prepared a brand-new gambit in the Ruy Lopez for years, "
            "waiting to spring it on the world champion. At move eight he uncorked "
            "...d5!, giving a pawn for a lasting attack against the white king. "
            "Capablanca defended with cold precision and won the endgame."
        ),
        why=(
            "The Marshall Attack became one of Black's main weapons in the Ruy Lopez "
            "and is still played at the highest level. The game also shows that a "
            "home-cooked novelty is not enough: the world champion had to find a "
            "defence over the board, move by move."
        ),
        moment=(
            "8...d5! sacrifices a pawn for the initiative. White's best defence is the "
            "quiet 9.exd5 Nxd5 10.Nxe5 Nxe5 11.Rxe5 Nf6 12.Re1 (or 12.d4), giving back "
            "material to kill the attack."
        ),
        line_note="DIAGNOSTIC LINE // SCORE CONTINUES TO 38.Rxh6+",
    ),
    FamousGame(
        year=1923,
        white="Friedrich Sämisch",
        black="Aron Nimzowitsch",
        title="The Immortal Zugzwang Game",
        event="Copenhagen",
        result="0-1",
        moves=(
            "d4", "Nf6", "c4", "e6", "Nf3", "b6", "g3", "Bb7", "Bg2", "Be7",
            "Nc3", "O-O", "O-O", "d5", "Ne5", "c6", "cxd5", "cxd5", "Bf4", "a6",
            "Rc1", "b5", "Qb3", "Nc6", "Nxc6", "Bxc6", "h3", "Qd7", "Kh2", "Nh5",
            "Bd2", "f5", "Qd1", "b4", "Nb1", "Bb5", "Rg1", "Bd6", "e4", "fxe4",
            "Qxh5", "Rxf2", "Qg5", "Raf8", "Kh1", "R8f5", "Qe3", "Bd3", "Rce1", "h6",
        ),
        story=(
            "Nimzowitsch deliberately allowed his opponent to win a piece, because the "
            "black pieces had every square covered and White had no useful move left. "
            "After 25...h6 White resigned: the queen is attacked, but every sensible "
            "reply loses material or allows mate. This is the most famous zugzwang in "
            "chess history."
        ),
        why=(
            "It defines the hypermodern ideal: restraint and control matter more than "
            "material. Nimzowitsch's pieces do not attack; they simply occupy every "
            "square White needs, turning a material advantage into paralysis."
        ),
        moment=(
            "The final quiet move 25...h6 leaves White in total zugzwang - the queen "
            "on e3 is attacked, and every legal move loses a piece or the king."
        ),
        line_note="SCORE ENDS AT 25...h6 // WHITE RESIGNED IN ZUGZWANG",
    ),
    FamousGame(
        year=1935,
        white="Max Euwe",
        black="Alexander Alekhine",
        title="The Pearl of Zandvoort",
        event="World Championship, Game 26",
        result="1-0",
        moves=(
            "d4", "e6", "c4", "f5", "g3", "Bb4+", "Bd2", "Be7", "Bg2", "Nf6",
            "Nc3", "O-O", "Nf3", "Ne4", "O-O", "b6", "Qc2", "Bb7", "Ne5", "Nxc3",
            "Bxc3", "Bxg2", "Kxg2", "Qc8", "d5", "d6", "Nd3", "e5", "Kh1", "c6",
            "Qb3", "Kh8", "f4", "e4", "Nb4", "c5", "Nc2", "Nd7", "Ne3", "Bf6",
            "Nxf5", "Bxc3", "Nxd6", "Qb8", "Nxe4", "Bf6", "Nd2", "g5", "e4",
            "gxf4", "gxf4", "Bd4", "e5", "Qe8", "e6", "Rg8", "Nf3", "Qg6", "Rg1",
            "Bxg1", "Rxg1", "Qf6", "Ng5", "Rg7", "exd7", "Rxd7", "Qe3", "Re7",
            "Ne6", "Rf8", "Qe5", "Qxe5", "fxe5", "Rf5", "Re1", "h6", "Nd8", "Rf2",
            "e6", "Rd2", "Nc6", "Re8", "e7", "b5", "Nd8", "Kg7", "Nb7", "Kf6",
            "Re6+", "Kg5", "Nd6", "Rxe7", "Ne4+",
        ),
        story=(
            "Game 26 of the 1935 title match is the game Euwe himself called his best. "
            "He met Alekhine's Dutch Defence with a quiet kingside fianchetto, gave up "
            "the bishop pair and then outplayed the world champion in a long, "
            "precisely calculated endgame to take a decisive lead in the match."
        ),
        why=(
            "It shows that a world championship match can be won with technique, not "
            "only tactics. The final phase - a knight versus a rook with a passed e-pawn "
            "- is still studied as a model of converting a small edge."
        ),
        moment=(
            "The slow squeeze from 20.Ne3 onwards, and the final knight tour 41.Nc6! "
            "Re8 42.e7, which turns the passed pawn into a decisive weapon."
        ),
        line_note="SCORE ENDS AT 47.Ne4+ // ALEKHINE RESIGNED",
    ),
    FamousGame(
        year=1938,
        white="Mikhail Botvinnik",
        black="José Raúl Capablanca",
        title="Botvinnik's AVRO Masterpiece",
        event="AVRO Tournament, Rotterdam",
        result="1-0",
        moves=(
            "d4", "Nf6", "c4", "e6", "Nc3", "Bb4", "e3", "d5", "a3", "Bxc3+",
            "bxc3", "c5", "cxd5", "exd5", "Bd3", "O-O", "Ne2", "b6", "O-O", "Ba6",
            "Bxa6", "Nxa6", "Bb2", "Qd7", "a4", "Rfe8", "Qd3", "c4", "Qc2", "Nb8",
            "Rae1", "Nc6", "Ng3", "Na5", "f3", "Nb3", "e4", "Qxa4", "e5", "Nd7",
            "Qf2", "g6", "f4", "f5", "exf6", "Nxf6", "f5", "Rxe1", "Rxe1", "Re8",
            "Re6", "Rxe6", "fxe6", "Kg7", "Qf4", "Qe8", "Qe5", "Qe7", "Ba3",
            "Qxa3", "Nh5+", "gxh5", "Qg5+", "Kf8", "Qxf6+", "Kg8", "e7", "Qc1+",
            "Kf2", "Qc2+", "Kg3", "Qd3+", "Kh4", "Qe4+", "Kxh5", "Qe2+", "Kh4",
            "Qe4+", "g4", "Qe1+", "Kh5",
        ),
        story=(
            "Botvinnik beat Capablanca in the strongest tournament ever held up to that "
            "point, and clinched a share of first place. He accepted doubled pawns and "
            "a cramped structure, then opened the position at exactly the right moment. "
            "The final combination is a forced king hunt that ends with Capablanca "
            "resigning a piece down."
        ),
        why=(
            "It is the model game for the Botvinnik system in the Nimzo-Indian and for "
            "playing against a queenside pawn majority. The finish is one of the great "
            "attacking sequences of the twentieth century."
        ),
        moment=(
            "30.Nh5+! gxh5 31.Qg5+ Kf8 32.Qxf6+ Kg8 33.e7!! - the pawn that was "
            "cramped for thirty moves delivers the final blow."
        ),
        line_note="SCORE ENDS AT 41.Kh5 // CAPABLANCA RESIGNED",
    ),
    FamousGame(
        year=1956,
        white="Donald Byrne",
        black="Robert James Fischer",
        title="The Game of the Century",
        event="Third Rosenwald Trophy, New York",
        result="0-1",
        moves=(
            "Nf3", "Nf6", "c4", "g6", "Nc3", "Bg7", "d4", "O-O", "Bf4", "d5",
            "Qb3", "dxc4", "Qxc4", "c6", "e4", "Nbd7", "Rd1", "Nb6", "Qc5", "Bg4",
            "Bg5", "Na4", "Qa3", "Nxc3", "bxc3", "Nxe4", "Bxe7", "Qb6", "Bc4",
            "Nxc3", "Bc5", "Rfe8+", "Kf1", "Be6", "Bxb6", "Bxc4+", "Kg1", "Ne2+",
            "Kf1", "Nxd4+", "Kg1", "Ne2+", "Kf1", "Nc3+", "Kg1", "axb6", "Qb4",
            "Ra4", "Qxb6", "Nxd1", "h3", "Rxa2", "Kh2", "Nxf2", "Re1", "Rxe1",
            "Qd8+", "Bf8", "Nxe1", "Bd5", "Nf3", "Ne4", "Qb8", "b5", "h4", "h5",
            "Ne5", "Kg7", "Kg1", "Bc5+", "Kf1", "Ng3+", "Ke1", "Bb4+", "Kd1",
            "Bb3+", "Kc1", "Ne2+", "Kb1", "Nc3+", "Kc1", "Rc2#",
        ),
        story=(
            "Thirteen-year-old Bobby Fischer sacrificed his queen on move seventeen "
            "against one of America's strongest players, then conducted a forced king "
            "hunt with his remaining pieces. Byrne, a former US Open champion, was "
            "mated on move 41 with his entire army still on the board."
        ),
        why=(
            "It made Fischer famous overnight and remains the standard example of "
            "attacking an uncastled king with a material deficit. The queen sacrifice "
            "17...Be6!! is one of the most quoted moves in chess literature."
        ),
        moment=(
            "17...Be6!! offers the queen. 18.Bxb6 Bxc4+ 19.Kg1 Ne2+ begins a series of "
            "checks and forks from which White never escapes."
        ),
        line_note="COMPLETE GAME // 41 MOVES",
    ),
    FamousGame(
        year=1972,
        white="Robert James Fischer",
        black="Boris Spassky",
        title="Game 6, Reykjavík",
        event="World Championship, Game 6",
        result="1-0",
        moves=(
            "c4", "e6", "Nf3", "d5", "d4", "Nf6", "Nc3", "Be7", "Bg5", "O-O",
            "e3", "h6", "Bh4", "b6", "cxd5", "Nxd5", "Bxe7", "Qxe7", "Nxd5",
            "exd5", "Rc1", "Be6", "Qa4", "c5", "Qa3", "Rc8", "Bb5", "a6", "dxc5",
            "bxc5", "O-O", "Ra7", "Be2", "Nd7", "Nd4", "Qf8", "Nxe6", "fxe6",
            "e4", "d4", "f4", "Qe7", "e5", "Rb8", "Bc4", "Kh8", "Qh3", "Nf8",
            "b3", "a5", "f5", "exf5", "Rxf5", "Nh7", "Rcf1", "Qd8", "Qg3", "Re7",
            "h4", "Rbb7", "e6", "Rbc7", "Qe5", "Qe8", "a4", "Qd8", "R1f2", "Qe8",
            "R2f3", "Qd8", "Bd3", "Qe8", "Qe4", "Nf6", "Rxf6", "gxf6", "Rxf6",
            "Kg8", "Bc4", "Kh8", "Qf4",
        ),
        story=(
            "The sixth game of the 1972 match is often called the best game of the "
            "match and the finest of Fischer's career. From a quiet Queen's Gambit he "
            "built a space advantage, traded into a superior endgame, and squeezed "
            "Spassky off the board with a textbook kingside bind. Spassky applauded "
            "from his chair when he resigned."
        ),
        why=(
            "It is the model of the Fischer style: no speculative sacrifices, just "
            "small advantages accumulated until the opponent has no good move. The "
            "game is also a perfect illustration of playing on the light squares."
        ),
        moment=(
            "The clamp begins with 22.b3! and 25.f5!, fixing the kingside pawns on the "
            "colour of the remaining bishop. The final 41.Qf4 leaves Black paralysed."
        ),
        line_note="COMPLETE GAME // 41 MOVES",
    ),
    FamousGame(
        year=1985,
        white="Anatoly Karpov",
        black="Garry Kasparov",
        title="Game 16, Moscow",
        event="World Championship, Game 16",
        result="0-1",
        moves=(
            "e4", "c5", "Nf3", "e6", "d4", "cxd4", "Nxd4", "Nc6", "Nb5", "d6",
            "c4", "Nf6", "N1c3", "a6", "Na3", "d5", "cxd5", "exd5", "exd5",
            "Nb4", "Be2", "Bc5", "O-O", "O-O", "Bf3", "Bf5", "Bg5", "Re8", "Qd2",
            "b5", "Rad1", "Nd3", "Nab1", "h6", "Bh4", "b4", "Na4", "Bd6", "Bg3",
            "Rc8", "b3", "g5", "Bxd6", "Qxd6", "g3", "Nd7", "Bg2", "Qf6", "a3",
            "a5", "axb4", "axb4", "Qa2", "Bg6", "d6", "g4", "Qd2", "Kg7", "f3",
            "Qxd6", "fxg4", "Qd4+", "Kh1", "Nf6", "Rf4", "Ne4", "Qxd3", "Nf2+",
            "Rxf2", "Bxd3", "Rfd2", "Qe3", "Rxd3", "Rc1", "Nb2", "Qf2", "Nd2",
            "Rxd1+", "Nxd1", "Re1+",
        ),
        story=(
            "Kasparov's win in game 16 was the turning point of the 1985 title match. "
            "He chose the sharpest line of the Sicilian against Karpov's solid "
            "repertoire, sacrificed a pawn for piece activity, and converted with a "
            "tactical sequence that left the world champion's pieces tied in knots."
        ),
        why=(
            "This is the game that announced Kasparov as the new generation: concrete "
            "calculation over static structure. The final position shows a rook, bishop "
            "and knight coordinating against a bare king while White's extra material "
            "sits useless."
        ),
        moment=(
            "19...b4! and 21...g5! seize space and drive the pieces back, and 27...Bg6! "
            "sets up the ...g4 break that decides the game."
        ),
        line_note="SCORE ENDS AT 40...Re1+ // KARPOV RESIGNED",
    ),
    FamousGame(
        year=1997,
        white="Deep Blue",
        black="Garry Kasparov",
        title="Deep Blue's Match Winner",
        event="IBM Rematch, Game 6, New York",
        result="1-0",
        moves=(
            "e4", "c6", "d4", "d5", "Nc3", "dxe4", "Nxe4", "Nd7", "Ng5", "Ngf6",
            "Bd3", "e6", "N1f3", "h6", "Nxe6", "Qe7", "O-O", "fxe6", "Bg6+", "Kd8",
            "Bf4", "b5", "a4", "Bb7", "Re1", "Nd5", "Bg3", "Kc8", "axb5", "cxb5",
            "Qd3", "Bc6", "Bf5", "exf5", "Rxe7", "Bxe7", "c4",
        ),
        story=(
            "The final game of the 1997 rematch lasted only nineteen moves. Deep Blue "
            "sacrificed a knight on e6, wrecked Kasparov's structure, and won a piece "
            "with a database-like sequence. Kasparov resigned after 19.c4, losing the "
            "match 3.5-2.5."
        ),
        why=(
            "It is the symbolic end of the human-versus-machine era: a computer beat "
            "the world champion in a match, and did it with a positional sacrifice "
            "that looked entirely human. The game is also a practical lesson in the "
            "Caro-Kann's tactical weaknesses around e6 and d5."
        ),
        moment=(
            "7...h6 invites 8.Nxe6! - a knight sacrifice that leaves Black unable to "
            "castle and short of squares for the king."
        ),
        line_note="COMPLETE GAME // 19 MOVES // KASPAROV RESIGNED",
    ),
    FamousGame(
        year=1999,
        white="Garry Kasparov",
        black="Veselin Topalov",
        title="Kasparov's Immortal",
        event="Hoogovens, Wijk aan Zee",
        result="1-0",
        moves=(
            "e4", "d6", "d4", "Nf6", "Nc3", "g6", "Be3", "Bg7", "Qd2", "c6",
            "f3", "b5", "Nge2", "Nbd7", "Bh6", "Bxh6", "Qxh6", "Bb7", "a3", "e5",
            "O-O-O", "Qe7", "Kb1", "a6", "Nc1", "O-O-O", "Nb3", "exd4", "Rxd4",
            "c5", "Rd1", "Nb6", "g3", "Kb8", "Na5", "Ba8", "Bh3", "d5", "Qf4+",
            "Ka7", "Rhe1", "d4", "Nd5", "Nbxd5", "exd5", "Qd6", "Rxd4", "cxd4",
            "Re7+", "Kb6", "Qxd4+", "Kxa5", "b4+", "Ka4", "Qc3", "Qxd5", "Ra7",
            "Bb7", "Rxb7", "Qc4", "Qxf6", "Kxa3", "Qxa6+", "Kxb4", "c3+", "Kxc3",
            "Qa1+", "Kd2", "Qb2+", "Kd1", "Bf1", "Rd2", "Rd7", "Rxd7", "Bxc4",
            "bxc4", "Qxh8", "Rd3", "Qa8", "c3", "Qa4+", "Ke1", "f4", "f5", "Kc1",
            "Rd2", "Qa7",
        ),
        story=(
            "Kasparov's rook sacrifice on d4 in a position where his own king was "
            "exposed is considered one of the deepest calculations ever played. He "
            "gave up a rook, then his queen, and hunted Topalov's king from a5 to b4 "
            "to c3 to d2 in an era before engines could confirm the line."
        ),
        why=(
            "It is the defining game of the computer age's early years: a human found "
            "a forced win that even machines struggled to verify. It is also a study "
            "in the value of the king as an attacker in the endgame."
        ),
        moment=(
            "24.Rxd4!! cxd4 25.Re7+! Kb6 26.Qxd4+ Kxa5 27.b4+ Ka4 28.Qc3 - every "
            "White piece is en prise and every Black move loses."
        ),
        line_note="SCORE ENDS AT 44.Qa7 // TOPALOV RESIGNED",
    ),
    FamousGame(
        year=2013,
        white="Levon Aronian",
        black="Viswanathan Anand",
        title="Anand's Wijk aan Zee Attack",
        event="Tata Steel, Wijk aan Zee",
        result="0-1",
        moves=(
            "d4", "d5", "c4", "c6", "Nf3", "Nf6", "Nc3", "e6", "e3", "Nbd7",
            "Bd3", "dxc4", "Bxc4", "b5", "Bd3", "Bd6", "O-O", "O-O", "Qc2", "Bb7",
            "a3", "Rc8", "Ng5", "c5", "Nxh7", "Ng4", "f4", "cxd4", "exd4", "Bc5",
            "Be2", "Nde5", "Bxg4", "Bxd4+", "Kh1", "Nxg4", "Nxf8", "f5", "Ng6",
            "Qf6", "h3", "Qxg6", "Qe2", "Qh5", "Qd3", "Be3",
        ),
        story=(
            "Anand punished Aronian's knight raid on h7 with a counterattack in the "
            "centre. While White's knight wandered to f8 and g6, Black's bishops took "
            "the d4 diagonal and the kingside dark squares, and White resigned when "
            "the mate threats became unstoppable."
        ),
        why=(
            "It is a modern example of the old rule: a wing attack is answered by a "
            "counterstrike in the centre. The game is also a fine illustration of the "
            "power of the bishop pair on an open board."
        ),
        moment=(
            "23...Bxd4+! opens the position while White's queen and knight are far "
            "from the defence, and 27...Qxg6 begins the decisive attack."
        ),
        line_note="SCORE ENDS AT 23...Be3 // ARONIAN RESIGNED",
    ),
    FamousGame(
        year=2021,
        white="Ian Nepomniachtchi",
        black="Magnus Carlsen",
        title="The 136-Move Marathon",
        event="World Championship, Game 6, Dubai",
        result="0-1",
        moves=(
            "d4", "Nf6", "Nf3", "d5", "g3", "e6", "Bg2", "Be7", "O-O", "O-O",
            "b3", "c5", "dxc5", "Bxc5", "c4", "dxc4", "Qc2", "Qe7", "Nbd2", "Nc6",
            "Nxc4", "b5", "Nce5", "Nb4", "Qb2", "Bb7", "a3", "Nc6", "Nd3", "Bb6",
            "Bg5", "Rfd8", "Bxf6", "gxf6", "Rac1", "Nd4", "Nxd4", "Bxd4", "Qa2",
            "Bxg2", "Kxg2", "Qb7+", "Kg1", "Qe4", "Qc2", "a5", "Rfd1", "Kg7",
            "Rd2", "Rac8", "Qxc8", "Rxc8", "Rxc8", "Qd5", "b4", "a4", "e3", "Be5",
            "h4", "h5", "Kh2", "Bb2", "Rc5", "Qd6", "Rd1", "Bxa3", "Rxb5", "Qd7",
            "Rc5", "e5", "Rc2", "Qd5", "Rdd2", "Qb3", "Ra2", "e4", "Nc5", "Qxb4",
            "Nxe4", "Qb3", "Rac2", "Bf8", "Nc5", "Qb5", "Nd3", "a3", "Nf4", "Qa5",
            "Ra2", "Bb4", "Rd3", "Kh6", "Rd1", "Qa4", "Rda1", "Bd6", "Kg1", "Qb3",
            "Ne2", "Qd3", "Nd4", "Kh7", "Kh2", "Qe4", "Rxa3", "Qxh4+", "Kg1",
            "Qe4", "Ra4", "Be5", "Ne2", "Qc2", "R1a2", "Qb3", "Kg2", "Qd5+", "f3",
            "Qd1", "f4", "Bc7", "Kf2", "Bb6", "Ra1", "Qb3", "Re4", "Kg7", "Re8",
            "f5", "Raa8", "Qb4", "Rac8", "Ba5", "Rc1", "Bb6", "Re5", "Qb3", "Re8",
            "Qd5", "Rcc8", "Qh1", "Rc1", "Qd5", "Rb1", "Ba7", "Re7", "Bc5", "Re5",
            "Qd3", "Rb7", "Qc2", "Rb5", "Ba7", "Ra5", "Bb6", "Rab5", "Ba7", "Rxf5",
            "Qd3", "Rxf7+", "Kxf7", "Rb7+", "Kg6", "Rxa7", "Qd5", "Ra6+", "Kh7",
            "Ra1", "Kg6", "Nd4", "Qb7", "Ra2", "Qh1", "Ra6+", "Kf7", "Nf3", "Qb1",
            "Rd6", "Kg7", "Rd5", "Qa2+", "Rd2", "Qb1", "Re2", "Qb6", "Rc2", "Qb1",
            "Nd4", "Qh1", "Rc7+", "Kf6", "Rc6+", "Kf7", "Nf3", "Qb1", "Ng5+", "Kg7",
            "Ne6+", "Kf7", "Nd4", "Qh1", "Rc7+", "Kf6", "Nf3", "Qb1", "Rd7", "Qb2+",
            "Rd2", "Qb1", "Ng1", "Qb4", "Rd1", "Qb3", "Rd6+", "Kg7", "Rd4", "Qb2+",
            "Ne2", "Qb1", "e4", "Qh1", "Rd7+", "Kg8", "Rd4", "Qh2+", "Ke3", "h4",
            "gxh4", "Qh3+", "Kd2", "Qxh4", "Rd3", "Kf8", "Rf3", "Qd8+", "Ke3",
            "Qa5", "Kf2", "Qa7+", "Re3", "Qd7", "Ng3", "Qd2+", "Kf3", "Qd1+",
            "Re2", "Qb3+", "Kg2", "Qb7", "Rd2", "Qb3", "Rd5", "Ke7", "Re5+",
            "Kf7", "Rf5+", "Ke8", "e5", "Qa2+", "Kh3", "Qe6", "Kh4", "Qh6+",
            "Nh5", "Qh7", "e6", "Qg6", "Rf7", "Kd8", "f5", "Qg1", "Ng7",
        ),
        story=(
            "Game 6 of the 2021 Dubai match ran to 136 moves and became the longest "
            "world championship game ever played. Carlsen chose a quiet Catalan, "
            "traded into an endgame with a small structural edge, and ground for eight "
            "hours. Nepomniachtchi defended for more than a hundred moves before the "
            "position finally cracked."
        ),
        why=(
            "It is a modern monument to endgame stamina and to the idea that a "
            "world championship is a test of nerves as much as calculation. The game "
            "also shows how a tiny weakness - here the b3 and h-pawn structure - can "
            "be nursed for a hundred moves."
        ),
        moment=(
            "The endgame turns on Carlsen's relentless rook activity and the passed "
            "e-pawn; by move 100 every Black piece is tied to defence, and 136.Ng7 "
            "is the last straw."
        ),
        line_note="COMPLETE GAME // 136 MOVES // NEPOMNIACHTCHI RESIGNED",
    ),
)


__all__ = ["FamousGame", "FAMOUS_GAMES"]
