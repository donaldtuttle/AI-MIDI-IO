"""Regression tests. Extraction fixtures use installed mido/packaging source,
not the inaccessible original binary archive; that limitation is intentional
and recorded in the repair report. No hardware or network actions are run.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
import wave
import zipfile

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import mido
import packaging
import ai_midi_io_runtime as runtime
from generate_verification import generate


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.references = self.root / "references"
        self.references.mkdir()

    def tearDown(self):
        self.temp.cleanup()

    def source_archive(self):
        archive = self.references / "AI_MIDI_IO_Python.zip"
        with zipfile.ZipFile(archive, "w") as z:
            for package in (mido, packaging):
                directory = Path(package.__file__).parent
                for p in directory.rglob("*.py"):
                    z.write(p, f"nested/vendor/{directory.name}/{p.relative_to(directory).as_posix()}")
        return archive

    def save(self, events, end=960, conductor=None):
        midi = mido.MidiFile(type=1, ticks_per_beat=480)
        if conductor is not None:
            midi.tracks.append(runtime.scheduled_track(conductor, end))
        midi.tracks.append(runtime.scheduled_track(events, end))
        path = self.root / "test.mid"
        midi.save(str(path))
        return path

    def test_initialize_idempotent(self):
        first = runtime.initialize(self.references, self.root / "outputs")
        second = runtime.initialize(self.references, self.root / "outputs")
        self.assertEqual(first["report"], second["report"])
        self.assertTrue(first["report"]["ready"])
        self.assertFalse(first["report"]["midifile_available"])
        for path in first["paths"].values():
            self.assertTrue(path.is_dir())

    def test_legacy_requirement_fails_honestly(self):
        with self.assertRaises(RuntimeError):
            runtime.initialize(self.references, self.root / "outputs", require_midifile=True)

    def test_broken_legacy_source_is_not_loaded(self):
        (self.references / "MIDIFile.py").write_text("def broken(:\n")
        state = runtime.initialize(self.references, self.root / "outputs")
        self.assertFalse(state["report"]["midifile_available"])
        self.assertIn("SyntaxError", state["report"]["midifile_issue"])

    def test_nested_archive_repeated_extraction(self):
        archive = self.source_archive()
        parents = runtime.extract_dependencies(archive, self.root / "cache")
        again = runtime.extract_dependencies(archive, self.root / "cache")
        self.assertEqual(parents, again)
        self.assertTrue(any((p / "mido/__init__.py").is_file() for p in parents))

    def test_empty_existing_directory_does_not_skip_extraction(self):
        archive = self.source_archive()
        digest = hashlib.sha256(archive.read_bytes()).hexdigest()
        (self.root / "cache" / digest).mkdir(parents=True)
        parents = runtime.extract_dependencies(archive, self.root / "cache")
        self.assertTrue(any((p / "mido/__init__.py").is_file() for p in parents))

    def test_missing_package_rebuilds_stale_cache(self):
        archive = self.source_archive()
        parents = runtime.extract_dependencies(archive, self.root / "cache")
        (parents[0] / "mido/__init__.py").unlink()
        again = runtime.extract_dependencies(archive, self.root / "cache")
        self.assertTrue((again[0] / "mido/__init__.py").is_file())

    def test_isolated_python_loads_local_archive_without_installation(self):
        self.source_archive()
        code = (f"import sys,json; sys.path.insert(0,{str(SCRIPTS)!r}); "
                "from ai_midi_io_runtime import initialize; "
                f"print(json.dumps(initialize({str(self.references)!r}, {str(self.root / 'isolated')!r})['report']))")
        run = subprocess.run([sys.executable, "-I", "-S", "-c", code],
                             capture_output=True, text=True, timeout=20)
        self.assertEqual(run.returncode, 0, run.stderr + run.stdout)
        report = json.loads(run.stdout)
        self.assertTrue(report["ready"])
        self.assertIn("ai_midi_io_dependencies", report["mido_path"])

    def test_zip_path_traversal_rejected(self):
        archive = self.root / "bad.zip"
        with zipfile.ZipFile(archive, "w") as z:
            z.writestr("../escape.py", "bad")
        with self.assertRaises(ValueError):
            runtime.extract_dependencies(archive, self.root / "cache")
        self.assertFalse((self.root / "escape.py").exists())

    def test_zip_symlink_rejected(self):
        archive = self.root / "bad.zip"
        info = zipfile.ZipInfo("link")
        info.create_system = 3
        info.external_attr = (stat.S_IFLNK | 0o777) << 16
        with zipfile.ZipFile(archive, "w") as z:
            z.writestr(info, "/etc/passwd")
        with self.assertRaises(ValueError):
            runtime.extract_dependencies(archive, self.root / "cache")

    def test_archive_without_required_package_rejected(self):
        archive = self.root / "bad.zip"
        with zipfile.ZipFile(archive, "w") as z:
            z.writestr("README.txt", "This is not a dependency archive.")
        with self.assertRaises(ImportError):
            runtime.extract_dependencies(archive, self.root / "cache")

    def test_release_before_retrigger(self):
        path = self.save([
            (0, mido.Message("note_on", note=60, velocity=90)),
            (480, mido.Message("note_on", note=60, velocity=100)),
            (480, mido.Message("note_off", note=60)),
            (960, mido.Message("note_off", note=60))])
        report = runtime.validate_midi(path, expected_musical_tracks=1, expected_end_tick=960)
        self.assertEqual(report["total_notes"], 2)
        self.assertFalse(report["note_overlaps"])
        self.assertEqual([msg.type for msg in mido.MidiFile(path).tracks[0]],
                         ["note_on", "note_off", "note_on", "note_off", "end_of_track"])

    def test_zero_velocity_note_on_releases(self):
        path = self.save([(0, mido.Message("note_on", note=60, velocity=90)),
                          (480, mido.Message("note_on", note=60, velocity=0))])
        self.assertEqual(runtime.validate_midi(path)["total_notes"], 1)

    def test_orphan_note_off_rejected(self):
        path = self.save([(480, mido.Message("note_off", note=60))])
        with self.assertRaisesRegex(ValueError, "Unmatched"):
            runtime.validate_midi(path)

    def test_unclosed_note_rejected(self):
        path = self.save([(0, mido.Message("note_on", note=60, velocity=90))])
        with self.assertRaisesRegex(ValueError, "Unclosed"):
            runtime.validate_midi(path)

    def test_legal_overlap_reported_not_forbidden(self):
        path = self.save([(0, mido.Message("note_on", note=60, velocity=90)),
                          (240, mido.Message("note_on", note=60, velocity=95)),
                          (480, mido.Message("note_off", note=60)),
                          (960, mido.Message("note_off", note=60))])
        self.assertEqual(len(runtime.validate_midi(path)["note_overlaps"]), 1)

    def test_channels_do_not_collide(self):
        events = []
        for pitch, channel in ((101, 5), (10, 15)):
            events.extend([(0, mido.Message("note_on", note=pitch, channel=channel, velocity=90)),
                           (480, mido.Message("note_off", note=pitch, channel=channel))])
        self.assertEqual(runtime.validate_midi(self.save(events))["total_notes"], 2)

    def test_tempo_cc_and_pitch_bend_round_trip(self):
        conductor = [(0, mido.MetaMessage("set_tempo", tempo=500000)),
                     (480, mido.MetaMessage("set_tempo", tempo=1000000))]
        path = self.save([(0, mido.Message("control_change", control=7, value=100)),
                          (0, mido.Message("pitchwheel", pitch=-8192)),
                          (0, mido.Message("note_on", note=60, velocity=90)),
                          (480, mido.Message("pitchwheel", pitch=8191)),
                          (960, mido.Message("note_off", note=60))], conductor=conductor)
        runtime.validate_midi(path)
        parsed = mido.MidiFile(path)
        self.assertEqual(parsed.length, 1.5)
        self.assertEqual([m.pitch for m in parsed.tracks[1] if m.type == "pitchwheel"], [-8192, 8191])
        self.assertEqual([m.value for m in parsed.tracks[1] if m.type == "control_change"], [100])

    def test_lead_in_and_tail_silence_preserved(self):
        path = self.save([(480, mido.Message("note_on", note=60, velocity=90)),
                          (720, mido.Message("note_off", note=60))], end=1440)
        self.assertEqual(mido.MidiFile(path).tracks[0][0].time, 480)
        self.assertEqual(runtime.validate_midi(path)["end_tick"], 1440)

    def test_negative_event_time_rejected(self):
        with self.assertRaises(ValueError):
            runtime.scheduled_track([(-1, mido.Message("note_on", note=60))], 480)

    def test_truncated_midi_rejected(self):
        path = self.save([])
        path.write_bytes(path.read_bytes()[:-1])
        with self.assertRaises(ValueError):
            runtime.validate_midi(path)

    def test_wav_round_trip_all_four_waveforms(self):
        for shape in ("sine", "square", "triangle", "sawtooth"):
            path = self.root / f"{shape}.wav"
            report = runtime.write_test_tone(path, 432.0, 0.1, shape)
            self.assertFalse(report["is_midi_render"])
            with wave.open(str(path), "rb") as audio:
                self.assertEqual(audio.getnframes(), 4410)
                self.assertNotEqual(set(audio.readframes(4410)), {0})

    def test_bad_wav_parameters_rejected(self):
        with self.assertRaises(ValueError):
            runtime.write_test_tone(self.root / "bad.wav", frequency=-1)
        with self.assertRaises(ValueError):
            runtime.write_test_tone(self.root / "bad.wav", waveform="unimplemented")

    def test_links_require_real_nonempty_sandbox_file(self):
        with self.assertRaises(FileNotFoundError):
            runtime.sandbox_link(self.root / "absent.mid")
        with tempfile.TemporaryDirectory(dir="/mnt/data") as temp:
            path = Path(temp) / "a file.mid"
            path.write_bytes(b"test")
            link = runtime.sandbox_link(path, "Download [test]")
            self.assertIn("sandbox:/mnt/data/", link)
            self.assertIn("a%20file.mid", link)
            self.assertNotIn("conversationID", link)
            self.assertNotIn("{file_path}", link)

    def test_original_project_prompt_fixture(self):
        report = generate(self.root / "generated", self.references)
        self.assertEqual(report["midi"]["total_notes"], 268)
        self.assertEqual(report["midi"]["musical_tracks"], 4)
        self.assertEqual(report["midi"]["track_chunks"], 5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
