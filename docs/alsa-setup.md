# ALSA Sound Equalizer Setup Guide

This guide explains how to set up a sound equalizer using ALSA (Advanced Linux Sound Architecture) on Debian-based Linux distributions.

## Prerequisites

- Debian-based Linux distribution
- ALSA utilities installed
- Terminal/command line access
- Basic understanding of ALSA configuration

## Overview

ALSA provides low-level audio functionality and can be configured with plugins to add equalization capabilities. This approach works without PulseAudio and is suitable for minimal systems or embedded devices.

## Installation

### Install Required Packages

```bash
sudo apt-get update
sudo apt-get install alsa-utils libasound2-plugins
```

### Install LADSPA Plugins

```bash
sudo apt-get install swh-plugins ladspa-sdk
```

### Install alsaequal (Optional - ALSA Equalizer Plugin)

```bash
sudo apt-get install libasound2-plugin-equal
```

Or build from source:
```bash
sudo apt-get install build-essential libasound2-dev libcap-dev
git clone https://github.com/raedwulf/alsaequal.git
cd alsaequal
make
sudo make install
```

## Configuration

### Method 1: Using alsaequal Plugin

#### 1. Create/Edit ~/.asoundrc

```bash
nano ~/.asoundrc
```

#### 2. Add Equalizer Configuration

```
# ALSA Equalizer Configuration
ctl.equal {
    type equal
}

pcm.plugequal {
    type equal
    slave.pcm "plughw:0,0"
}

# Set as default
pcm.!default {
    type plug
    slave.pcm plugequal
}

ctl.!default {
    type hw
    card 0
}
```

#### 3. Configure the Equalizer

Run the equalizer configuration tool:
```bash
alsamixer -D equal
```

Use F6 to select the "equal" control and adjust bands with arrow keys.

### Method 2: Using LADSPA Plugin with ALSA

#### 1. Configure ~/.asoundrc

```bash
nano ~/.asoundrc
```

#### 2. Add LADSPA Configuration

```
pcm.ladspa {
    type ladspa
    slave.pcm "plughw:0,0"
    path "/usr/lib/ladspa"
    plugins [
        {
            label mbeq
            id 1197
            input {
                controls [ 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 ]
            }
        }
    ]
}

pcm.!default {
    type plug
    slave.pcm "ladspa"
}
```

### Method 3: System-wide Configuration

For system-wide equalizer configuration:

#### 1. Edit /etc/asound.conf

```bash
sudo nano /etc/asound.conf
```

#### 2. Add Configuration

```
# System-wide equalizer
pcm.eq {
    type equal
    slave.pcm "plughw:0,0"
}

pcm.!default {
    type plug
    slave.pcm "eq"
}
```

## Testing the Configuration

### Test Audio Output

```bash
speaker-test -c 2 -t wav
```

### Check Current Configuration

```bash
aplay -L
```

You should see entries like "equal" or "ladspa" in the output.

### Play Audio Through Equalizer

```bash
aplay -D equal audio_file.wav
```

Or with mplayer:
```bash
mplayer -ao alsa:device=equal audio_file.mp3
```

## Advanced Configuration

### Multi-band Equalizer Configuration

Example with more detailed LADSPA plugin configuration:

```
pcm.eq_full {
    type ladspa
    slave.pcm "plughw:0,0"
    path "/usr/lib/ladspa"
    plugins [
        {
            label "mbeq"
            id 1197
            input {
                # 15 bands: 50, 100, 156, 220, 311, 440, 622, 880, 1250, 1750, 2500, 3500, 5000, 10000, 20000 Hz
                # Values in dB: -20 to +20
                controls [ 
                    0    # 50 Hz
                    0    # 100 Hz
                    0    # 156 Hz
                    0    # 220 Hz
                    0    # 311 Hz
                    0    # 440 Hz
                    0    # 622 Hz
                    0    # 880 Hz
                    0    # 1250 Hz
                    0    # 1750 Hz
                    0    # 2500 Hz
                    0    # 3500 Hz
                    0    # 5000 Hz
                    0    # 10000 Hz
                    0    # 20000 Hz
                ]
            }
        }
    ]
}

pcm.!default {
    type plug
    slave.pcm "eq_full"
}
```

### Combining Multiple Effects

Chain multiple LADSPA plugins:

