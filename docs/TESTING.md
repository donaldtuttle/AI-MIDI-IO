# Testing

```bash
python -m pytest
```

The test suite covers:

- structural validation of the verification fixture
- compatibility with the legacy MIDIFile writer
- plugin skill file presence
- demo generation

The verification fixture is generated at test time so the suite does not depend
on a checked-in binary.

CI runs the same suite on Python 3.10+.
