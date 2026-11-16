using System;
using System.Collections.Generic;

internal sealed class MidiSynth
{
    private const int Rate = MidiFile.SampleRate;
    private const int MaxVoices = 128;
    private readonly MidiFile song;
    private readonly InstrumentBank bank;
    private readonly List<Voice> voices = new List<Voice>(MaxVoices);
    private readonly Channel[] channels = new Channel[16];
    private readonly float[] mix;
    private int nextEvent;
    private long frame;

    public MidiSynth(MidiFile song, InstrumentBank bank, int blockSize)
    {
        this.song = song;
        this.bank = bank;
        mix = new float[blockSize * 2];
        Reset();
    }

    public int Render(short[] output)
    {
        int offset = 0;
        int count = output.Length / 2;
        Array.Clear(mix, 0, count * 2);
        while (offset < count)
        {
            while (nextEvent < song.Events.Count && song.Events[nextEvent].Time <= frame)
                Apply(song.Events[nextEvent++]);

            long nextFrame;
            if (frame >= song.Duration)
            {
                if (voices.Count == 0 || frame >= song.Duration + Rate * 3)
                    break;
                foreach (Voice voice in voices)
                    voice.Release();
                nextFrame = song.Duration + Rate * 3;
            }
            else
            {
                nextFrame = nextEvent < song.Events.Count ? song.Events[nextEvent].Time : song.Duration;
            }

            int length = (int)Math.Min(count - offset, nextFrame - frame);
            for (int index = voices.Count - 1; index >= 0; index--)
            {
                if (!voices[index].Render(mix, offset, length))
                    voices.RemoveAt(index);
            }
            offset += length;
            frame += length;
        }

        for (int index = 0; index < offset * 2; index++)
        {
            double value = mix[index];
            double over = Math.Abs(value) - 0.8;
            if (over > 0)
                value = Math.Sign(value) * (0.8 + 0.2 * over / (0.2 + over));
            output[index] = (short)(value * short.MaxValue);
        }
        return offset;
    }

    private void Reset()
    {
        voices.Clear();
        for (int i = 0; i < channels.Length; i++)
            channels[i] = new Channel();
    }

    private void Apply(MidiEvent item)
    {
        if (item.Status == 0xF0)
        {
            Reset();
            return;
        }
        Channel channel = channels[item.Status & 15];
        bool drums = (item.Status & 15) == 9;
        switch (item.Status & 0xF0)
        {
            case 0x80: NoteOff(channel, item.A); break;
            case 0x90:
                if (item.B == 0)
                    NoteOff(channel, item.A);
                else
                    NoteOn(channel, drums, item.A, item.B);
                break;
            case 0xB0: Control(channel, item.A, item.B); break;
            case 0xC0: channel.Program = item.A; break;
            case 0xE0: channel.Bend = (item.B << 7) | item.A; break;
        }
    }

    private void NoteOn(Channel channel, bool drums, int key, int velocity)
    {
        List<InstrumentBank.Region> regions = bank.GetRegions(drums, channel.BankMsb, channel.BankLsb, channel.Program);
        foreach (InstrumentBank.Region region in regions)
        {
            if (key < region.KeyLow || key > region.KeyHigh || velocity < region.VelLow || velocity > region.VelHigh)
                continue;
            foreach (Voice voice in voices)
            {
                if (voice.Channel == channel && region.Group != 0 && voice.Group == region.Group && voice.Key != key)
                    voice.Release(0.012);
            }
            if (voices.Count >= MaxVoices)
                voices.RemoveAt(0);
            voices.Add(new Voice(region, channel, drums, key, velocity));
        }
    }

    private void NoteOff(Channel channel, int key)
    {
        foreach (Voice voice in voices)
        {
            if (voice.Channel == channel && voice.Key == key)
                voice.NoteOff();
        }
    }

    private void Control(Channel channel, int control, int value)
    {
        switch (control)
        {
            case 0: channel.BankMsb = value; break;
            case 32: channel.BankLsb = value; break;
            case 6:
                if (channel.RpnMsb == 0 && channel.RpnLsb == 0)
                    channel.BendSemitones = value;
                break;
            case 38:
                if (channel.RpnMsb == 0 && channel.RpnLsb == 0)
                    channel.BendCents = value;
                break;
            case 7: channel.Volume = value; break;
            case 10: channel.Pan = value; break;
            case 11: channel.Expression = value; break;
            case 64:
                channel.Sustain = value >= 64;
                if (!channel.Sustain)
                    ReleasePedal(channel);
                break;
            case 100: channel.RpnLsb = value; break;
            case 101: channel.RpnMsb = value; break;
            case 120: voices.RemoveAll(voice => voice.Channel == channel); break;
            case 121:
                channel.ResetControllers();
                ReleasePedal(channel);
                break;
            case 123:
                foreach (Voice voice in voices)
                    if (voice.Channel == channel)
                        voice.NoteOff();
                break;
        }
    }

