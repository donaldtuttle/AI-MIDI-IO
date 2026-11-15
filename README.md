# AI MIDI IO

AI MIDI IO is a Python toolkit for MIDI composition, Standard MIDI File generation, structural validation, and repeatable music-production workflows. It combines a standalone command-line interface with reusable Python modules and a companion plugin.

The package uses [Mido](https://mido.readthedocs.io/) to construct, serialize and reopen Standard MIDI Files. AI MIDI IO adds absolute-tick scheduling, structural validation, note accounting, project initialization and a reproducible four-part composition. The core file workflows run locally without a hosted service.

## Install

The package requires Python 3.10 or later. The included GitHub Actions workflow targets 3.10 through 3.14. See [test results](docs/TESTING.md) for verified interpreters and execution environments.

```sh
python -m venv .venv
# Activate .venv using your shell, then run:
python -m pip install .
ai-midi-io --help
```

The CLI is also available as `python -m ai_midi_io`. Mido 1.3.3 or a compatible 1.x release is the sole direct runtime dependency. Mido brings in `packaging`. Optional MIDI port backends are outside the install.

## Generate and validate MIDI

```sh
ai-midi-io demo --output-root ./out > demo-report.json
ai-midi-io validate out/midi_generation/AI_MIDI_IO_Verification_4track_120BPM.mid \
  --expected-musical-tracks 4 --expected-end-tick 30720
```

The demo has four musical tracks plus one conductor track. It runs for 16 bars in C major at 120 BPM in 4/4. The repository includes the [MIDI file and validation report](examples/README.md).

Create your own one-track export with Mido messages and the AI MIDI IO scheduler.

```python
from pathlib import Path

import mido

from ai_midi_io.composition import scheduled_track
from ai_midi_io.validation import validate_midi

path = Path("two-notes.mid")
midi = mido.MidiFile(type=0, ticks_per_beat=480)
events = [
    (0, mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(120))),
    (0, mido.MetaMessage("time_signature", numerator=4, denominator=4)),
    (0, mido.Message("program_change", channel=0, program=0)),
    (0, mido.Message("note_on", channel=0, note=60, velocity=90)),
    (480, mido.Message("note_off", channel=0, note=60)),
    (480, mido.Message("note_on", channel=0, note=64, velocity=83)),
    (960, mido.Message("note_off", channel=0, note=64)),
]
midi.tracks.append(scheduled_track(events, end_tick=1920))
midi.save(path)
print(validate_midi(path, expected_musical_tracks=1, expected_end_tick=1920))
```

For a Type 1 arrangement, append a conductor track with tempo and meter, then append the named musical tracks. Use Mido’s zero-based channels and GM programs. GM percussion is code channel `9`, which is channel 10 in MIDI convention.

## Repository layout

| Path | Contents |
| --- | --- |
| `src/ai_midi_io/` | Installable scheduling, validation, project initialization, diagnostic WAV, example composition and CLI |
| `plugin/` | Plugin configuration, preserved reference material, adapters, and versioned source snapshots |
| `legacy/` | Independently evaluated MIDIUtil writer and applicable third-party notices |
| `examples/` | Reproducible MIDI fixture with its validation report |
| `tests/` | Standalone package and staged plugin tests |
| `tools/build_plugin.py` | Local plugin overlay builder using the same package source |

## Documentation

- [Python API and file validation](docs/API.md)
- [Source audit and dependency map](docs/SOURCE_INVENTORY.md)
- [Legacy backend and dependency provenance](docs/LEGACY.md)
- [Plugin integration and overlay build](docs/PLUGIN.md)
- [Runtime and plugin migration notes](docs/MIGRATION.md)
- [Testing and performance](docs/TESTING.md)
- [Changelog](CHANGELOG.md) and [roadmap](docs/ROADMAP.md)

## Scope

The package handles PPQ Standard MIDI Files and explicit note releases. Type 0 and Type 1 exports are exercised, and the validator checks Type 2 sequences independently. The validator reports same-pitch overlaps and preserves them in the file workflow. Hardware MIDI, OSC, receiver-side tuning, DAW playback and the mobile browser app were outside the verified runtime. The WAV helper generates four diagnostic oscillator shapes as mono PCM. The scale, rhythm, arpeggio, instrument and tuning documents remain available as musical references.

## Authorship and licensing

Donald Tuttle created AI MIDI IO. Mark Conway Wirt’s MIDIUtil writer and the Mido project retain their respective attribution and MIT license terms. Historical source references are preserved with their provenance. See [licensing and publication review](docs/LICENSING.md) for third-party notices and prerequisites for a public release.

## Run the tests

```sh
python -m unittest discover -s tests -v
python -m unittest discover -s legacy -p test_backend.py -v
python -m unittest discover -s plugin/skills/instructions/tests -v
```
