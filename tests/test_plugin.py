import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]


class PluginOverlayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        scratch = tempfile.TemporaryDirectory()
        cls.addClassCleanup(scratch.cleanup)
        cls.work = Path(scratch.name)
        cls.archive = cls.work / "overlay.zip"
        cls.stage = cls.work / "stage"
        subprocess.run(
            [sys.executable, str(ROOT / "tools/build_plugin.py"), str(cls.archive)],
            check=True,
            capture_output=True,
            timeout=20,
        )
        with ZipFile(cls.archive) as overlay:
            overlay.extractall(cls.stage)

    def test_overlay_preserves_identity_and_uses_canonical_source(self):
        for name in (".codex-plugin/plugin.json", "plugin.json"):
            with self.subTest(manifest=name):
                self.assertEqual((self.stage / name).read_bytes(), (ROOT / "plugin" / name).read_bytes())
        skill = self.stage / "skills/instructions"
        with (skill / "lookup/knowledge-index.json").open(encoding="utf-8") as stream:
            index = json.load(stream)
        for entry in index["files"]:
            if entry["name"] != "AI_MIDI_IO_Python.zip":
                with self.subTest(reference=entry["path"]):
                    self.assertTrue((skill / entry["path"]).is_file())
        self.assertFalse((skill / "references/AI_MIDI_IO_Python.zip").exists())
        self.assertFalse((self.stage / "provenance").exists())
        self.assertEqual(
            (skill / "scripts/ai_midi_io/runtime.py").read_bytes(),
            (ROOT / "src/ai_midi_io/runtime.py").read_bytes(),
        )

    def test_isolated_overlay_bootstraps_local_package(self):
        """A built overlay resolves its bundled source without site-packages."""
        import mido
        import packaging

        import shutil
        isolated_stage = self.work / "isolated-stage"
        shutil.copytree(self.stage, isolated_stage)
        skill = isolated_stage / "skills/instructions"
        archive = skill / "references/AI_MIDI_IO_Python.zip"
        with ZipFile(archive, "w") as bundle:
            for package in (mido, packaging):
                directory = Path(package.__file__).parent
                for path in directory.rglob("*.py"):
                    bundle.write(path, f"vendor/{directory.name}/{path.relative_to(directory).as_posix()}")
        scripts = skill / "scripts"
        code = ("import sys, json; "
                f"sys.path.insert(0, {str(scripts)!r}); "
                "from ai_midi_io_runtime import initialize; "
                f"print(json.dumps(initialize({str(skill / 'references')!r}, "
                f"{str(self.work / 'overlay-isolated')!r})['report']))")
        result = subprocess.run(
            [sys.executable, "-I", "-S", "-c", code],
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(json.loads(result.stdout)["ready"])

    def test_archived_regressions_against_staged_runtime(self):
        test_file = self.stage / "skills/instructions/tests/test_runtime.py"
        command = """
import runpy, sys, tempfile, unittest
from pathlib import Path

case = runpy.run_path(sys.argv[1])["RuntimeTests"]
import ai_midi_io.runtime
assert Path(ai_midi_io.runtime.__file__).is_relative_to(sys.argv[2])
try:
    with tempfile.TemporaryDirectory(dir="/mnt/data"):
        pass
except OSError:
    name = "test_links_require_real_nonempty_sandbox_file"
    setattr(case, name, unittest.skip("host has no writable /mnt/data")(getattr(case, name)))
suite = unittest.defaultTestLoader.loadTestsFromTestCase(case)
assert suite.countTestCases() == 24
result = unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(0 if result.wasSuccessful() else 1)
"""
        completed = subprocess.run(
            [sys.executable, "-I", "-c", command, str(test_file), str(self.stage)],
            cwd=self.work,
            capture_output=True,
            text=True,
            timeout=40,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)


if __name__ == "__main__":
    unittest.main()
