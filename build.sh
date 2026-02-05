#!/usr/bin/env bash
set -euo pipefail

# ── Constants ────────────────────────────────────────────────────────────────
APP_NAME="QuickKeys"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# ── Functions ────────────────────────────────────────────────────────────────
info()  { echo -e "${GREEN}[INFO]${NC} $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }

echo "============================================================"
echo "  QuickKeys - Build Script (macOS / Linux)"
echo "============================================================"
echo ""

cd "$SCRIPT_DIR"

# ── Preflight checks ────────────────────────────────────────────────────────
if [ ! -f "main.py" ]; then
    error "main.py not found. Run this script from the QuickKeys directory."
fi

if [ ! -f "quickkeys.spec" ]; then
    error "quickkeys.spec not found. Run this script from the QuickKeys directory."
fi

# Check Python 3
if command -v python3 &> /dev/null; then
    PYTHON=python3
elif command -v python &> /dev/null; then
    PYTHON=python
else
    error "Python 3 is not installed. Install it via your package manager or https://www.python.org/"
fi

PYTHON_VERSION=$($PYTHON --version 2>&1)
info "Using $PYTHON_VERSION"

# ── Detect platform ─────────────────────────────────────────────────────────
OS="$(uname -s)"
case "$OS" in
    Darwin)
        info "Detected platform: macOS"
        PLATFORM="macos"
        ;;
    Linux)
        info "Detected platform: Linux"
        PLATFORM="linux"
        ;;
    *)
        error "Unsupported platform: $OS. Use build.bat on Windows."
        ;;
esac

# ── Linux: check system dependencies ────────────────────────────────────────
if [ "$PLATFORM" = "linux" ]; then
    MISSING_DEPS=()

    if ! $PYTHON -c "import tkinter" 2>/dev/null; then
        MISSING_DEPS+=("python3-tk")
    fi

    if ! command -v xclip &>/dev/null && ! command -v xsel &>/dev/null; then
        MISSING_DEPS+=("xclip")
    fi

    if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
        warn "Missing system dependencies: ${MISSING_DEPS[*]}"
        warn "Install them with:"
        warn "  sudo apt-get install ${MISSING_DEPS[*]}  # Debian/Ubuntu"
        warn "  sudo dnf install ${MISSING_DEPS[*]}      # Fedora"
        warn "  sudo pacman -S ${MISSING_DEPS[*]}         # Arch"
        echo ""
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
fi

# ── Create virtual environment ───────────────────────────────────────────────
if [ ! -d ".venv" ]; then
    info "Creating virtual environment..."
    $PYTHON -m venv .venv
fi

info "Activating virtual environment..."
source .venv/bin/activate

# ── Install dependencies ────────────────────────────────────────────────────
info "Upgrading pip..."
python -m pip install --upgrade pip --quiet

info "Installing dependencies..."
pip install -r requirements.txt --quiet

# Linux: install PyGObject for pystray AppIndicator backend
if [ "$PLATFORM" = "linux" ]; then
    info "Installing PyGObject for Linux tray support..."
    pip install pygobject --quiet 2>/dev/null || \
        warn "PyGObject installation failed. System tray may not work. Install libgirepository1.0-dev first."
fi

info "Installing PyInstaller..."
pip install pyinstaller --quiet

# ── Clean previous builds ───────────────────────────────────────────────────
info "Cleaning previous builds..."
rm -rf dist/ build/

# ── Build ────────────────────────────────────────────────────────────────────
info "Building $APP_NAME..."
echo ""
pyinstaller quickkeys.spec --clean --noconfirm

# ── Verify output ────────────────────────────────────────────────────────────
echo ""
if [ "$PLATFORM" = "macos" ]; then
    if [ -d "dist/$APP_NAME.app" ]; then
        echo "============================================================"
        echo "  Build successful!"
        echo "  Output: dist/$APP_NAME.app"
        echo "============================================================"
        du -sh "dist/$APP_NAME.app"
        echo ""
        info "To install: drag dist/$APP_NAME.app to /Applications"
        echo ""
        warn "IMPORTANT: On first launch, macOS will require you to grant"
        warn "Accessibility permissions in System Settings > Privacy &"
        warn "Security > Accessibility for hotkey detection to work."
    else
        error "Build completed but $APP_NAME.app not found in dist/"
    fi
else
    if [ -f "dist/$APP_NAME" ]; then
        echo "============================================================"
        echo "  Build successful!"
        echo "  Output: dist/$APP_NAME"
        echo "============================================================"
        ls -lh "dist/$APP_NAME"
        chmod +x "dist/$APP_NAME"
        echo ""
        info "To run: ./dist/$APP_NAME"
    else
        error "Build completed but $APP_NAME not found in dist/"
    fi
fi

deactivate
