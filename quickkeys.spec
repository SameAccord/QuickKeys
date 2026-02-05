# -*- mode: python ; coding: utf-8 -*-
"""
QuickKeys PyInstaller spec file.
Cross-platform build configuration for Windows, macOS, and Linux.

Usage:
    pyinstaller quickkeys.spec
"""

import platform
from pathlib import Path

block_cipher = None

# ── Paths ──────────────────────────────────────────────────────────────────────
SPEC_DIR = Path(SPECPATH)
ASSETS_DIR = SPEC_DIR / 'assets'
ENTRY_POINT = str(SPEC_DIR / 'main.py')

# ── Platform detection ─────────────────────────────────────────────────────────
IS_WINDOWS = platform.system() == 'Windows'
IS_MACOS = platform.system() == 'Darwin'
IS_LINUX = platform.system() == 'Linux'

# ── Application metadata ──────────────────────────────────────────────────────
APP_NAME = 'QuickKeys'
APP_VERSION = '1.0.0'
APP_BUNDLE_ID = 'com.sameaccord.quickkeys'

# ── Data files to bundle ──────────────────────────────────────────────────────
# Format: (source_path, destination_folder_in_bundle)
datas = [
    (str(ASSETS_DIR / 'icon.ico'), 'assets'),
    (str(ASSETS_DIR / 'icon.png'), 'assets'),
]

# ── Hidden imports ────────────────────────────────────────────────────────────
# PyInstaller sometimes misses dynamically loaded platform backends.
hiddenimports = [
    # pynput platform backends
    'pynput.keyboard._win32' if IS_WINDOWS else
    'pynput.keyboard._darwin' if IS_MACOS else
    'pynput.keyboard._xorg',

    'pynput.mouse._win32' if IS_WINDOWS else
    'pynput.mouse._darwin' if IS_MACOS else
    'pynput.mouse._xorg',

    'pynput.keyboard',
    'pynput.mouse',

    # pystray platform backend
    'pystray._win32' if IS_WINDOWS else
    'pystray._darwin' if IS_MACOS else
    'pystray._appindicator',

    # cryptography backends
    'cryptography.hazmat.primitives.ciphers.aead',
    'cryptography.hazmat.backends.openssl',

    # argon2 low-level bindings
    'argon2.low_level',
    'argon2._ffi',

    # Pillow image plugins
    'PIL.IcoImagePlugin',
    'PIL.PngImagePlugin',
    'PIL.ImageDraw',

    # pyperclip
    'pyperclip',

    # tkinter
    'tkinter',
    'tkinter.ttk',
    'tkinter.messagebox',
    'tkinter.filedialog',
]

# ── Platform-specific extra hidden imports ────────────────────────────────────
if IS_LINUX:
    hiddenimports.extend([
        'pystray._appindicator',
        'pystray._xorg',
    ])
if IS_MACOS:
    hiddenimports.extend([
        'pystray._darwin',
        'Foundation',
        'AppKit',
        'objc',
    ])

# ── Analysis ──────────────────────────────────────────────────────────────────
a = Analysis(
    [ENTRY_POINT],
    pathex=[str(SPEC_DIR)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'pytest',
        'unittest',
        'test',
        'setuptools',
        'distutils',
        'wheel',
        'pip',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# ── PYZ (Python bytecode archive) ────────────────────────────────────────────
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher,
)

# ── Icon selection ───────────────────────────────────────────────────────────
if IS_WINDOWS:
    _icon = [str(ASSETS_DIR / 'icon.ico')]
elif IS_MACOS:
    _icon = [str(ASSETS_DIR / 'icon.png')]
else:
    _icon = []

# ── EXE (onefile mode) ──────────────────────────────────────────────────────
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=IS_MACOS,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=_icon,
)

# ── macOS .app bundle ────────────────────────────────────────────────────────
if IS_MACOS:
    app = BUNDLE(
        exe,
        name=f'{APP_NAME}.app',
        icon=str(ASSETS_DIR / 'icon.png'),
        bundle_identifier=APP_BUNDLE_ID,
        info_plist={
            'CFBundleName': APP_NAME,
            'CFBundleDisplayName': APP_NAME,
            'CFBundleVersion': APP_VERSION,
            'CFBundleShortVersionString': APP_VERSION,
            'CFBundleIdentifier': APP_BUNDLE_ID,
            'NSHighResolutionCapable': True,
            'LSMinimumSystemVersion': '10.15',
            'LSBackgroundOnly': False,
            'LSUIElement': True,  # Hide from Dock (tray-only app)
            'NSAppleEventsUsageDescription':
                'QuickKeys needs Accessibility access to monitor hotkeys.',
            'NSAccessibilityUsageDescription':
                'QuickKeys uses Accessibility to detect keyboard shortcuts.',
        },
    )