```
pcm.effects_chain {
    type ladspa
    slave.pcm "plughw:0,0"
    path "/usr/lib/ladspa"
    plugins [
        {
            label "mbeq"
            id 1197
            input {
                controls [ 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 ]
            }
        }
        {
            label "amp_mono"
            id 1048
            input {
                controls [ 1.0 ]  # Amplification factor
            }
        }
    ]
}
```

### Stereo Configuration

For stereo-specific equalization:

```
pcm.eq_stereo {
    type ladspa
    slave.pcm "plughw:0,0"
    channels 2
    path "/usr/lib/ladspa"
    plugins [
        {
            label mbeq
            id 1197
            input {
                bindings [ 0 ]
                controls [ 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 ]
            }
        }
        {
            label mbeq
            id 1197
            input {
                bindings [ 1 ]
                controls [ 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 ]
            }
        }
    ]
}
```

## Preset Examples

### Bass Boost Configuration
```
controls [ 6 4 2 0 0 0 0 0 0 0 0 0 0 0 0 ]
```

### Treble Boost Configuration
```
controls [ 0 0 0 0 0 0 0 0 0 0 3 4 5 6 5 ]
```

### Voice Clarity Configuration
```
controls [ -3 -2 0 2 4 3 2 0 -2 -3 -4 -4 -4 -4 -4 ]
```

### Classical Music Configuration
```
controls [ 0 0 0 0 -2 -2 0 2 3 2 0 0 2 3 2 ]
```

## Troubleshooting

### No Sound After Configuration

1. Check ALSA configuration syntax:
```bash
aplay -L
```

2. Test without equalizer:
```bash
aplay -D plughw:0,0 /usr/share/sounds/alsa/Front_Center.wav
```

3. Reset configuration:
```bash
mv ~/.asoundrc ~/.asoundrc.backup
```

### "Unknown PCM equal" Error

Install libasound2-plugin-equal:
```bash
sudo apt-get install libasound2-plugin-equal
```

### LADSPA Plugin Not Found

1. Verify plugin installation:
```bash
ls -la /usr/lib/ladspa/
```

2. Check plugin path in configuration:
```bash
analyseplugin /usr/lib/ladspa/mbeq_1197.so
```

### Distorted Audio

1. Reduce gain values in configuration
2. Add a limiter plugin to prevent clipping
3. Adjust sample rate conversion quality

### Configuration Not Applied

1. Restart ALSA:
```bash
sudo alsactl kill quit
```

2. Reload ALSA modules:
```bash
sudo alsa force-reload
```

## Performance Optimization

### Reduce Latency

```
pcm.eq_low_latency {
    type ladspa
    slave {
        pcm "plughw:0,0"
        period_size 64
        buffer_size 256
    }
    path "/usr/lib/ladspa"
    plugins [ ... ]
}
```

### Hardware-specific Configuration

For specific sound cards:

```bash
# List available cards
aplay -l

# Use specific card (e.g., card 1, device 0)
slave.pcm "plughw:1,0"
```

## Integration with Applications

### MPD (Music Player Daemon)

Edit `/etc/mpd.conf`:
```
audio_output {
    type "alsa"
    name "Equalizer Output"
    device "equal"
    mixer_type "software"
}
```

### VLC Media Player

Launch with specific ALSA device:
```bash
vlc --alsa-audio-device equal
```

### Firefox/Chromium

These browsers use PulseAudio by default, but can be configured to use ALSA directly if PulseAudio is disabled.

## Utility Scripts

### Save Current Settings

```bash
#!/bin/bash
# save_eq_settings.sh
alsactl store -f ~/.alsa_eq_settings.state equal
```

### Load Settings

```bash
#!/bin/bash
# load_eq_settings.sh
alsactl restore -f ~/.alsa_eq_settings.state equal
```

## Resources

- [ALSA Project](https://www.alsa-project.org/)
- [ALSA Configuration Guide](https://www.alsa-project.org/main/index.php/Asoundrc)
- [LADSPA Documentation](https://www.ladspa.org/)
- [alsaequal GitHub](https://github.com/raedwulf/alsaequal)

## Tips

1. Always backup ~/.asoundrc before making changes
2. Test configuration with simple audio files first
3. Start with flat EQ (all zeros) and adjust gradually
4. Use alsamixer to verify controls are accessible
5. Check system logs for ALSA errors: `dmesg | grep -i alsa`
6. Consider using PulseAudio for easier configuration if not limited by resources
