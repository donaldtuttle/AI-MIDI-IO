# Publication assessment

**Reviewed:** November 16, 2026
**Repository:** [donaldtuttle/AI-MIDI-IO](https://github.com/donaldtuttle/AI-MIDI-IO)
**Basis:** main at `afc1e47826e3b3f841aaffdbf2b0361c71242762`, repository metadata, archived source files, packaging configuration, and the historical ZIP identified below.

## Conclusion

**No verified credential leak or copyright violation was established by the material inspected.** Historical plugin and release identifiers alone do not justify rewriting Git history or abandoning the existing repository. Publishing the existing repository is a reasonable option once the owner confirms that the retained reference materials may be redistributed and reviews any uninspected historical activity.

The repository was **private** at the time of this assessment. This is a publication-readiness assessment, not a claim that a public release or ChatGPT directory submission has occurred.

## Evidence and disposition

| Finding | Evidence | Publication consequence |
| --- | --- | --- |
| First-party software licensing | Root [MIT License](../LICENSE); licensing scope recorded in [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md) | Original Python library, Windows player source and supporting first-party work have a defined public license. |
| Third-party executable material | `legacy/MIDIFile.py` carries the original MIDIUtil copyright and MIT notice; Mido is an MIT-licensed dependency with a preserved upstream notice | Retain notices when redistributing those components. No Windows `gm.dls` sound bank is included. |
| Historical plugin identifiers | `plugin/plugin.json`, `plugin/provenance/AI_MIDI_IO_Repair_Report.json`, a lookup file, and the historical runtime notes include plugin/release IDs | These are identifiers, not verified authentication tokens. Their mere presence is not grounds for mandatory history rewriting. |
| Previously committed ZIP | Git blob `821e9f9fae8f2fe22394a643c13d57675460dd6d`, added in `f45eea27` and deleted in `5a7ae452`, matches the available `AI-MIDI-IO-Synchronized-2026-11-15.zip` byte-for-byte | Its 78 files were scanned for common API keys, private keys, GitHub tokens, personal email addresses, ChatGPT conversation links and ID patterns. No matches to those credential/email/conversation-link patterns were found. Historical plugin identifiers were found. Apparent phone-number matches were SHA-256 hash substrings. |
| Original and optimized knowledge references | User-supplied original and optimized MIDI reference documents are preserved under `plugin/skills/instructions/references/` | Their complete authorship, third-party quotations and redistribution rights have not been independently authenticated. No specific infringement has been demonstrated. Verify rights before freely distributing the archival set. |
| Public plugin distribution | `tools/build_public_plugin.py` builds a focused skills-only package that excludes historical plugin provenance and extended reference archives; acceptance tests are in `tests/test_public_plugin.py` | Suitable as a separate distribution path subject to clean-environment checks, upload validation, and any applicable directory review. A plugin ZIP does not provide a Python runtime or Mido automatically. |
| CI status | Latest inspected GitHub Actions run on `afc1e478` completed successfully | A passing CI result supports build/test readiness but is not a security, licensing, runtime-platform, or public-directory approval. |

## Scope and limitations

- The common-pattern scan covered the available 78-file historical ZIP, including the Git blob once committed and deleted. Several current documentation, manifest, source, and licensing files were also directly inspected. This was **not an exhaustive credential scan of every reachable Git object, branch, tag, historical commit, or Actions log**.
- Pattern scanning cannot establish the absence of every possible secret or personal detail.
- The source audit identifies the preserved references as project-supplied, but does not provide independent evidence of rights to republish all excerpts. Publishing or relicensing someone else's text requires appropriate rights.
- Neither the existing private ChatGPT deployment nor third-party Grok installations are affected by these documentation findings.

## Recommendation

1. **Keep the existing repository and Git history.** Do not rewrite history solely to remove AI-related prose or historical plugin identifiers.
2. Confirm that the archived MIDI references, prompts, examples, and icons are owned or otherwise authorized for public distribution. If they are, there is no need to split the project for that reason.
3. Perform a final review of GitHub Actions logs and any other branches/tags or earlier commits not covered by this assessment. If a genuine secret is identified, revoke or rotate it; address its exposure directly. File deletion from `main` alone does not remove past Git objects.
4. Make the repository public through GitHub **Settings → General → Danger Zone → Change repository visibility** when the above checks are satisfactory. GitHub publishes source, commit history and Actions logs when visibility changes.
5. Treat GitHub publishing, distributable plugin ZIP generation, ChatGPT Plugin Directory review, and executable releases as separate publication steps.

A fresh, history-free public repository or a deliberate, backed-up history rewrite is **optional**, not automatically required. Either may be appropriate only if the owner decides that historical materials must not be exposed at all.

For release mechanics, see [PUBLIC_RELEASE.md](PUBLIC_RELEASE.md). This assessment is not legal advice or a security certification.
