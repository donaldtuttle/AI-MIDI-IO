# Public distribution and release checklist

AI MIDI IO has two independent distribution channels:

- **GitHub source:** Python MIDI toolkit, Windows C# MIDI Player, skills, tests, documentation and selectively licensed historical materials.
- **ChatGPT/Codex plugin:** a focused skills-only ZIP produced from the maintained Python source and the public plugin profile.

## Publication assessment

Read the [November 16, 2026 publication assessment](PUBLICATION_ASSESSMENT.md) before changing repository visibility.

**The existing Git history does not need to be rewritten merely because it contains historical plugin identifiers, AI development notes or archived instructions.** No confirmed leaked secret was identified in the inspected historical ZIP. That finding is scoped, not an exhaustive audit of all Git objects or Actions logs.

The practical remaining decision is whether the preserved original and optimized knowledge references may be publicly redistributed. The owner should confirm authorship or relevant permissions for that archival content. The root MIT License covers original first-party software, not automatically every imported reference or third-party excerpt.

### Publish this repository on GitHub

1. Review archived-reference redistribution rights and remaining GitHub Actions logs and history. Keep the existing repository if the retained archive is appropriate for public distribution.
2. On GitHub, open [AI MIDI IO](https://github.com/donaldtuttle/AI-MIDI-IO) → **Settings → General → Danger Zone → Change repository visibility**.
3. Choose **Public** and confirm GitHub's warnings. The GitHub UI action requires repository administration; it is not done by the plugin packaging script.
4. Verify the public URL from a signed-out browser, check the license and release links, and publish versioned release assets if desired.

Changing visibility exposes previous commits and Actions logs. If specific historical material must remain private, that needs a separate plan; removing it only from the latest commit is insufficient. A new public repository or backed-up history rewrite is an *option*, not a default prerequisite.

## Build the portable ChatGPT/Codex plugin

```sh
python tools/build_public_plugin.py dist/AI-MIDI-IO-plugin-public.zip
python -m unittest discover -s tests -p test_public_plugin.py -v
```

The public ZIP includes the plugin manifests, a packaged skill, a concise original MIDI reference, maintained Python sources, runtime adapters, a square SVG icon, the preserved MIT-licensed legacy writer and applicable notices. It excludes archival private-plugin IDs, historical repair reports, old prompts, and the extended unreviewed reference collection.

MIDI file generation still requires an executable Python environment and Mido 1.3.3 or compatible 1.x. The Windows MIDI Player is a separate application.

The ZIP is a distribution artifact, not an automatically installed ChatGPT plugin. Use the [OpenAI plugin packaging guide](https://developers.openai.com/plugins/build/plugins) and [submission process](https://developers.openai.com/plugins/deploy/submission) for supported import and public-directory publication. Directory listing requires upload checks, any applicable review, and publication by an authorized developer. A GitHub visibility change alone does not publish the plugin to ChatGPT.

## Release checklist

- [ ] Confirm the owner can publicly redistribute retained historical reference texts, diagrams and third-party excerpts.
- [ ] Review remaining Git history, branches/tags and Actions logs for confidential information before enabling public visibility.
- [ ] Build the plugin ZIP; verify manifests, referenced image paths, package integrity and dependency documentation.
- [ ] Run Python and plugin tests on the intended supported environments.
- [ ] Verify the Windows x64 player build and the distributable executable.
- [ ] Test installing the plugin from the actual ZIP in an eligible ChatGPT/Codex environment; verify real MIDI generation if Python and Mido are available.
- [ ] Make GitHub public, verify signed-out access, and publish download assets as appropriate.
- [ ] Submit the plugin separately to the directory if general in-product discovery is desired.

See [licensing](LICENSING.md), [third-party notices](../THIRD_PARTY_NOTICES.md), and [test results](TESTING.md). A successful CI build is not proof of a completed public release.
