"""Provider / model / key selection for AI games.

Privacy rules enforced here:
* the key input is a masked password field;
* the key is copied only into the in-memory session;
* keychain writes happen only after an explicit button press;
* status messages never echo the key.
"""

from __future__ import annotations

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Input, Static

from .. import theme
from ..ai import PROVIDERS, get_provider
from ..secrets_store import clear_api_key, keyring_available, load_api_key, save_api_key
from ..widgets import KeyboardList
from .game import GameScreen


class AISetupScreen(Screen):
    """Pick a provider and model, then start a game against it."""

    BINDINGS = [Binding("escape", "back", "Back")]

    def compose(self) -> ComposeResult:
        session = self.app.session
        provider = get_provider(session.provider_key)
        index = [p.key for p in PROVIDERS].index(provider.key)
        yield Static("CHESS.TERMINAL // AI UPLINK // BYOK", classes="telemetry")
        yield Static("KEY MATERIAL: RAM ONLY // NOTHING IS WRITTEN WITHOUT CONSENT", classes="telemetry-dim")
        yield Horizontal(
            Vertical(
                Static("PROVIDER // ↑/↓ OR 1-5", classes="panel-title"),
                KeyboardList(
                    [f"{n}. {p.label}" for n, p in enumerate(PROVIDERS, start=1)],
                    on_change=self._provider_changed,
                    on_select=self._provider_changed,
                    id="provider-list",
                    pad_width=30,
                ),
                Static("MODEL // EDITABLE", classes="panel-title"),
                Input(value=provider.default_model, id="model", placeholder="model name"),
                Static("", id="suggested", classes="hint"),
                Static("", id="key-hint", classes="hint"),
                classes="form-col-tight",
            ),
            Vertical(
                Static("API KEY // MASKED // SESSION RAM", classes="panel-title"),
                Input(
                    password=True,
                    id="api-key",
                    placeholder="paste key — hidden as you type",
                ),
                Static("", id="key-status"),
                Static(
                    "The key is never written to .env, logs or tracebacks. "
                    "Use the keychain only if you want it to survive a restart.",
                    classes="hint",
                ),
                Horizontal(
                    Button("SAVE TO KEYCHAIN", id="save-key"),
                    Button("LOAD SAVED", id="load-key"),
                ),
                Horizontal(
                    Button("CLEAR SAVED", id="clear-key"),
                    Button("START GAME", id="start", variant="primary"),
                ),
                Button("BACK TO MENU", id="back"),
                Static("", id="ai-status"),
                classes="form-col",
            ),
            id="screen-body",
        )
        yield Static(
            "TAB MOVE FOCUS // ENTER ACTIVATE // ESC BACK // KEYS STAY IN MEMORY",
            classes="footer",
        )

    def on_mount(self) -> None:
        self.query_one("#provider-list", KeyboardList).focus()
        keyring = "AVAILABLE" if keyring_available() else "UNAVAILABLE"
        self._set_status(f"OS KEYCHAIN: {keyring} // KEY HELD IN RAM FOR THIS SESSION", theme.DIM)
        self._provider_changed(self.query_one("#provider-list", KeyboardList).index)

    def _current_provider(self):
        return PROVIDERS[self.query_one("#provider-list", KeyboardList).index]

    def _provider_changed(self, index: int) -> None:
        if not index < len(PROVIDERS):
            return
        provider = PROVIDERS[index]
        session = self.app.session
        try:
            model_input = self.query_one("#model", Input)
            key_input = self.query_one("#api-key", Input)
            suggested = self.query_one("#suggested", Static)
            key_hint = self.query_one("#key-hint", Static)
        except Exception:
            return
        model_input.value = (
            session.model if getattr(session, "provider_key", "") == provider.key else provider.default_model
        )
        suggested.update(Text("SUGGESTED // " + " · ".join(provider.models), style=theme.DIM))
        key_hint.update(Text(provider.key_hint, style=theme.DIM))

        # Switching provider invalidates a key typed for the previous provider.
        if getattr(session, "provider_key", "") != provider.key:
            key_input.value = ""
            session.api_key = ""
        else:
            key_input.value = session.api_key

    def _set_status(self, message: str, colour: str = theme.BRIGHT) -> None:
        self.query_one("#ai-status", Static).update(Text(message, style=colour))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        provider = self._current_provider()
        key_input = self.query_one("#api-key", Input)
        key = key_input.value.strip() or self.app.session.api_key.strip()

        if event.button.id == "save-key":
            if not key:
                self._set_status("NO KEY IN RAM TO SAVE.")
                return
            ok, message = save_api_key(provider.key, key)
            self._set_status(message.upper(), theme.BRIGHT if ok else theme.AMBER)
        elif event.button.id == "load-key":
            saved = load_api_key(provider.key)
            if not saved:
                self._set_status(f"NO SAVED KEY FOR {provider.label.upper()}.")
                return
            key_input.value = saved
            self.app.session.api_key = saved
            self._set_status(f"SAVED KEY FOR {provider.label.upper()} LOADED INTO RAM.")
        elif event.button.id == "clear-key":
            ok, message = clear_api_key(provider.key)
            self._set_status(message.upper(), theme.BRIGHT if ok else theme.AMBER)
        elif event.button.id == "start":
            self._start()
        elif event.button.id == "back":
            self.action_back()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id in ("model", "api-key"):
            self._start()

    def _start(self) -> None:
        provider = self._current_provider()
        model = self.query_one("#model", Input).value.strip() or provider.default_model
        key = self.query_one("#api-key", Input).value.strip() or self.app.session.api_key.strip()
        if provider.requires_key and not key:
            self._set_status(f"{provider.label.upper()} REQUIRES AN API KEY IN RAM.")
            self.query_one("#api-key", Input).focus()
            return
        session = self.app.session
        session.provider_key = provider.key
        session.model = model
        session.api_key = key if provider.requires_key else ""
        self.query_one("#api-key", Input).value = ""
        self.app.push_screen(GameScreen(mode="ai"))

    def action_back(self) -> None:
        self.query_one("#api-key", Input).value = ""
        self.app.pop_screen()


__all__ = ["AISetupScreen"]
