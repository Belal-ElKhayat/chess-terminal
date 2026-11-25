import chess

from chess_terminal.data import ENTRIES, FAMOUS_GAMES, OPENINGS, REFERENCE_NOTES, TRAPS


def test_all_library_lines_are_legal():
    for entry in ENTRIES:
        entry.validate()  # raises on the first illegal SAN


def test_required_openings_are_present():
    names = " ".join(opening.name.lower() for opening in OPENINGS)
    for required in (
        "sicilian",
        "queen's gambit",
        "ruy lopez",
        "french",
        "king's indian",
    ):
        assert required in names


def test_required_traps_are_present():
    names = {trap.name.lower() for trap in TRAPS}
    for required in (
        "scholar's mate",
        "legal's mate",
        "fried liver attack",
        "stafford gambit",
        "englund gambit trap",
    ):
        assert required in names


def test_openings_have_eco_and_plans():
    for opening in OPENINGS:
        assert opening.eco
        assert opening.ideas
        assert len(opening.plans) >= 2


def test_reference_notes_have_body():
    for note in REFERENCE_NOTES:
        assert note.title
        assert note.body
        assert note.drills


def test_position_at_replays_prefix():
    entry = next(entry for entry in ENTRIES if entry.kind == "opening")
    board = entry.position_at(4)
    assert board.ply() == 4
    assert board.fen() != chess.Board().fen()
    assert entry.position_at(0).fen() == chess.Board().fen()


def test_search_text_includes_sections():
    entry = next(entry for entry in ENTRIES if entry.kind == "trap")
    haystack = entry.search_text()
    assert entry.title.lower() in haystack
    for _, content in entry.sections:
        assert content.split()[0].lower() in haystack


def test_archive_is_deep_enough():
    assert len(OPENINGS) >= 30
    assert len(TRAPS) >= 12
    assert len(FAMOUS_GAMES) >= 15


def test_famous_games_have_scores_and_stories():
    years = {game.year for game in FAMOUS_GAMES}
    assert {1851, 1858, 1956, 1972, 1997, 2021} <= years
    for game in FAMOUS_GAMES:
        assert game.moves
        assert game.story and game.why and game.moment
        assert game.result in ("1-0", "0-1", "1/2-1/2")


def test_library_labels_are_single_line():
    for entry in ENTRIES:
        assert "\n" not in entry.label
        assert entry.label == entry.label.strip()
