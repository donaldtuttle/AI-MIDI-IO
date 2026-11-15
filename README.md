# AI MIDI IO

AI MIDI IO began as DT’s Custom GPT for designing MIDI compositions and guiding MIDI workflows. Its repaired v0.63.2 runtime is the starting point for this standalone Python package. The repository keeps the historical prompts and musical references alongside the tested file workflow and the plugin that uses it.

The package uses [Mido](https://mido.readthedocs.io/) to construct, serialize and reopen Standard MIDI Files. AI MIDI IO adds absolute-tick scheduling, structural validation, note accounting, project initialization and a reproducible four-part composition. All of these run locally without an AI account or service.

## Install

The package requires Python 3.10 or later. The included GitHub Actions workflow targets 3.10 through 3.14. See [test results](docs/TESTING.md) for the interpreters exercised during this reconstruction.

```sh
python -m venv .venv
# Activate .venv using your shell, then run:
python -m pip install .
ai-midi-io --help
```

The CLI is also available as `python -m ai_midi_io`. Mido 1.3.3 or a compatible 1.x release is the sole direct runtime dependency. Mido brings in `packaging`. Optional MIDI port backends are outside the install.
