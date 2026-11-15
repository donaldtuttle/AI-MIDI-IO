"""Command-line interface for the local AI MIDI IO file workflow."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from collections.abc import Sequence

from .audio import write_test_tone
from .demo import generate
from .project import initialize
from .validation import validate_midi


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ai-midi-io", description=__doc__)
    subcommands = parser.add_subparsers(dest="command", required=True)

    init = subcommands.add_parser("init", help="check and initialize a local project")
    demo = subcommands.add_parser("demo", help="generate and verify the four-part MIDI fixture")
    for command in (init, demo):
        command.add_argument("--output-root", type=Path)
        command.add_argument("--references", type=Path)
    init.add_argument("--require-midifile", action="store_true")

    validate = subcommands.add_parser("validate", help="read and validate a PPQ MIDI file")
    validate.add_argument("path", type=Path)
    validate.add_argument("--expected-musical-tracks", type=int)
    validate.add_argument("--expected-end-tick", type=int)
    validate.add_argument("--allow-incomplete-notes", action="store_true")

    tone = subcommands.add_parser("tone", help="write a diagnostic PCM WAV")
    tone.add_argument("path", type=Path)
    tone.add_argument("--frequency", type=float, default=432.0)
    tone.add_argument("--duration", type=float, default=0.5)
    tone.add_argument("--waveform", choices=("sine", "square", "triangle", "sawtooth"), default="sine")
    tone.add_argument("--sample-rate", type=int, default=44100)
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            report = initialize(args.references, args.output_root, args.require_midifile)["report"]
        elif args.command == "demo":
            report = generate(args.output_root, args.references)
        elif args.command == "validate":
            report = validate_midi(
                args.path,
                expected_musical_tracks=args.expected_musical_tracks,
                expected_end_tick=args.expected_end_tick,
                require_complete_notes=not args.allow_incomplete_notes,
            )
        else:
            report = write_test_tone(
                args.path, args.frequency, args.duration, args.waveform, args.sample_rate
            )
    except (ValueError, OSError, ImportError, RuntimeError) as error:
        print(json.dumps({"error": f"{type(error).__name__}: {error}"}, indent=2), file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
