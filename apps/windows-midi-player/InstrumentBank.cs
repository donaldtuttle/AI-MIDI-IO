using System;
using System.Collections.Generic;
using System.IO;
using System.Text;

internal sealed class InstrumentBank
{
    private readonly Dictionary<uint, List<Region>> programs = new Dictionary<uint, List<Region>>();
    private const uint DrumBank = 0x80000000;

    public List<Region> GetRegions(bool drums, int bankMsb, int bankLsb, int program)
    {
        uint bank = drums ? DrumBank : (uint)((bankMsb << 8) | bankLsb);
        List<Region> regions;
        if (programs.TryGetValue(bank | ((uint)program << 16), out regions))
            return regions;
        return programs[drums ? DrumBank : ((uint)program << 16)];
    }

    public static InstrumentBank Load()
    {
        string path = Path.Combine(Environment.SystemDirectory, "drivers", "gm.dls");
        if (!File.Exists(path))
            throw new IOException("The General MIDI instrument bank supplied with Windows could not be found.");
        byte[] bytes = File.ReadAllBytes(path);
        var root = new Chunk(bytes, 0, bytes.Length).Find("DLS ");
        Chunk pool = root.Find("wvpl");
        Chunk table = root.Find("ptbl");
        var waves = new Dictionary<int, Sample>();
        foreach (Chunk wave in pool.Children())
        {
            if (wave.Tag != "wave")
                continue;
            using (BinaryReader format = wave.Find("fmt ").Reader())
            using (BinaryReader data = wave.Find("data").Reader())
            {
                if (format.ReadUInt16() != 1 || format.ReadUInt16() != 1)
                    throw new InvalidDataException("The Windows instrument bank contains an unexpected sample format.");
                int rate = format.ReadInt32();
                format.ReadInt32();
                format.ReadUInt16();
                if (format.ReadUInt16() != 16 || rate <= 0)
                    throw new InvalidDataException("The Windows instrument bank contains an unexpected sample format.");
                var samples = new short[data.BaseStream.Length / 2];
                for (int index = 0; index < samples.Length; index++)
                    samples[index] = data.ReadInt16();
                waves.Add(wave.Start - 12 - pool.Start, new Sample { Data = samples, Rate = rate });
            }
        }

        Sample[] samplesByCue;
        using (BinaryReader cues = table.Reader())
        {
            int headerSize = cues.ReadInt32();
            int cueCount = cues.ReadInt32();
            cues.BaseStream.Position = headerSize;
            samplesByCue = new Sample[cueCount];
            for (int index = 0; index < samplesByCue.Length; index++)
                samplesByCue[index] = waves[cues.ReadInt32()];
        }

        var result = new InstrumentBank();
        foreach (Chunk instrument in root.Find("lins").Children())
        {
            if (instrument.Tag != "ins ")
                continue;
            uint bank, program;
            using (BinaryReader info = instrument.Find("insh").Reader())
            {
                info.ReadUInt32();
                bank = info.ReadUInt32();
                program = info.ReadUInt32();
            }
            var regions = new List<Region>();
            Articulation defaults = ReadArticulation(instrument, Articulation.Default);
            foreach (Chunk region in instrument.Find("lrgn").Children())
            {
                if (region.Tag == "rgn ")
                    regions.Add(ReadRegion(region, samplesByCue, defaults));
            }
            result.programs.Add(bank | (program << 16), regions);
        }
        return result;
    }

    private static Region ReadRegion(Chunk chunk, Sample[] waves, Articulation defaults)
    {
        var region = new Region { Art = ReadArticulation(chunk, defaults) };
        using (BinaryReader info = chunk.Find("rgnh").Reader())
        {
            region.KeyLow = info.ReadUInt16();
            region.KeyHigh = info.ReadUInt16();
            region.VelLow = info.ReadUInt16();
            region.VelHigh = info.ReadUInt16();
            info.ReadUInt16();
            region.Group = info.ReadUInt16();
        }
        using (BinaryReader link = chunk.Find("wlnk").Reader())
        {
            link.BaseStream.Position = 8;
            region.Sample = waves[link.ReadInt32()];
        }
        using (BinaryReader info = chunk.Find("wsmp").Reader())
        {
            int headerSize = info.ReadInt32();
            region.Root = info.ReadUInt16();
            region.Tune = info.ReadInt16() / 100.0;
            region.Gain = FromGain(info.ReadInt32() / 65536.0);
            info.ReadUInt32();
            int loops = info.ReadInt32();
            if (loops > 0)
            {
                info.BaseStream.Position = headerSize + 8;
                int start = info.ReadInt32();
                int length = info.ReadInt32();
                if (start >= 0 && length > 1 && length <= region.Sample.Data.Length - start)
                {
                    region.LoopStart = start;
                    region.LoopEnd = start + length;
                }
            }
        }
        return region;
    }

