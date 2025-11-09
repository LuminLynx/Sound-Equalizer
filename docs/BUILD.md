# Building the Sound Equalizer GUI Executable

This guide explains how to build a standalone executable of the Sound Equalizer GUI that can be distributed to users who don't have Python installed.

## Prerequisites

- Python 3.8 or higher
- All project dependencies installed (see requirements.txt)
- PyInstaller

## Installation

1. Install project dependencies:
```bash
pip install -r requirements.txt
```

2. Install PyInstaller:
```bash
pip install pyinstaller
```

## Building the Executable

### Method 1: Using the provided spec file (Recommended)

```bash
pyinstaller equalizer_gui.spec
```

The executable will be created in `dist/sound-equalizer-gui`.

### Method 2: Using command line options

```bash
pyinstaller --onefile \
  --windowed \
  --name sound-equalizer-gui \
  --add-data "python-equalizer/config.json:." \
  python-equalizer/equalizer_gui.py
```

## Build Output

After a successful build:

- **Executable**: `dist/sound-equalizer-gui` (or `dist/sound-equalizer-gui.exe` on Windows)
- **Size**: Approximately 100-120 MB (includes Python, Qt, NumPy, SciPy, Matplotlib)
- **Build artifacts**: `build/` directory (can be deleted)

## Testing the Executable

Test the built executable:

```bash
# Linux/macOS
./dist/sound-equalizer-gui

# Windows
dist\sound-equalizer-gui.exe
```

## Distribution

The executable in the `dist/` directory is self-contained and can be distributed to users. It includes:

- Python interpreter
- All required libraries (PyQt5, NumPy, SciPy, Matplotlib)
- Application code
- Configuration file (config.json)

Users only need to:
1. Download the executable
2. Make it executable (Linux/macOS): `chmod +x sound-equalizer-gui`
3. Run it

## Platform-Specific Notes

### Linux

The executable is built for the current Linux distribution and architecture. For maximum compatibility:

- Build on the oldest supported distribution (e.g., Ubuntu 20.04 LTS)
- Test on multiple distributions (Ubuntu, Fedora, Debian, etc.)
- Note: Some X11/Wayland libraries may be required on the target system

Required system libraries (usually pre-installed):
```bash
# Ubuntu/Debian
sudo apt-get install libxcb-xinerama0 libxcb-cursor0

# Fedora
sudo dnf install xcb-util-cursor
```

### macOS

To create a macOS .app bundle, use the spec file:

```bash
pyinstaller equalizer_gui.spec
```

This creates `dist/Sound Equalizer.app` that can be distributed to macOS users.

### Windows

On Windows, PyInstaller creates a `.exe` file. Additional notes:

- Include `--icon=icon.ico` to add an application icon
- Test on Windows 10 and 11
- The executable may be flagged by antivirus software (common for PyInstaller apps)

## Troubleshooting

### Large Executable Size

The executable is large (~120 MB) because it includes:
- Python runtime
- Qt5 libraries
- NumPy/SciPy (scientific computing libraries)
- Matplotlib (plotting library)

To reduce size:
- Use `--onefile` (already default)
- Consider using `upx` compression (may trigger antivirus)
- Remove unused imports

### Missing Dependencies

If the executable fails to run:

```bash
# Check for missing libraries
ldd dist/sound-equalizer-gui  # Linux
otool -L dist/sound-equalizer-gui  # macOS
```

### Import Errors

If you get import errors, try:

```bash
# Clean build
rm -rf build/ dist/
pyinstaller --clean equalizer_gui.spec
```

### Hidden Imports

If modules are not found at runtime, add them to the spec file:

```python
hiddenimports=[
    'numpy',
    'scipy.signal',
    'matplotlib.backends.backend_qt5agg',
    # Add any missing modules here
],
```

## Build Script

For convenience, create a build script:

**build.sh** (Linux/macOS):
```bash
#!/bin/bash
set -e

echo "Building Sound Equalizer GUI..."

# Clean previous builds
rm -rf build/ dist/

# Build executable
pyinstaller equalizer_gui.spec

# Create archive
cd dist
tar -czf sound-equalizer-gui-linux-$(uname -m).tar.gz sound-equalizer-gui
cd ..

echo "Build complete! Executable: dist/sound-equalizer-gui"
echo "Archive: dist/sound-equalizer-gui-linux-$(uname -m).tar.gz"
```

**build.bat** (Windows):
```batch
@echo off
echo Building Sound Equalizer GUI...

REM Clean previous builds
rmdir /s /q build dist 2>nul

REM Build executable
pyinstaller equalizer_gui.spec

echo Build complete! Executable: dist\sound-equalizer-gui.exe
```

Make the script executable:
```bash
chmod +x build.sh
./build.sh
```

## Continuous Integration

To automate builds in CI/CD:

```yaml
# .github/workflows/build.yml
name: Build Executable

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pyinstaller
      - name: Build executable
        run: pyinstaller equalizer_gui.spec
      - name: Upload artifact
        uses: actions/upload-artifact@v2
        with:
          name: sound-equalizer-gui-linux
          path: dist/sound-equalizer-gui
```

## Alternatives to PyInstaller

If you experience issues with PyInstaller, consider:

1. **Nuitka**: Compiles Python to C++ (smaller, faster)
   ```bash
   pip install nuitka
   python -m nuitka --standalone --onefile --enable-plugin=pyqt5 python-equalizer/equalizer_gui.py
   ```

2. **cx_Freeze**: Cross-platform freezer
   ```bash
   pip install cx_Freeze
   # Create setup.py and build
   ```

3. **PyOxidizer**: Rust-based packager
   ```bash
   pip install pyoxidizer
   # Create pyoxidizer.toml and build
   ```

## Best Practices

1. **Version Control**: Tag releases with version numbers
2. **Testing**: Test on multiple systems before release
3. **Documentation**: Include README with system requirements
4. **Updates**: Provide a mechanism for users to check for updates
5. **Signing**: Consider code signing for macOS/Windows

## Release Checklist

- [ ] Update version number in code
- [ ] Run all tests
- [ ] Build executable on target platform(s)
- [ ] Test executable on clean system
- [ ] Create release notes
- [ ] Create installers (optional: .deb, .rpm, .dmg, .msi)
- [ ] Upload to GitHub Releases
- [ ] Update documentation

## Resources

- [PyInstaller Documentation](https://pyinstaller.readthedocs.io/)
- [PyInstaller Manual](https://pyinstaller.org/en/stable/)
- [Creating a macOS .app bundle](https://pyinstaller.readthedocs.io/en/stable/usage.html#macos-app-bundle)
- [Windows executable signing](https://docs.microsoft.com/en-us/windows/win32/seccrypto/signtool)
