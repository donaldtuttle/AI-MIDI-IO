using System;
using System.ComponentModel;
using System.Drawing;
using System.IO;
using System.Reflection;
using System.Windows.Forms;

[assembly: AssemblyTitle("MIDI Player")]
[assembly: AssemblyProduct("MIDI Player")]
[assembly: AssemblyDescription("Plays Standard MIDI files through Windows audio.")]
[assembly: AssemblyVersion("1.0.0.0")]
[assembly: AssemblyFileVersion("1.0.0.0")]

internal static class Program
{
    [STAThread]
    private static void Main()
    {
        Application.EnableVisualStyles();
        Application.SetCompatibleTextRenderingDefault(false);
        using (var player = new PlayerForm())
            Application.Run(player);
    }
}

internal sealed class PlayerForm : Form
{
    private readonly Button openButton, playButton, stopButton;
    private readonly Label fileLabel, timeLabel, stateLabel;
    private readonly ProgressBar progress;
    private readonly Timer timer;
    private readonly ToolTip tooltip = new ToolTip();
    private MidiFile file;
    private InstrumentBank bank;
    private IPlayback audio;
    private readonly ComboBox output;
    private bool paused;

    public PlayerForm()
    {
        Text = "MIDI Player";
        AccessibleName = "MIDI Player";
        Icon = Icon.ExtractAssociatedIcon(Application.ExecutablePath);
        ClientSize = new Size(486, 233);
        AutoScaleMode = AutoScaleMode.Dpi;
        FormBorderStyle = FormBorderStyle.FixedDialog;
        MaximizeBox = false;
        StartPosition = FormStartPosition.CenterScreen;
        Font = new Font("Segoe UI", 10f);
        bool highContrast = SystemInformation.HighContrast;
        BackColor = highContrast ? SystemColors.Window : Color.FromArgb(245, 247, 252);
        ForeColor = highContrast ? SystemColors.WindowText : Color.FromArgb(22, 31, 52);
        Color muted = highContrast ? SystemColors.WindowText : Color.FromArgb(75, 88, 111);

        var layout = new TableLayoutPanel
        {
            ColumnCount = 1, RowCount = 5, Dock = DockStyle.Fill, Padding = new Padding(22, 17, 22, 19)
        };
        layout.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 100));
        layout.RowStyles.Add(new RowStyle(SizeType.Absolute, 42));
        layout.RowStyles.Add(new RowStyle(SizeType.Absolute, 47));
        layout.RowStyles.Add(new RowStyle(SizeType.Absolute, 22));
        layout.RowStyles.Add(new RowStyle(SizeType.Percent, 100));
        layout.RowStyles.Add(new RowStyle(SizeType.Absolute, 41));
        Controls.Add(layout);

        openButton = MakeButton("&Open MIDI…", 125, false);
        openButton.Click += delegate { ChooseFile(); };
        var fileControls = new FlowLayoutPanel { Dock = DockStyle.Fill, WrapContents = false, Margin = Padding.Empty };
        fileControls.Controls.Add(openButton);
        output = new ComboBox
        {
            DropDownStyle = ComboBoxStyle.DropDownList, Width = 235, Margin = new Padding(8, 5, 0, 0),
            AccessibleName = "Playback output"
        };
        output.DropDown += delegate { RefreshOutputs(); };
        RefreshOutputs();
        fileControls.Controls.Add(output);
        layout.Controls.Add(fileControls, 0, 0);

        fileLabel = new Label
        {
            Text = "Choose a MIDI file to play",
            Dock = DockStyle.Fill, AutoEllipsis = true, TextAlign = ContentAlignment.MiddleLeft,
            Font = new Font(Font.FontFamily, 15f, FontStyle.Bold), Margin = Padding.Empty
        };
        layout.Controls.Add(fileLabel, 0, 1);

        progress = new ProgressBar
        {
            Dock = DockStyle.Top, Height = 8, Maximum = 1000, Style = ProgressBarStyle.Continuous,
            Margin = new Padding(0, 6, 0, 0), AccessibleName = "Playback progress"
        };
        layout.Controls.Add(progress, 0, 2);

        var information = new TableLayoutPanel { ColumnCount = 2, RowCount = 1, Dock = DockStyle.Fill, Margin = Padding.Empty };
        information.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 50));
        information.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 50));
        stateLabel = new Label { Dock = DockStyle.Fill, Margin = Padding.Empty, ForeColor = muted };
        timeLabel = new Label
        {
            Dock = DockStyle.Fill, Margin = Padding.Empty, ForeColor = muted,
            TextAlign = ContentAlignment.TopRight, AccessibleName = "Elapsed and total time"
        };
        information.Controls.Add(stateLabel, 0, 0);
        information.Controls.Add(timeLabel, 1, 0);
        layout.Controls.Add(information, 0, 3);

        var transport = new FlowLayoutPanel { Dock = DockStyle.Fill, WrapContents = false, Margin = Padding.Empty };
        playButton = MakeButton("&Play", 106, true);
        stopButton = MakeButton("&Stop", 79, false);
        playButton.Click += delegate { TogglePlayback(); };
        stopButton.Click += delegate { StopPlayback(); SetState("Ready to play", 0); };
        transport.Controls.Add(playButton);
        transport.Controls.Add(stopButton);
        layout.Controls.Add(transport, 0, 4);

        timer = new Timer { Interval = 10 };
        timer.Tick += delegate { UpdatePlayback(); };
        SetState("", 0);
        ActiveControl = openButton;
    }

    private void RefreshOutputs()
    {
        string previous = output.SelectedItem == null ? "" : output.SelectedItem.ToString();
        output.Items.Clear();
        output.Items.Add("Built-in sounds");
        foreach (MidiOutput.Port port in MidiOutput.GetPorts())
            output.Items.Add(port);
        int selection = output.FindStringExact(previous);
        output.SelectedIndex = selection >= 0 ? selection : 0;
    }

    private static Button MakeButton(string caption, int width, bool primary)
    {
        var button = new Button
        {
            Text = caption, Size = new Size(width, 36), Margin = new Padding(0, 0, 8, 0),
            UseVisualStyleBackColor = true
        };
        if (primary && !SystemInformation.HighContrast)
        {
            button.FlatStyle = FlatStyle.Flat;
            button.BackColor = Color.FromArgb(39, 69, 183);
            button.ForeColor = Color.White;
            button.FlatAppearance.BorderSize = 0;
            button.FlatAppearance.MouseOverBackColor = Color.FromArgb(49, 81, 200);
            button.FlatAppearance.MouseDownBackColor = Color.FromArgb(29, 53, 145);
            button.EnabledChanged += delegate
            {
                button.BackColor = button.Enabled ? Color.FromArgb(39, 69, 183) : Color.FromArgb(221, 228, 242);
            };
        }
        return button;
    }

    protected override bool ProcessCmdKey(ref Message message, Keys keys)
    {
        if (keys == (Keys.Control | Keys.O))
        {
            ChooseFile();
            return true;
        }
        return base.ProcessCmdKey(ref message, keys);
    }

    private void ChooseFile()
    {
        using (var dialog = new OpenFileDialog
        {
            Title = "Open a MIDI file", Filter = "MIDI files (*.mid; *.midi)|*.mid;*.midi|All files (*.*)|*.*",
            CheckFileExists = true, RestoreDirectory = true
        })
        {
            if (dialog.ShowDialog(this) == DialogResult.OK)
                OpenFile(dialog.FileName);
        }
    }

    private void OpenFile(string path)
    {
        MidiFile selected;
        try
        {
            selected = MidiFile.Read(path);
        }
        catch (Exception error)
        {
            if (!(error is IOException || error is InvalidDataException || error is UnauthorizedAccessException))
                throw;
            ShowError("Could not open the MIDI file", error);
            return;
        }

        StopPlayback();
        file = selected;
        fileLabel.Text = Path.GetFileName(path);
        tooltip.SetToolTip(fileLabel, path);
        SetState("Ready to play", 0);
        playButton.Focus();
    }

    private void TogglePlayback()
    {
        if (file == null)
            return;
        try
        {
            if (audio == null)
            {
                var port = output.SelectedItem as MidiOutput.Port;
                if (port != null)
                    audio = new MidiOutput(file, port);
                else
                {
                    if (bank == null)
                        bank = InstrumentBank.Load();
                    audio = new WaveOutput(file, bank);
                }
                timer.Start();
            }
            else if (paused)
            {
                audio.Resume();
                paused = false;
                timer.Start();
            }
            else
            {
                audio.Pause();
                paused = true;
                timer.Stop();
            }
            SetState(paused ? "Paused" : "Playing", audio.Position);
        }
        catch (Exception error)
        {
            if (!(error is IOException || error is InvalidDataException
                || error is UnauthorizedAccessException || error is Win32Exception || error is InvalidOperationException))
                throw;
            PlaybackError(error);
        }
    }

    private void UpdatePlayback()
    {
        try
        {
            if (audio.Pump())
            {
                SetProgress(audio.Position);
                return;
            }
            StopPlayback();
            SetState("Finished", file.Duration);
        }
        catch (Win32Exception error)
        {
            PlaybackError(error);
        }
    }

    private void PlaybackError(Exception error)
    {
        StopPlayback();
        SetState("Ready to play", 0);
        ShowError("Could not play the MIDI file", error);
    }

    private void StopPlayback()
    {
        timer.Stop();
        if (audio != null)
        {
            audio.Dispose();
            audio = null;
        }
        paused = false;
    }

    private void SetState(string state, long frame)
    {
        stateLabel.Text = state;
        playButton.Enabled = file != null;
        stopButton.Enabled = audio != null;
        output.Enabled = audio == null;
        playButton.Text = audio == null ? "&Play" : paused ? "&Resume" : "&Pause";
        AcceptButton = file == null ? openButton : playButton;
        SetProgress(frame);
    }

    private void SetProgress(long frame)
    {
        long total = file == null ? 0 : file.Duration;
        long position = Math.Max(0, Math.Min(total, frame));
        int value = total > 0 ? (int)(position * progress.Maximum / total) : 0;
        if (value != progress.Value)
            progress.Value = value;
        string label = TimeText(position) + " / " + TimeText(total);
        if (label != timeLabel.Text)
            timeLabel.Text = label;
    }

    private static string TimeText(long frames)
    {
        long seconds = frames / MidiFile.SampleRate;
        return seconds >= 3600
            ? string.Format("{0}:{1:00}:{2:00}", seconds / 3600, seconds / 60 % 60, seconds % 60)
            : string.Format("{0}:{1:00}", seconds / 60, seconds % 60);
    }

    private void ShowError(string title, Exception error)
    {
        MessageBox.Show(this, error.Message, title, MessageBoxButtons.OK, MessageBoxIcon.Error);
    }

    protected override void Dispose(bool disposing)
    {
        if (disposing)
        {
            if (timer != null)
            {
                StopPlayback();
                timer.Dispose();
            }
            tooltip.Dispose();
        }
        base.Dispose(disposing);
    }
}
