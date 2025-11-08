# Getting Started with Sound Equalizer

This guide will help you quickly get started with the Sound Equalizer project.

## For End Users

### Quick Start with GUI Tools

The easiest way to use a sound equalizer on Linux is with a GUI application:

**Option 1: EasyEffects (for PipeWire)**
```bash
sudo apt-get install easyeffects
easyeffects
```

**Option 2: PulseEffects (for PulseAudio)**
```bash
sudo apt-get install pulseeffects
pulseeffects
```

See [QUICKSTART.md](QUICKSTART.md) for more detailed instructions.

## For Developers

### Prerequisites

- Linux system (Ubuntu/Debian recommended)
- Python 3.8 or higher
- Git

### Quick Setup

1. **Clone the repository:**
```bash
git clone https://github.com/LuminLynx/Sound-Equalizer.git
cd Sound-Equalizer
```

2. **Run the automated setup script:**
```bash
./setup-dev.sh
```

This will install all system and Python dependencies and set up your development environment.

3. **Activate the virtual environment:**
```bash
source venv/bin/activate
```

### Manual Setup

If the automated script doesn't work for your system:

1. **Install system dependencies:**

   Ubuntu/Debian:
   ```bash
   sudo apt-get update
   sudo apt-get install python3 python3-pip python3-venv portaudio19-dev
   ```

   Fedora:
   ```bash
   sudo dnf install python3 python3-pip portaudio-devel
   ```

   Arch Linux:
   ```bash
   sudo pacman -S python python-pip portaudio
   ```

2. **Create and activate virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install Python dependencies:**
```bash
pip install numpy scipy
# PyAudio is optional for real-time processing
pip install pyaudio  # May fail on some systems, that's OK
```

### Running the Python Equalizer

1. **Test mode (no audio hardware required):**
```bash
cd python-equalizer
python equalizer.py --test
```

2. **List available presets:**
```bash
python equalizer.py --list-presets
```

3. **Run examples:**
```bash
python examples.py
```

4. **Real-time processing (requires audio hardware and PyAudio):**
```bash
# Use default configuration
python equalizer.py

# Use a preset
python equalizer.py --preset bass_boost
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=python-equalizer
```

## Project Structure

```
Sound-Equalizer/
├── python-equalizer/          # Python implementation
│   ├── equalizer.py          # Main equalizer application
│   ├── audio_processor.py    # Audio processing core
│   ├── config.json           # Configuration and presets
│   └── examples.py           # Usage examples
├── docs/                      # Detailed documentation
│   ├── pulseaudio-setup.md
│   ├── alsa-setup.md
│   └── jack-setup.md
├── tests/                     # Unit tests
├── ROADMAP.md                # Project roadmap
├── CONTRIBUTING.md           # Contribution guidelines
└── README.md                 # Project overview
```

## Understanding the Code

### Basic Usage Example

```python
from audio_processor import AudioProcessor

# Create processor
processor = AudioProcessor(sample_rate=44100)

# Add equalizer bands
processor.add_band(frequency=100, gain_db=6.0, q_factor=1.0)   # Bass boost
processor.add_band(frequency=1000, gain_db=0.0, q_factor=1.0)  # Flat
processor.add_band(frequency=10000, gain_db=3.0, q_factor=1.0) # Treble boost

# Process audio
import numpy as np
audio_input = np.random.randn(1000).astype(np.float32)
audio_output = processor.process_block(audio_input)

# Get frequency response
freqs, magnitude, phase = processor.get_frequency_response()
```

## Next Steps

- Read [CONTRIBUTING.md](CONTRIBUTING.md) to learn how to contribute
- Check [ROADMAP.md](ROADMAP.md) for planned features
- Explore the detailed setup guides in the `docs/` directory
- Join discussions in GitHub Issues

## Getting Help

- **Documentation**: Check README.md and docs/ folder
- **Issues**: Search [existing issues](https://github.com/LuminLynx/Sound-Equalizer/issues)
- **Questions**: Open a new issue with the "question" label
- **Community**: Participate in GitHub Discussions

## Common Issues

### PyAudio Installation Fails

PyAudio is only needed for real-time audio processing. You can still use the equalizer for:
- Testing configurations (`--test` mode)
- Processing audio files
- Understanding the algorithms
- Running unit tests

To install PyAudio:
```bash
# Install system dependencies first
sudo apt-get install portaudio19-dev python3-pyaudio

# Then try pip
pip install pyaudio
```

### Import Errors

Make sure you're in the project directory and have activated the virtual environment:
```bash
cd Sound-Equalizer
source venv/bin/activate
```

### "No sound" After Configuration

If you're trying system-wide equalization, see the detailed guides:
- [PulseAudio Setup](docs/pulseaudio-setup.md)
- [ALSA Setup](docs/alsa-setup.md)
- [JACK Setup](docs/jack-setup.md)

## Resources

- [Digital Signal Processing Tutorial](https://en.wikipedia.org/wiki/Digital_signal_processing)
- [Audio EQ Basics](https://en.wikipedia.org/wiki/Equalization_(audio))
- [Linux Audio Wiki](https://wiki.linuxaudio.org/)
- [Python Audio Libraries](https://wiki.python.org/moin/Audio/)

---

**Happy equalizing!** 🎵🎶
