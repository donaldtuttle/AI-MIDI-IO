# Source inventory

This document lists the files that make up the AI MIDI IO distribution and
notes their roles.

See `docs/source_inventory.json` for the machine-readable form.

## Package

- `src/ai_midi_io/` — runtime, composition helpers, validation, CLI
- `pyproject.toml` — packaging
- `tests/` — unit and compatibility tests

## Documentation

- `docs/` — API, migration, plugin, testing, and inventory notes
- `README.md` — project overview

## Legacy

- `legacy/MIDIFile.py` — original single-file writer
- `legacy/License.txt` — its license
- `legacy/notices/` — third-party notices

## Plugin

- `plugin/` — AI skill overlay and knowledge base

## Examples

- `examples/verification/` — validation report and (optional) binary fixture
