import platform
from pathlib import Path
from typing import Optional


APP_NAME = "QuickKeys"


def get_data_dir() -> Path:
    system = platform.system()

    if system == "Windows":
        base = Path.home() / "AppData" / "Local"
    elif system == "Darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path.home() / ".config"

    data_dir = base / APP_NAME
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_assets_dir() -> Path:
    source_assets = Path(__file__).parent.parent / "assets"
    if source_assets.exists():
        return source_assets

    import sys
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS) / "assets"

    return source_assets


def get_icon_path() -> Optional[Path]:
    assets = get_assets_dir()
    system = platform.system()

    if system == "Windows":
        icon_path = assets / "icon.ico"
    else:
        icon_path = assets / "icon.png"

    return icon_path if icon_path.exists() else None


def get_png_icon_path() -> Optional[Path]:
    assets = get_assets_dir()
    icon_path = assets / "icon.png"
    return icon_path if icon_path.exists() else None


def is_windows() -> bool:
    return platform.system() == "Windows"


def is_macos() -> bool:
    return platform.system() == "Darwin"


def is_linux() -> bool:
    return platform.system() == "Linux"
