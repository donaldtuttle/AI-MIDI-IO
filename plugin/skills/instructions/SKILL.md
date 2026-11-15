---
name: instructions
description: Create, edit, analyze, and validate multitrack MIDI files; develop musical ideas, scales, arpeggios, rhythm, CC modulation, and sound-design experiments using AI MIDI IO's reference library. Use when AI MIDI IO is invoked or the user requests this MIDI workflow.
---

# AI MIDI IO

Help musicians, composers, and developers create and manipulate MIDI, develop compositions, and explore sound design. Preserve the user's requested tempo, meter, key or tuning, arrangement, instruments, dynamics, and workflow. Treat musical suggestions as proposals, not restrictions. Do not replace a user's arrangement or introduce a GUI, live bridge, extra installation, or unrelated features without a reason tied to the request.

## Source library and precedence

Read `lookup/knowledge-index.json` to locate the relevant references, then read the actual source material needed for the task. Resolve indexed paths from this skill's root, not from `lookup/` or the working directory. A filename or an earlier summary is not a substitute for its contents.

The original ten migrated reference files remain unchanged under `references/`. All sixteen files from the user's optimized ZIP are preserved under `references/optimized/`, including its table of contents. The separately supplied current prompt and iOS guide are preserved under `references/source/`. Do not assume that an optimized version contains all details in its original counterpart. Compare them when the difference matters.

**For execution, use this skill and the repaired scripts.** Older setup examples in `AI MIDI IO Guide.txt`, `set_project.txt`, and the source prompt are historical references, not competing initializers. They include broken indentation, environment/path assumptions, conflicting library requirements, and stale links. Do not run those examples unchanged. The explicit repairs and remaining limitations are recorded in `references/Runtime_and_Migration_Notes.md`.

### Reading map

| Task | Start with |
| --- | --- |
| Project setup, downloads, validation | `scripts/ai_midi_io_runtime.py`; `references/Runtime_and_Migration_Notes.md` |
| Scales, harmony, voicing, alternative tunings | `references/optimized/MIDI_Scales_and_Theory.txt` and the original counterpart |
| Arpeggios and rhythmic feel | `references/optimized/MIDI_Arpeggios.txt`; `MIDI_Shuffle_and_Rhythms.txt` in the same directory |
| Tempo and meter | `references/optimized/MIDI_Tempo_and_BPM.txt` |
| MIDI messages, file structure, binary output | `references/optimized/MIDI_Message_Types.txt`, `MIDI_File_Structure_Guidelines.txt`, `MIDI_Binary_Output_Instructions.txt` |
| Velocity, CC, and modulation | `references/optimized/MIDI_Control_Change_and_Velocity.txt` and the original counterpart |
| General MIDI program assignments | `references/optimized/MIDI_Voice_Table.txt` |
| Instrument-specific concepts | `references/optimized/Lexicon_of_Instruments.txt`; verify exact hardware implementation separately |
| MIDI/OSC design | `references/optimized/MIDI_CC_to_OSC_Mapping.txt`; `OSC_Guidelines.txt` in the same directory |
| Source examples and capabilities | `references/optimized/Core_Functionalities.txt`, `Example_User_Requests.txt`, `MIDI_Python_Code.txt` |
| Original standalone MIDIFile API | `references/MIDIFile.py`, read the actual implementation before using an unfamiliar call |
| iOS browser guidance | `references/source/AI_MIDI_IO_iOS_User_Guide(20261115-134555).md` |

The reference documents describe capabilities and examples. They do not establish that a runtime, audio renderer, browser API, network service, or hardware connection is currently available. Keep source-derived facts, proposed implementation, and actual test results distinct. Preserve source text rather than silently rewriting it to resolve disagreements.

## Set project and runtime initialization

Run initialization before generating, editing, or programmatically analyzing files, and whenever the user explicitly says **set project**. Pure music-theory discussion does not need to create files or run diagnostics.

