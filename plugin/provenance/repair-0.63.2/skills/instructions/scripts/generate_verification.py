"""Deterministic verification fixture for the original four-part project prompt.

This is a file/runtime test, not a replacement for a user-directed composition.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from ai_midi_io_runtime import initialize, scheduled_track, validate_midi


def generate(output_root: Path, references: Path | None = None) -> dict:
    runtime = initialize(references, output_root)
    mido = runtime["mido"]
    ppq, bars, bpm = 480, 16, 120
    end_tick = bars * 4 * ppq
    mid = mido.MidiFile(type=1, ticks_per_beat=ppq)
    conductor = [(0, mido.MetaMessage("track_name", name="Conductor")),
                 (0, mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(bpm))),
                 (0, mido.MetaMessage("time_signature", numerator=4, denominator=4)),
                 (0, mido.MetaMessage("key_signature", key="C"))]
    mid.tracks.append(scheduled_track(conductor, end_tick))
    roles = [("Melody - Square Lead", 0, 80), ("Bass - Synth Bass 1", 1, 38),
             ("Drums - GM channel 10", 9, None), ("Harmony - Warm Pad", 2, 89)]
    event_sets = []
    for name, channel, program in roles:
        events = [(0, mido.MetaMessage("track_name", name=name))]
        if program is not None:
            events.append((0, mido.Message("program_change", channel=channel, program=program)))
        event_sets.append(events)

    def note(track, pitch, start, length, velocity):
        channel = roles[track][1]
        event_sets[track].append((start, mido.Message("note_on", channel=channel, note=pitch, velocity=velocity)))
        event_sets[track].append((start + length, mido.Message("note_off", channel=channel, note=pitch, velocity=0)))

    phrase = [60, 64, 67, 72, 71, 67, 64, 62]
    for bar in range(bars):
        origin = bar * 4 * ppq
        for step, pitch in enumerate(phrase):
            note(0, pitch, origin + step * ppq // 2, ppq // 2, 83 + step % 3 * 5 + bar % 4 * 2)
        for beat in range(4):
            note(1, 36 if beat % 2 == 0 else 48, origin + beat * ppq, 3 * ppq // 4, 92 + beat % 2 * 7)
        # Literal interpretation of the starter: kick AND snare on beats 1 and 3.
        for beat in (0, 2):
            note(2, 36, origin + beat * ppq, ppq // 8, 108)
            note(2, 38, origin + beat * ppq, ppq // 8, 91)
    for section, chord in enumerate(((60, 64, 67), (57, 60, 64), (53, 57, 60), (55, 59, 62))):
        for voice, pitch in enumerate(chord):
            note(3, pitch, section * 16 * ppq, 16 * ppq, 62 + voice * 4)
    for events in event_sets:
        mid.tracks.append(scheduled_track(events, end_tick))
    output = runtime["paths"]["midi_generation"] / "AI_MIDI_IO_Verification_4track_120BPM.mid"
    mid.save(str(output))
    report = validate_midi(output, expected_musical_tracks=4, expected_end_tick=end_tick)
    report.update({"bars": bars, "bpm": bpm, "time_signature": "4/4", "backend": "mido",
                   "duration_seconds": mido.MidiFile(str(output)).length,
                   "fixture_not_auditioned": True})
    expected_counts = [0, 128, 64, 64, 12]
    assert [t["notes"] for t in report["tracks"]] == expected_counts
    assert report["note_overlaps"] == []
    assert report["duration_seconds"] == 32.0
    assert [t["channels"] for t in report["tracks"]] == [[], [0], [1], [9], [2]]
    assert [t["programs"] for t in report["tracks"]] == [[],
        [{"tick": 0, "channel": 0, "program": 80}],
        [{"tick": 0, "channel": 1, "program": 38}], [],
        [{"tick": 0, "channel": 2, "program": 89}]]
    return {"initialization": runtime["report"], "midi": report}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=Path("/mnt/data"))
    parser.add_argument("--references", type=Path)
    args = parser.parse_args()
    print(json.dumps(generate(args.output_root, args.references), indent=2))
