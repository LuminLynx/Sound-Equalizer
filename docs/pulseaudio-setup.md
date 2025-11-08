# PulseAudio Sound Equalizer Setup Guide

This guide explains how to set up a sound equalizer using PulseAudio and LADSPA plugins on Debian-based Linux distributions.

## Prerequisites

- Debian-based Linux distribution (Debian, Ubuntu, Linux Mint, etc.)
- PulseAudio sound server (usually pre-installed)
- Terminal/command line access

## Method 1: Using PulseAudio with LADSPA Plugins

### Installation

1. Install required packages:
```bash
sudo apt-get update
sudo apt-get install pulseaudio pulseaudio-utils ladspa-sdk swh-plugins
```

2. Verify LADSPA plugins are installed:
```bash
listplugins
```

### Configuration

#### Option A: Command-Line Configuration

1. List available LADSPA plugins:
```bash
analyseplugin /usr/lib/ladspa/mbeq_1197.so
```

2. Load the multiband equalizer module:
```bash
pacmd load-module module-ladspa-sink sink_name=ladspa_equalizer plugin=mbeq_1197 label=mbeq control=0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
```

The control parameters represent gain values for different frequency bands.

3. Set the equalizer as default:
```bash
pacmd set-default-sink ladspa_equalizer
```

4. To unload the module:
```bash
pacmd unload-module module-ladspa-sink
```

#### Option B: Persistent Configuration

1. Edit PulseAudio configuration file:
```bash
nano ~/.config/pulse/default.pa
```

2. Add the following lines at the end:
```
# Load LADSPA equalizer
.ifexists module-ladspa-sink.so
.nofail
load-module module-ladspa-sink sink_name=ladspa_equalizer master=@DEFAULT_SINK@ plugin=mbeq_1197 label=mbeq control=0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
set-default-sink ladspa_equalizer
.fail
.endif
```

3. Restart PulseAudio:
```bash
pulseaudio -k
pulseaudio --start
```

### Available LADSPA Plugins

#### DJ EQ (DJ EQ from Steve Harris plugin pack)
- Plugin: `dj_eq_1901`
- 3-band equalizer with low, mid, and high controls

#### Multiband EQ (MBEQ from Steve Harris plugin pack)
- Plugin: `mbeq_1197`
- 15-band equalizer
- Frequency bands: 50Hz, 100Hz, 156Hz, 220Hz, 311Hz, 440Hz, 622Hz, 880Hz, 1250Hz, 1750Hz, 2500Hz, 3500Hz, 5000Hz, 10000Hz, 20000Hz

### Adjusting Equalizer Settings

To adjust equalizer settings dynamically:

```bash
# Get the module number
pacmd list-modules | grep -A 3 "name: <module-ladspa-sink>"

# Unload current module (replace X with module number)
pacmd unload-module X

# Load with new settings (adjust control values)
pacmd load-module module-ladspa-sink sink_name=ladspa_equalizer plugin=mbeq_1197 label=mbeq control=0,3,5,3,0,-3,-5,-3,0,0,0,0,0,0,0
```

## Method 2: Using PulseEffects

PulseEffects is a GUI application that makes equalizer configuration much easier.

### Installation

1. Install PulseEffects:
```bash
sudo apt-get install pulseeffects
```

2. Launch PulseEffects:
```bash
pulseeffects
```

### Features

- Graphical 30-band equalizer
- Pre-configured presets
- Real-time spectrum analyzer
- Additional effects (limiter, compressor, reverb, etc.)
- Per-application audio routing
- Preset import/export

### Usage

1. Open PulseEffects
2. Navigate to the "Equalizer" section
3. Enable the equalizer by clicking the power button
4. Adjust frequency bands using sliders
5. Save custom presets for different scenarios

## Method 3: Using Easy Effects (for PipeWire)

If your system uses PipeWire instead of PulseAudio:

### Installation

```bash
sudo apt-get install easyeffects
```

### Features

Similar to PulseEffects but designed for PipeWire:
- Modern GUI
- Multiple effect plugins
- Low latency
- Better integration with modern systems

## Troubleshooting

### PulseAudio Not Starting

1. Check PulseAudio status:
```bash
systemctl --user status pulseaudio
```

2. Restart PulseAudio:
```bash
systemctl --user restart pulseaudio
```

### No Sound After Configuration

1. Check default sink:
```bash
pacmd list-sinks | grep -e 'name:' -e 'index:'
```

2. Set correct default sink:
```bash
pacmd set-default-sink <sink_name>
```

### Module Load Errors

1. Verify LADSPA plugin exists:
```bash
ls -la /usr/lib/ladspa/ | grep mbeq
```

2. Check PulseAudio logs:
```bash
journalctl --user -u pulseaudio -n 50
```

### High CPU Usage

- Reduce equalizer band count
- Increase buffer size in PulseAudio configuration
- Use fewer LADSPA effects

## Advanced Configuration

### Custom Filter Chains

Create complex audio processing chains:

```bash
load-module module-ladspa-sink sink_name=eq1 plugin=mbeq_1197 label=mbeq control=...
load-module module-ladspa-sink sink_name=compressor master=eq1 plugin=sc4_1882 label=sc4 control=...
```

### Per-Application Routing

Route specific applications through the equalizer:

```bash
# List applications
pacmd list-sink-inputs

# Move application to equalizer (replace X with input index)
pacmd move-sink-input X ladspa_equalizer
```

## Preset Examples

### Bass Boost
```
control=6,4,2,0,0,0,0,0,0,0,0,0,0,0,0
```

### Treble Boost
```
control=0,0,0,0,0,0,0,0,0,0,3,4,5,6,5
```

### Voice Enhancement
```
control=-3,-2,0,2,4,3,2,0,-2,-3,-4,-4,-4,-4,-4
```

### Rock Music
```
control=5,3,0,-2,-1,0,0,1,3,3,3,3,3,2,2
```

## Resources

- [PulseAudio Documentation](https://www.freedesktop.org/wiki/Software/PulseAudio/Documentation/)
- [LADSPA Plugin List](http://plugin.org.uk/)
- [Steve Harris Plugin Pack](http://plugin.org.uk/ladspa-swh/docs/ladspa-swh.html)
- [PulseEffects GitHub](https://github.com/wwmm/pulseeffects)

## Tips

1. Start with small gain adjustments (±3 dB)
2. Listen for distortion when increasing gain
3. Use a spectrum analyzer to visualize changes
4. Save configurations before experimenting
5. Test with different audio sources (music, voice, movies)
