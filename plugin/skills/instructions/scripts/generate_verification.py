"""Compatibility entry point for the original plugin verification fixture."""

from __future__ import annotations

from pathlib import Path

from ai_midi_io.demo import generate as _generate, main
from ai_midi_io_runtime import _reference_directory


def generate(output_root: Path, references: Path | None = None) -> dict:
    return _generate(output_root, references or _reference_directory())


if __name__ == "__main__":
    raise SystemExit(main(default_output_root=Path("/mnt/data"), default_references=_reference_directory()))
