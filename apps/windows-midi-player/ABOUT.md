# Windows MIDI Player

This folder contains the native Windows MIDI Player application, separate from the Python MIDI composition and validation library.

## Capabilities

- Open and play Standard MIDI Files on 64-bit Windows.
- Render MIDI using the local Windows General MIDI DLS sound bank and Windows audio output.
- Select a Windows MIDI output port to send channel messages to a hardware interface, virtual MIDI port, or DAW.
- Play offline without a network service.

MIDI output timing follows the loaded file. The current implementation does not provide MIDI clock or external transport synchronization.

## Source

The player is maintained as C# source in this directory. `Player.cs` defines the Windows interface, `MidiFile.cs` parses MIDI events and timing, `MidiSynth.cs` and `InstrumentBank.cs` provide software synthesis, `WaveOutput.cs` handles PCM audio output, and `MidiOutput.cs` handles Windows MIDI output ports.

## Build

On Windows x64 with .NET Framework 4.x and PowerShell:

```powershell
cd apps/windows-midi-player
.\build.ps1
```

The build script invokes the system C# compiler at `%WINDIR%\Microsoft.NET\Framework64\v4.0.30319\csc.exe` and produces `MIDI Player.exe` in the same folder.

## Relationship to AI MIDI IO

The Python package generates and validates `.mid` files. The Windows player is an optional, independent playback application that can open those MIDI files. No Python runtime or interprocess bridge is necessary.

The included `build.ps1` compiles the maintained source. GitHub Actions also provides a Windows x64 build workflow under `.github/workflows/windows-midi-player.yml`.
