# Verification composition

The project's reproducible four-track MIDI example is available in
[AI_MIDI_IO_Verification_4track_120BPM.mid](verification/AI_MIDI_IO_Verification_4track_120BPM.mid).
Its [validation report](verification/validation.json) records the serialized
structure and note balance. The file is Standard MIDI File Type 1 at 480 PPQ.
It runs for 16 bars in C major, in 4/4 at 120 BPM, for 32 seconds.

| Track | Role | MIDI channel | Mido program (`0–127`) | Note attacks |
| --- | --- | ---: | ---: | ---: |
| 1 | Conductor metadata |  |  | 0 |
| 2 | Melody, Lead 1 (square) | 1 | 80 | 128 |
| 3 | Bass, Synth Bass 1 | 2 | 38 | 64 |
| 4 | GM percussion | 10 |  | 64 |
| 5 | Harmony, Pad 2 (warm) | 3 | 89 | 12 |

The bass alternates MIDI notes 36 and 48, an octave apart on C. Percussion
notes 36 and 38 trigger kick and snare together on beats 1 and 3. The harmony
holds C, Am, F, and G triads for four bars each. Mido represents MIDI channel
10 as channel `9`.

After installing the Python package, regenerate into a fresh output directory.

```sh
python -m ai_midi_io.demo --output-root demo-output > demo-validation.json
ai-midi-io validate demo-output/midi_generation/AI_MIDI_IO_Verification_4track_120BPM.mid
```

The exporter reopens the MIDI, checks track structure and note releases, and
reports the measured duration. The regression suite compares the bytes against
this reference SHA-256 digest.

```text
2576e4ca517a2c5f9d1c0038c063db59f192f2e6478e73607a47cbd8b06331d1
```

The verification covers the file itself. Playback and DAW import were outside
the scope of these checks. See the [General MIDI Level 1 reference](https://midi.org/general-midi-level-1)
for the sound-set convention behind the program numbers.
