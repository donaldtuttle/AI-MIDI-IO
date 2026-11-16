# AI MIDI IO: Distribution and releases

AI MIDI IO is an AI-assisted MIDI composition toolkit that began as a Custom GPT. The project includes a reusable Python MIDI engine, agent-oriented skills and plugin packaging, and a standalone Windows MIDI Player.

The [source repository](https://github.com/donaldtuttle/AI-MIDI-IO) is **public**. The project's first-party software is [MIT-licensed](../LICENSE); third-party components and archived reference documents retain their applicable rights. See [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md).

## Use the Python toolkit

Clone the repository, install the package, and generate or validate a Standard MIDI File:

```sh
git clone https://github.com/donaldtuttle/AI-MIDI-IO.git
cd AI-MIDI-IO
python -m pip install .
ai-midi-io demo --output-root ./out
ai-midi-io validate out/midi_generation/AI_MIDI_IO_Verification_4track_120BPM.mid --expected-musical-tracks 4 --expected-end-tick 30720
```

Python 3.10 or later is required. Mido is a declared package dependency.

## Build the Windows MIDI Player

On Windows x64 with .NET Framework 4.x and PowerShell:

```powershell
cd apps/windows-midi-player
.\build.ps1
```

The resulting `MIDI Player.exe` can open Standard MIDI Files for playback. Windows MIDI Out can send channel messages to a selected hardware or virtual MIDI device. The player uses the General MIDI DLS sound bank installed with Windows; sound-bank samples are not included in this repository.

The [Windows build workflow](../.github/workflows/windows-midi-player.yml) also compiles the tracked source and uploads its executable as a GitHub Actions artifact. A successful automated build does not establish that independently supplied older executables are byte-identical.

## Build the ChatGPT/Codex plugin

```sh
python tools/build_public_plugin.py dist/AI-MIDI-IO-plugin-public.zip
python -m unittest discover -s tests -p test_public_plugin.py -v
```

The resulting ZIP contains plugin manifests, a packaged MIDI skill, an original compact MIDI reference, Python source modules, runtime adapters, an icon, and applicable license notices. The historical plugin provenance and extended archived references are not included in this distribution ZIP.

The plugin is designed to work with an AI agent that has an executable Python environment. Standard MIDI File generation and validation require Mido 1.3.3 or compatible 1.x. Installing the plugin alone does not provision Python, Mido, MIDI hardware, or an audio renderer.

To make the plugin available within ChatGPT, use the supported import and publishing workflow; making the GitHub repository public does not automatically publish a ChatGPT Plugin Directory listing.

- [Plugin packaging](https://developers.openai.com/plugins/build/plugins)
- [Plugin submission](https://developers.openai.com/plugins/deploy/submission)

## Release checklist

Before announcing a tagged, downloadable release:

- Run the Python, legacy backend, and plugin packaging tests.
- Confirm the Windows x64 player builds and the executable launches.
- Validate the downloadable MIDI fixture and package archives.
- Include MIT and third-party notices in distributed assets.
- Verify that the plugin installs and generates a validated MIDI file in a supported host environment.
- Create a versioned GitHub Release and attach the intended downloadable assets.

The [publication assessment](PUBLICATION_ASSESSMENT.md) is a dated historical audit record, not current installation guidance. See [testing notes](TESTING.md) for the scope of completed verification.
