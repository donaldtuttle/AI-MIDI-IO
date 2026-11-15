# Testing and performance

## Executed results

The standalone wheel was built and installed into separate Linux virtual environments using official Mido 1.3.3 and packaging 26.3. Dependency checks passed in both environments.

| Suite | Python 3.12.14 | Python 3.13.5 |
| --- | --- | --- |
| Repository tests, including staged plugin integration | 15 passed | 15 passed |
| Independent legacy writer tests | 5 passed | 5 passed |
| Historical cases replayed within staged plugin integration | 23 passed, 1 skipped | 23 passed, 1 skipped |
| Untouched v0.63.2 test source against untouched runtime | 23 passed, 1 environment error | Outside this replay |

The original failing case was `test_links_require_real_nonempty_sandbox_file`. It raised `FileNotFoundError` while creating its fixture under `/mnt/data`, a host path absent here. The compatibility run preserves the case and skips it when no writable path is available. A separate portable test checks the equivalent real-file, nonempty-file, containment and escaping behavior against a temporary root.

The staged plugin also initialized in an isolated Python process with the actual ZIP recovered from the backup and separately supplied packaging. It loaded the exact legacy writer and regenerated the same verification MIDI. Without separately supplied packaging, that isolated archive import failed with `ModuleNotFoundError`. This reproduces a requirement of the original archive.

Additional installed-CLI checks initialized the checked-in legacy backend, generated the fixture on Python 3.12, reopened it on Python 3.13, and wrote and reopened a 22,050-frame triangle WAV at 44.1 kHz. The WAV sample payload was nonconstant. The [MIDI report](../examples/verification/validation.json) records the digest, programs, track counts, note counts and end tick. The demo file matches the digest recorded in the v0.63.2 repair.

The GitHub Actions matrix is included for Python 3.10 through 3.14. Local execution used the two Python versions above. Hosted CI, DAW import, audible playback and live plugin activation remain outside these results.

## Reproduce

From the repository root in an activated virtual environment:

```sh
python -m pip install .
python -m pip check
python -m unittest discover -s tests -v
python -m unittest discover -s legacy -p test_backend.py -v
ai-midi-io init --references ./legacy --require-midifile --output-root ./out
ai-midi-io demo --output-root ./out
```

To replay the unchanged baseline, extract the original repair ZIP and run the following with the installed dependency and a path to the extracted files:

```sh
python -m unittest discover -v -s ./repair/skills/instructions/tests
```

## Local timing

CPython 3.12.14 with Mido 1.3.3, local temporary directory, installed package, one warm-up and 31 measured repetitions per operation. Times are wall-clock milliseconds from `time.perf_counter_ns()`.

| Operation | Median | Min–max |
| --- | ---: | ---: |
| Warm project initialization | 0.48 | 0.35–3.86 |
| Build fixture in memory | 4.99 | 4.16–7.45 |
| Save the assembled fixture | 1.07 | 0.93–1.64 |
| Reopen and validate the fixture | 2.65 | 2.28–4.74 |
| Current full generation and verification | 14.38 | 12.25–20.83 |
| Exact v0.63.2 full generation and verification | 14.88 | 13.03–21.52 |

One first initialization, including the first Mido import, took 39.45 ms. The end-to-end ranges overlap in this sample. These measurements cover a 2,505-byte fixture on this host.


## Synchronization verification (November 15, 2026)

The restored source archive was tested locally on Python 3.13, with installed Mido 1.3.3. The plugin runtime adapter was adjusted to resolve the canonical package inside either a source checkout or a built plugin overlay when Python runs with `-I -S`. The MIDI generation and validation implementations were not changed.

- Full pytest collection: **45 passed, 37 subtests passed**.
- Main unittest suite: **16 passed**.
- Independent legacy suite: **5 passed**.
- The new isolated-overlay bootstrap test passed with a local ZIP containing Mido and packaging source.
- The CLI help entry point was verified with a local editable installation.

A regular isolated package installation could not be bootstrapped using pip's default build isolation because the test container does not have network access. An editable install with `--no-build-isolation --no-deps` succeeded using dependencies already present in the environment. Hosted CI and other interpreter versions were not rerun during this synchronization.
