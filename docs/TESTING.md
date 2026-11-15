# Testing

The package is tested with the standard library `unittest` module.

## Local run

```sh
python -m unittest discover -s tests -v
```

GitHub Actions runs the same suite on Python 3.10 through 3.14.

The verification MIDI file and its expected note counts are covered by `tests/test_validation.py` and `tests/test_demo.py`.
