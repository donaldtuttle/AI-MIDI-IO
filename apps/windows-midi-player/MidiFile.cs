using System;
using System.Collections.Generic;
using System.IO;

internal struct MidiEvent
{
    public long Time;
    public int Status, A, B;
    public int Order;
}

internal sealed class MidiFile
{
    public const int SampleRate = 44100;
    public readonly List<MidiEvent> Events = new List<MidiEvent>();
    public long Duration;

    public static MidiFile Read(string path)
    {
        byte[] data;
        using (var stream = File.OpenRead(path))
        using (var reader = new BinaryReader(stream))
        {
            if (stream.Length > 64 * 1024 * 1024)
                throw new InvalidDataException("This MIDI file is too large to open.");
            data = reader.ReadBytes((int)stream.Length);
        }

        var file = new MidiFile();
        var input = new MidiReader(data, 0, data.Length);
        if (input.UInt32() != 0x4D546864)
            throw new InvalidDataException("Choose a Standard MIDI file (.mid or .midi).");
        MidiReader header = input.Chunk();
        int format = header.UInt16();
        int tracks = header.UInt16();
        int division = header.UInt16();
        if (format > 2 || tracks < 1 || (format == 0 && tracks != 1) || division == 0)
            throw new InvalidDataException("This file has an invalid MIDI header.");

        double framesPerTick = 0;
        if ((division & 0x8000) != 0)
        {
            int rate = 256 - (division >> 8);
            int ticksPerFrame = division & 255;
            if ((rate != 24 && rate != 25 && rate != 29 && rate != 30) || ticksPerFrame == 0)
                throw new InvalidDataException("This file has an invalid MIDI time division.");
            framesPerTick = SampleRate / ((rate == 29 ? 30000.0 / 1001 : rate) * ticksPerFrame);
        }

        var events = new List<MidiEvent>();
        long end = 0;
        for (int track = 0; track < tracks;)
        {
            uint tag = input.UInt32();
            MidiReader chunk = input.Chunk();
            if (tag != 0x4D54726B)
                continue;
            end = Math.Max(end, ReadTrack(chunk, events));
            track++;
            if (format == 2)
            {
                file.AddSequence(events, end, division, framesPerTick);
                // Format 2 tracks are independent patterns. Reset the synth between them.
                if (track < tracks)
                    file.Events.Add(new MidiEvent { Time = file.Duration, Status = 0xF0 });
                events.Clear();
                end = 0;
            }
        }

        if (format < 2)
            file.AddSequence(events, end, division, framesPerTick);
        return file;
    }

    private void AddSequence(List<MidiEvent> events, long end, int division, double framesPerTick)
    {
        events.Sort(delegate(MidiEvent x, MidiEvent y)
        {
            int order = x.Time.CompareTo(y.Time);
            return order == 0 ? x.Order.CompareTo(y.Order) : order;
        });
        bool smpte = framesPerTick != 0;
        double tickLength = smpte ? framesPerTick : SampleRate * 0.5 / division;
        double frame = Duration;
        long previousTick = 0;
        foreach (MidiEvent timed in events)
        {
            frame += (timed.Time - previousTick) * tickLength;
            previousTick = timed.Time;
            if (timed.Status == 0xFF)
            {
                if (!smpte)
                    tickLength = timed.A * (SampleRate / 1000000.0) / division;
                continue;
            }
            MidiEvent playable = timed;
            playable.Time = ToFrame(frame);
            Events.Add(playable);
        }
        Duration = ToFrame(frame + (end - previousTick) * tickLength);
    }

    private static long ToFrame(double frame)
    {
        if (frame > 24L * 60 * 60 * SampleRate)
            throw new InvalidDataException("This MIDI file lasts more than 24 hours.");
        return (long)Math.Round(frame);
    }

