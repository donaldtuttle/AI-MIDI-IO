# AI MIDI IO — iOS User Guide

This version is adjusted to behave better on iPhone and iPad Safari.

## What changed

The original page had a few issues that blocked or weakened iOS support:

- CSS variables were broken because many `var(--name)` references used the wrong dash character.
- Form controls were too small, which can trigger iOS zoom when you tap inputs.
- Download behavior was not friendly to Safari on iPhone/iPad.
- Web MIDI hardware routing was treated like a core feature, but on iOS browsers it is often unavailable.
- The MIDI writer could place note-on before note-off at the same tick, which can cause stuck or doubled notes in some players.

## What works on iOS now

- Audio preview in the browser
- Editing sections, BPM, root, scale, and instruments
- Exporting a `.mid` file
- Using the iOS Share Sheet to save the MIDI file to Files, AirDrop, or another app when supported

## What usually does **not** work on iOS browsers

- Direct Web MIDI hardware input/output inside Safari or other iOS browsers

That limitation is usually from browser support, not from your app logic. The fixed app now degrades cleanly and stays usable.

## How to use it

### 1. Open the HTML file
Open the fixed HTML file in Safari on your iPhone or iPad.

### 2. Set the musical basics
Use the top controls to choose:

- BPM
- Root note
- Octave
- Scale

### 3. Pick instruments
Choose:

- Chords instrument
- Bass instrument
- Arp instrument
- Arp direction

You can also toggle Bass, Arp, and Drums on or off.

### 4. Shape the arrangement
Each section has:

- Name
- Bars
- Progression
- Drum pattern
- Chord variation
- Velocity
- Humanize
- Drop percentage
- Fill frequency
- Inversion cycle toggle

Use **+ Section** to add more parts.

### 5. Preview
Tap **PREVIEW**.

On iOS, audio starts only after a user gesture, so tapping the button is the correct way to start playback.

### 6. Export the MIDI file
Tap **SAVE / SHARE .MID**.

On supported iPhones/iPads, the Share Sheet should appear and let you:

- Save to Files
- AirDrop
- Open in another music app
- Send to another device

If the Share Sheet does not appear, Safari may fall back to opening or downloading the file another way.

## Best way to install it on iPhone/iPad

For a more app-like experience:

1. Open the file or hosted page in Safari.
2. Tap the Share button.
3. Choose **Add to Home Screen**.

This makes it feel more like a standalone tool.

## Hardware MIDI notes

If you need live MIDI hardware routing, use a browser and platform that exposes Web MIDI support. The fixed page will show a message when that feature is unavailable and will still let you preview and export files.

## Files included

- `ai_midi_io_ios_fixed.html` — the corrected iOS-friendly app
- `AI_MIDI_IO_iOS_User_Guide.md` — this guide
