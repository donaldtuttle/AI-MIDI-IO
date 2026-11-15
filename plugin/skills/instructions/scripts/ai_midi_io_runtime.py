"""Compatibility entry point for the AI MIDI IO plugin runtime."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

# Support an installed package, a source checkout, or a built plugin overlay.
# The isolated plugin bootstrap runs with -I -S, so site-packages and PYTHONPATH
# are unavailable until the local dependency archive is initialized.
_scripts = Path(__file__).resolve().parent
for _root in (_scripts, _scripts.parents[3] / "src"):
    if (_root / "ai_midi_io" / "__init__.py").is_file():
        if str(_root) not in sys.path:
            sys.path.insert(0, str(_root))
        break


from ai_midi_io.runtime import (
    VERSION,
    extract_dependencies,
    initialize as _initialize,
    sandbox_link,
    scheduled_track,
    validate_midi,
    write_test_tone,
)

__all__ = [
    "VERSION",
    "extract_dependencies",
    "initialize",
    "sandbox_link",
    "scheduled_track",
    "validate_midi",
    "write_test_tone",
]


def _reference_directory() -> Path:
    sibling = Path(__file__).resolve().parents[1] / "references"
    return Path(os.environ.get("AI_MIDI_IO_REFERENCE_DIR", str(sibling)))


def initialize(
    reference_dir: str | Path | None = None,
    output_root: str | Path | None = None,
    require_midifile: bool = False,
) -> dict:
    """Use the original plugin reference and output defaults in this host adapter."""
    return _initialize(
        reference_dir or _reference_directory(),
        output_root or Path(os.environ.get("AI_MIDI_IO_BASE_DIR", "/mnt/data")),
        require_midifile,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--references", type=Path)
    parser.add_argument("--output-root", type=Path)
    parser.add_argument("--require-midifile", action="store_true")
    args = parser.parse_args()
    try:
        result = initialize(args.references, args.output_root, args.require_midifile)
    except Exception as error:
        print(json.dumps({"ready": False, "error": f"{type(error).__name__}: {error}"}, indent=2))
        return 1
    print(json.dumps(result["report"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
