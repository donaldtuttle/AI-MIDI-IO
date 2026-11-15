# Legacy backend and bundled dependency provenance

## Backup integrity

The supplied knowledge backup contained ten source files and
`BACKUP_MANIFEST.json`. All ten byte counts and SHA-256 hashes matched the
manifest. The outer backup and the nested Python ZIP also passed full ZIP CRC
checks. These checks establish consistency with the supplied backup manifest.
The upstream comparisons below establish the identity of the two executable
components.

## MIDIFile.py is MIDIUtil

`legacy/MIDIFile.py` is preserved byte for byte from the original backup.
The source identifies Mark Conway Wirt as its author and carries his
2009–2016 copyright notice. Its self-reported version is `HEAD`. The 73,304
bytes were compared with the author's `develop` branch, Git blob
`3c1e92010754cb251702b3ea787b7cd9f7e31645`. The only differing line is the
header's filename capitalization, from `MidiFile.py` to `MIDIFile.py`.
There are no code differences in that comparison. The corresponding MIT
license is included verbatim as `legacy/License.txt`, Git blob
`6714626e43ef4d0700352deff2eeca9a1b0c805c`.

Sources: [Upstream source](https://github.com/MarkCWirt/MIDIUtil/blob/develop/src/midiutil/MidiFile.py),
[upstream license](https://github.com/MarkCWirt/MIDIUtil/blob/develop/License.txt),
[MIDIUtil PyPI listing](https://pypi.org/project/MIDIUtil/).

The file implements a standard-library-only SMF writer. It defines event
classes, track sorting, duplicate removal, deinterleaving, delta-time and
variable-length encoding, MIDI headers, and track chunks. It also contains
helpers for RPN/NRPN, SysEx messages, tuning message construction, and
frequency-to-MIDI tuning data. Those helpers remain archival code. The
snapshot exposes no general SMF file reader, live port transport, synthesis
engine, or complete tuning playback path. Internal variable-length decoding is
a low-level utility.

The repository preserves this writer as a separate reference backend. The
installable AI MIDI IO package uses the Mido-backed repair code. Historical
examples calling methods such as `addNote` and `writeFile` can be examined
against the archived backend without introducing it into the current package's
dependency graph.

## Independent verification

The archived module generated an `MThd` stream in CPython 3.12 with
`python -S`, using only the standard library. Five separate checks against
official Mido 1.3.3 then passed. Run from the repository root with the project's
runtime dependency installed:

```sh
python -m unittest discover -v -s legacy -p test_backend.py
```

| Check | Observed behavior |
| --- | --- |
| Type 0 | One-track file reloaded at 480 PPQ with 120 BPM, 4/4, and the expected channel, velocity, program, CC, pitch bend, and timed note release. |
| Type 1 | Two musical tracks reloaded with a dedicated conductor track, metadata on track zero, and a channel-9 percussion note with a complete release. |
| Type 2 | Two independent tracks reloaded. This check is specific to the legacy writer. |
| Same-channel, same-pitch overlap | With `removeDuplicates=False` and `deinterleave=False`, both starts and releases retained the requested absolute ticks. |
| Legacy default overlap behavior | The first note's requested release at tick 480 moved to tick 240, the second note's onset. |

Additional manual probes found that the archived writer accepted a two-track
Type 0 header, which is outside the supported one-track form. The historical
default settings also raised `IndexError` on two same-pitch, same-channel
notes beginning at the same tick with different durations. The deinterleave
lookup concatenates decimal pitch and channel digits. In a controlled probe,
pitch 101 on channel 5 and pitch 10 on channel 15 both keyed to `1015`,
causing the first release to move to the other channel's onset. These findings
explain why this source remains a separately evaluated backend and why current
AI MIDI IO code relies on Mido and its own scheduling rules.

## Original nested Mido ZIP

The backup's `AI_MIDI_IO_Python.zip` held 35 Python files across five
directory entries, all under `mido/`. Every source path and byte matched the
installed-package payload of the official `mido-1.3.3-py3-none-any.whl`.
The wheel SHA-256 was verified against PyPI:

```text
01033c9b10b049e4436fca2762194ca839b09a4334091dd3c34e7f4ae674fd8a
```

Mido is MIT-licensed third-party code by Ole Martin Bjørndalen and contributors.
The wheel's `mido-1.3.3.dist-info/LICENSE` contains the applicable notice,
preserved verbatim at `legacy/notices/Mido-LICENSE.txt`. The original ZIP
omits that license file and the distribution metadata. In an isolated
`python -I -S` probe with only the nested ZIP added to the import path,
`import mido` failed on missing `packaging`. With `packaging` available and
without Mido distribution metadata, import succeeded and reported
`0.0.0.dev0` even though its source matches 1.3.3. The wheel declares
`packaging`, plus `importlib-metadata` only on Python versions below 3.8.
Port backends in the ZIP can require additional libraries or platform
tools, such as RtMidi bindings, Pygame, the PortMidi shared library, or
`amidi`. The current package's file workflow uses none of those port backends.

The original nested ZIP stays in the supplied backup. The repository installs
Mido as a dependency with upstream package metadata and license, avoiding a
second bundled executable copy. If an archival plugin deployment redistributes
the original nested ZIP, include the corresponding Mido copyright and MIT
permission notice from the verified wheel.

Sources: [Mido 1.3.3 release and hashes](https://pypi.org/project/mido/1.3.3/#files),
[upstream Mido license](https://github.com/mido/mido/blob/main/LICENSE).
