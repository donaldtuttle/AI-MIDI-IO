# Public distribution and publication checklist

AI MIDI IO provides two different distribution surfaces:

1. **Public source**: Python composition library, Windows C# MIDI Player, skills, tests and documentation.
2. **ChatGPT/Codex plugin**: a skills-based ZIP built by `python tools/build_public_plugin.py dist/AI-MIDI-IO-plugin-public.zip`.

## Build and verify the plugin

```sh
python tools/build_public_plugin.py dist/AI-MIDI-IO-plugin-public.zip
python -m unittest discover -s tests -p test_public_plugin.py -v
```

The distributable plugin includes an Agent Plugins manifest, Codex compatibility manifest, skill, concise independent MIDI reference, reusable first-party Python modules, runtime adapters, a square SVG logo, and the MIT-licensed legacy MIDIUtil writer with its notice. It does **not** include the archived prompts, source backups, private ChatGPT identifiers, or unreviewed extended reference collections.

The plugin does not host a MIDI service and cannot itself provision Python or install dependencies. MIDI file generation needs a Python execution environment with Mido 1.3.3 or compatible 1.x available. The Windows MIDI Player is a separate application.

## Install in ChatGPT

Eligible account or workspace administrators can upload the plugin ZIP through ChatGPT's plugin management interface. For general discovery, upload the ZIP as a public plugin submission and complete its automated checks, review and publication. The public directory is a distinct publishing step and may require developer verification. The GitHub source being public does not by itself install a ChatGPT plugin.

- [OpenAI packaging guide](https://developers.openai.com/plugins/build/plugins)
- [OpenAI submission process](https://developers.openai.com/plugins/deploy/submission)

## GitHub visibility and history warning

**Do not change the existing historical repository to public without addressing its Git history.** It currently includes preserved plugin identifiers and old conversation references. Removing files from `main` does not remove them from old commits. The archived references also require separate rights review.

For a safe public source release, publish a new repository initialized from a curated, verified export, or perform a deliberate, backed-up history rewrite and review every branch/tag and previously pushed object. Do not publish archived private source files by accident. Historical files are intentionally excluded from the public plugin ZIP.

Changing repository visibility requires repository administration access through GitHub Settings. Making a repository public exposes code, earlier commits and Actions logs.

## Before creating a public GitHub release

- [ ] Review public package contents for personal identifiers, credentials and external copyrighted material.
- [ ] Verify the package manifest, icon size/paths, and no missing referenced resources.
- [ ] Run Python and plugin package tests in a clean environment.
- [ ] Test importing the plugin into an eligible ChatGPT or Codex account.
- [ ] Review third-party copyright/license notices.
- [ ] Build and test the Windows MIDI Player on Windows x64.
- [ ] Publish release assets, with clear known limitations and dependency setup.
- [ ] Verify the public URL in a signed-out browser.
