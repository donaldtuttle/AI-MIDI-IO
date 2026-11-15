# API Reference

AI MIDI IO provides a small, focused set of modules for building, validating, and exporting Standard MIDI Files.

## Core modules

- `ai_midi_io.runtime` — absolute-tick scheduler and SMF writer built on Mido.
- `ai_midi_io.validation` — structural checks, note accounting, and end-tick verification.
- `ai_midi_io.composition` — helpers for scales, arpeggios, and multi-track arrangement.
- `ai_midi_io.project` — project initialization and path conventions.
- `ai_midi_io.cli` — command-line interface (`ai-midi-io` and `python -m ai_midi_io`).
- `ai_midi_io.demo` — reproducible four-track verification composition.

See the source and tests for the exact contracts. The verification fixture in `examples/verification/` is the canonical output of the demo.
