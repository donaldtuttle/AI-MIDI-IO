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
ROLES = (
    ("Melody - Square Lead", 0, 80),
    ("Bass - Synth Bass 1", 1, 38),
    ("Drums - GM channel 10", 9, None),
    ("Harmony - Warm Pad", 2, 89),
)


def build_demo() -> MidiFile:
    """Build the original v0.63.2 verification composition in memory."""
    import mido

    midi = mido.MidiFile(type=1, ticks_per_beat=PPQ)
    conductor = [
        (0, mido.MetaMessage("track_name", name="Conductor")),
        (0, mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(BPM))),
        (0, mido.MetaMessage("time_signature", numerator=4, denominator=4)),
        (0, mido.MetaMessage("key_signature", key="C")),
    ]
    midi.tracks.append(scheduled_track(conductor, END_TICK))

    event_sets = []
    for name, channel, program in ROLES:
        events = [(0, mido.MetaMessage("track_name", name=name))]
        if program is not None:
            events.append((0, mido.Message("program_change", channel=channel, program=program)))
        event_sets.append(events)

    def note(track: int, pitch: int, start: int, length: int, velocity: int) -> None:
        channel = ROLES[track][1]
        attack = mido.Message("note_on", channel=channel, note=pitch, velocity=velocity)
        release = mido.Message("note_off", channel=channel, note=pitch, velocity=0)
        event_sets[track].extend([(start, attack), (start + length, release)])

    phrase = (60, 64, 67, 72, 71, 67, 64, 62)
    for bar in range(BARS):
        origin = bar * BEATS_PER_BAR * PPQ
        for step, pitch in enumerate(phrase):
            note(0, pitch, origin + step * PPQ // 2, PPQ // 2, 83 + step % 3 * 5 + bar % 4 * 2)
        for beat in range(BEATS_PER_BAR):
            note(1, 36 if beat % 2 == 0 else 48, origin + beat * PPQ, 3 * PPQ // 4, 92 + beat % 2 * 7)
        # The original prompt specifies both kick and snare on beats 1 and 3.
        for beat in (0, 2):
            note(2, 36, origin + beat * PPQ, PPQ // 8, 108)
            note(2, 38, origin + beat * PPQ, PPQ // 8, 91)

    chords = ((60, 64, 67), (57, 60, 64), (53, 57, 60), (55, 59, 62))
    section_ticks = 4 * BEATS_PER_BAR * PPQ
    for section, chord in enumerate(chords):
        for voice, pitch in enumerate(chord):
            note(3, pitch, section * section_ticks, section_ticks, 62 + voice * 4)

    for events in event_sets:
        midi.tracks.append(scheduled_track(events, END_TICK))
    return midi


def generate(output_root: Path | None = None, references: Path | None = None) -> dict:
    """Save and reopen the demo, returning initialization and validation reports."""
    runtime = initialize(references, output_root)
    output = runtime["paths"]["midi_generation"] / MIDI_FILENAME
    build_demo().save(filename=output)
    report = validate_midi(output, expected_musical_tracks=4, expected_end_tick=END_TICK)
    duration = runtime["mido"].MidiFile(output).length

    tracks = report["tracks"]
    track_programs = [
        [] if program is None else [{"tick": 0, "channel": channel, "program": program}]
        for _, channel, program in ROLES
    ]
    if (
        [track["notes"] for track in tracks] != [0, 128, 64, 64, 12]
        or [track["channels"] for track in tracks] != [[], [0], [1], [9], [2]]
        or [track["programs"] for track in tracks] != [[], *track_programs]
        or report["note_overlaps"]
        or duration != 32.0
    ):
        raise RuntimeError("Generated MIDI does not match the verification composition")

    report.update({
        "bars": BARS,
        "bpm": BPM,
        "time_signature": "4/4",
        "key_signature": "C",
        "backend": "mido",
        "duration_seconds": duration,
        "fixture_not_auditioned": True,
    })
    return {"initialization": runtime["report"], "midi": report}


def main(
    argv: Sequence[str] | None = None,
    *,
    default_output_root: Path | None = None,
    default_references: Path | None = None,
) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=default_output_root)
    parser.add_argument("--references", type=Path, default=default_references)
    args = parser.parse_args(argv)
    print(json.dumps(generate(args.output_root, args.references), indent=2))


if __name__ == "__main__":
    main()
