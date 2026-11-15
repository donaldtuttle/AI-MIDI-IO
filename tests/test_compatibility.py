"""Compatibility with the legacy MIDIFile writer."""
from __future__ import annotations

from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

# Make legacy importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "legacy"))

from MIDIFile import MIDIFile  # type: ignore
from ai_midi_io.validation import validate_file


class CompatibilityTests(unittest.TestCase):
    def test_legacy_writer_produces_valid_smf(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "legacy.mid"
            midi = MIDIFile(1)
            midi.addTempo(0, 0, 120)
            midi.addNote(0, 0, 60, 0, 1, 100)
            with path.open("wb") as fh:
                midi.writeFile(fh)
            report = validate_file(path)
            self.assertEqual(report["type"], 1)
            self.assertEqual(report["ticks_per_beat"], 480)


if __name__ == "__main__":
    unittest.main()
