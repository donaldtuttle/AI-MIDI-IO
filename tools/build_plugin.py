"""Build an AI MIDI IO source overlay while retaining the existing plugin identity."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugin"
SKILL = "skills/instructions"
LIBRARIES = "AI_MIDI_IO_Python.zip"


def _verified_source(source: bytes, name: str) -> bytes:
    manifest = json.loads((PLUGIN / "provenance" / "BACKUP_MANIFEST.json").read_bytes())
    entry = next(row for row in manifest["original_files"] if row["path"] == name)
    if len(source) != entry["bytes"] or hashlib.sha256(source).hexdigest() != entry["sha256"]:
        raise ValueError(f"Checksum or size mismatch for {name}")
    return source


def build(output: Path, *, original_backup: Path | None = None, icon: Path | None = None) -> Path:
    """Build the overlay; optionally restore the old dependency ZIP for private use."""
    output = output.resolve()
    source = ROOT / "src" / "ai_midi_io"
    if not (source / "__init__.py").is_file():
        raise FileNotFoundError(f"Canonical Python package not found at {source}")
    output.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix="ai-midi-io-plugin-", dir=output.parent) as directory:
        temporary = Path(directory) / output.name
        with ZipFile(temporary, "w", compression=ZIP_DEFLATED) as bundle:
            for manifest in (".codex-plugin/plugin.json", "plugin.json"):
                bundle.write(PLUGIN / manifest, manifest)
            for path in sorted((PLUGIN / "skills").rglob("*")):
                if path.is_file() and "__pycache__" not in path.parts:
                    bundle.write(path, path.relative_to(PLUGIN).as_posix())

            for path in sorted(source.rglob("*.py")):
                member = path.relative_to(source.parent).as_posix()
                bundle.write(path, f"{SKILL}/scripts/{member}")

            legacy = (ROOT / "legacy" / "MIDIFile.py").read_bytes()
            bundle.writestr(f"{SKILL}/references/MIDIFile.py", _verified_source(legacy, "MIDIFile.py"))
            bundle.write(ROOT / "legacy" / "License.txt", f"{SKILL}/references/MIDIFile-LICENSE.txt")

            if original_backup is not None:
                with ZipFile(original_backup) as backup:
                    dependencies = _verified_source(backup.read(LIBRARIES), LIBRARIES)
                bundle.writestr(f"{SKILL}/references/{LIBRARIES}", dependencies)
                bundle.write(
                    ROOT / "legacy" / "notices" / "Mido-LICENSE.txt",
                    f"{SKILL}/references/Mido-LICENSE.txt",
                )
            if icon is not None:
                bundle.write(icon, "assets/gpt-icon.jpg")
        temporary.replace(output)
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="Destination ZIP for the source overlay")
    parser.add_argument("--original-backup", type=Path, help="Restore the dependency ZIP in a private overlay")
    parser.add_argument("--icon", type=Path, help="Add an owner-supplied copy of the original icon")
    args = parser.parse_args()
    print(build(args.output, original_backup=args.original_backup, icon=args.icon))


if __name__ == "__main__":
    main()
