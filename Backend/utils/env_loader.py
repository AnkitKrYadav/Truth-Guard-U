"""Shared helpers for loading environment variables from project .env files."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from dotenv import find_dotenv, load_dotenv

_LOADED = False


def _candidate_paths() -> Iterable[Path]:
    """Yield likely .env locations relative to the backend package."""
    utils_dir = Path(__file__).resolve().parent
    backend_dir = utils_dir.parent
    yield backend_dir / ".env"
    yield backend_dir.parent / ".env"


def load_env(*, override: bool = False) -> None:
    """Load environment variables once from common .env locations."""
    global _LOADED
    if _LOADED and not override:
        return

    loaded = load_dotenv(override=override)

    if not loaded:
        for candidate in _candidate_paths():
            if candidate.exists() and load_dotenv(dotenv_path=candidate, override=override):
                loaded = True
                break

    if not loaded:
        env_path = find_dotenv(usecwd=True)
        if env_path:
            load_dotenv(env_path, override=override)

    _LOADED = True