1. Establish whether a Python execution tool is actually available. Never claim an operation ran merely because Python code was written.
2. Locate `scripts/ai_midi_io_runtime.py` and the actual reference directory. Plugin resource URIs are not filesystem paths. If files are not mounted, retrieve the necessary packaged source using the available skill/file tools and save an exact text copy in the working runtime. Pass the known reference directory explicitly when a script is copied alone. Do not invent a mounted path or recreate a third-party dependency from memory.
3. Use the repaired `initialize(reference_dir=..., output_root=...)` function. The output root defaults to `/mnt/data`, or the existing `AI_MIDI_IO_BASE_DIR` environment setting. It creates and checks `knowledge`, `midi_generation`, and `wav_generation` directories.
4. `mido` is the default writer/reader, matching the user's separately supplied current prompt. Use an importable local copy. If it is unavailable, the initializer can extract the actual bundled `AI_MIDI_IO_Python.zip` into a content-keyed cache and locate nested package directories. It checks real package files, not just whether an output directory exists. No pip or network installation is performed.
5. The original `MIDIFile.py` is retained as an optional legacy backend. The initializer imports that exact file only when accessible. For a task specifically using that API, call `initialize(..., require_midifile=True)` and stop that operation if the import fails. Do not substitute the installed `midiutil` package or claim that the legacy backend loaded when it did not.
6. Report measured readiness briefly. Default-backend readiness is not proof that the optional legacy writer, OSC, audio rendering, or hardware MIDI is available. If a required dependency is missing, name the actual missing file/import and the failed operation. Do not fabricate successful status output.

When scripts are present on the filesystem, add the discovered `scripts` directory to `sys.path`, then use:

```python
from ai_midi_io_runtime import initialize
runtime = initialize(reference_dir=actual_reference_directory)
mido = runtime["mido"]
print(runtime["report"])
```

`actual_reference_directory` must be a path verified in the current session, not a literal placeholder passed to Python. Code-only responses must be labeled as unexecuted when no runtime is available.

## MIDI composition and delivery

Use the user's musical brief. If essential musical choices are unspecified, select reasonable choices and disclose them briefly. Do not substitute a fixed demo for a requested composition.

- Construct separate named musical tracks. With Standard MIDI File type 1, use a conductor track for tempo/meter; distinguish musical-track count from physical track-chunk count.
- Preserve tempo maps, rests, lead-in, and arrangement tails. With `mido`, saved message times are delta ticks, not seconds; an absolute event schedule can be converted using `scheduled_track`. It orders releases before retriggers at the same tick and adds the requested final end-of-track time.
- Use MIDI channel numbers 0 through 15 in code. General MIDI percussion uses channel 9 in code, conventionally called channel 10. General MIDI programs are zero-based in messages. Do not assume an arbitrary hardware synth implements GM, a specific CC, or a tuning standard.
- Support velocity, CC, pitch bend, tempo changes, harmony, and arpeggios as requested. Keep valid data ranges and preserve intentional overlaps; do not manufacture a rule that all overlapping same-pitch notes are invalid.
- For A4=432 Hz or microtuning, name the actual tuning mechanism and receiver requirements. A note-number sequence or text label alone does not retune playback. Do not claim that channel-wide pitch bend provides independent polyphonic note tuning.
- Save the real file in the current runtime. Then call `validate_midi(path, ...)` to reopen it and check chunk structure, positive PPQ timing, delta times, end-of-track events, note balance, and requested counts/duration where applicable. This helper is for generated PPQ exports; it is not a universal validator for every MIDI timing mode.
- Inspect the actual program/channel assignments, musical constraints, and expected event counts for the specific request. Structural validation is not proof that a composition sounds good or imports correctly into an untested DAW.
- Return `sandbox_link(path, label)` only after the file exists and is nonempty. Use a real `sandbox:/mnt/data/...` link, never encoded `{file_path}` placeholders or old conversation/message query strings.

`scripts/generate_verification.py` is a deterministic regression fixture based on the original four-part starter prompt. Use it for diagnostics, not automatically for user compositions. `tests/test_runtime.py` contains regression checks for the repaired default workflow.

## Audio and modulation

Retain the source prompt's scope for waveform synthesis, harmonic processing, dynamic modulation, and WAV experiments. Check available local modules before implementing a requested operation. `wave` is Python's standard-library WAV writer; no external installation is needed for it.

`write_test_tone` provides a validated simple PCM diagnostic tone with four waveform choices. It is not a GM renderer and does not render a MIDI arrangement. For actual MIDI-to-audio work, establish the available instrument renderer or implement the requested synthesis explicitly. Distinguish an approximate synthesized preview from the sound of the user's hardware. Verify the WAV header, duration, and samples after writing; never claim listening or sound quality verification without an actual audition.

## Live hardware, OSC, and iOS boundaries

The migrated package is a skills/reference plugin, not a live MIDI/OSC bridge. Preserve the design references without treating them as evidence of a running integration. Do not open hardware ports, send MIDI/OSC, reset devices, or launch persistent services as a side effect of setup. A live request needs an explicitly available backend, verified device/endpoint, and appropriate user authorization.

The iOS guide is included, but its referenced HTML application was not supplied and is not added by this repair. Do not claim to have tested that application. Browser hardware support and compatibility require current verification when relevant.
