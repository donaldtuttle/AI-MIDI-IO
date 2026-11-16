"""Build a privacy-reviewed AI MIDI IO skills plugin ZIP without archived records."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugin"
SKILL_DIR = "skills/ai-midi-io"
VERSION = "0.63.3"


def _manifest() -> dict:
    interface = {
        "displayName": "AI MIDI IO",
        "shortDescription": "Compose and validate MIDI",
        "longDescription": (
            "Create and inspect Standard MIDI Files, develop musical arrangements, "
            "and validate note timing, tracks and metadata. Includes a reusable Python "
            "MIDI toolkit and concise music-theory reference. File generation requires "
            "an available Python execution environment with Mido installed. This "
            "skills-only plugin does not connect to audio hardware or a DAW."
        ),
        "developerName": "Donald Tuttle",
        "category": "Developer Tools",
        "capabilities": ["skills"],
        "logo": "./assets/ai-midi-io.svg",
        "composerIcon": "./assets/ai-midi-io.svg",
        "defaultPrompt": [
            "Generate and validate a four-track 120 BPM MIDI demo in C major.",
            "Create a 16-bar synthwave arrangement with melody, bass, drums, and pads.",
            "Explain MIDI CC automation and generate a short example file.",
        ],
    }
    return {
        "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
        "name": "ai-midi-io",
        "version": VERSION,
        "description": "MIDI composition, arrangement and Standard MIDI File validation",
        "author": {"name": "Donald Tuttle"},
        "homepage": "https://github.com/donaldtuttle/AI-MIDI-IO",
        "repository": "https://github.com/donaldtuttle/AI-MIDI-IO",
        "license": "MIT",
        "keywords": ["midi", "music composition", "music theory", "python"],
        "extensions": {"com.openai": {"interface": interface}},
    }


def _codex_manifest(manifest: dict) -> dict:
    return {
        "name": manifest["name"],
        "version": manifest["version"],
        "description": manifest["description"],
        "author": manifest["author"],
        "skills": "./skills",
        "interface": manifest["extensions"]["com.openai"]["interface"],
    }


def build(output: Path) -> Path:
    """Create a self-contained skills ZIP, except for declared external Mido dependency."""
    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest = _manifest()
    with TemporaryDirectory(prefix="ai-midi-io-public-", dir=output.parent) as directory:
        temp = Path(directory) / output.name
        with ZipFile(temp, "w", compression=ZIP_DEFLATED) as z:
            z.writestr("plugin.json", json.dumps(manifest, indent=2) + "\n")
            z.writestr(".codex-plugin/plugin.json", json.dumps(_codex_manifest(manifest), indent=2) + "\n")
            source_files = {
                "assets/ai-midi-io.svg": PLUGIN / "assets" / "ai-midi-io.svg",
                f"{SKILL_DIR}/SKILL.md": PLUGIN / "public" / "SKILL.md",
                f"{SKILL_DIR}/references/QUICK_REFERENCE.md": PLUGIN / "public" / "QUICK_REFERENCE.md",
                f"{SKILL_DIR}/references/MIDIFile.py": ROOT / "legacy" / "MIDIFile.py",
                f"{SKILL_DIR}/references/MIDIFile-LICENSE.txt": ROOT / "legacy" / "License.txt",
                f"{SKILL_DIR}/scripts/ai_midi_io_runtime.py": PLUGIN / "skills" / "instructions" / "scripts" / "ai_midi_io_runtime.py",
                f"{SKILL_DIR}/scripts/generate_verification.py": PLUGIN / "skills" / "instructions" / "scripts" / "generate_verification.py",
                "LICENSE": ROOT / "LICENSE",
                "THIRD_PARTY_NOTICES.md": ROOT / "THIRD_PARTY_NOTICES.md",
            }
            for p in sorted((ROOT / "src" / "ai_midi_io").glob("*.py")):
                source_files[f"{SKILL_DIR}/scripts/ai_midi_io/{p.name}"] = p
            for archive_name, source in sorted(source_files.items()):
                if not source.is_file():
                    raise FileNotFoundError(f"Required public plugin source is missing: {source}")
                z.write(source, archive_name)
        temp.replace(output)
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", nargs="?", type=Path,
                        default=ROOT / "dist" / f"AI-MIDI-IO-plugin-public-{VERSION}.zip")
    args = parser.parse_args()
    print(build(args.output))


if __name__ == "__main__":
    main()
