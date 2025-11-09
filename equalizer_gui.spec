# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Sound Equalizer GUI

This file defines how to package the Sound Equalizer GUI as a standalone
executable using PyInstaller.

Usage:
    pyinstaller equalizer_gui.spec
"""

import sys
from pathlib import Path

block_cipher = None

# Get the path to the python-equalizer directory
python_eq_dir = Path('python-equalizer').resolve()

a = Analysis(
    [str(python_eq_dir / 'equalizer_gui.py')],
    pathex=[str(python_eq_dir)],
    binaries=[],
    datas=[
        (str(python_eq_dir / 'config.json'), '.'),
    ],
    hiddenimports=[
        'numpy',
        'scipy',
        'scipy.signal',
        'matplotlib',
        'matplotlib.backends.backend_qt5agg',
        'PyQt5',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'test',
        'unittest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='sound-equalizer-gui',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for windowed mode (no console)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# For macOS, create an app bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='Sound Equalizer.app',
        icon=None,
        bundle_identifier='com.luminlynx.sound-equalizer',
    )
