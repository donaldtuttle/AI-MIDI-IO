"""Publish the verified project tree to its GitHub repository using local Git credentials.

Run from the extracted release tree with: python tools/publish_to_github.py
The script does not force-push, delete remote files, or modify Git settings.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
REMOTE = "https://github.com/donaldtuttle/AI-MIDI-IO.git"
SKIP_DIRS = {".git", ".pytest_cache", "__pycache__", ".venv", "build", "dist", "*.egg-info"}


def run(*args: str, cwd: Path | None = None) -> str:
    completed = subprocess.run(args, cwd=cwd, text=True, check=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return completed.stdout.strip()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--remote", default=REMOTE)
    parser.add_argument("--branch", default="main")
    parser.add_argument("--dry-run", action="store_true", help="Stage and report changes without pushing")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="ai-midi-io-sync-") as temp:
        clone = Path(temp) / "repo"
        run("git", "clone", "--branch", args.branch, args.remote, str(clone))
        for path in ROOT.rglob("*"):
            relative = path.relative_to(ROOT)
            if any(part in SKIP_DIRS or part.endswith(".egg-info") for part in relative.parts):
                continue
            if path.is_file():
                target = clone / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, target)
        run("git", "add", "-A", cwd=clone)
        status = run("git", "status", "--short", cwd=clone)
        if not status:
            print("Repository is already synchronized.")
            return
        print(status)
        if args.dry_run:
            print("Dry run only; no commit or push performed.")
            return
        run("git", "commit", "-m", "Restore complete AI MIDI IO package, tests and documentation", cwd=clone)
        run("git", "push", "origin", args.branch, cwd=clone)
        print("Published commit:", run("git", "rev-parse", "HEAD", cwd=clone))


if __name__ == "__main__":
    main()
