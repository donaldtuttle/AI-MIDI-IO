---
name: ai-midi-io
description: "Generate, validate, and inspect Standard MIDI Files with the AI MIDI IO package. Use for multi-track composition, absolute-tick scheduling, structural validation, and reproducible MIDI workflows. Not for live hardware, OSC bridges, or DAW playback claims."
type: workflow
lifecycle: active
---

# AI MIDI IO — Local MIDI Composition and Validation

Generate and validate Standard MIDI Files using the AI MIDI IO package (Mido-based). Prefer the installed package over historical scripts or the legacy MIDIFile.py writer.

## Core Workflow

1. Preserve the user's requested tempo, meter, key, arrangement, instruments, and dynamics. Disclose any reasonable defaults.
2. Build events as absolute integer ticks + Mido messages.
3. Convert with `scheduled_track(events, end_tick)`.
4. For Type 1: include a conductor track (tempo + time signature) plus named musical tracks.
5. Save the file.
6. Validate with `validate_midi`. Supply expected musical track count and end tick when known.

## Generation Pattern

```python
from pathlib import Path
import mido
from ai_midi_io.composition import scheduled_track
from ai_midi_io.validation import validate_midi

path = Path("out.mid")
midi = mido.MidiFile(type=1, ticks_per_beat=480)

conductor = scheduled_track([
    (0, mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(120))),
    (0, mido.MetaMessage("time_signature", numerator=4, denominator=4)),
], end_tick=1920)
midi.tracks.append(conductor)

events = [
    (0, mido.Message("program_change", channel=0, program=0)),
    (0, mido.Message("note_on", channel=0, note=60, velocity=90)),
    (480, mido.Message("note_off", channel=0, note=60)),
]
midi.tracks.append(scheduled_track(events, end_tick=1920))
midi.save(path)

report = validate_midi(path, expected_musical_tracks=1, expected_end_tick=1920)
```

## Key Rules

- Channels in code: 0–15. GM percussion: channel 9.
- Programs: zero-based.
- Positive PPQ required. Verification fixture uses 480.
- Explicit note releases (note-off or zero-velocity note-on).
- Overlaps are reported, not rejected.
- Always validate generated files.

## Verification Fixture (reference only)

- 16 bars, C major, 120 BPM, 4/4
- 1 conductor + 4 musical tracks
- End tick: 30720
- PPQ: 480
- Use for regression checks, not as a substitute for user compositions.

## Boundaries

- Do not claim live MIDI, OSC, hardware, or DAW playback succeeded.
- Do not invent sandbox links or file paths.
- Do not execute historical knowledge-library examples unchanged.
- Structural validation does not prove musical quality or DAW compatibility.
- Diagnostic WAV tones are not MIDI renders.

## Knowledge References

The plugin knowledge library (scales, voices, CC, structure, theory) is available for musical ideas. Prefer optimized references when present. Execution still goes through the package API and `validate_midi`.
