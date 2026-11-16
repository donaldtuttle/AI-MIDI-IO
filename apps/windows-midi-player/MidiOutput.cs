using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Text;

internal sealed class MidiOutput : IPlayback
{
    private readonly MidiFile file;
    private readonly Stopwatch transport = new Stopwatch();
    private readonly bool[] usedChannels = new bool[16];
    private IntPtr handle;
    private int next;

    public MidiOutput(MidiFile file, Port port)
    {
        this.file = file;
        Capabilities current;
        Check(midiOutGetDevCapsW((UIntPtr)port.Id, out current, CapabilitySize));
        if (current.Name != port.Name)
            throw new InvalidOperationException("The MIDI output changed. Choose the port again.");
        Check(midiOutOpen(out handle, port.Id, IntPtr.Zero, IntPtr.Zero, 0));
        transport.Start();
    }

    public long Position { get { return (long)(transport.Elapsed.TotalSeconds * MidiFile.SampleRate); } }

    public bool Pump()
    {
        long position = Position;
        while (next < file.Events.Count && file.Events[next].Time <= position)
        {
            MidiEvent message = file.Events[next++];
            if (message.Status >= 0xF0)
            {
                Silence();
                continue;
            }
            usedChannels[message.Status & 15] = true;
            Check(midiOutShortMsg(handle, (uint)(message.Status | (message.A << 8) | (message.B << 16))));
        }
        return position < file.Duration;
    }

    public void Pause()
    {
        transport.Stop();
        Silence();
    }

    public void Resume() { transport.Start(); }

    private void Silence()
    {
        for (int channel = 0; channel < usedChannels.Length; channel++)
        {
            if (!usedChannels[channel])
                continue;
            uint status = (uint)(0xB0 | channel);
            midiOutShortMsg(handle, status | (64u << 8));
            midiOutShortMsg(handle, status | (123u << 8));
            midiOutShortMsg(handle, status | (120u << 8));
            usedChannels[channel] = false;
        }
    }

    public void Dispose()
    {
        if (handle == IntPtr.Zero)
            return;
        transport.Stop();
        Silence();
        midiOutClose(handle);
        handle = IntPtr.Zero;
    }

    public static IEnumerable<Port> GetPorts()
    {
        uint count = midiOutGetNumDevs();
        for (uint index = 0; index < count; index++)
        {
            Capabilities caps;
            if (midiOutGetDevCapsW((UIntPtr)index, out caps, CapabilitySize) == 0)
                yield return new Port { Id = index, Name = caps.Name };
        }
    }

    internal sealed class Port
    {
        public uint Id;
        public string Name;
        public override string ToString() { return Name + " (" + (Id + 1) + ")"; }
    }

    private static readonly uint CapabilitySize = (uint)Marshal.SizeOf(typeof(Capabilities));

    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
    private struct Capabilities
    {
        public ushort Manufacturer, Product;
        public uint DriverVersion;
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 32)]
        public string Name;
        public ushort Technology, Voices, Notes, ChannelMask;
        public uint Support;
    }

    private static void Check(uint error)
    {
        if (error == 0)
            return;
        var message = new StringBuilder(256);
        midiOutGetErrorTextW(error, message, (uint)message.Capacity);
        throw new Win32Exception((int)error, message.Length > 0 ? message.ToString() : "The MIDI output could not be opened.");
    }

    [DllImport("winmm.dll")]
    private static extern uint midiOutGetNumDevs();
    [DllImport("winmm.dll", CharSet = CharSet.Unicode, ExactSpelling = true)]
    private static extern uint midiOutGetDevCapsW(UIntPtr id, out Capabilities capabilities, uint size);
    [DllImport("winmm.dll")]
    private static extern uint midiOutOpen(out IntPtr handle, uint id, IntPtr callback, IntPtr instance, uint flags);
    [DllImport("winmm.dll")]
    private static extern uint midiOutShortMsg(IntPtr handle, uint message);
    [DllImport("winmm.dll")]
    private static extern uint midiOutClose(IntPtr handle);
    [DllImport("winmm.dll", CharSet = CharSet.Unicode, ExactSpelling = true)]
    private static extern uint midiOutGetErrorTextW(uint error, StringBuilder message, uint size);
}

