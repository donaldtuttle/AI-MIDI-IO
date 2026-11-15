"""Convert a musical event schedule into a Mido track."""

from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mido import Message, MetaMessage, MidiTrack


_MAX_SMF_DELTA = 0x0FFFFFFF


def _priority(message: Message | MetaMessage) -> int:
    if message.type == "note_on":
        return 2 if message.velocity > 0 else 1
    return int(message.type == "note_off")


def scheduled_track(
    events: Iterable[tuple[int, Message | MetaMessage]], end_tick: int
) -> MidiTrack:
    """Copy absolute-tick events into a delta-tick track with an explicit tail.

    At a shared tick, non-note events come first, then note releases, then note
    onsets. Events of equal priority keep input order. Notes are not deduplicated.
    """
    from mido import MetaMessage, MidiTrack

    if type(end_tick) is not int or end_tick < 0:
        raise ValueError("end_tick must be a nonnegative integer")
    schedule = list(events)
    for tick, message in schedule:
        if type(tick) is not int or not 0 <= tick <= end_tick:
            raise ValueError("Event lies outside the nonnegative export interval")
        if message.type == "end_of_track":
            raise ValueError("scheduled_track creates its own end_of_track")

    track = MidiTrack()
    previous = 0
    for tick, message in sorted(schedule, key=lambda event: (event[0], _priority(event[1]))):
        delta = tick - previous
        if delta > _MAX_SMF_DELTA:
            raise ValueError("Event delta exceeds the four-byte SMF limit")
        track.append(message.copy(time=delta))
        previous = tick
    tail = end_tick - previous
    if tail > _MAX_SMF_DELTA:
        raise ValueError("End-of-track delta exceeds the four-byte SMF limit")
    track.append(MetaMessage("end_of_track", time=tail))
    return track
