"""Structural checks and note accounting for AI MIDI IO Standard MIDI Files."""
from __future__ import annotations

from collections.abc import Iterator
import hashlib
import io
from pathlib import Path
import struct
from typing import Any


def _smf_track_chunks(raw: bytes) -> tuple[int, int, list[memoryview]]:
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

    view = memoryview(raw)
    chunks = []
    pos = 14
    for _ in range(count):
        if pos + 8 > len(raw) or raw[pos:pos + 4] != b"MTrk":
            raise ValueError("Missing or truncated MIDI track chunk")
        length = struct.unpack_from(">I", raw, pos + 4)[0]
        start = pos + 8
        pos = start + length
        if pos > len(raw):
            raise ValueError("Track chunk extends beyond file")
        chunks.append(view[start:pos])
    if pos != len(raw):
        raise ValueError("Unexpected bytes outside declared MIDI chunks")
    return file_type, division, chunks


def _read_vlq(data: memoryview, pos: int) -> tuple[int, int]:
    value = 0
    for _ in range(4):
        if pos == len(data):
            raise ValueError("Truncated variable-length quantity")
        byte = data[pos]
        pos += 1
        value = (value << 7) | (byte & 0x7F)
        if byte < 0x80:
            return value, pos
    raise ValueError("SMF variable-length quantity exceeds four bytes")


def _track_event_ticks(data: memoryview) -> Iterator[int]:
    """Check event framing within one chunk and retain deltas on unknown meta events."""
    pos = tick = 0
    running_status = None
    while pos < len(data):
        delta, pos = _read_vlq(data, pos)
        tick += delta
        if pos == len(data):
            raise ValueError("Missing event after delta time")
        status = data[pos]
        if status >= 0x80:
            pos += 1
        else:
            if running_status is None:
                raise ValueError("MIDI data byte without a running channel status")
            status = running_status

        if status < 0xF0:
            running_status = status
            pos += 1 if status >> 4 in (0xC, 0xD) else 2
        elif status in (0xF0, 0xF7, 0xFF):
            running_status = None
            meta_type = None
            if status == 0xFF:
                if pos == len(data):
                    raise ValueError("Missing MIDI meta-event type")
                meta_type = data[pos]
                pos += 1
            length, pos = _read_vlq(data, pos)
            pos += length
            if meta_type == 0x2F:
                if length != 0:
                    raise ValueError("end_of_track must have an empty payload")
                if pos != len(data):
                    raise ValueError("events after end_of_track")
                yield tick
                return
        else:
            raise ValueError(f"Invalid SMF event status 0x{status:02x}")
        if pos > len(data):
            raise ValueError("MIDI event extends beyond its track chunk")
        yield tick
    raise ValueError("expected exactly one end_of_track")


def validate_midi(
    path: str | Path,
    *,
    expected_musical_tracks: int | None = None,
    expected_end_tick: int | None = None,
    require_complete_notes: bool = True,
) -> dict[str, Any]:
    """Reopen a PPQ SMF and report track structure, timing and note balance.

    Type 0 and 1 share output-port/channel state. Type 2 tracks are separate
    sequences. At equal ticks, track order breaks ties and each track retains
    its original event order. A player can use a different inter-track order.
    Overlaps count separately and do not fail validation. Set
    require_complete_notes=False to report unclosed notes and unmatched note
    releases without raising for note balance. Releases require explicit
    note-off or zero-velocity note-on messages. Pedal and channel-mode playback
    semantics are outside note accounting. Framing and parser checks apply
    in either mode.
    """
    import mido

    path = Path(path).resolve()
    raw = path.read_bytes()
    file_type, ppq, chunks = _smf_track_chunks(raw)
    ticks_by_track = []
    for index, chunk in enumerate(chunks):
        try:
            ticks_by_track.append(list(_track_event_ticks(chunk)))
        except ValueError as error:
            raise ValueError(f"Track {index}: {error}") from error
    try:
        midi = mido.MidiFile(file=io.BytesIO(raw), clip=False)
    except (EOFError, LookupError, OSError, ValueError) as error:
        raise ValueError(f"Cannot decode MIDI events: {type(error).__name__}: {error}") from error

    tracks, events, overlaps = [], [], []
    tempo_changes, time_signatures = [], []
    for ti, (track, ticks) in enumerate(zip(midi.tracks, ticks_by_track, strict=True)):
        note_count, port = 0, 0
        channels, programs = set(), []
        for ei, (msg, tick) in enumerate(zip(track, ticks, strict=True)):
            if hasattr(msg, "channel"):
                channels.add(msg.channel)
            if msg.type == "midi_port":
                port = msg.port
            elif msg.type == "set_tempo":
                tempo_changes.append({"track": ti, "tick": tick, "tempo": msg.tempo})
            elif msg.type == "time_signature":
                time_signatures.append({
                    "track": ti,
                    "tick": tick,
                    "numerator": msg.numerator,
                    "denominator": msg.denominator,
                    "clocks_per_click": msg.clocks_per_click,
                    "notated_32nd_notes_per_beat": msg.notated_32nd_notes_per_beat,
                })
            elif msg.type == "program_change":
                programs.append({"tick": tick, "channel": msg.channel, "program": msg.program})
            elif msg.type in ("note_on", "note_off"):
                starts_note = msg.type == "note_on" and msg.velocity > 0
                note_count += starts_note
                events.append((tick, ti, ei, port, msg.channel, msg.note, starts_note))
        tracks.append({"index": ti, "name": track.name, "notes": note_count,
                       "end_tick": ticks[-1], "channels": sorted(channels), "programs": programs})

    active: dict[tuple[int, int, int, int], int] = {}
    unmatched_note_offs = 0
    for tick, ti, _, port, channel, note, starts_note in sorted(events, key=lambda item: item[:3]):
        sequence = ti if file_type == 2 else 0
        key = (sequence, port, channel, note)
        previous = active.get(key, 0)
        if starts_note:
            if previous:
                overlap = {"tick": tick, "channel": channel, "note": note}
                if port:
                    overlap["port"] = port
                overlaps.append(overlap)
            active[key] = previous + 1
        elif previous > 1:
            active[key] = previous - 1
        elif previous == 1:
            del active[key]
        elif require_complete_notes:
            raise ValueError(f"Unmatched note-off: track={ti}, tick={tick}, key={key}")
        else:
            unmatched_note_offs += 1
    if require_complete_notes and active:
        raise ValueError(f"Unclosed notes: {active}")
    musical_tracks = sum(track["notes"] > 0 for track in tracks)
    end_tick = max(track["end_tick"] for track in tracks)
    if expected_musical_tracks is not None and musical_tracks != expected_musical_tracks:
        raise ValueError(f"Expected {expected_musical_tracks} musical tracks, got {musical_tracks}")
    if expected_end_tick is not None and end_tick != expected_end_tick:
        raise ValueError(f"Expected end tick {expected_end_tick}, got {end_tick}")
    tempo_changes.sort(key=lambda event: (event["tick"], event["track"]))
    time_signatures.sort(key=lambda event: (event["tick"], event["track"]))
    return {"path": str(path), "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
            "format": file_type, "ppq": ppq, "track_chunks": len(chunks),
            "musical_tracks": musical_tracks, "total_notes": sum(t["notes"] for t in tracks),
            "end_tick": end_tick, "note_overlaps": overlaps, "unclosed_notes": sum(active.values()),
            "unmatched_note_offs": unmatched_note_offs, "tempo_changes": tempo_changes,
            "time_signatures": time_signatures, "tracks": tracks}
