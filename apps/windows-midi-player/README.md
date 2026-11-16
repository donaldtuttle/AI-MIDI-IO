# MIDI Player

A portable MIDI player for 64-bit Windows. Open a .mid or .midi file, then click Play. The player works offline. It reads the General MIDI sound bank supplied by Windows and sends audio to the default sound output.

## Build

Run .\build.ps1 from PowerShell on 64-bit Windows with .NET Framework 4.x installed. It produces MIDI Player.exe in the source directory.

## Extending the player

Player.cs contains the Windows interface. MidiFile.cs reads and times MIDI events. MidiSynth.cs renders events using the samples loaded by InstrumentBank.cs. WaveOutput.cs sends the rendered audio to Windows.

## Send MIDI to a DAW or instrument

Choose a Windows MIDI output in the dropdown next to Open MIDI. For a DAW such as FL Studio, use a Windows virtual MIDI port and select that same port as an input in the DAW. Route the input to a software instrument. For hardware, choose the MIDI interface or USB-MIDI output for the connected instrument. Press Play in MIDI Player.

The player follows the timing in the file. Output sends MIDI channel messages. MIDI clock and external transport synchronization are outside this version.

## License

The original MIDI Player C# source and build script are licensed under the
[MIT License](../../LICENSE), copyright (c) 2026 Donald Tuttle.

The application uses the `gm.dls` sound bank installed with Windows. Those
samples are not bundled with this project and are not covered by its MIT grant.
Other third-party assets and historical materials retain their own rights;
see [third-party notices](../../THIRD_PARTY_NOTICES.md).
