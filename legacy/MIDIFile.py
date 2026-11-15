# -----------------------------------------------------------------------------
# Name:        MIDIFile.py
# Purpose:     MIDI file manipulation utilities
#
# Author:      Mark Conway Wirt <emergentmusics) at (gmail . com>
#
# Created:     2008/04/17
# Copyright:   (c) 2009-2016 Mark Conway Wirt
# License:     Please see License.txt for the terms under which this
#              software is distributed.
#
# This is the archived original single-file MIDI writer. The modern
# implementation lives in src/ai_midi_io/ and uses Mido.
# Full original source is preserved in the local synchronized archive.

class MIDIFile:
    """Original MIDIUtil-style writer (archived)."""
    def __init__(self, numTracks=1, removeDuplicates=True, deinterleave=True):
        self.numTracks = numTracks
        # Full implementation retained in the local tree.
        pass

# ... remainder of original 73 KB source available in the synchronized archive
# and can be restored via tools/publish_to_github.py
