# Source audit

## Archives and integrity

The uploaded archive names end in `(2)`. They supply every original reference named as retained in the v0.63.2 repair, alongside the 28-file repair snapshot.

| Input | Contents | Integrity |
| --- | --- | --- |
| `AI_MIDI_IO_Knowledge_Backup_2026-11-15(2).zip` | Ten original source/reference files and `BACKUP_MANIFEST.json` | All ten files match the backup manifest's byte counts and SHA-256 hashes. Their sizes also match both repair metadata records. |
| Nested `AI_MIDI_IO_Python.zip` | Five ZIP directory entries and 35 Python modules, all within `mido/` | Nested ZIP CRCs and the outer manifest's hash for the exact nested ZIP match. The snapshot has no distribution metadata, full license file, or `packaging` source. |
| `AI_MIDI_IO_Repair_Update_0.63.2(2).zip` | Four metadata/instruction files, two lookup records, one migration note, 16 optimized references, two separate historical sources, and three executable Python files | The ZIP size, member count and SHA-256 match the historical repair report. The 18 added-source payloads match both repair metadata records. |
| `AI_MIDI_IO_Repair_Report(1).json` | Historical 24-test result, verification output, release metadata and repair constraints | Recorded as historical evidence. Reproduced execution and any environment differences are documented separately. |

All three ZIP containers passed CRC checks. The [machine-readable inventory](source_inventory.json) records every entry, including its exact source path, hash, size, category and detected Python imports. Archive and member hashes identify bytes and support comparison with the supplied manifests. The manifests provide no signature or authorship authentication.

The attached sources omit the icon at `assets/gpt-icon.jpg` that both plugin manifests reference and the `ai_midi_io_ios_fixed.html` app described by the iOS guide. The historical MIDI download named in the repair report is also absent from the attachments. The runnable verification generator can recreate the fixture. Neither missing UI asset affects local Python file generation.

## Executable source and attribution

| Source | Classification | Reusable engineering |
| --- | --- | --- |
| `scripts/ai_midi_io_runtime.py` | AI MIDI IO v0.63.2 integration code around mido and the standard library | Environment initialization, writable output directories, local ZIP fallback and optional legacy loader, absolute-to-delta scheduling, SMF chunk inspection and note-pair validation, diagnostic PCM generation, and ChatGPT sandbox links. |
| `scripts/generate_verification.py` | AI MIDI IO project-specific fixture | C-major melody with varying velocities, alternating-octave C bass, kick/snare on both beats 1 and 3, and a four-section pad progression (C–Am–F–G). The fixed arrangement also exercises metadata, GM program changes, the percussion channel, and note releases. |
| `tests/test_runtime.py` | AI MIDI IO standard-library `unittest` suite | 24 regression cases for initialization, ZIP extraction, MIDI event and structural checks, WAV generation, sandbox paths and the deterministic fixture. The suite's isolated ZIP test builds a synthetic archive containing both mido and packaging. |
| `MIDIFile.py` | Third-party MIDIUtil legacy writer supplied as a standalone module | Independent SMF writer with event classes, header/track serialization, VLQ helpers, controller and tuning message methods. Its low-level decoding helpers do not form a general MIDI reader. See the [legacy audit](LEGACY.md). |
| `AI_MIDI_IO_Python.zip` | Third-party mido source snapshot | MIDI message codecs, MIDI file reader/writer, track and meta-message utilities, parser/tokenizer, SysEx, optional backends, sockets and external-port CLI modules. These modules belong to mido. |

AI MIDI IO's Python code combines a runtime support layer with reusable scheduling, validation and PCM utilities. The file-generation workflow depends on mido's message types and codecs. The repair's short fixture is the only supplied project-specific, executable arrangement generator. The standalone legacy writer, nested third-party code, and embedded teaching examples account for the rest of the original Python material. Plugin instructions supplied a separate composition and decision workflow around those resources.

### Dependency map

| Source surface | Dependencies | Scope |
| --- | --- | --- |
| Repaired runtime | Python standard library plus mido. Optional dynamic import of the exact `MIDIFile.py` path. | The mido backend builds and reopens SMF exports. Validation adds its own checks above mido's reader. The sandbox link formatter applies to files below `/mnt/data`. |
| Repair fixture | Repaired runtime and mido | Calls the runtime to initialize, schedule, export and validate. Uses mido's tempo conversion and file length calculation. |
| Repair tests | `unittest`, mido, packaging, repaired runtime and fixture | Imports packaging for the synthetic fallback archive. Exercises portable helpers and one host-specific link path under `/mnt/data`. |
| Diagnostic tone | `math`, `struct`, `wave` | Local mono 16-bit PCM with a short envelope and sine, square, triangle or sawtooth waveform. |
| Legacy writer | `math`, `struct`, `warnings` | Optional independent writer. The current runtime can load its class, with separate behavior and API. |
| Bundled mido | Requires `packaging.version`. The version helper also has a conditional `importlib_metadata` fallback for older Python. | The historical ZIP includes mido sources only. Its optional backend modules separately refer to `rtmidi`, `rtmidi_python`, `pygame.midi`, a PortMidi native library, and the ALSA `amidi` command. The old `amidi.py` also references a missing internal `._common` module. |
| Knowledge snippets | Various examples reference `mido`, `midiutil`, legacy `MIDIFile`, `pygame.midi`, `pythonosc`, `numpy`, or only the standard library. | Example imports and suggested alternatives are historical. They are outside the installed project dependency surface. |

