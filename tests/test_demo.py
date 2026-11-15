"""Independent checks of the preserved verification composition."""

from __future__ import annotations

import hashlib
from pathlib import Path
import tempfile
import unittest

import mido

from ai_midi_io.demo import generate


class DemoTests(unittest.TestCase):
    def test_export_preserves_the_repair_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            report = generate(root)["midi"]
            output = Path(report["path"])
            content = output.read_bytes()
            reopened = mido.MidiFile(output)

        self.assertEqual(len(content), 2505)
        expected_sha256 = "2576e4ca517a2c5f9d1c0038c063db59f192f2e6478e73607a47cbd8b06331d1"
        self.assertEqual(hashlib.sha256(content).hexdigest(), expected_sha256)
        self.assertEqual(report["sha256"], expected_sha256)
        self.assertEqual((reopened.type, reopened.ticks_per_beat), (1, 480))
        self.assertEqual(len(reopened.tracks), 5)
        self.assertEqual(reopened.length, 32.0)
        self.assertEqual(report["musical_tracks"], 4)
        self.assertEqual(report["total_notes"], 268)
        self.assertEqual(report["unclosed_notes"], 0)

        conductor = reopened.tracks[0]
        self.assertEqual(conductor[0].name, "Conductor")
        self.assertEqual(conductor[1].tempo, 500_000)
        self.assertEqual((conductor[2].numerator, conductor[2].denominator), (4, 4))
        self.assertEqual(conductor[3].key, "C")
        self.assertTrue(all(event.is_meta for event in conductor))
        for track in reopened.tracks:
            self.assertEqual(track[-1].type, "end_of_track")
            self.assertEqual(sum(event.time for event in track), 30_720)

        channels = [0, 1, 9, 2]
        for track, channel in zip(reopened.tracks[1:], channels):
            self.assertEqual({event.channel for event in track if not event.is_meta}, {channel})
        for index, channel, program in ((1, 0, 80), (2, 1, 38), (4, 2, 89)):
            changes = [event for event in reopened.tracks[index] if event.type == "program_change"]
            self.assertEqual(changes, [mido.Message("program_change", channel=channel, program=program)])

        drums = reopened.tracks[3]
        self.assertFalse(any(event.type == "program_change" for event in drums))
        hits = []
        tick = 0
        for event in drums:
            tick += event.time
            if event.type == "note_on" and event.velocity:
                hits.append((tick, event.note))
        self.assertEqual(
            hits,
            [(bar * 1920 + beat * 480, note) for bar in range(16) for beat in (0, 2) for note in (36, 38)],
        )


if __name__ == "__main__":
    unittest.main()
