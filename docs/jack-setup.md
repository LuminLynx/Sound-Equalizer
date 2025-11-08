# JACK Audio Sound Equalizer Setup Guide

This guide explains how to set up a sound equalizer using JACK (JACK Audio Connection Kit) on Debian-based Linux distributions.

## Prerequisites

- Debian-based Linux distribution
- Basic understanding of audio routing
- Terminal/command line access
- Real-time kernel recommended (optional, for best performance)

## Overview

JACK is a professional-grade audio server that provides low-latency audio routing and processing. It's ideal for music production, live performance, and applications requiring precise audio control.

## Installation

### Install JACK2 (Recommended)

```bash
sudo apt-get update
sudo apt-get install jackd2 qjackctl
```

### Install Additional Tools

```bash
# JACK utilities and clients
sudo apt-get install jack-tools meterbridge

# LADSPA plugins for JACK
sudo apt-get install swh-plugins tap-plugins cmt

# JACK rack for LADSPA hosting
sudo apt-get install jack-rack

# Non-Mixer for advanced audio routing
sudo apt-get install non-mixer

# Carla - Plugin host
sudo apt-get install carla
```

### Optional: Real-time Audio Configuration

For best performance, configure real-time audio:

```bash
# Add user to audio group
sudo usermod -aG audio $USER

# Edit limits configuration
sudo nano /etc/security/limits.d/audio.conf
```

Add these lines:
```
@audio   -  rtprio     95
@audio   -  memlock    unlimited
```

Log out and log back in for changes to take effect.

## Starting JACK

### Method 1: Using QjackCtl (GUI)

1. Launch QjackCtl:
```bash
qjackctl
```

2. Configure JACK:
   - Click "Setup" button
   - Set Sample Rate (44100 or 48000 Hz recommended)
   - Set Frames/Period (256 or 512 for low latency)
   - Select audio driver (alsa recommended)
   - Select audio interface

3. Start JACK:
   - Click "Start" button
   - Monitor status in main window

### Method 2: Command Line

```bash
# Start JACK with default settings
jackd -d alsa -r 48000 -p 512 -n 2

# Start JACK with real-time priority
jackd -R -d alsa -r 48000 -p 256 -n 2
```

Common parameters:
- `-d alsa`: Use ALSA driver
- `-r 48000`: Sample rate (48000 Hz)
- `-p 512`: Period size (buffer size)
- `-n 2`: Number of periods
- `-R`: Enable real-time mode

## Equalizer Setup

### Method 1: Using jack-rack

jack-rack is a LADSPA plugin host for JACK.

#### Installation and Setup

```bash
# Install jack-rack
sudo apt-get install jack-rack

# Launch jack-rack
jack-rack
```

#### Adding Equalizer

1. Open jack-rack
2. Right-click in the rack area
3. Select "Add Plugin"
4. Search for "mbeq" or "DJ EQ"
5. Click "Add" to add the equalizer plugin
6. Adjust sliders for each frequency band

#### Connect Audio

Using QjackCtl connections panel:
1. Click "Connect" button
2. In "Audio" tab:
   - Connect system capture ports to jack-rack input
   - Connect jack-rack output to system playback ports

### Method 2: Using Carla

Carla is a modern, full-featured plugin host.

#### Installation and Setup

```bash
# Launch Carla
carla
```

#### Adding Equalizer

1. Click "Add Plugin" button
2. Select "LADSPA" or "LV2" tab
3. Search for equalizer plugins:
   - "Calf Equalizer 5 Band"
   - "LSP Parametric Equalizer"
   - "TAP Equalizer"
4. Double-click to add plugin
5. Click plugin name to open GUI and adjust settings

#### Patchbay Setup

1. Click "Patchbay" button
2. Create connections:
   - system:capture → Carla:audio_in
   - Carla:audio_out → system:playback

### Method 3: Using Non-Mixer

Non-Mixer provides a mixing console interface with EQ on each channel.

```bash
# Launch Non-Mixer
non-mixer
```

#### Setup

1. Add a new strip (Track > New)
2. Click on the strip's "EQ" button
3. Enable equalizer section
4. Adjust frequency bands using the GUI
5. Connect audio sources and outputs using JACK

### Method 4: Using jalv (LV2 Plugin Host)

```bash
# Install jalv
sudo apt-get install jalv

# List available LV2 plugins
lv2ls | grep -i eq

# Launch specific EQ plugin
jalv.gtk http://calf.sourceforge.net/plugins/Equalizer5Band
```

## Available Equalizer Plugins

### LADSPA Plugins

1. **Multiband EQ (mbeq_1197)**
   - 15-band graphic equalizer
   - Part of swh-plugins package
   - Frequencies: 50Hz to 20kHz

2. **DJ EQ (dj_eq_1901)**
   - 3-band DJ-style equalizer
   - Kill switches for each band
   - Part of swh-plugins package

3. **TAP Equalizer**
   - Parametric equalizer
   - 8 bands
   - Adjustable Q factor

### LV2 Plugins

1. **Calf Equalizer 5 Band**
   - 5-band parametric equalizer
   - High-quality filters
   - Professional interface

2. **LSP Parametric Equalizer**
   - Up to 32 bands
   - Multiple filter types
   - Spectrum analyzer

3. **X42 EQ**
   - Professional parametric EQ
   - High precision
   - Multiple filter shapes

## Connection Examples

