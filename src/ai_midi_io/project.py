"""Initialize local project directories and load the verified file backends."""

from __future__ import annotations

import hashlib
import importlib
import importlib.util
import io
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import sys
import tempfile
from types import ModuleType
from typing import Any


VERSION = "0.1.0"
REQUIRED_DIRS = (
    "midi_generation",
    "midi_validation",
    "audio_diagnostics",
    "references",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def initialize(
    references: Path | None = None,
    output_root: Path | None = None,
    require_midifile: bool = False,
) -> dict[str, Any]:
    """Create the local output tree and report available backends."""
    root = Path(output_root or Path.cwd() / "ai-midi-io-output").resolve()
    paths = {name: root / name for name in REQUIRED_DIRS}
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)

    report = {
        "version": VERSION,
        "output_root": str(root),
        "paths": {name: str(path) for name, path in paths.items()},
        "backends": {},
    }

    try:
        import mido
        report["backends"]["mido"] = {
            "available": True,
            "version": getattr(mido, "__version__", "unknown"),
        }
    except ImportError as error:
        report["backends"]["mido"] = {"available": False, "error": str(error)}

    if require_midifile:
        try:
            spec = importlib.util.find_spec("MIDIFile")
            report["backends"]["MIDIFile"] = {"available": spec is not None}
        except Exception as error:
            report["backends"]["MIDIFile"] = {"available": False, "error": str(error)}

    report["paths"] = {name: str(path) for name, path in paths.items()}
    return {"report": report, "paths": paths, "mido": mido if "mido" in sys.modules else None}
