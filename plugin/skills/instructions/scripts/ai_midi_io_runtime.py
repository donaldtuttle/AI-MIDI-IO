"""Compatibility entry point for the AI MIDI IO plugin runtime."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project")
    args = parser.parse_args()
    print(json.dumps({"status": "ok", "project": args.project}))

if __name__ == "__main__":
    main()
