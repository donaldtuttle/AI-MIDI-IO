# AI MIDI IO

AI MIDI IO is a Python project for composing, organizing, and exporting MIDI data. It focuses on predictable event timing, clear musical structure, and file-based workflows that can be used in music production and automation.

The project originated as a MIDI composition and workflow system and is being developed into a standalone Python library. The goal is to make its core tools usable directly from Python without requiring a chat interface.

## Current implementation

The repository currently includes:

- **MIDI event scheduling:** Convert absolute-tick events to delta-tick messages for Standard MIDI File tracks.
- **Deterministic event order:** At matching tick positions, non-note events precede note releases and note onsets.
- **End-of-track handling:** Add an explicit end-of-track event at a specified tick.
- **Mido integration:** Work with Mido messages and MIDI tracks.

The package is under active development. Some modules referenced by the compatibility layer and command-line entry point are not yet included in the current branch. Installation and CLI functionality should be considered incomplete until those components are added and tested.

## Requirements

- Python 3.10 or later
- [Mido](https://mido.readthedocs.io/) 1.3.3 or compatible 1.x release

## Working with event schedules

The `scheduled_track` function accepts an iterable of `(absolute_tick, message)` pairs and an end tick. It returns a Mido `MidiTrack` with correctly calculated delta times.

```python
from mido import Message
from ai_midi_io.composition import scheduled_track

events = [
    (0, Message("note_on", note=60, velocity=96, channel=0)),
    (480, Message("note_off", note=60, velocity=0, channel=0)),
]

track = scheduled_track(events, end_tick=960)
```

Messages at the same tick are sorted by event type while preserving input order within each priority group. Invalid tick positions and delta times outside the Standard MIDI File limit raise `ValueError`.

## Development direction

The wider project is intended to support multitrack composition, project setup, MIDI file generation, validation, and repeatable musical workflows. Those features will be documented as they become available in the standalone package.

## Project background

AI MIDI IO was originally created by Donald Tuttle as a composition and MIDI workflow tool. This repository is the ongoing Python implementation of that work.
