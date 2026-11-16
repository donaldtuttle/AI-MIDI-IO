using System;
using System.ComponentModel;
using System.Runtime.InteropServices;
using System.Text;

internal interface IPlayback : IDisposable
{
    long Position { get; }
    bool Pump();
    void Pause();
    void Resume();
}

internal sealed class WaveOutput : IPlayback
{
    private const int BlockFrames = 2048;
    private const uint HeaderDone = 1;
    private const uint TimeSamples = 2;
    private static readonly uint HeaderSize = (uint)Marshal.SizeOf(typeof(WaveHeader));
    private readonly Buffer[] buffers = new Buffer[5];
    private readonly short[] samples = new short[BlockFrames * 2];
    private readonly MidiSynth synth;
    private IntPtr handle;
    private long playedFrames;
    private bool end;

    public WaveOutput(MidiFile file, InstrumentBank bank)
    {
        synth = new MidiSynth(file, bank, BlockFrames);
        var format = new WaveFormat {
            Format = 1, Channels = 2, SamplesPerSecond = MidiFile.SampleRate,
            BytesPerSecond = MidiFile.SampleRate * 4, BlockAlign = 4, BitsPerSample = 16
        };
        try
        {
            Check(waveOutOpen(out handle, uint.MaxValue, ref format, IntPtr.Zero, IntPtr.Zero, 0));
            for (int i = 0; i < buffers.Length; i++)
            {
                var buffer = new Buffer();
                buffers[i] = buffer;
                buffer.Data = Marshal.AllocHGlobal(samples.Length * sizeof(short));
                buffer.Header = Marshal.AllocHGlobal((int)HeaderSize);
            }
            Check(waveOutPause(handle));
            if (!Pump())
                throw new InvalidOperationException("This MIDI file has no playback duration.");
            Resume();
        }
        catch
        {
            Dispose();
            throw;
        }
    }

    public long Position
    {
        get
        {
            var time = new WaveTime { Kind = TimeSamples };
            if (waveOutGetPosition(handle, ref time, (uint)Marshal.SizeOf(typeof(WaveTime))) == 0
                && time.Kind == TimeSamples)
                return time.Value;
            return playedFrames;
        }
    }

    public bool Pump()
    {
        bool pending = false;
        foreach (Buffer buffer in buffers)
        {
            if (buffer.Prepared)
            {
                var header = (WaveHeader)Marshal.PtrToStructure(buffer.Header, typeof(WaveHeader));
                if ((header.Flags & HeaderDone) == 0)
                {
                    pending = true;
                    continue;
                }
                Check(waveOutUnprepareHeader(handle, buffer.Header, HeaderSize));
                buffer.Prepared = false;
                playedFrames += buffer.Frames;
            }

            if (end)
                continue;
            buffer.Frames = synth.Render(samples);
            if (buffer.Frames == 0)
            {
                end = true;
                continue;
            }
            Marshal.Copy(samples, 0, buffer.Data, buffer.Frames * 2);
            var next = new WaveHeader { Data = buffer.Data, BufferLength = (uint)buffer.Frames * 4 };
            Marshal.StructureToPtr(next, buffer.Header, false);
            Check(waveOutPrepareHeader(handle, buffer.Header, HeaderSize));
            buffer.Prepared = true;
            Check(waveOutWrite(handle, buffer.Header, HeaderSize));
            pending = true;
        }
        return pending;
    }

    public void Pause() { Check(waveOutPause(handle)); }
    public void Resume() { Check(waveOutRestart(handle)); }

    public void Dispose()
    {
        if (handle != IntPtr.Zero)
            waveOutReset(handle);
        foreach (Buffer buffer in buffers)
        {
            if (buffer == null)
                continue;
            if (buffer.Prepared)
                waveOutUnprepareHeader(handle, buffer.Header, HeaderSize);
            Marshal.FreeHGlobal(buffer.Header);
            Marshal.FreeHGlobal(buffer.Data);
        }
        Array.Clear(buffers, 0, buffers.Length);
        if (handle != IntPtr.Zero)
        {
            waveOutClose(handle);
            handle = IntPtr.Zero;
        }
    }

    private static void Check(uint error)
    {
        if (error == 0)
            return;
        var message = new StringBuilder(256);
        waveOutGetErrorTextW(error, message, (uint)message.Capacity);
        throw new Win32Exception((int)error, message.Length > 0 ? message.ToString() : "Windows audio could not be started.");
    }

    private sealed class Buffer
    {
        public IntPtr Header, Data;
        public bool Prepared;
        public int Frames;
    }

    [StructLayout(LayoutKind.Sequential, Pack = 2)]
    private struct WaveFormat
    {
        public ushort Format, Channels;
        public uint SamplesPerSecond, BytesPerSecond;
        public ushort BlockAlign, BitsPerSample, ExtraBytes;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct WaveHeader
    {
        public IntPtr Data;
        public uint BufferLength, BytesRecorded;
        public UIntPtr User;
        public uint Flags, Loops;
        public IntPtr Next;
        public UIntPtr Reserved;
    }

    [StructLayout(LayoutKind.Sequential, Size = 12)]
    private struct WaveTime
    {
        public uint Kind, Value;
    }

    [DllImport("winmm.dll")]
    private static extern uint waveOutOpen(out IntPtr handle, uint device, ref WaveFormat format, IntPtr callback, IntPtr instance, uint flags);

    [DllImport("winmm.dll")]
    private static extern uint waveOutPrepareHeader(IntPtr handle, IntPtr header, uint size);

    [DllImport("winmm.dll")]
    private static extern uint waveOutUnprepareHeader(IntPtr handle, IntPtr header, uint size);

    [DllImport("winmm.dll")]
    private static extern uint waveOutWrite(IntPtr handle, IntPtr header, uint size);

    [DllImport("winmm.dll")]
    private static extern uint waveOutGetPosition(IntPtr handle, ref WaveTime time, uint size);

    [DllImport("winmm.dll")]
    private static extern uint waveOutPause(IntPtr handle);

    [DllImport("winmm.dll")]
    private static extern uint waveOutRestart(IntPtr handle);

    [DllImport("winmm.dll")]
    private static extern uint waveOutReset(IntPtr handle);

    [DllImport("winmm.dll")]
    private static extern uint waveOutClose(IntPtr handle);

    [DllImport("winmm.dll", CharSet = CharSet.Unicode, ExactSpelling = true)]
    private static extern uint waveOutGetErrorTextW(uint error, StringBuilder message, uint size);
}
