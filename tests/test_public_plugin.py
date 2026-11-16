"""Portable public plugin package acceptance tests (standard library only)."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile

from tools.build_public_plugin import build


class PublicPluginPackageTests(unittest.TestCase):
    def test_manifest_and_public_files(self):
        with TemporaryDirectory() as temp:
            path = build(Path(temp) / "public.zip")
            with ZipFile(path) as z:
                names = set(z.namelist())
                self.assertEqual(len(names), len(z.namelist()))
                self.assertIn("plugin.json", names)
                self.assertIn(".codex-plugin/plugin.json", names)
                self.assertIn("assets/ai-midi-io.svg", names)
                self.assertIn("skills/ai-midi-io/SKILL.md", names)
                self.assertIn("skills/ai-midi-io/scripts/ai_midi_io/validation.py", names)
                self.assertIn("skills/ai-midi-io/references/MIDIFile-LICENSE.txt", names)
                self.assertIn("THIRD_PARTY_NOTICES.md", names)
                manifest = json.loads(z.read("plugin.json"))
                self.assertEqual(manifest["name"], "ai-midi-io")
                self.assertEqual(manifest["version"], "0.63.3")
                ui = manifest["extensions"]["com.openai"]["interface"]
                self.assertLessEqual(len(ui["shortDescription"]), 30)
                for prompt in ui["defaultPrompt"]:
                    self.assertLessEqual(len(prompt), 128)
                for item in ("logo", "composerIcon"):
                    self.assertIn(ui[item].removeprefix("./"), names)
                svg = z.read(ui["logo"].removeprefix("./"))
                self.assertIn(b'width="256"', svg)
                self.assertIn(b'height="256"', svg)
                self.assertEqual(z.testzip(), None)

    def test_does_not_bundle_private_or_unreviewed_sources(self):
        with TemporaryDirectory() as temp:
            path = build(Path(temp) / "public.zip")
            with ZipFile(path) as z:
                content = b"\n".join(z.read(n) for n in z.namelist() if n.endswith((".md", ".json", ".txt", ".py")))
                for private in (b"_chatgptios_conversationID", b"plugin_e2c6", b"pluginrel_", b"chatgpt.com/plugins/plugin_"):
                    self.assertNotIn(private, content)
                self.assertFalse(any("provenance" in n or "reference/source" in n or "reference/optimized" in n for n in z.namelist()))


if __name__ == "__main__":
    unittest.main()
