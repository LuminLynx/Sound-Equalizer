# Quick Start Guide

## For End Users (Easiest Options)

### Option 1: EasyEffects (Recommended for Desktop Users)
```bash
# Install
sudo apt-get update
sudo apt-get install easyeffects

# Run
easyeffects
```
Click the "Equalizer" button and adjust the sliders. That's it!

### Option 2: PulseEffects (for older systems)
```bash
# Install
sudo apt-get install pulseeffects

# Run
pulseeffects
```

## For Python Developers

### Installation
```bash
# Clone or download this repository
cd Sound-Equalizer

# Install Python dependencies
pip3 install -r requirements.txt

# Note: PyAudio may need system packages
sudo apt-get install portaudio19-dev python3-pyaudio
```

### Quick Test
```bash
cd python-equalizer
python3 equalizer.py --test
```

### Run Examples
```bash
python3 examples.py
```

### Use with Different Presets
```bash
# List available presets
python3 equalizer.py --list-presets

# Run with bass boost
python3 equalizer.py --preset bass_boost

# Run with rock preset
python3 equalizer.py --preset rock
```

## For Audio Professionals

### JACK Setup
```bash
# Install JACK
sudo apt-get install jackd2 qjackctl jack-rack

# Start JACK GUI
qjackctl

# Click "Start" in QjackCtl
# Launch jack-rack for equalizer
jack-rack
```

See [docs/jack-setup.md](docs/jack-setup.md) for detailed configuration.

## For System Administrators

### PulseAudio System-wide EQ
```bash
# Install LADSPA plugins
sudo apt-get install swh-plugins

# Load equalizer module
pacmd load-module module-ladspa-sink sink_name=ladspa_equalizer plugin=mbeq_1197 label=mbeq control=0,0,0,0,0,0,0,0,0,0,0,0,0,0,0

# Set as default
pacmd set-default-sink ladspa_equalizer
```

See [docs/pulseaudio-setup.md](docs/pulseaudio-setup.md) for persistent configuration.

## For Embedded/Minimal Systems

### ALSA Configuration
```bash
# Install ALSA plugins
sudo apt-get install libasound2-plugins swh-plugins

# Edit configuration
nano ~/.asoundrc
```

Add equalizer configuration (see [docs/alsa-setup.md](docs/alsa-setup.md) for examples).

## Common Issues

### "PyAudio not found"
```bash
sudo apt-get install portaudio19-dev
pip3 install pyaudio
```

### "No module named numpy"
```bash
pip3 install -r requirements.txt
```

### "No sound after configuration"
- Check PulseAudio status: `pulseaudio --check`
- Restart PulseAudio: `pulseaudio -k && pulseaudio --start`
- Verify sink: `pacmd list-sinks | grep name`

## Documentation

- **README.md** - Complete overview of all approaches
- **docs/pulseaudio-setup.md** - PulseAudio configuration
- **docs/alsa-setup.md** - ALSA configuration
- **docs/jack-setup.md** - JACK Audio setup

## Getting Help

1. Read the relevant documentation in `docs/`
2. Check the troubleshooting sections
3. Run the Python equalizer in test mode: `python3 equalizer.py --test`
4. Check system logs: `journalctl --user -u pulseaudio -n 50`

## Next Steps

- Experiment with different presets
- Create your own custom configurations
- Learn about digital signal processing
- Explore professional audio production with JACK
- Contribute improvements to this project
