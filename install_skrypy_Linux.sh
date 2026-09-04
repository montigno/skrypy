#!/usr/bin/env bash

set -e

echo "======================================"
echo "        Skrypy install"
echo "======================================"
echo

# ============================================================
# Test if user is admnistrator
# ============================================================

#if ! sudo -n true 2>/dev/null; then
#    echo "Administrator privileges are required to install the dependencies.."
#    echo "Your user does not appear to have permission to use sudo."
#    echo "Try this command : sudo usermod -aG sudo <your_user_name>"
#	echo
#    exit 1
#fi

# ============================================================
# Select installation folder
# ============================================================

DEFAULT_INSTALL_DIR="$HOME/Applications"

echo "Default installation folder :"
echo "  $DEFAULT_INSTALL_DIR"
echo

read -p "Installation folder [$DEFAULT_INSTALL_DIR] : " INSTALL_DIR

# If the user simply presses Enter
if [ -z "$INSTALL_DIR" ]; then
    INSTALL_DIR="$DEFAULT_INSTALL_DIR"
fi

# Expansion of ~ if the user enters ~/...
INSTALL_DIR="${INSTALL_DIR/#\~/$HOME}"

echo
echo "Install in :"
echo "  $INSTALL_DIR"
echo

mkdir -p "$INSTALL_DIR"

# ============================================================
# Package manager detection
# ============================================================

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

# ============================================================
# Installing system packages
# ============================================================

install_packages() {
    case $PKG_MANAGER in
        apt)
            sudo apt update
            sudo apt install -y \
                python3 \
                python3-venv \
                python3-pip \
                python3-tk \
                rsync
            ;;
        dnf)
            sudo dnf install -y \
                python3 \
                python3-virtualenv \
                python3-pip \
                python3-tkinter \
                rsync
            ;;
        pacman)
            sudo pacman -Sy --noconfirm \
                python \
                python-pip \
                python-virtualenv \
                tk \
                rsync
            ;;
    esac
}

# ============================================================
# Searching for Python >= 3.10
# ============================================================

echo
echo "=== Searching for Python >= 3.10 ==="

check_python_version() {
    "$1" - <<EOF
import sys
exit(0 if sys.version_info >= (3,10) else 1)
EOF
}

PYTHON=""

if command -v python3 &> /dev/null && check_python_version python3; then
    PYTHON=python3

elif command -v python &> /dev/null && check_python_version python; then
    PYTHON=python

elif [ -x "/usr/bin/python3" ] && check_python_version /usr/bin/python3; then
    PYTHON=/usr/bin/python3

else
    echo "Python >= 3.10 not found. Installing..."

    install_packages

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

# ============================================================
# Verifying tkinter
# ============================================================

echo
echo "=== tkinter verification ==="

if ! "$PYTHON" -c "import tkinter" &> /dev/null; then
    echo "tkinter missing. Installing..."
    install_packages
fi

# ============================================================
# Defining project paths
# ============================================================

BASE="$INSTALL_DIR/skrypy_venv"

SOURCE="$(dirname "$0")/skrypy-pyqt5"

DEST="$BASE/skrypy-pyqt5"

echo
echo "=== Installation paths ==="
echo "Virtual environment : $BASE"
echo "Application          : $DEST"

# ============================================================
# Creation of the virtual environment
# ============================================================

echo
echo "=== Creating virtual environment ==="

if [ ! -d "$BASE" ]; then
    "$PYTHON" -m venv "$BASE"
    echo "Virtual environment created."
else
    echo "Virtual environment already exists."
fi

# ============================================================
# Copying files
# ============================================================

echo
echo "=== Copy files (rsync) ==="

mkdir -p "$DEST"

rsync -a --delete "$SOURCE/" "$DEST/"

echo "Copy finished."

# ============================================================
# Activating the venv
# ============================================================

echo
echo "=== Activating virtual environment ==="

source "$BASE/bin/activate"

# ============================================================
# Installing PyYAML
# ============================================================

echo
echo "=== Checking PyYAML ==="

if ! python -c "import yaml" &> /dev/null; then
    echo "PyYAML missing. Installing..."
    python -m pip install PyYAML
else
    echo "PyYAML already installed."
fi

# ============================================================
# Installing Python modules
# ============================================================

echo
echo "=== Installing Python modules ==="

python "$DEST/install_modules.py"


# ============================================================
# Creating command line launcher
# ============================================================

echo

echo "=== Creating terminal launcher ==="

LOCAL_BIN="$HOME/.local/bin"
LAUNCHER="$LOCAL_BIN/skrypy"

mkdir -p "$LOCAL_BIN"

cat > "$LAUNCHER" <<EOL
#!/usr/bin/env bash

SKRYPY_DIR="$DEST"
PYTHON="$BASE/bin/python"
MAIN="$DEST/main.py"

cd "\$SKRYPY_DIR" || {
    echo "========================================"
    echo " ERROR : Unable to access Skrypy"
    echo "========================================"
    echo
    echo "Directory : \$SKRYPY_DIR"
    echo
    read -r -p "Press Enter to close..."
    exit 1
}

echo "========================================"
echo "              SKRYPY"
echo "========================================"
echo
echo "Python : \$PYTHON"
echo "Script : \$MAIN"
echo
echo "----------------------------------------"
echo

"\$PYTHON" "\$MAIN" "\$@"
STATUS=\$?

echo
echo "----------------------------------------"

if [ \$STATUS -eq 0 ]; then
    echo "Skrypy finished normally."
else
    echo
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    echo "        ERROR PYTHON - SKRYPY"
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    echo
    echo "Error code : \$STATUS"
fi

echo
read -r -p "Press Enter to close..."

exit \$STATUS
EOL

chmod +x "$LAUNCHER"

echo "Launcher created: $LAUNCHER"

# Add ~/.local/bin to PATH if needed

if ! grep -q 'HOME/.local/bin' "$HOME/.bashrc"; then

    cat >> "$HOME/.bashrc" <<'EOF'

# Skrypy
export PATH="$HOME/.local/bin:$PATH"

EOF

fi


# ============================================================
# Creating the application shortcut
# ============================================================

echo

echo "=== Creating application shortcut ==="

DESKTOP_FILE="$HOME/.local/share/applications/skrypy.desktop"

mkdir -p "$(dirname "$DESKTOP_FILE")"

cat > "$DESKTOP_FILE" <<EOL
[Desktop Entry]
Version=1.0
Name=Skrypy
Comment=Skrypy Application
Exec=$LAUNCHER
Path=$DEST
Icon=$DEST/ressources/skrypy.png
Terminal=true
Type=Application
Categories=Utility;
EOL

chmod +x "$DESKTOP_FILE"

echo "Shortcut created in application menu."


# ============================================================
# Desktop shortcut
# ============================================================

echo

echo "=== Optional desktop shortcut ==="

DESKTOP_SHORTCUT="$HOME/Desktop/Skrypy.desktop"

cp "$DESKTOP_FILE" "$DESKTOP_SHORTCUT" 2>/dev/null || true

chmod +x "$DESKTOP_SHORTCUT" 2>/dev/null || true


# ============================================================
# End
# ============================================================

echo
echo "======================================"
echo "      Installation finished"
echo "======================================"
echo
echo "Application : $DEST"
echo "Python       : $BASE/bin/python"
echo
