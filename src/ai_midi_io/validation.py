"""Structural checks and note accounting for AI MIDI IO Standard MIDI Files."""
from __future__ import annotations

from collections.abc import Iterator
import hashlib
import io
from pathlib import Path
import struct
from typing import Any

from mido import MidiFile


def _read_varlen(data: bytes, index: int) -> tuple[int, int]:
    value = 0
    while True:
        byte = data[index]
        index += 1
        value = (value << 7) | (byte & 0x7F)
        if not byte & 0x80:
            return value, index


def _iter_events(track: bytes) -> Iterator[tuple[int, int, bytes]]:
    index = 0
    while index < len(track):
        delta, index = _read_varlen(track, index)
        status = track[index]
        if status < 0x80:
            # running status is not used in these generated files
            raise ValueError("running status is not supported by the validator")
        index += 1
        if status == 0xFF:
            meta_type = track[index]
            index += 1
            length, index = _read_varlen(track, index)
            payload = track[index:index + length]
            index += length
            yield delta, meta_type, payload
        elif status & 0xF0 in {0x80, 0x90, 0xA0, 0xB0, 0xE0}:
            payload = track[index:index + 2]
            index += 2
            yield delta, status, payload
        elif status & 0xF0 in {0xC0, 0xD0}:
            payload = track[index:index + 1]
            index += 1
            yield delta, status, payload
        else:
            raise ValueError(f"unsupported status byte: {status:#x}")


def validate_file(path: Path | str) -> dict[str, Any]:
    """Return a structural report for an AI MIDI IO SMF."""
    path = Path(path)
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    midi = MidiFile(path)
    if midi.type != 1:
        raise ValueError(f"expected SMF type 1, got {midi.type}")
    if midi.ticks_per_beat != 480:
        raise ValueError(f"expected 480 ticks per beat, got {midi.ticks_per_beat}")

    # Parse the raw tracks so meta and channel events can be counted without
    # relying on Mido's interpretation of running status or end-of-track.
    if data[:4] != b"MThd":
        raise ValueError("missing MThd header")
    header_length = struct.unpack(">I", data[4:8])[0]
    if header_length != 6:
        raise ValueError(f"unexpected header length {header_length}")
    format_type, track_count, division = struct.unpack(">HHH", data[8:14])
    if format_type != 1:
        raise ValueError(f"header format is {format_type}, expected 1")
    if track_count != len(midi.tracks):
        raise ValueError("header track count does not match parsed tracks")
    if division != 480:
        raise ValueError(f"header division is {division}, expected 480")

    index = 14
    tracks: list[bytes] = []
    for _ in range(track_count):
        if data[index:index + 4] != b"MTrk":
            raise ValueError("missing MTrk chunk")
        length = struct.unpack(">I", data[index + 4:index + 8])[0]
        index += 8
        tracks.append(data[index:index + length])
        index += length
    if index != len(data):
        raise ValueError("trailing bytes after final track")

    report: dict[str, Any] = {
        "path": str(path),
        "sha256": digest,
        "bytes": len(data),
        "type": midi.type,
        "ticks_per_beat": midi.ticks_per_beat,
        "track_count": track_count,
        "tracks": [],
    }
    total_notes = 0
    for track_number, track in enumerate(tracks):
        events = list(_iter_events(track))
        note_on = 0
        note_off = 0
        absolute = 0
        for delta, status, payload in events:
            absolute += delta
            if isinstance(status, int) and status & 0xF0 == 0x90 and payload[1]:
                note_on += 1
            elif isinstance(status, int) and status & 0xF0 == 0x80:
                note_off += 1
        total_notes += note_on
        report["tracks"].append({
            "index": track_number,
            "events": len(events),
            "note_on": note_on,
            "note_off": note_off,
            "ticks": absolute,
        })
    report["note_on_events"] = total_notes
    return report


def write_report(path: Path | str, destination: Path | str | None = None) -> dict[str, Any]:
    """Validate a file and optionally write the report as JSON."""
    report = validate_file(path)
    if destination is not None:
        Path(destination).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report
