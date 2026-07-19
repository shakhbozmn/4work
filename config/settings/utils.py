"""Helpers for reading environment variables with fail-closed semantics."""

import os


class MissingSettingError(RuntimeError):
    """Raised when a required environment variable is missing or blank."""


def required_env(name: str) -> str:
    """Return the value of `name` or raise if it is missing or empty."""
    value = os.environ.get(name, "").strip()
    if not value:
        raise MissingSettingError(f"Required environment variable {name} is not set")
    return value


def optional_env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def csv_env(name: str) -> list[str]:
    """Parse a comma-separated env var into a list of non-empty stripped values."""
    return [item.strip() for item in os.environ.get(name, "").split(",") if item.strip()]


def bool_env(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")
