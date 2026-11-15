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
