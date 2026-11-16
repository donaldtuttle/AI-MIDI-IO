# Roadmap

| Priority | Proposed work | Acceptance criterion |
| --- | --- | --- |
| Public distribution | Source is public and first-party software is MIT-licensed. Prepare versioned download packages and complete remaining reference-rights review. | A tagged release includes tested assets, build instructions and applicable third-party notices. |
| Release coverage | Run the workflow on GitHub and extend confirmed Windows and macOS coverage. | Clean wheel install, passing tests and identical demo SHA-256 on the claimed platforms. |
| Plugin verification | Stage the overlay with the original icon and approved dependency source on the actual host. | A fresh hosted conversation loads the skill and creates a newly generated, downloadable and validated SMF. |
| Musical utilities | Evaluate extracting scale, chord, rhythm and arpeggio material into small reusable functions. | Independently testable musical contracts with explicit data provenance. Add functions only when they serve an actual composition or editing workflow. |
| Audio and live workflows | Evaluate optional MIDI-to-audio, hardware MIDI, OSC or receiver-specific tuning as distinct projects. | Each approved feature has a real backend, sample input, observable output and its own verification. |

The [README](../README.md) and [test results](TESTING.md) describe implemented behavior.
