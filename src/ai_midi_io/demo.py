"""Generate and validate the deterministic four-part MIDI example."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import TYPE_CHECKING, Sequence

from .composition import scheduled_track
from .project import initialize
from .validation import validate_midi

if TYPE_CHECKING:
    from mido import MidiFile


MIDI_FILENAME = "AI_MIDI_IO_Verification_4track_120BPM.mid"
PPQ = 480
BARS = 16
BPM = 120
BEATS_PER_BAR = 4
END_TICK = BARS * BEATS_PER_BAR * PPQ


def note(channel: int, pitch: int, start: int, duration: int, velocity: int) -> list:
    return [
        (start, {"type": "note_on", "channel": channel, "note": pitch, "velocity": velocity}),
        (start + duration, {"type": "note_off", "channel": channel, "note": pitch}),
    ]


def build_demo() -> MidiFile:
    from mido import Message, MetaMessage, MidiFile

    midi = MidiFile(type=1, ticks_per_beat=PPQ)
    conductor = [
        (0, MetaMessage("set_tempo", tempo=500000)),
        (0, MetaMessage("time_signature", numerator=4, denominator=4)),
        (0, MetaMessage("key_signature", key="C")),
        (0, MetaMessage("track_name", name="Conductor")),
    ]
    midi.tracks.append(scheduled_track(conductor, END_TICK))

    event_sets = [[] for _ in range(4)]
    names = ("Melody - Square Lead", "Bass - Synth Bass 1", "Drums - GM channel 10", "Harmony - Warm Pad")
    programs = (80, 38, None, 89)
    channels = (0, 1, 9, 2)

    for index, (name, program, channel) in enumerate(zip(names, programs, channels)):
        events = event_sets[index]
        events.append((0, MetaMessage("track_name", name=name)))
        if program is not None:
            events.append((0, Message("program_change", channel=channel, program=program)))

    def add(index: int, channel: int, pitch: int, start: int, duration: int, velocity: int) -> None:
        event_sets[index].extend(note(channel, pitch, start, duration, velocity))

    # Melody: simple arpeggio-like line
    melody_notes = [60, 64, 67, 72, 67, 64, 60, 55] * 8
    for i, pitch in enumerate(melody_notes):
        add(0, 0, pitch, i * (PPQ // 2), PPQ // 2, 90)

    # Bass: root notes
    for bar in range(BARS):
        root = 36 + (0, 5, 7, 3)[bar % 4]
        add(1, 1, root, bar * BEATS_PER_BAR * PPQ, BEATS_PER_BAR * PPQ, 80)

    # Drums: kick and snare
    for bar in range(BARS):
        origin = bar * BEATS_PER_BAR * PPQ
        add(2, 9, 36, origin, PPQ // 8, 108)
        add(2, 9, 38, origin + 2 * PPQ, PPQ // 8, 91)

    # Pad chords
    chords = ((60, 64, 67), (57, 60, 64), (53, 57, 60), (55, 59, 62))
    for section, chord in enumerate(chords):
        start = section * 4 * BEATS_PER_BAR * PPQ
        for voice, pitch in enumerate(chord):
            add(3, 2, pitch, start, 4 * BEATS_PER_BAR * PPQ, 62 + voice * 4)

    for events in event_sets:
        midi.tracks.append(scheduled_track(events, END_TICK))
    return midi


def generate(output_root: Path | None = None, references: Path | None = None) -> dict:
    runtime = initialize(references, output_root)
    output = runtime["paths"]["midi_generation"] / MIDI_FILENAME
    build_demo().save(filename=output)
    report = validate_midi(output, expected_musical_tracks=4, expected_end_tick=END_TICK)
    return report
