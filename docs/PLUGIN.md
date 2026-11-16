# AI MIDI IO plugin integration

AI MIDI IO originated as a Custom GPT for AI-assisted MIDI composition and music-theory workflows. Its agent-facing plugin and skills provide musical instructions and reference context, while the maintained Python package supplies reproducible MIDI file generation and validation. This separation also allows developers to use the Python tools independently.

The plugin uses the same Python source as the standalone package. The two manifests, skill instructions, conversation starters, and lookups retain their supplied v0.63.2 bytes and plugin identity. The plugin version and the Python distribution version describe separate packages.

## Run the adapter locally

Install the standalone package first using the [repository instructions](../README.md). The plugin adapter keeps the original script filenames, `initialize(...)` arguments and return shape, and fixture entry point. It also keeps the plugin's `AI_MIDI_IO_BASE_DIR` and `AI_MIDI_IO_REFERENCE_DIR` overrides and `/mnt/data` output default. Use an explicit writable output path on other hosts.

```bash
python plugin/skills/instructions/scripts/ai_midi_io_runtime.py --output-root ./out
python plugin/skills/instructions/scripts/generate_verification.py --output-root ./out
```

The source checkout stores the verified legacy writer and its MIT license in `legacy/`. Pass `--references ./legacy --require-midifile` to the runtime command to load it directly. A built overlay places both files in the historical reference directory, where `initialize()` checks for the writer automatically.

## Build a source overlay

```bash
python tools/build_plugin.py dist/AI-MIDI-IO-plugin-overlay.zip
```

The builder copies the canonical `src/ai_midi_io/` Python modules into `skills/instructions/scripts/ai_midi_io/` for the plugin's import context. The package must accompany the entry scripts when transferring them into an execution environment without the installed distribution. For MIDI file work the host needs an importable `mido`, or access to its existing `AI_MIDI_IO_Python.zip` fallback and any dependencies it requires.

The two manifests refer to `assets/gpt-icon.jpg`, which is absent from the supplied archives. Use this bundle as an overlay that retains existing plugin assets. To assemble a fresh tree locally, provide the original icon with `--icon PATH`. To restore the historical dependency ZIP for a private overlay, pass `--original-backup PATH` pointing to the supplied knowledge backup. The builder verifies the recovered ZIP against the archived checksum and includes the Mido MIT notice. The historical bundle needs a separately available `packaging` dependency. The standard install supplies that dependency through `mido`.

The builder creates a local ZIP. Review the output and the publication decision before applying it to an existing plugin. Live installation, skill loading in a new hosted conversation, and remote updating require separate verification.

## Historical material

`plugin/skills/instructions/references/` carries the unchanged text reference files, the 16 optimized files, the original prompt, and the iOS guide. The optimized table of contents keeps its original relative links. The exact v0.63.2 runtime and verification generator, the repair report, and the backup manifest are stored under `plugin/provenance/`. The old executables are historical replay material. The overlay stages the maintained runtime and generator.

`plugin/skills/instructions/tests/test_runtime.py` preserves all 24 archived assertions. The repository's overlay test runs this exact suite against the staged adapter, using the installed test environment for Mido. The original sandbox URL test requires a writable `/mnt/data` and is skipped when that host path is unavailable.

```bash
python -m unittest discover -s tests -p test_plugin.py -v
```
