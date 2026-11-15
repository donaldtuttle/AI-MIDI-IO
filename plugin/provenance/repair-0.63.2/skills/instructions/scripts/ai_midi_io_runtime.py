"""Local runtime for AI MIDI IO 0.63.2. No pip installs or network access.

Use mido for the validated default file workflow. The original standalone
MIDIFile.py remains supported when its actual source is accessible. This module
never substitutes another package for that legacy source or claims hardware I/O.
"""
from __future__ import annotations

import hashlib
import importlib
import importlib.util
import json
import math
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import struct
import sys
import tempfile
from types import ModuleType
from typing import Any
from urllib.parse import quote
import wave
import zipfile

VERSION = "0.63.2"


def _package_parents(root: Path, package: str) -> list[Path]:
    return sorted({p.parent.parent for p in root.rglob(f"{package}/__init__.py")})


def extract_dependencies(archive: Path, cache_root: Path) -> list[Path]:
    """Extract a local dependency bundle, checking contents rather than dir existence.

    Cache completion depends on archive bytes AND a real mido package. A stale
    directory or incomplete extraction is rebuilt. Nested archive layouts work.
    """
    archive, cache_root = Path(archive).resolve(), Path(cache_root).resolve()
    if not archive.is_file():
        raise FileNotFoundError(f"Dependency archive not found: {archive}")
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    destination = cache_root / digest
    marker = destination / ".complete"
    if marker.is_file() and marker.read_text() == digest:
        parents = _package_parents(destination, "mido")
        if parents:
            return parents
    cache_root.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix="extract-", dir=cache_root))
    try:
        with zipfile.ZipFile(archive) as bundle:
            for info in bundle.infolist():
                name = info.filename
                rel = PurePosixPath(name)
                mode = (info.external_attr >> 16) & 0xFFFF
                if (rel.is_absolute() or ".." in rel.parts or "\\" in name
                        or any(":" in part for part in rel.parts)
                        or stat.S_ISLNK(mode)):
                    raise ValueError(f"Unsafe ZIP member: {name!r}")
                target = staging.joinpath(*rel.parts)
                if info.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with bundle.open(info) as source, target.open("wb") as output:
                        shutil.copyfileobj(source, output)
        if not _package_parents(staging, "mido"):
            raise ImportError("The local dependency archive contains no mido/__init__.py")
        (staging / ".complete").write_text(digest)
        if destination.exists():
            shutil.rmtree(destination)
        staging.rename(destination)
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return _package_parents(destination, "mido")


def _load_mido(references: Path, knowledge: Path) -> ModuleType:
    try:
        return importlib.import_module("mido")
    except ImportError as initial_error:
        archive = references / "AI_MIDI_IO_Python.zip"
        if not archive.is_file():
            raise ImportError(
                "mido is not importable and the bundled AI_MIDI_IO_Python.zip "
                f"is not accessible at {archive}. Retrieve the actual packaged "
                "file and pass its reference directory; do not invent modules "
                "or report setup as complete."
            ) from initial_error
        parents = extract_dependencies(archive, knowledge / "ai_midi_io_dependencies")
        # Include siblings such as packaging, when supplied in the archive.
        roots = set(parents)
        extraction_root = knowledge / "ai_midi_io_dependencies"
        roots.update(_package_parents(extraction_root, "packaging"))
        for parent in sorted(roots, reverse=True):
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
        importlib.invalidate_caches()
        return importlib.import_module("mido")


def _load_midifile(path: Path) -> ModuleType:
    """Import precisely the original source file, not an unrelated installed module."""
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


def initialize(reference_dir: str | Path | None = None,
               output_root: str | Path | None = None,
               require_midifile: bool = False) -> dict[str, Any]:
    """Initialize only available capabilities and return measured diagnostics.

    If this script was copied alone from a skill resource, pass reference_dir
    explicitly for legacy/bundled files. A skill URI is not a filesystem path.
    """
    default_references = Path(__file__).resolve().parents[1] / "references"
    references = Path(reference_dir or os.environ.get(
        "AI_MIDI_IO_REFERENCE_DIR", str(default_references))).expanduser().resolve()
    base = Path(output_root or os.environ.get(
        "AI_MIDI_IO_BASE_DIR", "/mnt/data")).expanduser().resolve()
    directories = {name: base / name for name in (
        "knowledge", "midi_generation", "wav_generation")}
    for directory in directories.values():
        directory.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryFile(dir=directory) as test:
            test.write(b"write-test")
    mido = _load_mido(references, directories["knowledge"])
    # Confirm construction/serialization works, not merely module presence.
    if mido.Message("note_on", channel=0, note=60, velocity=64).bytes() != [144, 60, 64]:
        raise RuntimeError("mido message serialization failed")
    legacy = None
    legacy_path = references / "MIDIFile.py"
    legacy_problem = None
    try:
        legacy = _load_midifile(legacy_path)
    except (ImportError, OSError, SyntaxError) as error:
        legacy_problem = f"{type(error).__name__}: {error}"
        if require_midifile:
            raise RuntimeError(f"The requested MIDIFile backend is not ready: {legacy_problem}") from error
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


