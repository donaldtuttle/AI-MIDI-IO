# Examples

## Verification fixture

`examples/verification/` contains:

- `validation.json` — structural report for the canonical 4-track, 120 BPM fixture
- (optional) `AI_MIDI_IO_Verification_4track_120BPM.mid` — the binary itself

Generate a fresh fixture with:

```bash
python -m ai_midi_io fixture
```

Validate any SMF with:

```bash
python -m ai_midi_io validate path/to/file.mid
```