The unchanged v0.63.2 initializer was tested against the actual nested ZIP on Python 3.12. With Python's `-I` flag, system site-packages provided packaging and the absent mido import triggered successful extraction and initialization. The source-only mido import reported `0.0.0.dev0`, its fallback version when distribution metadata is absent. With both `-I -S`, the same run failed importing `packaging.version`, confirming the archive alone is insufficient. The source snapshot stays in the original attachment. The standalone install uses a declared mido distribution dependency.

## Reference map

| Subject | Original or historical material | Optimized reference material |
| --- | --- | --- |
| SMF, MIDI messages, encoding | `MIDI File Structure Guidelines.txt` | `MIDI_File_Structure_Guidelines.txt`, `MIDI_Binary_Output_Instructions.txt`, `MIDI_Message_Types.txt` |
| Scales, modes, chords and expressions | `MIDI_Scales_and_Theory.txt` covers roots/intervals, major/minor/pentatonic/chromatic/Dorian, triads, velocities and pitch bend | `MIDI_Scales_and_Theory.txt` |
| Rhythm, arpeggios and timing | `MIDI_Python.txt` includes MIDIUtil/mido generation, random melodies, rhythm, arpeggiated chords, VLQ and live-port examples | `MIDI_Python_Code.txt`, `MIDI_Arpeggios.txt`, `MIDI_Shuffle_and_Rhythms.txt`, `MIDI_Tempo_and_BPM.txt` |
| Instruments | `MIDI_Voice_Table.txt` provides GM program mapping | `MIDI_Voice_Table.txt`, `Lexicon_of_Instruments.txt` (hardware summaries and device-specific mappings) |
| CC, velocity and OSC | `MIDI_Control_Change_and_Velocity.txt`, `MIDI_CC to OSC Mapping Implementation Guide.txt` | `MIDI_Control_Change_and_Velocity.txt`, `MIDI_CC_to_OSC_Mapping.txt`, `OSC_Guidelines.txt` |
| Setup, diagnostic audio and historical prompts | `AI MIDI IO Guide.txt`, `set_project.txt`, preserved Custom GPT prompt, and iOS guide | `Core_Functionalities.txt`, `Example_User_Requests.txt`, `AI_MIDI_IO_TOC.md` |

Six optimized files have direct original counterparts. Five match after normalizing CRLF and LF. The only content change in the sixth replaces `from MIDIFile import MIDIFile` with `from midiutil import MIDIFile` in the opening structure-guide example. Other topics excerpt significant sections of the longer sources. For example, the binary guide overlaps with the structure guide's dictionary templates, the message-types guide shares text with the CC/velocity guide, and arpeggio/shuffle examples overlap with the Python guide. Preserve original and optimized bytes and source identities. Keep fixes in executable code and current documentation.

Several examples need interpretation before reuse. The old `set_project.txt` creates its knowledge directory before testing whether it exists, so its extraction branch can be skipped. It and the old guide contain damaged indentation and stale download links. The historical prompt imports NumPy in a velocity-scaling example that uses only builtin arithmetic and mido. Its assertions about Fourier processing and adaptive harmonic shaping have no corresponding executable files. The GM voice-table prose uses `C1 51` for Square Lead, while the same table assigns zero-based program 80 (hex `0x50`). The fixture uses 80. Device mappings in the lexicon require the relevant manufacturer documentation before use. None of these reference excerpts serve as executable tests or validated hardware definitions.

## Scope of the v0.63.2 execution baseline

| Capability | Code that implements it | Scope of evidence |
| --- | --- | --- |
| SMF generation, write and read | `mido.MidiFile`, `mido.MidiTrack`, `scheduled_track` and the fixture | Default writer/reader is mido. Fixture writes Type 1 with conductor and four musical tracks. The original validation precheck accepts PPQ SMF Types 0, 1 and 2; Type 0 and Type 2 lacked direct baseline test cases. |
| Timing, tempo, meter and expression | `scheduled_track`, mido meta/channel messages and fixture | Absolute ticks become delta ticks. The scheduler retains silence, and orders releases before retriggers on the same track and tick. Musical applications can construct tempo, meter, velocity, CC, program and pitch wheel events through mido. |
| File structure and note validity | `_check_smf_chunks` and `validate_midi` | The precheck checks chunk layout, header length, positive PPQ, declared track count and boundaries. The reopened message view checks track termination and note balance, reports same-pitch overlap, tracks channels/programs, and validates expected note-bearing track count or end tick when provided. The accepted export profile excludes SMPTE timing and unknown chunk types. |
| Musical structures | Fixed original fixture plus historical prose/example code | The original code has no general-purpose theory engine, arpeggiator, progression generator, humanization model or automatic arrangement system. |
| Audio | `write_test_tone` | Plain PCM oscillator diagnostic. No use of a MIDI sequence, GM instrument renderer, sample library, spectral processing, effects engine or instrument-faithful audio test. |
| Hardware ports, OSC, microtonal playback and mobile app | Third-party backend files and historical reference text | No project-level bridge or verified device/endpoint behavior. Legacy tuning-message encoding can be evaluated as file output independently of receiver behavior. The iOS app source is absent. |

Refer to current package/API documentation and the recorded test results for verified changes beyond this baseline.
