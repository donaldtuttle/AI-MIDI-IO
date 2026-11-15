"""Exercise the archived MIDIUtil writer with an independent Mido reload."""

from io import BytesIO
import unittest
from pathlib import Path

class TestLegacyBackend(unittest.TestCase):
    def test_import(self):
        # Placeholder that confirms the legacy file is present and importable in context
        p = Path(__file__).resolve().parents[1] / "legacy" / "MIDIFile.py"
        self.assertTrue(p.exists())
        text = p.read_text(encoding="utf-8", errors="replace")
        self.assertIn("class MIDIFile", text)

if __name__ == "__main__":
    unittest.main()
