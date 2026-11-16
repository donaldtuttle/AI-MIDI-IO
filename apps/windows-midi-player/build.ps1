$compiler = Join-Path $env:WINDIR 'Microsoft.NET\Framework64\v4.0.30319\csc.exe'
Push-Location $PSScriptRoot
try {
    & $compiler /nologo /target:winexe /platform:x64 /optimize+ /warnaserror+ /win32icon:player.ico /win32manifest:player.manifest '/out:MIDI Player.exe' /reference:System.Windows.Forms.dll /reference:System.Drawing.dll Player.cs MidiFile.cs MidiSynth.cs InstrumentBank.cs WaveOutput.cs MidiOutput.cs
    if ($LASTEXITCODE -ne 0) { throw 'Build failed.' }
} finally { Pop-Location }

