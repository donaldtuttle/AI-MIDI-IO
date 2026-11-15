# Python API

The reusable functions operate with Mido message objects. Applications can use Mido directly to edit events, select programs and write files.

| Module | Interface | Behavior |
| --- | --- | --- |
| `ai_midi_io.composition` | `scheduled_track(events, end_tick)` | Accepts an iterable of absolute integer tick and message pairs. Returns a `MidiTrack` with copied messages, delta times and one end-of-track marker. |
| `ai_midi_io.validation` | `validate_midi(path, *, expected_musical_tracks=None, expected_end_tick=None, require_complete_notes=True)` | Reopens a PPQ SMF and returns a JSON-compatible report. Raises `ValueError` for a file outside the accepted export profile, a structural error, a strict note-pairing error or a failed expectation. Filesystem errors propagate. |
| `ai_midi_io.project` | `initialize(reference_dir=None, output_root=None, require_midifile=False)` | Creates and probes `knowledge`, `midi_generation` and `wav_generation`. Returns `mido`, optional `MIDIFile` class, `paths` and `report`. |
| `ai_midi_io.demo` | `build_demo()` and `generate(output_root=None, references=None)` | Builds the deterministic four-part example in memory or initializes a project, saves the file and returns initialization plus verification reports. |
| `ai_midi_io.audio` | `write_test_tone(path, frequency=432.0, duration=0.5, waveform="sine", sample_rate=44100)` | Writes and reopens 16-bit mono PCM. Waveforms are `sine`, `square`, `triangle` and `sawtooth`. Frequency is in Hz and duration in seconds. |
| `ai_midi_io.runtime` | Compatibility exports and `sandbox_link(path, label="Download file")` | Re-exports legacy runtime functions. The link helper requires a nonempty file inside ChatGPT’s `/mnt/data` sandbox. |

## Timing and note accounting

- The scheduler preserves lead-in and tail silence. At equal ticks it puts non-note messages first, releases next and positive-velocity attacks last. Within each group input order is stable. A delta may be at most `0x0FFFFFFF`.
- For validation, event order within a track comes from the file. At the same absolute tick, across tracks, lower track index comes first. Type 0 and Type 1 note balance uses output port, channel and pitch, so a Type 1 track can release a note started in another track. The default output port is zero. Type 2 tracks are independent sequences.
- Both `note_off` and zero-velocity `note_on` release a note. Repeated attacks on an active key increase its count and record an overlap. A subsequent release decrements that count. This checks explicit events irrespective of sustain pedal, All Notes Off or synthesizer voice-stealing behavior.
- Set `require_complete_notes=False` to count unmatched releases and open attacks in inspection mode. Timing, chunk and event-framing checks still apply.

The validator reads the bytes once, independently checks the six-byte SMF header, declared chunks, event framing and termination, then reopens those same bytes with Mido. It accounts for timing from raw deltas, including unknown meta events. It reports the SHA-256, byte count, PPQ, format, end tick, number of physical track chunks, number of tracks with attacks, total attacks, overlap and release counts, per-track channels and programs, and tempo/meter events. Tempo is reported in microseconds per quarter note.

The accepted profile uses positive PPQ in ordinary `MThd`/`MTrk` files. SMPTE timing, container formats and additional chunk types are outside that profile. Specialized events remain subject to Mido’s decoding, including its handling of SysEx and `F7` escapes. Structural validation does not establish playback behavior on a particular synth or DAW.

## Project directories

Explicit arguments have priority over `AI_MIDI_IO_REFERENCE_DIR` and `AI_MIDI_IO_BASE_DIR`. Without either, the standalone package resolves `./references` and `./ai-midi-io-output` relative to the working directory. The plugin adapters default to the skill’s own references and `/mnt/data`.

For legacy compatibility, initialization can import an exact `MIDIFile.py` from the reference directory. If Mido is unavailable it can attempt to import from the historical local dependency bundle, with its prerequisites present. Supply trusted files only. Both routes load executable Python. Installing the package normally supplies Mido and requires neither archival file.

For standard file operations, see [Mido’s Standard MIDI File documentation](https://mido.readthedocs.io/en/stable/files/midi.html) and the [Standard MIDI Files specification](https://midi.org/standard-midi-files).
