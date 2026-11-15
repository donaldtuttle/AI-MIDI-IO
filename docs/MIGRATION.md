# Runtime and plugin compatibility

The v0.63.2 runtime and verification fixture define the original compatibility baseline. The archived materials include the legacy writer, Mido source ZIP and historical references. Reference scripts, tests, manifests and reports are retained under their documented paths.

| Surface | Compatibility behavior |
| --- | --- |
| Project setup | Moved the existing initialized directories, write probes, backend checks and return schema into `project.py`. The standalone package uses working-directory defaults. The plugin adapter retains historical defaults and environment overrides. |
| Dependency fallback | Retains the local ZIP option for existing plugin deployments. Extracts a stable snapshot of the ZIP into a content-keyed cache and promotes each complete tree without deleting trees another process may use. Installed Mido remains the default. |
| Scheduling | Retains release-before-retrigger order and explicit silence. Accepts an iterable and checks the SMF four-byte delta limit before writing. |
| Validation | Retains strict note releases, overlap reporting and per-track counts. Adds optional note-balance inspection, tempo/meter events, MIDI port-aware pairing and raw event framing before Mido decode. Raw deltas fix reporting for unknown meta events. |
| MIDI fixture | Reuses the established C-major arrangement, names, programs, channels, velocity pattern and precise timing. Same MIDI bytes and SHA-256 as the historical repair result. Adds an in-memory entry point and a key field in the report. |
| Audio diagnostics | Retains the same four PCM shapes, sample scaling and short fade. Selects the oscillator once per export and verifies the reopened WAV header. |
| Plugin | Keeps the supplied manifests and skill text. Thin path adapters expose the existing entry points; the overlay copies the standalone Python source. |
| Legacy and dependencies | Keeps the exact MIDIUtil source with its verified license. Uses the upstream Mido package distribution for standalone installs. The historical nested Mido ZIP stays in the original backup and can be restored to a private overlay by checksum. |
| Knowledge | Keeps original and optimized reference bytes. The repair instructions remain in the plugin; historical prompts and instructional examples remain archival. |

The Python distribution starts at `0.1.0`. The staged plugin manifests and compatibility readiness report retain `0.63.2`. The standalone distribution does not modify any existing installed plugin deployment.
