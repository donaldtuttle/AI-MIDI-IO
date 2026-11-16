# MIDI essentials for AI MIDI IO

This is a short, independently authored reference for the public plugin. Extended historical reference archives are not part of the distributable package.

## Standard MIDI Files

- Type 0: all channel messages in one track.
- Type 1: simultaneous tracks, typically with a conductor track containing tempo and meter.
- Type 2: independent sequential patterns; not the default for shared-time arrangements.
- PPQ determines ticks per quarter note. At 480 PPQ, a 4/4 bar is 1,920 ticks.
- MIDI channel numbers in the Python API range from 0 to 15. General MIDI percussion uses channel index 9, conventionally called channel 10.
- General MIDI program numbers in Mido are zero-based. For example: Acoustic Grand Piano = 0, Lead 1 (square) = 80, Pad 2 (warm) = 89.

## Timing

MIDI tempo meta messages store microseconds per quarter note. BPM = 60,000,000 / microseconds_per_beat. At 120 BPM, tempo = 500,000.

At `ticks_per_beat=480`, quarter note=480 ticks, eighth note=240 ticks, and sixteenth note=120 ticks. Meter is separately encoded in `time_signature` metadata.

## Standard channel events

- `note_on` velocity 1 to 127 starts a note; zero-velocity note-on is commonly treated as note-off.
- `note_off` explicitly ends a pitch on its channel.
- `program_change` selects an instrument preset, interpreted by the receiver.
- `control_change` sets controllers (for example, CC1 modulation, CC7 volume, CC10 pan, CC11 expression, CC64 sustain).
- `pitchwheel` changes pitch subject to the receiving instrument's bend range.

## Validation

Match notes by channel and pitch; track exact tick positions and report overlaps rather than silently deleting them. Verify legal SMF header and track framing, end-of-track events, expected bar duration, intended programs, and explicit releases. Structural validation is not an audible performance check.
