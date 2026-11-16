# Windows MIDI Player

This folder contains the native Windows MIDI Player application, separate from the Python MIDI composition and validation library.

## Capabilities

- Open and play Standard MIDI Files on 64-bit Windows.
- Render MIDI using the local Windows General MIDI DLS sound bank and Windows audio output.
- Select a Windows MIDI output port to send channel messages to a hardware interface, virtual MIDI port, or DAW.
- Play offline without a network service.

MIDI output timing follows the loaded file. The current implementation does not provide MIDI clock or external transport synchronization.

## Source

The original, user-verified C# source is retained as independent files in this directory. `Player.cs` provides the interface, `MidiFile.cs` handles parsing and event timing, `MidiSynth.cs` and `InstrumentBank.cs` render the local sound bank, `WaveOutput.cs` handles PCM output, and `MidiOutput.cs` handles Windows MIDI ports.

## Build

On Windows x64 with .NET Framework 4.x and PowerShell:

```powershell
cd apps/windows-midi-player
.\build.ps1
```

The build script invokes the system C# compiler at `%WINDIR%\Microsoft.NET\Framework64\v4.0.30319\csc.exe` and produces `MIDI Player.exe` in the same folder.

## Relationship to AI MIDI IO

The Python package generates and validates `.mid` files. The Windows player is an optional, independent playback application that can open those MIDI files. No Python runtime or interprocess bridge is necessary.

Three separately supplied Windows executable builds were not added to version control. Their correspondence to the archived source is not established by this source import; the Windows project can be built directly from the retained C# files.
