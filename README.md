# Sound Equalizer for Linux (Debian)

A comprehensive guide and implementation for creating sound equalizers on Linux systems, specifically targeting Debian-based distributions.

## Overview

This project explores multiple approaches to implementing audio equalization on Linux systems. Sound equalizers allow users to adjust audio frequencies to enhance listening experience, compensate for hardware limitations, or achieve specific audio characteristics.

## Approaches to Creating a Linux Sound Equalizer

### 1. PulseAudio with LADSPA Plugins

**Description:** PulseAudio is the default sound server on most modern Linux distributions. It supports LADSPA (Linux Audio Developer's Simple Plugin API) plugins for audio processing.

**Advantages:**
- Native integration with most Linux desktop environments
- Easy to configure and use
- Wide plugin availability
- Real-time audio processing
- System-wide audio equalization

**Requirements:**
- PulseAudio (pre-installed on most Debian systems)
- LADSPA plugins (swh-plugins, cmt, etc.)
- PulseAudio module: `module-ladspa-sink`

**Installation:**
```bash
sudo apt-get update
sudo apt-get install pulseaudio ladspa-sdk swh-plugins
```

**Configuration:**
Load the LADSPA equalizer module:
```bash
pacmd load-module module-ladspa-sink sink_name=ladspa_output plugin=mbeq_1197 label=mbeq
```

### 2. ALSA with Plugins

**Description:** ALSA (Advanced Linux Sound Architecture) is the kernel-level sound system. It can be extended with plugins for equalization.

**Advantages:**
- Low-level control
- Lower latency
- Works without PulseAudio
- Direct hardware access

**Requirements:**
- ALSA utilities
- libasound2-plugins
- alsaequal or caps LADSPA plugin

**Installation:**
```bash
sudo apt-get install alsa-utils libasound2-plugins
```

**Configuration:**
Edit `~/.asoundrc` to configure the equalizer pipeline.

### 3. JACK Audio Connection Kit

**Description:** JACK is a professional audio server designed for low-latency audio routing and processing.

**Advantages:**
- Professional-grade audio processing
- Extremely low latency
- Flexible audio routing
- Ideal for music production
- Supports complex audio graphs

**Requirements:**
- JACK audio server
- JACK clients and plugins
- QjackCtl (GUI control)

**Installation:**
```bash
sudo apt-get install jackd2 qjackctl
```

### 4. Python-Based Equalizer (PyAudio + NumPy)

**Description:** A custom equalizer built using Python libraries for audio processing.

**Advantages:**
- Full control over implementation
- Educational value
- Customizable for specific needs
- Cross-platform potential
- Easy to extend and modify

**Requirements:**
- Python 3.x
- PyAudio
- NumPy
- SciPy

**See the `python-equalizer/` directory for implementation details.**

### 5. PipeWire with Filter Chain

**Description:** PipeWire is the modern audio server that aims to replace both PulseAudio and JACK.

**Advantages:**
- Modern architecture
- Low latency
- Compatible with PulseAudio and JACK applications
- Built-in filter chain support
- Future-proof solution

**Requirements:**
- PipeWire
- PipeWire filter chain plugins

**Installation:**
```bash
sudo apt-get install pipewire pipewire-audio-client-libraries
```

### 6. EasyEffects (formerly PulseEffects)

**Description:** A GUI application for audio effects including equalization, built on PipeWire.

**Advantages:**
- User-friendly GUI
- Multiple effects beyond equalization
- Preset management
- Real-time visualization

**Installation:**
```bash
sudo apt-get install easyeffects
```

## Quick Start

### Using the Python Implementation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the equalizer:
```bash
python3 python-equalizer/equalizer.py
```

### Using PulseAudio with Built-in Equalizer

1. Install PulseEffects (for GUI):
```bash
sudo apt-get install pulseeffects
```

2. Launch and configure:
```bash
pulseeffects
```

## Project Structure

```
.
├── README.md                 # This file
├── LICENSE                   # MIT License
├── requirements.txt          # Python dependencies
├── python-equalizer/         # Python implementation
│   ├── equalizer.py         # Main equalizer implementation
│   ├── audio_processor.py   # Audio processing functions
│   └── config.json          # Default configuration
└── docs/                     # Additional documentation
    ├── pulseaudio-setup.md  # PulseAudio configuration guide
    ├── alsa-setup.md        # ALSA configuration guide
    └── jack-setup.md        # JACK configuration guide
```

## Comparison of Approaches

| Approach | Difficulty | Latency | GUI | Best For |
|----------|-----------|---------|-----|----------|
| PulseAudio + LADSPA | Easy | Medium | Yes | General desktop use |
| ALSA + Plugins | Medium | Low | No | Minimal systems |
| JACK | Hard | Very Low | Yes | Audio production |
| Python Custom | Medium | High | Customizable | Learning/Development |
| PipeWire | Easy | Low | Yes | Modern systems |
| EasyEffects | Very Easy | Low | Yes | End users |

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details on how to contribute to this project.

For the project roadmap and planned features, see [ROADMAP.md](ROADMAP.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Resources

- [PulseAudio Documentation](https://www.freedesktop.org/wiki/Software/PulseAudio/Documentation/)
- [ALSA Project](https://www.alsa-project.org/)
- [JACK Audio Connection Kit](https://jackaudio.org/)
- [PipeWire](https://pipewire.org/)
- [LADSPA Plugins](https://www.ladspa.org/)

## Project Status

![CI](https://github.com/LuminLynx/Sound-Equalizer/workflows/CI/badge.svg)

This project is actively maintained. See [ROADMAP.md](ROADMAP.md) for planned features and improvements.

## Acknowledgments

- The Linux audio development community
- PulseAudio, ALSA, JACK, and PipeWire developers
- LADSPA plugin developers
