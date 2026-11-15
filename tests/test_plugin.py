"""Plugin knowledge files are present."""
from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugin"


class PluginTests(unittest.TestCase):
    def test_skill_md_exists(self) -> None:
        skill = PLUGIN / "skills" / "instructions" / "SKILL.md"
        self.assertTrue(skill.is_file())

    def test_plugin_json_exists(self) -> None:
        self.assertTrue((PLUGIN / "plugin.json").is_file())


if __name__ == "__main__":
    unittest.main()
