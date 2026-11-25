"""Optional OS-keychain storage for API keys.

Nothing is persisted unless the user explicitly presses "save" in the AI setup
screen. The key itself is never logged or included in error messages.
"""

from __future__ import annotations

SERVICE_NAME = "chess-terminal"


def _entry(provider: str) -> str:
    return f"{SERVICE_NAME}:{provider}"


def _keyring():
    import keyring  # imported lazily so the app still runs if it is unavailable

    return keyring


def keyring_available() -> bool:
    try:
        import keyring

        backend = keyring.get_keyring()
        return backend is not None and "fail" not in type(backend).__name__.lower()
    except Exception:
        return False


def save_api_key(provider: str, api_key: str) -> tuple[bool, str]:
    """Store a key in the OS credential store. Returns (ok, safe message)."""
    if not api_key.strip():
        return False, "No key to save."
    try:
        keyring = _keyring()
        keyring.set_password(SERVICE_NAME, _entry(provider), api_key)
    except Exception:
        return False, "Could not reach the OS keychain. The key stays in RAM only."
    return True, f"Key for {provider} saved to the OS keychain."


def load_api_key(provider: str) -> str | None:
    """Read a previously saved key, or ``None``."""
    try:
        keyring = _keyring()
        return keyring.get_password(SERVICE_NAME, _entry(provider)) or None
    except Exception:
        return None


def clear_api_key(provider: str) -> tuple[bool, str]:
    """Delete a saved key from the OS credential store."""
    try:
        keyring = _keyring()
        try:
            keyring.delete_password(SERVICE_NAME, _entry(provider))
        except Exception:
            return True, f"No saved key for {provider}."
    except Exception:
        return False, "Could not reach the OS keychain."
    return True, f"Saved key for {provider} cleared from the OS keychain."


__all__ = ["keyring_available", "save_api_key", "load_api_key", "clear_api_key"]
