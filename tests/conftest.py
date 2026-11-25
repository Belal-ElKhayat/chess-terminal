import pytest


@pytest.fixture(autouse=True)
def isolated_home(tmp_path, monkeypatch):
    """Keep session autosaves and PGN exports out of the real home directory."""
    monkeypatch.setenv("CHESS_TERMINAL_HOME", str(tmp_path / "home"))
    yield