    private static long ReadTrack(MidiReader track, List<MidiEvent> events)
    {
        int runningStatus = 0;
        long tick = 0;
        while (track.Remaining > 0)
        {
            tick += track.VariableLength();
            int status = track.Peek();
            if (status >= 0x80)
            {
                track.Byte();
                runningStatus = status < 0xF0 ? status : 0;
            }
            else
            {
                status = runningStatus;
            }

            if (status == 0xFF)
            {
                int type = track.Byte();
                int length = track.VariableLength();
                if (type == 0x2F)
                {
                    track.Skip(length);
                    break;
                }
                if (type == 0x51 && length == 3)
                {
                    int tempo = (track.Byte() << 16) | (track.Byte() << 8) | track.Byte();
                    if (tempo > 0)
                        Add(events, tick, status, tempo, 0);
                }
                else
                {
                    track.Skip(length);
                }
            }
            else if (status == 0xF0 || status == 0xF7)
            {
                int length = track.VariableLength();
                MidiReader message = track.Take(length);
                if (status == 0xF0 && IsReset(message))
                    Add(events, tick, status, 0, 0);
            }
            else if (status >= 0x80 && status <= 0xEF)
            {
                int command = status & 0xF0;
                int a = track.DataByte();
                int b = command == 0xC0 || command == 0xD0 ? 0 : track.DataByte();
                Add(events, tick, status, a, b);
            }
            else
            {
                throw new InvalidDataException("This MIDI file contains a malformed track.");
            }
        }
        return tick;
    }

    private static bool IsReset(MidiReader msg)
    {
        if (msg.Remaining < 4)
            return false;
        int manufacturer = msg.Byte();
        msg.Byte(); // Device number
        if (manufacturer == 0x7E && msg.Byte() == 0x09)
        {
            int mode = msg.Byte();
            return mode >= 1 && mode <= 3;
        }
        return manufacturer == 0x41 && msg.Remaining >= 6
            && msg.Byte() == 0x42 && msg.Byte() == 0x12
            && msg.Byte() == 0x40 && msg.Byte() == 0x00 && msg.Byte() == 0x7F && msg.Byte() == 0x00;
    }

    private static void Add(List<MidiEvent> events, long tick, int status, int a, int b)
    {
        if (events.Count >= 2000000)
            throw new InvalidDataException("This MIDI file contains too many events to open.");
        events.Add(new MidiEvent { Time = tick, Status = status, A = a, B = b, Order = events.Count });
    }

    private sealed class MidiReader
    {
        private readonly byte[] data;
        private readonly int end;
        private int position;

        public MidiReader(byte[] data, int position, int end)
        {
            this.data = data;
            this.position = position;
            this.end = end;
        }

        public int Remaining { get { return end - position; } }

        public int Peek()
        {
            if (position >= end)
                throw new InvalidDataException("This MIDI file ends before its track data is complete.");
            return data[position];
        }

        public int Byte()
        {
            int result = Peek();
            position++;
            return result;
        }

        public int DataByte()
        {
            int value = Byte();
            if (value >= 0x80)
                throw new InvalidDataException("This MIDI file contains a malformed event.");
            return value;
        }

        public int UInt16() { return (Byte() << 8) | Byte(); }
        public uint UInt32() { return ((uint)UInt16() << 16) | (uint)UInt16(); }

        public MidiReader Chunk()
        {
            uint length = UInt32();
            if (length > (uint)Remaining)
                throw new InvalidDataException("This MIDI file has incomplete chunk data.");
            return Take((int)length);
        }

        public MidiReader Take(int length)
        {
            int start = position;
            Skip(length);
            return new MidiReader(data, start, position);
        }

        public void Skip(int count)
        {
            if (count > Remaining)
                throw new InvalidDataException("This MIDI file has an incomplete event.");
            position += count;
        }

        public int VariableLength()
        {
            int result = 0;
            for (int i = 0; i < 4; i++)
            {
                int value = Byte();
                result = (result << 7) | (value & 127);
                if ((value & 128) == 0)
                    return result;
            }
            throw new InvalidDataException("This MIDI file contains an invalid event length.");
        }
    }
}