def _check_smf_chunks(path: Path) -> tuple[int, int]:
    raw = path.read_bytes()
    if len(raw) < 14 or raw[:4] != b"MThd":
        raise ValueError("Missing or incomplete MIDI header")
    header_length = struct.unpack_from(">I", raw, 4)[0]
    if header_length != 6:
        raise ValueError("Expected a six-byte SMF header for this export")
    file_type, count, division = struct.unpack_from(">HHH", raw, 8)
    if file_type not in (0, 1, 2) or count < 1 or (file_type == 0 and count != 1):
        raise ValueError("Invalid SMF format/track count")
    if division == 0 or division & 0x8000:
        raise ValueError("This export validator requires positive PPQ timing, not SMPTE")
    pos = 14
    for _ in range(count):
        if pos + 8 > len(raw) or raw[pos:pos + 4] != b"MTrk":
            raise ValueError("Missing or truncated MIDI track chunk")
        length = struct.unpack_from(">I", raw, pos + 4)[0]
        pos += 8 + length
        if pos > len(raw):
            raise ValueError("Track chunk extends beyond file")
    if pos != len(raw):
        raise ValueError("Unexpected bytes outside declared MIDI chunks")
    return count, division


def validate_midi(path: str | Path, *, expected_musical_tracks: int | None = None,
                  expected_end_tick: int | None = None) -> dict[str, Any]:
    """Reopen an exported file and validate structure, timing, and note balance.

    Same-pitch overlaps are reported, not prohibited. Synth interpretation can
    differ. Validation is structural; it is not an audition or a DAW import test.
    """
    import mido
    path = Path(path).resolve()
    track_count, ppq = _check_smf_chunks(path)
    mid = mido.MidiFile(str(path), clip=False)
    tracks, events, overlaps = [], [], []
    for ti, track in enumerate(mid.tracks):
        tick, note_count, endings = 0, 0, 0
        channels, programs = set(), []
        for ei, msg in enumerate(track):
            if type(msg.time) is not int or msg.time < 0:
                raise ValueError(f"Track {ti}: invalid delta time")
            tick += msg.time
            if msg.type == "end_of_track":
                endings += 1
                if ei != len(track) - 1:
                    raise ValueError(f"Track {ti}: events after end_of_track")
            if not msg.is_meta:
                msg.bytes()  # Uses the parser's validated message representation.
            if hasattr(msg, "channel"):
                channels.add(msg.channel)
            if msg.type == "program_change":
                programs.append({"tick": tick, "channel": msg.channel, "program": msg.program})
            if msg.type in ("note_on", "note_off"):
                if msg.type == "note_on" and msg.velocity > 0:
                    note_count += 1
                events.append((tick, ti, ei, msg))
        if endings != 1:
            raise ValueError(f"Track {ti}: expected exactly one end_of_track")
        tracks.append({"index": ti, "name": track.name, "notes": note_count,
                       "end_tick": tick, "channels": sorted(channels), "programs": programs})
    active: dict[tuple[int, int, int], int] = {}
    for tick, ti, ei, msg in sorted(events, key=lambda item: item[:3]):
        # Type-2 tracks are separate sequences; type-0/1 share MIDI channels.
        group = ti if mid.type == 2 else 0
        key = (group, msg.channel, msg.note)
        if msg.type == "note_on" and msg.velocity > 0:
            if active.get(key, 0):
                overlaps.append({"tick": tick, "channel": msg.channel, "note": msg.note})
            active[key] = active.get(key, 0) + 1
        else:
            if active.get(key, 0) == 0:
                raise ValueError(f"Unmatched note-off: track={ti}, tick={tick}, key={key}")
            active[key] -= 1
    unclosed = {str(key): count for key, count in active.items() if count}
    if unclosed:
        raise ValueError(f"Unclosed notes: {unclosed}")
    musical_tracks = sum(track["notes"] > 0 for track in tracks)
    end_tick = max(track["end_tick"] for track in tracks)
    if expected_musical_tracks is not None and musical_tracks != expected_musical_tracks:
        raise ValueError(f"Expected {expected_musical_tracks} musical tracks, got {musical_tracks}")
    if expected_end_tick is not None and end_tick != expected_end_tick:
        raise ValueError(f"Expected end tick {expected_end_tick}, got {end_tick}")
    return {"path": str(path), "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "format": mid.type, "ppq": ppq, "track_chunks": track_count,
            "musical_tracks": musical_tracks, "total_notes": sum(t["notes"] for t in tracks),
            "end_tick": end_tick, "note_overlaps": overlaps, "unclosed_notes": 0,
            "tracks": tracks}


