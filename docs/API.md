# AI MIDI IO API

The public runtime is intentionally small. It writes, reads, and validates
Standard MIDI Files. It does not synthesize audio or interpret musical intent.

## Runtime

```python
from ai_midi_io import MidiRuntime

runtime = MidiRuntime()
path = runtime.write_verification_fixture()
report = runtime.validate(path)
```

`MidiRuntime.write_verification_fixture()` returns a `pathlib.Path` to a
temporary SMF Type 1 file at 480 ticks per beat. The fixture has four tracks
and is the canonical verification case used by the tests and the plugin overlay.

`MidiRuntime.validate(path)` returns a dictionary with the SHA-256 digest, byte
count, SMF type, ticks per beat, track count, and per-track event accounting.

## Composition helpers

The `composition` module contains the note and track builders used by the
verification fixture and the demo. They are stable enough for internal use but
are not yet a public composition API.

## Audio preview

`ai_midi_io.audio` can render a short preview using the system MIDI synthesizer
when one is available. It is optional and not required for the core runtime.

## CLI

```bash
python -m ai_midi_io validate path/to/file.mid
python -m ai_midi_io fixture
```

The CLI is a thin wrapper around the runtime. It is suitable for scripts and
CI.
