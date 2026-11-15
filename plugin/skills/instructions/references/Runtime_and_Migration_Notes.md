# AI MIDI IO 0.63.2: runtime and preservation notes

## Scope

This is an in-place repair of private plugin `plugin_e2c6d0aa1a648191ac5612f86daf6761`, starting from release `pluginrel_eb3288c6730481919339e3942cbcfef3` (0.63.1+bundle.5d5182aa5c389c4d78d789c357f2c46d). No plugin identity, icon, author, conversation starters, sharing, or external integrations are changed. The original release remains the pre-repair baseline; a complete local archive backup could not be retrieved in this environment.

## Preserved and added sources

All ten original reference files are retained at their existing paths without edits, including MIDIFile.py and AI_MIDI_IO_Python.zip. The update archive deliberately omits them so the backend keeps their stored bytes.

All sixteen entries of AI_MIDI_IO_Optimized_Files.zip are added under references/optimized/, byte-for-byte in the submitted patch: fifteen topic/example text files and one table-of-contents Markdown file. The contents index's relative links remain together with its source files. No assumption is made that these replace all detail in the older references.

The separate current prompt and iOS user guide are copied under references/source/. These are preserved source documents, not competing live skill instructions. The old prompt's internal relative links describe its original layout; use lookup/knowledge-index.json to resolve those names in this plugin. The iOS guide describes an HTML file that was not supplied. No browser application was fabricated or claimed repaired.

## Explicit execution changes

1. Replaced the migrated skill's unindented initialization code and hard-coded source-file locations with a standalone tested runtime. Reference paths and writable output paths are separate.
2. Removed unconditional printed readiness assertions from the active workflow. Initialization reports actual import paths and capability-specific results.
3. Corrected the extraction decision. The historical set_project example creates the target directory before testing whether it exists, so extraction can be skipped. The repaired code checks a content-keyed completion marker and actual package files, supports nested package layouts, and repairs an empty/stale extraction directory.
4. Replaced stale download URL construction in the active workflow with real file-existence checks and sandbox paths. Old source documents remain unchanged for provenance.
5. Resolved the writer conflict explicitly. The migrated skill mandates the standalone MIDIFile.py; the user's separately supplied current prompt and example generate files with mido. The repaired default uses mido, retains the original MIDIFile.py as an explicitly checked optional backend, and does not import or install midiutil. Default readiness does not imply legacy-backend readiness.
6. Kept local-only execution. An importable mido is used first; the existing bundled archive is the fallback if actually accessible. No pip, network installs, fabricated dependency modules, or hardware-port access are part of initialization.
7. Added structural export validation, note-release checks, event ordering, precise musical-versus-physical track reporting, and verified download links.
8. Preserved audio synthesis scope while labeling the included WAV helper accurately as a simple diagnostic tone generator, not an instrument renderer. The older guide's treatment of wave as an external library is not adopted: the helper uses the Python standard library.

## Validation performed for this repair

The included default-backend regression suite ran in this conversation's Python environment: 24 tests passed. The actual four-part fixture exported a type-1 MIDI file at 120 BPM in 4/4, 16 bars / 32 seconds, with four musical tracks plus a conductor track. It contains 268 note-on events, complete releases, GM percussion on code channel 9, and zero-based programs 80, 38, and 89 for the melodic parts. The output was reopened and inspected with mido, with independent chunk-length checks. PCM WAV test files for sine, square, triangle, and sawtooth were also generated and reopened.

Extraction tests used a temporary nested ZIP constructed from the locally installed mido and packaging source, including an isolated Python run with site-packages disabled. This validates the extraction and import mechanism, NOT the contents of the original stored AI_MIDI_IO_Python.zip.

## Not verified

- The original dependency ZIP could be listed but its binary contents were not downloaded into this runtime. It is preserved unchanged by the partial update.
- The exact original MIDIFile.py was inspected through the source reader but was not executed locally. The repaired default does not depend on its availability; requests specifically requiring it must validate it at runtime.
- Fresh-chat plugin loading after publication, FL Studio import/playback, auditory quality, hardware MIDI, OSC endpoints, and the missing iOS HTML application were not tested here.

Do not translate these scoped tests into a claim that every documented feature or every host environment has been validated.
