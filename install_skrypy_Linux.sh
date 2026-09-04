#!/usr/bin/env bash

set -e

echo "=== Detecting package manager ==="

if command -v apt &> /dev/null; then
    PKG_MANAGER="apt"
elif command -v dnf &> /dev/null; then
    PKG_MANAGER="dnf"
elif command -v pacman &> /dev/null; then
    PKG_MANAGER="pacman"
else
    echo "Unsupported distribution. Install Python manually."
    exit 1
fi

echo "Using: $PKG_MANAGER"

install_packages() {
    case $PKG_MANAGER in
        apt)
            sudo apt update
            sudo apt install -y python3 python3-venv python3-pip python3-tk rsync
            ;;
        dnf)
            sudo dnf install -y python3 python3-virtualenv python3-pip python3-tkinter rsync
            ;;
        pacman)
            sudo pacman -Sy --noconfirm python python-pip python-virtualenv tk rsync
            ;;
    esac
}

echo
echo "=== Searching for Python >= 3.10 ==="

check_python_version() {
    "$1" - <<EOF
import sys
exit(0 if sys.version_info >= (3,10) else 1)
EOF
}

PYTHON=""

# 1. Test python3
if command -v python3 &> /dev/null && check_python_version python3; then
    PYTHON=python3

# 2. Test python
elif command -v python &> /dev/null && check_python_version python; then
    PYTHON=python

# 3. Test chemin absolu
elif [ -x "/usr/bin/python3" ] && check_python_version /usr/bin/python3; then
    PYTHON=/usr/bin/python3

else
    echo "Python >= 3.10 not found. Installing..."

    install_packages

    # Re-check après install
    if command -v python3 &> /dev/null && check_python_version python3; then
        PYTHON=python3
    elif command -v python &> /dev/null && check_python_version python; then
        PYTHON=python
    elif [ -x "/usr/bin/python3" ] && check_python_version /usr/bin/python3; then
        PYTHON=/usr/bin/python3
    else
        echo "Python >= 3.10 installation failed."
        exit 1
    fi
fi

echo "Using: $PYTHON"
"$PYTHON" --version

echo
echo "=== Pip verification ==="

if ! python3 -m pip --version >/dev/null 2>&1; then
    if python3 -m ensurepip --version >/dev/null 2>&1; then
        python3 -m ensurepip --upgrade
    else
        echo "ensurepip non disponible, installation via le système..."
		case $PKG_MANAGER in
		        apt)
		            sudo apt install -y python3-pip
		            ;;
		        dnf)
		            sudo dnf install -y python3-pip
		            ;;
		        pacman)
		            sudo pacman -S python-pip
		            ;;
		esac
    fi
fi

echo
echo "=== tkinter verification ==="
if ! python3 -c "import tkinter" &> /dev/null; then
    echo "tkinter missing. Installing..."
    install_packages
fi

echo
echo "=== venv verification ==="
if ! "$PYTHON" -m venv --help &> /dev/null; then
    echo "venv missing. Installing..."
    install_packages
fi

BASE="$HOME/Applications/skrypy_venv"
SOURCE="$(dirname "$0")/skrypy-pyqt5"
DEST="$BASE/skrypy-pyqt5"

echo
echo "=== Creating virtual environment ==="
if [ ! -d "$BASE" ]; then
    "$PYTHON" -m venv "$BASE"
    echo "Virtual environment created."
fi

echo
echo "=== Copy files (rsync) ==="
mkdir -p "$DEST"
rsync -a --delete "$SOURCE/" "$DEST/"

echo "Copy finished."

echo
echo "=== Installing Python modules ==="
source "$BASE/bin/activate"
python "$DEST/install_modules.py"

echo
echo "=== Creating application shortcut ==="

DESKTOP_FILE="$HOME/.local/share/applications/skrypy.desktop"

mkdir -p "$(dirname "$DESKTOP_FILE")"

cat > "$DESKTOP_FILE" <<EOL
[Desktop Entry]
Version=1.0
Name=Skrypy
Comment=Skrypy Application
Exec=bash -c "$BASE/bin/python $DEST/main.py; echo; read -p 'Press Enter to close...'"
Path=$DEST
Icon=$DEST/ressources/skrypy.png
Terminal=true
Type=Application
Categories=Utility;
EOL

chmod +x "$DESKTOP_FILE"

echo "Shortcut created in application menu."

echo
echo "=== Optional desktop shortcut ==="

DESKTOP_SHORTCUT="$HOME/Desktop/Skrypy.desktop"

cp "$DESKTOP_FILE" "$DESKTOP_SHORTCUT" 2>/dev/null || true
chmod +x "$DESKTOP_SHORTCUT" 2>/dev/null || true

echo
echo "=== Installation finished ==="