    private static Articulation ReadArticulation(Chunk owner, Articulation art)
    {
        Chunk list;
        if (!owner.TryFind("lart", out list))
            return art;
        using (BinaryReader values = list.Find("art1").Reader())
        {
            int headerSize = values.ReadInt32();
            int count = values.ReadInt32();
            values.BaseStream.Position = headerSize;
            for (int index = 0; index < count; index++)
            {
                int source = values.ReadUInt16();
                int control = values.ReadUInt16();
                int destination = values.ReadUInt16();
                int transform = values.ReadUInt16();
                int value = values.ReadInt32();
                if (source != 0 || control != 0 || transform != 0)
                    continue;
                double scale = value / 65536.0;
                switch (destination)
                {
                    case 1: art.Gain = FromGain(scale); break;
                    case 3: art.Tune = scale / 100; break;
                    case 4: art.Pan = scale / 500; break;
                    case 0x206: art.Attack = Seconds(value); break;
                    case 0x207: art.Decay = Seconds(value); break;
                    case 0x209: art.Release = Seconds(value); break;
                    case 0x20A: art.Sustain = Math.Max(0, Math.Min(1, scale / 1000)); break;
                }
            }
        }
        return art;
    }

    private static double Seconds(int value)
    {
        return value == int.MinValue ? 0 : Math.Pow(2, value / (65536.0 * 1200));
    }

    private static double FromGain(double tenthsOfADecibel)
    {
        return Math.Pow(10, tenthsOfADecibel / 200);
    }

    internal sealed class Sample
    {
        public short[] Data;
        public int Rate;
    }

    internal sealed class Region
    {
        public Sample Sample;
        public Articulation Art;
        public int KeyLow, KeyHigh, VelLow, VelHigh, Root, Group, LoopStart, LoopEnd;
        public double Gain, Tune;
    }

    internal struct Articulation
    {
        public double Gain, Pan, Tune, Attack, Decay, Sustain, Release;
        public static readonly Articulation Default = new Articulation { Gain = 1, Sustain = 1, Release = 0.15 };
    }

    private struct Chunk
    {
        private readonly byte[] data;
        private readonly int end;
        public readonly int Start;
        public readonly string Tag;

        public Chunk(byte[] data, int start, int end, string tag = "")
        {
            this.data = data;
            Start = start;
            this.end = end;
            Tag = tag;
        }

        public BinaryReader Reader()
        {
            return new BinaryReader(new MemoryStream(data, Start, end - Start, false));
        }

        public IEnumerable<Chunk> Children()
        {
            for (int offset = Start; offset <= end - 8;)
            {
                string tag = Encoding.ASCII.GetString(data, offset, 4);
                int length = BitConverter.ToInt32(data, offset + 4);
                int body = offset + 8;
                if (length < 0 || length > end - body)
                    throw new InvalidDataException("The Windows instrument bank is incomplete.");
                int chunkEnd = body + length;
                if ((tag == "RIFF" || tag == "LIST") && length >= 4)
                {
                    tag = Encoding.ASCII.GetString(data, body, 4);
                    body += 4;
                }
                yield return new Chunk(data, body, chunkEnd, tag);
                offset = chunkEnd + (length & 1);
            }
        }

        public bool TryFind(string tag, out Chunk match)
        {
            foreach (Chunk chunk in Children())
            {
                if (chunk.Tag == tag)
                {
                    match = chunk;
                    return true;
                }
            }
            match = default(Chunk);
            return false;
        }

        public Chunk Find(string tag)
        {
            Chunk match;
            if (!TryFind(tag, out match))
                throw new InvalidDataException("The Windows instrument bank is incomplete.");
            return match;
        }
    }
}
