"""Portable checks for compatibility behavior and the local dependency cache."""

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import quote
import zipfile

from ai_midi_io import runtime


class CompatibilityTests(unittest.TestCase):
    def test_sandbox_link_requires_real_nonempty_file_within_root(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            sandbox = root / "sandbox"
            sandbox.mkdir()
            path = sandbox / "a file.mid"
            with patch.object(runtime, "_SANDBOX_ROOT", sandbox):
                with self.assertRaises(FileNotFoundError):
                    runtime.sandbox_link(path)
                path.touch()
                with self.assertRaises(FileNotFoundError):
                    runtime.sandbox_link(path)
                path.write_bytes(b"test")
                link = runtime.sandbox_link(path, "Download [test]")
                expected_root = quote(sandbox.resolve().as_posix(), safe="/")
                self.assertEqual(link, rf"[Download \[test\]](sandbox:{expected_root}/a%20file.mid)")
                outside = root / "outside.mid"
                outside.write_bytes(b"test")
                with self.assertRaises(ValueError):
                    runtime.sandbox_link(outside)

    def test_concurrent_cache_repairs_leave_complete_extractions(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive = root / "bundle.zip"
            with zipfile.ZipFile(archive, "w") as bundle:
                bundle.writestr("vendor/mido/__init__.py", "# test-only fixture")
            cache = root / "cache"
            first, = runtime.extract_dependencies(archive, cache)
            (first / "mido" / "__init__.py").unlink()

            with ThreadPoolExecutor(max_workers=4) as workers:
                futures = [workers.submit(runtime.extract_dependencies, archive, cache) for _ in range(8)]
                published = [future.result()[0] for future in futures]
            for parent in published:
                self.assertEqual((parent / "mido" / "__init__.py").read_text(), "# test-only fixture")
            self.assertIn(runtime.extract_dependencies(archive, cache)[0], published)

    def test_scheduler_rejects_oversized_smf_deltas(self):
        import mido

        with self.assertRaisesRegex(ValueError, "delta"):
            runtime.scheduled_track([], 0x10000000)
        track = runtime.scheduled_track(
            [(0x0FFFFFFF, mido.MetaMessage("marker", text="split"))], 0x10000000
        )
        self.assertEqual([message.time for message in track], [0x0FFFFFFF, 1])
