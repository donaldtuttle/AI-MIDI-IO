"""Compatibility facade for the AI MIDI IO plugin runtime API."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import quote

from .audio import write_test_tone
from .composition import scheduled_track
from .project import VERSION, extract_dependencies, initialize
from .validation import validate_midi

__all__ = [
    "VERSION", "extract_dependencies", "initialize", "sandbox_link",
    "scheduled_track", "validate_midi", "write_test_tone",
]

_SANDBOX_ROOT = Path("/mnt/data")


def sandbox_link(path: str | Path, label: str = "Download file") -> str:
    """Format a ChatGPT download link for a nonempty file under its sandbox root."""
    path = Path(path).expanduser().resolve()
    if not path.is_file() or path.stat().st_size == 0:
        raise FileNotFoundError(f"No nonempty generated file at {path}")
    if not path.is_relative_to(_SANDBOX_ROOT.resolve()):
        raise ValueError(f"Sandbox links require a file actually under {_SANDBOX_ROOT}")
    safe_label = label.replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]")
    return f"[{safe_label}](sandbox:{quote(path.as_posix(), safe='/')})"
