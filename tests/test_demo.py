"""Demo generation produces a valid file."""
from __future__ import annotations

from tempfile import TemporaryDirectory
from pathlib import Path
import unittest

from ai_midi_io.demo import write_demo
from ai_midi_io.validation import validate_file


class DemoTests(unittest.TestCase):
    def test_demo_is_valid(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "demo.mid"
            write_demo(path)
            report = validate_file(path)
            self.assertGreater(report["note_on_events"], 0)
            self.assertEqual(report["type"], 1)


if __name__ == "__main__":
    unittest.main()
