# Licensing and publication review

DT created AI MIDI IO and its original Custom GPT composition workflow. This repository records the origin and role of each source in the [source audit](SOURCE_INVENTORY.md). Supply the desired public copyright holder spelling before releasing the first-party work.

MIT is the proposed license for the first-party Python code and integration files. It fits a small reusable library and matches the licenses of the MIDI libraries used here. DT’s approval is needed before applying it. The repository does not yet carry a project-wide license grant.

| Material | Treatment |
| --- | --- |
| Archived `legacy/MIDIFile.py` | Third-party MIDIUtil source, kept with the exact [upstream copyright and MIT notice](../legacy/License.txt). |
| Mido | MIT dependency installed from its public distribution. The upstream notice is preserved for the optional local archive restore. |
| `packaging` | Mido’s transitive dependency, obtained as an upstream distribution. Its code is absent from this repository. |
| Knowledge, instructions, reports and examples | Preserved as supplied for continuity and source review. Embedded third-party excerpts or examples require their own permission and attribution where applicable. |

Review historical files for redistribution permissions, embedded links and private release metadata before public publication. The reference material contains historical plugin and conversation identifiers. Decide which archival bytes belong in a public tree before authorizing a push. The legacy code’s verified license evidence and byte comparisons are in [the legacy audit](LEGACY.md).
