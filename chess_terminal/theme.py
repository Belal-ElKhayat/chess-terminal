"""The phosphor-amber CRT visual identity for Chess.Terminal."""

from __future__ import annotations

BG = "#0D0800"
AMBER = "#FF9900"
BRIGHT = "#FFCC33"
DIM = "#663D00"
INK = "#0D0800"

# Board surfaces, all kept inside the amber phosphor family. The light squares
# carry enough amber that the 8x8 grid stays readable around the small glyphs.
SQ_LIGHT = "#3B2200"
SQ_DARK = "#170D00"
SQ_LAST = "#5A3600"
SQ_TARGET = "#4A2C00"
SQ_CHECK = "#7A4A00"


CSS = f"""
Screen {{
    background: {BG};
    color: {AMBER};
    overflow: hidden;
}}

.telemetry {{
    height: 1;
    background: {AMBER};
    color: {BG};
    padding: 0 1;
    text-style: bold;
}}

.telemetry-dim {{
    height: 1;
    color: {DIM};
    padding: 0 1;
}}

.title {{
    color: {BRIGHT};
    text-style: bold;
}}

.bright {{
    color: {BRIGHT};
}}

.dim {{
    color: {DIM};
}}

.hint {{
    height: 1;
    color: {DIM};
    padding: 0 1;
}}

.panel-title {{
    height: 1;
    color: {BRIGHT};
    text-style: bold;
}}

.panel {{
    border: round {DIM};
    padding: 1 2;
    height: 1fr;
}}

.side {{
    width: 1fr;
    min-width: 36;
    padding: 0 1;
}}

.scroll-log {{
    height: 1fr;
    border: round {DIM};
    padding: 0 1;
}}

Input {{
    background: {BG};
    color: {BRIGHT};
    border: tall {DIM};
    padding: 0 1;
    height: 3;
}}

Input:focus {{
    border: tall {AMBER};
    color: {BRIGHT};
}}

Button {{
    background: {BG};
    color: {AMBER};
    border: tall {DIM};
    min-width: 18;
    height: 3;
    margin: 0 1 0 0;
}}

Button:focus {{
    background: {AMBER};
    color: {BG};
    border: tall {AMBER};
    text-style: bold;
}}

Button.-active {{
    background: {AMBER};
    color: {BG};
}}

KeyboardList {{
    height: auto;
    width: 1fr;
    padding: 0 1;
    color: {AMBER};
}}

KeyboardList:focus {{
    color: {BRIGHT};
}}

BoardView {{
    height: auto;
    width: auto;
    padding: 0 1;
}}

#banner {{
    height: auto;
    width: auto;
    color: {BRIGHT};
    text-align: center;
    text-style: bold;
}}

#splash-center {{
    width: auto;
    height: 1fr;
    align: center middle;
}}

#splash-mid {{
    height: 1fr;
    align: center middle;
}}

#pieces-left, #pieces-right {{
    width: 20;
    height: 1fr;
    color: {DIM};
    text-align: center;
    content-align: center middle;
}}

#menu {{
    width: 52;
    margin-top: 1;
}}

#screen-body {{
    height: 1fr;
    padding: 0 1;
}}

.form-col {{
    width: 1fr;
    padding: 0 2;
}}

.form-col-tight {{
    width: 46;
    padding: 0 1;
}}

.form-col Button, .form-col-tight Button {{
    min-width: 14;
    width: 1fr;
}}

#game-board-col {{
    width: 1fr;
    height: 1fr;
}}

#board-stage {{
    width: 1fr;
    height: 1fr;
    align: center middle;
}}

#board-hint {{
    text-align: center;
}}

#game-side {{
    width: 42;
    height: 1fr;
    padding: 0 1;
}}

#ai-panel {{
    height: auto;
    max-height: 7;
}}

#library-left {{
    width: 54;
    height: 1fr;
    border: round {DIM};
    padding: 0 1;
}}

#library-right {{
    width: 1fr;
    height: 1fr;
    padding: 0 1;
}}

#lib-stage {{
    width: 1fr;
    height: auto;
    align: center middle;
}}

#search {{
    height: 3;
}}

ResultScreen {{
    align: center middle;
    background: {BG} 85%;
}}

.result-card {{
    width: 56;
    height: auto;
    border: round {AMBER};
    padding: 1 2;
    background: {BG};
}}

#result-title {{
    text-align: center;
}}

#result-wave {{
    text-align: center;
    margin: 1 0 1 0;
}}

#result-detail {{
    text-align: center;
    margin: 0 0 1 0;
}}

#result-keys {{
    text-align: center;
    color: {DIM};
}}

ClockPickerScreen {{
    align: center middle;
    background: {BG} 85%;
}}

.clock-card {{
    width: 42;
    height: auto;
    border: round {AMBER};
    padding: 1 2;
    background: {BG};
}}

#clock-title {{
    text-align: center;
    color: {BRIGHT};
    text-style: bold;
}}

#clock-note {{
    color: {DIM};
    margin: 0 0 1 0;
}}

#clock-keys {{
    text-align: center;
    color: {DIM};
}}

#analysis-board-col, #puzzle-board-col {{
    width: 1fr;
    height: 1fr;
}}

#analysis-stage, #puzzle-stage {{
    width: 1fr;
    height: 1fr;
    align: center middle;
}}

#analysis-board-hint {{
    text-align: center;
}}

#analysis-side {{
    width: 52;
    height: 1fr;
    padding: 0 1;
}}

#analysis-head, #scout-head {{
    height: auto;
    margin-top: 1;
}}

#analysis-body, #scout-body, #coach-body {{
    height: 1fr;
    border: round {DIM};
    padding: 0 1;
}}

#coach-head {{
    height: auto;
}}

#scout-side, #review-side {{
    width: 1fr;
    height: 1fr;
    padding: 0 1;
}}

#review-head {{
    height: auto;
    margin-top: 1;
}}

#review-body {{
    height: 1fr;
    border: round {DIM};
    padding: 0 1;
}}

#review-run {{
    width: 28;
}}

#stockfish-status {{
    height: 1;
}}

#stockfish-hint {{
    height: auto;
    max-height: 2;
}}

#engine-note {{
    height: auto;
    color: {DIM};
    padding: 0 1;
    margin-top: 1;
}}

#scout-run {{
    width: 28;
}}

#puzzle-side {{
    width: 48;
    height: 1fr;
    padding: 0 1;
}}

#puzzle-prompt {{
    color: {AMBER};
    margin: 1 0 0 0;
}}

#puzzle-feedback {{
    height: auto;
    margin: 1 0 0 0;
}}

#puzzle-hint {{
    height: auto;
    color: {DIM};
}}

#puzzle-score {{
    margin: 1 0 1 0;
}}

#lib-pgn {{
    height: 1;
}}

.move-current {{
    color: {BG};
    background: {AMBER};
}}

.footer {{
    height: 1;
    background: {AMBER};
    color: {BG};
    padding: 0 1;
}}
"""
