"""Exercise the archived MIDIUtil writer with an independent Mido reload."""

from io import BytesIO
from struct import unpack
import unittest

from mido import MidiFile
from MIDIFile import MIDIFile


def write_smf(writer, expected_format, expected_tracks, expected_ppq):
    stream = BytesIO()
    writer.writeFile(stream)
    header = unpack(">4sIHHH", stream.getvalue()[:14])
    assert header == (b"MThd", 6, expected_format, expected_tracks, expected_ppq)
    stream.seek(0)
    return MidiFile(file=stream)


def note_timeline(track):
    tick = 0
    notes = []
    for message in track:
        tick += message.time
        if message.type in {"note_on", "note_off"}:
            notes.append((message.type, tick, message.channel, message.note, message.velocity))
    return notes


def make_arrangement(file_format, num_tracks):
    writer = MIDIFile(num_tracks, file_format=file_format, ticks_per_quarternote=480)
    writer.addTempo(0, 0, 120)
    writer.addTimeSignature(0, 0, 4, 2, 24)
    writer.addTrackName(0, 0, "Lead")
    writer.addProgramChange(0, 2, 0, 81)
    writer.addControllerEvent(0, 2, 0, 1, 32)
    writer.addPitchWheelEvent(0, 2, 0.25, -1024)
    writer.addNote(0, 2, 60, 0.25, 0.75, 91)
    if num_tracks > 1:
        writer.addNote(1, 9, 36, 0, 1, 100)
    return writer


class LegacyBackendTests(unittest.TestCase):
    def assert_tempo_and_meter(self, track):
        tempo = next(message for message in track if message.type == "set_tempo")
        meter = next(message for message in track if message.type == "time_signature")
        self.assertEqual((tempo.tempo, meter.numerator, meter.denominator), (500000, 4, 4))

    def assert_lead(self, track):
        self.assertEqual(track.name, "Lead")
        self.assertEqual(
            [(message.type, message.channel) for message in track if not message.is_meta],
            [
                ("program_change", 2), ("control_change", 2), ("pitchwheel", 2),
                ("note_on", 2), ("note_off", 2),
            ],
        )
        self.assertEqual(
            note_timeline(track),
            [("note_on", 120, 2, 60, 91), ("note_off", 480, 2, 60, 91)],
        )
        program = next(message for message in track if message.type == "program_change")
        cc = next(message for message in track if message.type == "control_change")
        pitch = next(message for message in track if message.type == "pitchwheel")
        self.assertEqual((program.program, cc.control, cc.value, pitch.pitch), (81, 1, 32, -1024))
        self.assertEqual(track[-1].type, "end_of_track")

    def assert_drums(self, track):
        self.assertEqual(
            note_timeline(track),
            [("note_on", 0, 9, 36, 100), ("note_off", 480, 9, 36, 100)],
        )

    def test_type_0_single_track_round_trip(self):
        midi = write_smf(make_arrangement(0, 1), 0, 1, 480)
        self.assertEqual((midi.type, len(midi.tracks), midi.ticks_per_beat), (0, 1, 480))
        self.assert_tempo_and_meter(midi.tracks[0])
        self.assert_lead(midi.tracks[0])

    def test_type_1_with_conductor_round_trip(self):
        midi = write_smf(make_arrangement(1, 2), 1, 3, 480)
        conductor, lead, drums = midi.tracks
        self.assert_tempo_and_meter(conductor)
        self.assertTrue(all(message.is_meta for message in conductor))
        self.assert_lead(lead)
        self.assert_drums(drums)

    def test_type_2_writer_round_trip(self):
        midi = write_smf(make_arrangement(2, 2), 2, 2, 480)
        lead, drums = midi.tracks
        self.assertEqual(midi.type, 2)
        self.assert_tempo_and_meter(lead)
        self.assert_lead(lead)
        self.assert_drums(drums)

    def test_overlapping_notes_preserve_ticks_with_transforms_off(self):
        writer = MIDIFile(removeDuplicates=False, deinterleave=False, eventtime_is_ticks=True)
        writer.addNote(0, 0, 60, 0, 480, 90)
        writer.addNote(0, 0, 60, 240, 480, 70)
        midi = write_smf(writer, 1, 2, 960)
        self.assertEqual(
            note_timeline(midi.tracks[1]),
            [
                ("note_on", 0, 0, 60, 90), ("note_on", 240, 0, 60, 70),
                ("note_off", 480, 0, 60, 90), ("note_off", 720, 0, 60, 70),
            ],
        )

    def test_legacy_default_moves_first_release_to_retrigger(self):
        writer = MIDIFile(eventtime_is_ticks=True)
        writer.addNote(0, 0, 60, 0, 480, 90)
        writer.addNote(0, 0, 60, 240, 480, 70)
        midi = write_smf(writer, 1, 2, 960)
        self.assertEqual(
            note_timeline(midi.tracks[1]),
            [
                ("note_on", 0, 0, 60, 90), ("note_off", 240, 0, 60, 90),
                ("note_on", 240, 0, 60, 70), ("note_off", 720, 0, 60, 70),
            ],
        )