    private void ReleasePedal(Channel channel)
    {
        foreach (Voice voice in voices)
            if (voice.Channel == channel && voice.KeyReleased)
                voice.NoteOff();
    }

    private sealed class Channel
    {
        public int BankMsb, BankLsb, Program;
        public int Volume = 100, Pan = 64, Expression, Bend, BendSemitones, BendCents, RpnMsb, RpnLsb;
        public bool Sustain;

        public Channel() { ResetControllers(); }

        public void ResetControllers()
        {
            Expression = 127;
            Bend = 8192;
            BendSemitones = 2;
            BendCents = 0;
            RpnMsb = RpnLsb = 127;
            Sustain = false;
        }
    }

    private sealed class Voice
    {
        private readonly InstrumentBank.Region region;
        private readonly double step, gain, attackStep, decayFactor, sustain;
        private readonly bool oneShot;
        private double position, level, releaseFactor;
        private bool attacking = true, releasing;
        public readonly int Key;
        public readonly Channel Channel;
        public bool KeyReleased;
        public int Group { get { return region.Group; } }

        public Voice(InstrumentBank.Region region, Channel channel, bool drums, int key, int velocity)
        {
            this.region = region;
            Key = key;
            Channel = channel;
            oneShot = drums && region.LoopEnd == 0;
            step = (double)region.Sample.Rate / Rate * Math.Pow(2, (key - region.Root + region.Tune + region.Art.Tune) / 12);
            gain = 0.75 * region.Gain * region.Art.Gain * Math.Pow(velocity / 127.0, 1.5);
            attackStep = 1 / (Rate * Math.Max(0.002, region.Art.Attack));
            decayFactor = EnvelopeFactor(Math.Max(0.01, region.Art.Decay));
            sustain = region.Art.Sustain;
        }

        public void NoteOff()
        {
            KeyReleased = true;
            if (!oneShot && !Channel.Sustain)
                Release();
        }

        public void Release(double maxSeconds = 3)
        {
            if (releasing)
                return;
            releasing = true;
            releaseFactor = EnvelopeFactor(Math.Min(maxSeconds, Math.Max(0.035, region.Art.Release)));
        }

        public bool Render(float[] mix, int offset, int length)
        {
            double bend = (Channel.Bend - 8192) / 8192.0 * (Channel.BendSemitones + Channel.BendCents / 100.0);
            double increment = step * Math.Pow(2, bend / 12);
            double channelGain = Channel.Volume * Channel.Expression / (127.0 * 127);
            double amplitude = gain * channelGain * channelGain / 32768;
            double pan = Math.Max(-1, Math.Min(1, (Channel.Pan - 64) / 64.0 + region.Art.Pan));
            double angle = (pan + 1) * Math.PI / 4;
            double left = amplitude * Math.Cos(angle);
            double right = amplitude * Math.Sin(angle);
            short[] data = region.Sample.Data;
            int loopEnd = region.LoopEnd;
            int loopLength = loopEnd - region.LoopStart;
            int index = offset * 2;

            for (int frame = 0; frame < length; frame++)
            {
                if (loopLength > 0 && position >= loopEnd)
                    position = region.LoopStart + (position - loopEnd) % loopLength;
                if (position >= data.Length || (releasing && level < 0.000025))
                    return false;
                int current = (int)position;
                int next = current + 1;
                if (loopLength > 0 && next == loopEnd)
                    next = region.LoopStart;
                double tail = next < data.Length ? data[next] : 0;
                double sample = data[current] + (tail - data[current]) * (position - current);

                if (releasing)
                    level *= releaseFactor;
                else if (attacking)
                {
                    level = Math.Min(1, level + attackStep);
                    attacking = level < 1;
                }
                else
                    level = Math.Max(sustain, level * decayFactor);
                mix[index++] += (float)(sample * level * left);
                mix[index++] += (float)(sample * level * right);
                position += increment;
            }
            return true;
        }

        private static double EnvelopeFactor(double seconds)
        {
            return Math.Pow(0.000016, 1 / (seconds * Rate));
        }
    }
}
