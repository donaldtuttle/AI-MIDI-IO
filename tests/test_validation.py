"""Focused coverage of SMF framing and cross-track note accounting."""
from __future__ import annotations

from pathlib import Path
import struct
from tempfile import TemporaryDirectory
import unittest

import mido

from ai_midi_io.validation import validate_midi


class ValidationTests(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.path = Path(temp.name) / "file.mid"

    def save(self, file_type, *tracks):
        midi = mido.MidiFile(type=file_type, ticks_per_beat=480)
        midi.tracks.extend(mido.MidiTrack(messages) for messages in tracks)
        midi.save(self.path)
        return self.path

    def write_raw(self, track_hex, *, division=480):
        track = bytes.fromhex(track_hex)
        header = b"MThd" + struct.pack(">IHHH", 6, 0, 1, division)
        self.path.write_bytes(header + b"MTrk" + struct.pack(">I", len(track)) + track)
        return self.path

    def test_type_zero_reports_music_and_timing_metadata(self):
        self.save(0, [
            mido.MetaMessage("set_tempo", tempo=500000),
            mido.MetaMessage("time_signature", numerator=7, denominator=8),
            mido.Message("program_change", channel=2, program=38),
            mido.Message("note_on", channel=2, note=60, velocity=100, time=480),
            mido.Message("note_on", channel=2, note=60, velocity=0, time=240),
            mido.MetaMessage("set_tempo", tempo=600000),
        ])
        report = validate_midi(self.path, expected_musical_tracks=1, expected_end_tick=720)
        self.assertEqual((report["format"], report["ppq"], report["track_chunks"]), (0, 480, 1))
        self.assertEqual(report["total_notes"], 1)
        self.assertEqual(report["tracks"][0]["programs"], [{"tick": 0, "channel": 2, "program": 38}])
        self.assertEqual(report["tempo_changes"], [
            {"track": 0, "tick": 0, "tempo": 500000},
            {"track": 0, "tick": 720, "tempo": 600000},
        ])
        self.assertEqual(report["time_signatures"], [{
            "track": 0,
            "tick": 0,
            "numerator": 7,
            "denominator": 8,
            "clocks_per_click": 24,
            "notated_32nd_notes_per_beat": 8,
        }])

    def test_type_one_can_release_a_note_in_another_track(self):
        self.save(1, [mido.Message("note_on", note=60, velocity=90)], [
            mido.Message("note_off", note=60, time=240),
        ])
        report = validate_midi(self.path)
        self.assertEqual(report["unclosed_notes"], 0)
        self.assertEqual(report["unmatched_note_offs"], 0)
        self.assertEqual(report["musical_tracks"], 1)
        self.assertEqual(report["track_chunks"], 2)

    def test_same_tick_across_tracks_uses_track_order(self):
        held = [
            mido.Message("note_on", note=60, velocity=100),
            mido.Message("note_off", note=60, time=240),
        ]
        retrigger = [
            mido.Message("note_on", note=60, velocity=100, time=240),
            mido.Message("note_off", note=60, time=240),
        ]
        self.save(1, held, retrigger)
        self.assertEqual(validate_midi(self.path)["note_overlaps"], [])
        self.save(1, retrigger, held)
        self.assertEqual(validate_midi(self.path)["note_overlaps"], [
            {"tick": 240, "channel": 0, "note": 60},
        ])

    def test_same_tick_within_track_uses_file_event_order(self):
        on = mido.Message("note_on", note=60, velocity=95)
        off = mido.Message("note_off", note=60)
        self.save(0, [on, off])
        self.assertEqual(validate_midi(self.path)["unclosed_notes"], 0)
        self.save(0, [off, on])
        with self.assertRaisesRegex(ValueError, "Unmatched note-off"):
            validate_midi(self.path)

    def test_different_output_ports_can_use_same_channel_and_pitch(self):
        def notes_on_port(port):
            return [
                mido.MetaMessage("midi_port", port=port),
                mido.Message("note_on", channel=2, note=60, velocity=95),
                mido.Message("note_off", channel=2, note=60, time=240),
            ]

        self.save(1, notes_on_port(3), notes_on_port(4))
        self.assertEqual(validate_midi(self.path)["note_overlaps"], [])
        self.save(1, notes_on_port(3), notes_on_port(3))
        self.assertEqual(validate_midi(self.path)["note_overlaps"], [
            {"tick": 0, "port": 3, "channel": 2, "note": 60},
        ])

    def test_type_two_sequences_are_independent_and_can_be_inspected_non_strictly(self):
        self.save(2, [mido.Message("note_on", note=60, velocity=90)], [
            mido.Message("note_off", note=60, time=240),
        ])
        with self.assertRaisesRegex(ValueError, "Unmatched note-off"):
            validate_midi(self.path)
        report = validate_midi(self.path, require_complete_notes=False)
        self.assertEqual(report["unclosed_notes"], 1)
        self.assertEqual(report["unmatched_note_offs"], 1)

    def test_unknown_meta_delta_is_included_in_report(self):
        self.write_raw("04 ff 10 00 0c c0 26 00 90 3c 40 12 3c 00 00 ff 2f 00")
        report = validate_midi(self.path, expected_end_tick=34)
        self.assertEqual(report["tracks"][0]["programs"], [{"tick": 16, "channel": 0, "program": 38}])

    def test_rejects_malformed_framing_even_when_note_checks_are_disabled(self):
        cases = {
            "exceeds four bytes": "81 80 80 80 00 ff 2f 00",
            "empty payload": "00 ff 2f 01 00",
            "events after end_of_track": "00 ff 2f 00 00 ff 2f 00",
            "Invalid SMF event status": "00 f8 00 ff 2f 00",
            "without a running channel status": "00 90 3c 40 00 ff 10 00 12 3c 00 00 ff 2f 00",
            "Cannot decode MIDI events": "00 ff 51 02 07 a1 00 ff 2f 00",
            "extends beyond its track chunk": "00 90 3c",
        }
        for error, track_hex in cases.items():
            with self.subTest(error=error), self.assertRaisesRegex(ValueError, error):
                validate_midi(self.write_raw(track_hex), require_complete_notes=False)

    def test_rejects_smpte_without_interpreting_it_as_ppq(self):
        with self.assertRaisesRegex(ValueError, "PPQ timing"):
            validate_midi(self.write_raw("00 ff 2f 00", division=0xE728))


if __name__ == "__main__":
    unittest.main()
