"""Focused coverage of SMF framing and cross-track note accounting."""
from __future__ import annotations

from pathlib import Path
import struct
from tempfile import TemporaryDirectory
import unittest

from ai_midi_io.runtime import MidiRuntime
from ai_midi_io.validation import validate_file


class ValidationTests(unittest.TestCase):
    def test_verification_fixture(self) -> None:
        runtime = MidiRuntime()
        with TemporaryDirectory() as tmp:
            path = runtime.write_verification_fixture(Path(tmp))
            report = validate_file(path)
            self.assertEqual(report["type"], 1)
            self.assertEqual(report["ticks_per_beat"], 480)
            self.assertEqual(report["track_count"], 4)
            self.assertGreater(report["note_on_events"], 0)

    def test_rejects_bad_header(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.mid"
            path.write_bytes(b"not a midi file")
            with self.assertRaises(ValueError):
                validate_file(path)


if __name__ == "__main__":
    unittest.main()
