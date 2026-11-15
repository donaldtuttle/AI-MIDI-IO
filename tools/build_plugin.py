"""Build the plugin overlay from the current knowledge files."""
from __future__ import annotations

from pathlib import Path
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugin"
SKILL = PLUGIN / "skills" / "instructions"

def main() -> None:
    # Placeholder: the knowledge files are already in place.
    # This script can later copy or regenerate optimized references.
    print(f"plugin tree at {PLUGIN}")
    print(f"skill at {SKILL}")

if __name__ == "__main__":
    main()
