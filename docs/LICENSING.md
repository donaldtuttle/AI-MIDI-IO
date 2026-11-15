# Licensing and publication review

AI MIDI IO and its original composition workflow were created by Donald Tuttle. The [source audit](SOURCE_INVENTORY.md) documents the origin and role of the bundled components.

The repository does not currently include a project-wide license grant for its first-party code. MIT is a potential license for those components, but no first-party license should be assumed until one is explicitly published.

| Material | Treatment |
| --- | --- |
| Archived `legacy/MIDIFile.py` | Third-party MIDIUtil source, kept with the exact [upstream copyright and MIT notice](../legacy/License.txt). |
| Mido | MIT dependency installed from its public distribution. The upstream notice is preserved for the optional local archive restore. |
| `packaging` | Mido’s transitive dependency, obtained as an upstream distribution. Its code is absent from this repository. |
| Knowledge, instructions, reports and examples | Preserved as supplied for continuity and source review. Embedded third-party excerpts or examples require their own permission and attribution where applicable. |

Before public distribution, the historical references and bundled files require review for redistribution rights, embedded links, and private identifiers. The preserved plugin references contain historical conversation and plugin identifiers. The legacy code’s verified license evidence and byte comparisons are in [the legacy audit](LEGACY.md).
