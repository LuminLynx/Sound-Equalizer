#!/bin/bash
# Installation script for Sound Equalizer development environment

set -e

echo "=========================================="
echo "Sound Equalizer Development Setup"
echo "=========================================="
echo ""

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo "Cannot detect OS. This script supports Debian/Ubuntu, Fedora, and Arch Linux."
    exit 1
fi

echo "Detected OS: $OS"
echo ""

# Install system dependencies based on OS
case "$OS" in
    ubuntu|debian)
        echo "Installing system dependencies for Ubuntu/Debian..."
        sudo apt-get update
        sudo apt-get install -y \
            python3 \
            python3-pip \
            python3-venv \
            portaudio19-dev \
            pulseaudio \
            ladspa-sdk \
            swh-plugins \
            git
        ;;
    fedora|rhel|centos)
        echo "Installing system dependencies for Fedora/RHEL..."
        sudo dnf install -y \
            python3 \
            python3-pip \
            portaudio-devel \
            pulseaudio \
            ladspa \
            swh-plugins \
            git
        ;;
    arch|manjaro)
        echo "Installing system dependencies for Arch Linux..."
        sudo pacman -S --noconfirm \
            python \
            python-pip \
            portaudio \
            pulseaudio \
            ladspa \
            swh-plugins \
            git
        ;;
    *)
        echo "Unsupported OS: $OS"
        echo "Please install dependencies manually:"
        echo "  - Python 3.8+"
        echo "  - pip"
        echo "  - portaudio development files"
        echo "  - PulseAudio"
        echo "  - LADSPA SDK and swh-plugins"
        exit 1
        ;;
esac

echo ""
echo "System dependencies installed successfully!"
echo ""

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip

echo ""
echo "Installing Python dependencies..."
pip install -r requirements.txt || echo "Note: PyAudio installation failed. This is OK for testing without real-time audio."

echo ""
echo "Installing development dependencies..."
pip install -r requirements-dev.txt

echo ""
echo "Installing pre-commit hooks..."
pre-commit install

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To run tests:"
echo "  python -m pytest"
echo ""
echo "To run the equalizer in test mode:"
echo "  cd python-equalizer && python equalizer.py --test"
echo ""
echo "To run examples:"
echo "  cd python-equalizer && python examples.py"
echo ""
echo "See CONTRIBUTING.md for more information."
echo ""
