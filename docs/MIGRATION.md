# Migration Notes

This package replaces earlier ad-hoc MIDI writing scripts with a structured runtime, validation layer, and reproducible demo.

Key changes:

- Absolute-tick scheduling instead of delta-only thinking.
- Explicit conductor track and PPQ 480.
- Structural validation and note accounting.
- Plugin knowledge overlay kept separate from the core package.

See `docs/LEGACY.md` for the relationship to the original MIDIFile.py.
