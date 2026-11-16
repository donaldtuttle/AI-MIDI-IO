---
name: ai-midi-io
description: Generate, inspect and validate Standard MIDI Files with the AI MIDI IO Python toolkit. Use for multitrack composition, event scheduling, MIDI theory and reproducible MIDI file exports.
---

# AI MIDI IO: MIDI composition and validation

Use the bundled AI MIDI IO Python modules and Mido library when an executable Python environment is available. Preserve requested tempo, time signature, key, duration, channel, General MIDI program, musical role and dynamics. Do not invent execution results, file paths, or MIDI playback that has not occurred.

## Start here

- The source package is bundled under `scripts/ai_midi_io/`; runtime adapters are in `scripts/`.
- Read `references/QUICK_REFERENCE.md` for MIDI channel numbers, tempo calculations and common controls.
- Standard MIDI File creation and validation require `mido>=1.3.3,<2`. The plugin does not install dependencies or grant access to an execution environment by itself.
- If Python execution or Mido is unavailable, provide clear, executable code and instructions rather than claiming a generated file exists.
- The legacy MIDIUtil writer in `references/MIDIFile.py` is optional and retains its upstream license. The maintained runtime uses Mido.

## Composition workflow

1. Establish explicit tempo, meter, key, track roles, bars, General MIDI instruments and rhythmic feel; state any defaults.
2. Use absolute integer ticks with Mido `Message` and `MetaMessage` objects. Choose positive `ticks_per_beat` (the regression fixture uses 480).
3. Convert scheduled events using `ai_midi_io.composition.scheduled_track(events, end_tick)`. At shared ticks, note releases precede retriggers.
4. For Type 1 MIDI, add a conductor track carrying tempo, meter and other global metadata, followed by musical tracks on their intended channels. Channel 9 in code is GM percussion channel 10.
5. Save `.mid`, reopen and validate with `ai_midi_io.validation.validate_midi` using expected track count and end tick where available.
6. Report the actual file path, validation results, note count and any errors only after they have been measured. Do not call MIDI file validation an audible playback test.

## Example

```python
from pathlib import Path
import mido
from ai_midi_io.composition import scheduled_track
from ai_midi_io.validation import validate_midi

path = Path('demo.mid')
midi = mido.MidiFile(type=1, ticks_per_beat=480)
midi.tracks.append(scheduled_track([
    (0, mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(120))),
    (0, mido.MetaMessage('time_signature', numerator=4, denominator=4)),
], end_tick=1920))
midi.tracks.append(scheduled_track([
    (0, mido.Message('program_change', channel=0, program=80)),
    (0, mido.Message('note_on', channel=0, note=60, velocity=90)),
    (480, mido.Message('note_off', channel=0, note=60)),
], end_tick=1920))
midi.save(path)
print(validate_midi(path, expected_musical_tracks=1, expected_end_tick=1920))
```

## Reproducible four-track fixture

The bundled generation script `scripts/generate_verification.py` builds a 16-bar C-major composition in 4/4 at 120 BPM, with melody, bass, drums and pad parts, plus conductor. Expected PPQ is 480 and end tick is 30,720. The source-generated MIDI and validation output are reference fixtures, not claims of musical quality.

## Musical guidance

Offer scales, chords, progressions, voice leading, arpeggiation, and CC automation as musical guidance. Distinguish theory ideas from capabilities implemented by this Python runtime. There is no native hardware MIDI transport, DAW control, OSC bridge, or audio rendering of General MIDI instruments within the Python package. The separate Windows MIDI Player can play exported files, but is not bundled in this plugin.

## File delivery and safety

Only present links to actual generated files after verifying that they exist and are nonempty in the execution environment. Do not assume a specific sandbox or filesystem is available. Do not install packages, access local devices, transmit data, or create network connections unless the user's environment and tools permit it.
