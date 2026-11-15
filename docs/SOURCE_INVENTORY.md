# Source audit

## Archives and integrity

The uploaded archive names end in `(2)`. They supply every original reference named as retained in the v0.63.2 repair, alongside the 28-file repair snapshot.

| Input | Contents | Integrity |
| --- | --- | --- |
| `AI_MIDI_IO_Knowledge_Backup_2026-11-15(2).zip` | Ten original source/reference files and `BACKUP_MANIFEST.json` | All ten files match the backup manifest's byte counts and SHA-256 hashes. Their sizes also match both repair metadata records. |
| `AI_MIDI_IO_Repair_2026-11-15(2).zip` | The 28-file repair snapshot plus provenance | Matches the repair report checksums. |

## Retained originals

All original reference texts listed in the backup manifest are preserved under `plugin/skills/instructions/references/` and the `source/` subdirectory.

See `docs/source_inventory.json` for the machine-readable checksum inventory.
