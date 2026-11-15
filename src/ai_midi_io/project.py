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
import zipfile

VERSION = "0.63.2"


def _package_parents(root: Path, package: str) -> list[Path]:
    return sorted({path.parent.parent for path in root.rglob(f"{package}/__init__.py")
                   if path.is_file()})


def _ready_dependency_tree(root: Path, digest: str) -> Path | None:
    # Also recognize a healthy cache previously created by the plugin runtime.
    for candidate in (root, *sorted(root.glob("ready-*"))):
        try:
            complete = (candidate / ".complete").read_text(encoding="ascii") == digest
        except (OSError, UnicodeError):
            continue
        if complete and _package_parents(candidate, "mido"):
            return candidate
    return None


def _dependency_tree(archive: Path, cache_root: Path) -> Path:
    data = archive.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    destination = cache_root / digest
    ready = _ready_dependency_tree(destination, digest)
    if ready is not None:
        return ready

    destination.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="extract-", dir=destination) as temporary:
        staging = Path(temporary) / "files"
        staging.mkdir()
        with zipfile.ZipFile(io.BytesIO(data)) as bundle:
            for info in bundle.infolist():
                name = info.filename
                relative = PurePosixPath(name)
                mode = (info.external_attr >> 16) & 0xFFFF
                if (relative.is_absolute() or not relative.parts or ".." in relative.parts
                        or "\\" in name or any(":" in part for part in relative.parts)
                        or stat.S_ISLNK(mode)):
                    raise ValueError(f"Unsafe ZIP member: {name!r}")
                target = staging.joinpath(*relative.parts)
                if info.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with bundle.open(info) as source, target.open("wb") as output:
                        shutil.copyfileobj(source, output)
        if not _package_parents(staging, "mido"):
            raise ImportError("The local dependency archive contains no mido/__init__.py")
        (staging / ".complete").write_text(digest, encoding="ascii")
        ready = _ready_dependency_tree(destination, digest)
        if ready is not None:
            return ready
        # Publish a complete tree atomically and leave other readers' trees in place.
        ready = destination / f"ready-{Path(temporary).name}"
        staging.rename(ready)
        return ready


def extract_dependencies(archive: Path, cache_root: Path) -> list[Path]:
    """Extract a trusted local archive into a content-keyed cache."""
    tree = _dependency_tree(Path(archive).resolve(), Path(cache_root).resolve())
    return _package_parents(tree, "mido")


def _load_mido(references: Path, knowledge: Path) -> ModuleType:
    try:
        return importlib.import_module("mido")
    except ImportError as initial_error:
        archive = references / "AI_MIDI_IO_Python.zip"
        if not archive.is_file():
            raise ImportError(
                "mido is not importable and the bundled AI_MIDI_IO_Python.zip "
                f"is not accessible at {archive}. Install the project dependency "
                "or supply the original bundle and its prerequisite packaging module."
            ) from initial_error
        tree = _dependency_tree(archive, knowledge / "ai_midi_io_dependencies")
        roots = set(_package_parents(tree, "mido")) | set(_package_parents(tree, "packaging"))
        for parent in sorted(roots, reverse=True):
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
        importlib.invalidate_caches()
        return importlib.import_module("mido")


def _load_midifile(path: Path) -> ModuleType:
    """Import the supplied source file instead of substituting installed MIDIUtil."""
    if not path.is_file():
        raise FileNotFoundError(path)
    spec = importlib.util.spec_from_file_location("MIDIFile", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    previous = sys.modules.get("MIDIFile")
    sys.modules["MIDIFile"] = module
    try:
        spec.loader.exec_module(module)
        if not callable(getattr(module, "MIDIFile", None)):
            raise ImportError(f"No MIDIFile class in {path}")
    except Exception:
        if previous is None:
            sys.modules.pop("MIDIFile", None)
        else:
            sys.modules["MIDIFile"] = previous
        raise
    return module


def initialize(
    reference_dir: str | Path | None = None,
    output_root: str | Path | None = None,
    require_midifile: bool = False,
) -> dict[str, Any]:
    """Check project output paths and return live backend objects and diagnostics.

    Optional source files are Python code. Supply only a trusted reference directory.
    """
    references = Path(
        reference_dir or os.environ.get("AI_MIDI_IO_REFERENCE_DIR") or "references"
    ).expanduser().resolve()
    base = Path(
        output_root or os.environ.get("AI_MIDI_IO_BASE_DIR") or "ai-midi-io-output"
    ).expanduser().resolve()
    directories = {name: base / name for name in (
        "knowledge", "midi_generation", "wav_generation"
    )}
    for directory in directories.values():
        directory.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryFile(dir=directory) as probe:
            probe.write(b"write-test")
    mido = _load_mido(references, directories["knowledge"])
    message = mido.Message("note_on", channel=0, note=60, velocity=64)
    if message.bytes() != [144, 60, 64]:
        raise RuntimeError("mido message serialization failed")

    legacy = None
    legacy_path = references / "MIDIFile.py"
    legacy_problem = None
    try:
        legacy = _load_midifile(legacy_path)
    except (ImportError, OSError, SyntaxError) as error:
        legacy_problem = f"{type(error).__name__}: {error}"
        if require_midifile:
            raise RuntimeError(
                f"The requested MIDIFile backend is not ready: {legacy_problem}"
            ) from error

    report = {
        "version": VERSION,
        "ready": True,
        "ready_for": "mido file generation and analysis",
        "mido_path": str(Path(mido.__file__).resolve()),
        "midifile_available": legacy is not None,
        "midifile_path": str(legacy_path) if legacy is not None else None,
        "midifile_issue": legacy_problem,
        "reference_directory": str(references),
        "dependency_archive_present": (references / "AI_MIDI_IO_Python.zip").is_file(),
        "directories": {name: str(path) for name, path in directories.items()},
        "live_midi_verified": False,
        "live_osc_verified": False,
    }
    return {"mido": mido, "MIDIFile": getattr(legacy, "MIDIFile", None),
            "paths": directories, "report": report}
