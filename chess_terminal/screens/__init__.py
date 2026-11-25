"""Textual screens for Chess.Terminal."""

from .ai_setup import AISetupScreen
from .clock_picker import ClockPickerScreen
from .coach import CoachScreen
from .engine_room import AnalysisScreen, EngineRoomScreen, ScoutScreen
from .friend import FriendScreen
from .game import GameScreen
from .library import LibraryScreen
from .puzzles import PuzzlesScreen
from .result import ResultScreen
from .splash import SplashScreen

__all__ = [
    "SplashScreen",
    "AISetupScreen",
    "FriendScreen",
    "GameScreen",
    "LibraryScreen",
    "ResultScreen",
    "EngineRoomScreen",
    "AnalysisScreen",
    "ScoutScreen",
    "PuzzlesScreen",
    "CoachScreen",
    "ClockPickerScreen",
]