### Basic System-wide Equalization

```bash
# Start JACK
jackd -d alsa -r 48000 -p 512 &

# Start jack-rack with saved settings
jack-rack -c ~/.jack-rack/equalizer.rack &

# Connect system audio through jack-rack
jack_connect system:capture_1 jack_rack:in_1
jack_connect system:capture_2 jack_rack:in_2
jack_connect jack_rack:out_1 system:playback_1
jack_connect jack_rack:out_2 system:playback_2
```

### Application-specific Equalization

```bash
# Start JACK
jackd -d alsa -r 48000 -p 512 &

# Start media player with JACK support
vlc --aout jack

# Start equalizer
jack-rack &

# Connect VLC through equalizer
jack_connect vlc:out_1 jack_rack:in_1
jack_connect vlc:out_2 jack_rack:in_2
jack_connect jack_rack:out_1 system:playback_1
jack_connect jack_rack:out_2 system:playback_2
```

## Advanced Configurations

### Parallel Processing

Create parallel effect chains:

```bash
# Route audio to multiple processors
jack_connect system:capture_1 jack_rack_eq:in_1
jack_connect system:capture_1 jack_rack_comp:in_1

# Mix outputs
jack_connect jack_rack_eq:out_1 system:playback_1
jack_connect jack_rack_comp:out_1 system:playback_1
```

### Frequency-split Processing

Use crossover filters to split frequency ranges:

1. Add crossover plugin
2. Route low frequencies to bass EQ
3. Route high frequencies to treble EQ
4. Mix back together

### Session Management

Use JACK session management to save and restore setups:

```bash
# Install session manager
sudo apt-get install jack-session-manager

# Or use Non Session Manager
sudo apt-get install non-session-manager
```

## JACK Integration with PulseAudio

### Bridge JACK and PulseAudio

```bash
# Install PulseAudio JACK module
sudo apt-get install pulseaudio-module-jack

# Load JACK sink and source
pactl load-module module-jack-sink
pactl load-module module-jack-source

# Connect in QjackCtl Connections panel
```

This allows PulseAudio applications to work while JACK is running.

## Troubleshooting

### JACK Won't Start

1. Check if another audio application is using the device:
```bash
lsof /dev/snd/*
```

2. Stop PulseAudio:
```bash
pulseaudio --kill
```

3. Check for errors:
```bash
jackd -v -d alsa
```

### High Latency/Xruns

1. Increase period size:
```bash
jackd -d alsa -r 48000 -p 1024
```

2. Reduce number of applications
3. Use real-time kernel
4. Adjust CPU governor:
```bash
sudo cpupower frequency-set -g performance
```

### No Audio Through Equalizer

1. Check connections in QjackCtl
2. Verify plugin is loaded in rack
3. Check plugin parameters (not bypassed)
4. Monitor levels with meterbridge:
```bash
meterbridge jack_rack:out_1 jack_rack:out_2
```

### Audio Distortion

1. Reduce equalizer gain settings
2. Add limiter plugin after equalizer
3. Check for clipping in meterbridge
4. Increase bit depth if possible

## Performance Monitoring

### Monitor JACK Performance

```bash
# Show JACK statistics
jack_bufsize
jack_samplerate
jack_wait -t 10  # Monitor for xruns
```

### CPU Usage

```bash
# Monitor specific JACK clients
top -p $(pgrep jackd)
```

## Preset Management

### Save jack-rack Presets

File → Save As → `~/.jack-rack/mypreset.rack`

### Load Presets

```bash
jack-rack -c ~/.jack-rack/mypreset.rack
```

### Example Presets

#### Bass Boost
```xml
<!-- Save to ~/.jack-rack/bass_boost.rack -->
<rack>
  <plugin>
    <id>1197</id>
    <label>mbeq</label>
    <control>
      <number>0</number>
      <value>6.0</value>
    </control>
    <control>
      <number>1</number>
      <value>4.0</value>
    </control>
    <!-- ... other controls ... -->
  </plugin>
</rack>
```

## Automation Scripts

### Auto-start Script

```bash
#!/bin/bash
# start_jack_eq.sh

# Kill existing JACK instances
killall jackd 2>/dev/null

# Start JACK
jackd -R -d alsa -r 48000 -p 512 -n 2 &
sleep 2

# Start equalizer
jack-rack -c ~/.jack-rack/default.rack &
sleep 2

# Connect audio
jack_connect system:capture_1 jack_rack:in_1
jack_connect system:capture_2 jack_rack:in_2
jack_connect jack_rack:out_1 system:playback_1
jack_connect jack_rack:out_2 system:playback_2

echo "JACK Equalizer started"
```

Make executable:
```bash
chmod +x start_jack_eq.sh
```

## Resources

- [JACK Official Site](https://jackaudio.org/)
- [QjackCtl Documentation](https://qjackctl.sourceforge.io/)
- [Carla Plugin Host](https://kx.studio/Applications:Carla)
- [Linux Audio Wiki](https://wiki.linuxaudio.org/)
- [JACK Applications List](https://jackaudio.org/applications/)

## Tips

1. Start with larger buffer sizes (512-1024) for stability
2. Use QjackCtl for visual connection management
3. Save session configurations for different use cases
4. Monitor CPU usage and xruns regularly
5. Use real-time priority only when needed
6. Keep JACK and plugins updated
7. Document your connection setups for complex routing
8. Test presets before live performance use
