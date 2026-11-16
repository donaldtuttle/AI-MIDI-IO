# Third-party notices and license scope

The [root MIT License](LICENSE) grants permission for the first-party software
and documentation owned by Donald Tuttle and created for AI MIDI IO. This
includes the standalone Python implementation in `src/ai_midi_io/`, the C#
Windows MIDI Player source and build script in `apps/windows-midi-player/`,
and first-party supporting tools, tests and project documentation.

The root license **does not relicense materials owned by others**. It also does
not automatically grant rights to redistribute historical or imported reference
files, artwork, or other archived assets whose licensing has not been
established. These remain available in this repository for provenance and
technical reference, subject to their applicable rights.

## MIDIUtil (legacy MIDIFile.py)

- Location: `legacy/MIDIFile.py`
- Copyright: 2009–2016 Mark Conway Wirt
- License: MIT (upstream notice preserved at [legacy/License.txt](legacy/License.txt))
- Treatment: Retain the original copyright and license notice when distributing
  this third-party code.

## Mido

- Location: Python package dependency, not vendored in the installable package
- Copyright: Ole Martin Bjørndalen and contributors
- License: MIT ([preserved notice](legacy/notices/Mido-LICENSE.txt))
- Treatment: Mido is installed independently through the package dependency.
  If redistributing a source archive containing Mido, provide its MIT notice.

## Other runtime dependencies

- `packaging` is installed as a transitive Mido dependency; its code is not
  included in this repository. Redistributions including dependencies must
  comply with their respective license terms.

## Windows MIDI Player sound bank

- The player loads the Windows-installed `gm.dls` sound bank at runtime.
- No Windows General MIDI samples or instrument bank are included in this
  repository.
- The root MIT License does not grant any rights to redistribute third-party
  sound samples or Windows system assets.

## Archived plugin and reference material

The following contain imported, preserved or historical material and are **not
automatically relicensed** by the root MIT License:

- `legacy/` (third-party code with its own license and notices)
- `plugin/provenance/` (historical repair and backup artifacts)
- `plugin/skills/instructions/references/` (original and optimized references,
  examples, prompts and guides)
- Third-party excerpts, logos, icons or other assets wherever located

First-party maintained application code and tooling are covered by the root MIT
License; separately owned components retain their own terms. A public release
should review archived sources and private identifiers before publication.

See [docs/LICENSING.md](docs/LICENSING.md) and
[docs/LEGACY.md](docs/LEGACY.md) for more detail.