def sandbox_link(path: str | Path, label: str = "Download file") -> str:
    path = Path(path).expanduser().resolve()
    if not path.is_file() or path.stat().st_size == 0:
        raise FileNotFoundError(f"No nonempty generated file at {path}")
    if not path.is_relative_to(Path("/mnt/data").resolve()):
        raise ValueError("Sandbox links require a file actually under /mnt/data")
    safe_label = label.replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]")
    return f"[{safe_label}](sandbox:{quote(path.as_posix(), safe='/')})"


def scheduled_track(events: list[tuple[int, Any]], end_tick: int):
    """Convert absolute ticks to deltas. Release then retrigger at equal ticks."""
    import mido
    if type(end_tick) is not int or end_tick < 0:
        raise ValueError("end_tick must be a nonnegative integer")
    for tick, msg in events:
        if type(tick) is not int or not 0 <= tick <= end_tick:
            raise ValueError("Event lies outside the nonnegative export interval")
        if msg.type == "end_of_track":
            raise ValueError("scheduled_track creates its own end_of_track")
    def priority(msg):
        if msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
            return 1
        if msg.type == "note_on":
            return 2
        return 0
    track, previous = mido.MidiTrack(), 0
    for _, (tick, msg) in sorted(enumerate(events),
                                  key=lambda item: (item[1][0], priority(item[1][1]), item[0])):
        track.append(msg.copy(time=tick - previous))
        previous = tick
    track.append(mido.MetaMessage("end_of_track", time=end_tick - previous))
    return track


def write_test_tone(path: str | Path, frequency: float = 432.0,
                    duration: float = 0.5, waveform: str = "sine",
                    sample_rate: int = 44100) -> dict[str, Any]:
    """Write a simple PCM diagnostic tone, NOT an instrument-faithful MIDI render."""
    if (not math.isfinite(frequency) or frequency <= 0 or frequency >= sample_rate / 2
            or not math.isfinite(duration) or duration <= 0
            or type(sample_rate) is not int or sample_rate <= 0):
        raise ValueError("Invalid tone frequency, duration, or sample rate")
    if waveform not in ("sine", "square", "triangle", "sawtooth"):
        raise ValueError(f"Unsupported waveform: {waveform}")
    path = Path(path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    frames = int(round(duration * sample_rate))
    if frames < 1:
        raise ValueError("Tone duration produces no samples")
    ramp = min(max(1, int(sample_rate * 0.005)), max(1, frames // 2))
    with wave.open(str(path), "wb") as audio:
        audio.setnchannels(1); audio.setsampwidth(2); audio.setframerate(sample_rate)
        block = bytearray()
        for n in range(frames):
            phase = (n * frequency / sample_rate) % 1.0
            value = {"sine": lambda: math.sin(2 * math.pi * phase),
                     "square": lambda: 1.0 if phase < 0.5 else -1.0,
                     "triangle": lambda: 1.0 - 4.0 * abs(phase - 0.5),
                     "sawtooth": lambda: 2.0 * phase - 1.0}[waveform]()
            envelope = min(1.0, n / ramp, (frames - 1 - n) / ramp)
            block.extend(struct.pack("<h", round(0.2 * envelope * value * 32767)))
            if len(block) >= 8192:
                audio.writeframesraw(block); block.clear()
        if block:
            audio.writeframesraw(block)
    with wave.open(str(path), "rb") as audio:
        if (audio.getnframes(), audio.getframerate(), audio.getnchannels(), audio.getsampwidth()) != (frames, sample_rate, 1, 2):
            raise RuntimeError("WAV header validation failed")
    return {"path": str(path), "frames": frames, "sample_rate": sample_rate,
            "channels": 1, "bits_per_sample": 16, "frequency_hz": frequency,
            "waveform": waveform, "is_midi_render": False}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--references", type=Path)
    parser.add_argument("--output-root", type=Path)
    parser.add_argument("--require-midifile", action="store_true")
    args = parser.parse_args()
    try:
        result = initialize(args.references, args.output_root, args.require_midifile)
        print(json.dumps(result["report"], indent=2))
    except Exception as error:
        print(json.dumps({"ready": False, "error": f"{type(error).__name__}: {error}"}, indent=2))
        raise SystemExit(1)
