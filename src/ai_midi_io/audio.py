"""Generate simple mono PCM diagnostic tones."""

from __future__ import annotations

import math
from pathlib import Path
import struct
from typing import Any
import wave


_WAVEFORMS = {
    "sine": lambda phase: math.sin(2 * math.pi * phase),
    "square": lambda phase: 1.0 if phase < 0.5 else -1.0,
    "triangle": lambda phase: 1.0 - 4.0 * abs(phase - 0.5),
    "sawtooth": lambda phase: 2.0 * phase - 1.0,
}


def write_test_tone(
    path: str | Path,
    frequency: float = 432.0,
    duration: float = 0.5,
    waveform: str = "sine",
    sample_rate: int = 44100,
) -> dict[str, Any]:
    """Write and reopen a mono, 16-bit PCM diagnostic waveform."""
    if (type(sample_rate) is not int or sample_rate <= 0
            or not math.isfinite(frequency) or not 0 < frequency < sample_rate / 2
            or not math.isfinite(duration) or duration <= 0):
        raise ValueError("Invalid tone frequency, duration, or sample rate")
    if waveform not in _WAVEFORMS:
        raise ValueError(f"Unsupported waveform: {waveform}")
    frames = round(duration * sample_rate)
    if frames < 1:
        raise ValueError("Tone duration produces no samples")
    value_at_phase = _WAVEFORMS[waveform]
    path = Path(path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    ramp = min(max(1, int(sample_rate * 0.005)), max(1, frames // 2))

    with wave.open(str(path), "wb") as audio:
        audio.setparams((1, 2, sample_rate, frames, "NONE", "not compressed"))
        block = bytearray()
        for n in range(frames):
            phase = (n * frequency / sample_rate) % 1.0
            envelope = min(1.0, n / ramp, (frames - 1 - n) / ramp)
            sample = round(0.2 * envelope * value_at_phase(phase) * 32767)
            block.extend(struct.pack("<h", sample))
            if len(block) >= 8192:
                audio.writeframesraw(block)
                block.clear()
        if block:
            audio.writeframesraw(block)
    with wave.open(str(path), "rb") as audio:
        header = (audio.getnframes(), audio.getframerate(), audio.getnchannels(), audio.getsampwidth())
        if header != (frames, sample_rate, 1, 2):
            raise RuntimeError("WAV header validation failed")

    return {"path": str(path), "frames": frames, "sample_rate": sample_rate,
            "channels": 1, "bits_per_sample": 16, "frequency_hz": frequency,
            "waveform": waveform, "is_midi_render": False}
