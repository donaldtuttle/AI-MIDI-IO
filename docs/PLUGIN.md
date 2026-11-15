# Plugin overlay

The `plugin/` directory is an AI-agent skill overlay for the AI MIDI IO runtime.
It is not required to use the Python package.

## Layout

- `plugin.json` — plugin metadata
- `skills/instructions/` — skill definition, knowledge references, and scripts
- `provenance/` — repair reports and earlier snapshots

The skill expects the runtime to be available on the Python path so that
verification can call `ai_midi_io` directly.

## Knowledge

Reference files under `skills/instructions/references/` contain MIDI theory,
file-structure notes, and worked examples. They are plain text so they can be
included in an agent context window.

Optimized versions live under `references/optimized/`.

## Verification

The skill can generate and validate the canonical 4-track fixture using the
runtime. See `skills/instructions/scripts/generate_verification.py`.
