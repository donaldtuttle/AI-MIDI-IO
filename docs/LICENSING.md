# Licensing and publication

## First-party software: MIT License

AI MIDI IO was created by Donald Tuttle. The original, maintained software and
project documentation are available under the [MIT License](../LICENSE):

```text
SPDX-License-Identifier: MIT
Copyright (c) 2026 Donald Tuttle
```

This includes the Python MIDI toolkit (`src/ai_midi_io/`), the C# Windows MIDI
Player source and build script (`apps/windows-midi-player/`), and first-party
tests and tooling. The MIT License permits use, copying, modification and
distribution, including commercial use, provided its copyright and permission
notice are retained. It includes a warranty and liability disclaimer.

## Third-party code and archived material

The root MIT License applies only where the copyright holder has authority to
license the material. It does not replace other copyright notices or grant
rights to external archives and media.

| Component | Applicable treatment |
| --- | --- |
| `legacy/MIDIFile.py` | Third-party MIDIUtil by Mark Conway Wirt, under its own MIT terms; preserve [upstream notice](../legacy/License.txt). |
| Mido | MIT-licensed runtime dependency; preserve [Mido notice](../legacy/notices/Mido-LICENSE.txt) when redistributing its code. |
| `packaging` | Transitive dependency, not bundled; comply with its separately distributed license if redistributed. |
| Windows `gm.dls` | Operating-system sound bank read at runtime; samples are not included or licensed by this project. |
| `plugin/provenance/` and `plugin/skills/instructions/references/` | Historical and reference material preserved for provenance. Not automatically relicensed; some files may contain third-party excerpts or identifiers. |
| Logos, icons and other externally sourced media | Not included in the first-party MIT grant unless ownership and permission to license them are established. |

See [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md) for the scope summary
and [LEGACY.md](LEGACY.md) for verification of bundled third-party material.

## Distributing builds

Distributions of the MIT-licensed Python library and Windows Player should
accompany the license and copyright notice. If including third-party sources,
also include their applicable attribution and license notices.

The GitHub repository's license status does not by itself establish that every
historical reference, archived file or third-party asset can be republished.
Review those files for rights and private identifiers before changing the
repository to public.
