#!/bin/bash
# Filename: install_wrappers.bash
# Install universal wrapper scripts to system

set -e

echo "════════════════════════════════════════════════════════════════"
echo "  G90-SDR Universal Wrapper Installation"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Check if running with sudo
if [ "$EUID" -ne 0 ]; then
    echo "This script needs sudo access to install to /usr/local/bin/"
    echo ""
    read -p "Continue with sudo? (y/n): " response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "Installation cancelled"
        exit 0
    fi
    echo ""
fi

# Use L_SDR_DIR or current directory
if [ -n "$L_SDR_DIR" ]; then
    SOURCE_DIR="$L_SDR_DIR"
else
    SOURCE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
fi

echo "Source directory: $SOURCE_DIR"
echo ""

# Create wrapper scripts in temp location
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

echo "Creating wrapper scripts..."

# 1. Main G90-SDR wrapper
cat > "$TEMP_DIR/g90-sdr" << 'WRAPPER_EOF'
#!/bin/bash
# G90-SDR Universal Launcher

VERSION="1.0.0"

find_installation() {
    if [ -n "$L_SDR_DIR" ] && [ -d "$L_SDR_DIR" ]; then
        echo "$L_SDR_DIR"
        return 0
    fi
    
    local USER_LOCATIONS=(
        "$HOME/Virtual/G90-SDR"
        "$HOME/G90-SDR"
        "$HOME/Documents/G90-SDR"
        "$HOME/.local/share/G90-SDR"
    )
    
    for location in "${USER_LOCATIONS[@]}"; do
        if [ -d "$location" ] && [ -f "$location/scripts/start_sdr.py" ]; then
            echo "$location"
            return 0
        fi
    done
    
    local SYSTEM_LOCATIONS=(
        "/opt/G90-SDR"
        "/usr/local/share/G90-SDR"
    )
    
    for location in "${SYSTEM_LOCATIONS[@]}"; do
        if [ -d "$location" ] && [ -f "$location/scripts/start_sdr.py" ]; then
            echo "$location"
            return 0
        fi
    done
    
    return 1
}

show_error() {
    local message="$1"
    if command -v zenity &> /dev/null; then
        zenity --error --title="G90-SDR Error" --text="$message" --width=400
    elif command -v notify-send &> /dev/null; then
        notify-send "G90-SDR Error" "$message" -u critical -i dialog-error
    else
        echo "ERROR: $message" >&2
    fi
}

main() {
    SDR_DIR=$(find_installation)
    
    if [ -z "$SDR_DIR" ]; then
        show_error "G90-SDR installation not found!\n\nSearched:\n• \$L_SDR_DIR\n• \$HOME/Virtual/G90-SDR\n• \$HOME/G90-SDR\n• /opt/G90-SDR"
        exit 1
    fi
    
    if [ ! -f "$SDR_DIR/scripts/start_sdr.py" ]; then
        show_error "Invalid installation at:\n$SDR_DIR"
        exit 1
    fi
    
    cd "$SDR_DIR" || exit 1
    
    if [ ! -d "venv" ]; then
        show_error "Virtual environment not found!\n\nRun: cd $SDR_DIR && bash install.bash"
        exit 1
    fi
    
    source venv/bin/activate || exit 1
    python3 scripts/start_sdr.py
    deactivate 2>/dev/null || true
}

case "${1:-}" in
    --version|-v)
        echo "G90-SDR v$VERSION"
        exit 0
        ;;
    --help|-h)
        echo "G90-SDR Universal Launcher v$VERSION"
        echo ""
        echo "Usage: g90-sdr [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --version, -v    Show version"
        echo "  --help, -h       Show help"
        echo "  --find           Show installation location"
        exit 0
        ;;
    --find)
        SDR_DIR=$(find_installation)
        if [ -n "$SDR_DIR" ]; then
            echo "Found at: $SDR_DIR"
            exit 0
        else
            echo "Not found"
            exit 1
        fi
        ;;
    "")
        main
        ;;
    *)
        echo "Unknown option: $1"
        exit 1
        ;;
esac
WRAPPER_EOF

echo "  ✓ g90-sdr wrapper created"

# 2. FlRig wrapper
cat > "$TEMP_DIR/g90-flrig" << 'FLRIG_EOF'
#!/bin/bash
# FlRig G90 Launcher

find_installation() {
    if [ -n "$L_SDR_DIR" ] && [ -d "$L_SDR_DIR" ]; then
        echo "$L_SDR_DIR"
        return 0
    fi
    
    local LOCATIONS=(
        "$HOME/Virtual/G90-SDR"
        "$HOME/G90-SDR"
        "$HOME/Documents/G90-SDR"
        "/opt/G90-SDR"
    )
    
    for location in "${LOCATIONS[@]}"; do
        if [ -d "$location" ] && [ -f "$location/config/flrig_g90.xml" ]; then
            echo "$location"
            return 0
        fi
    done
    
    return 1
}

main() {
    if ! command -v flrig &> /dev/null; then
        echo "ERROR: FlRig not installed"
        exit 1
    fi
    
    SDR_DIR=$(find_installation)
    
    if [ -z "$SDR_DIR" ] || [ ! -f "$SDR_DIR/config/flrig_g90.xml" ]; then
        echo "Warning: G90 config not found, using FlRig defaults"
        exec flrig "$@"
    fi
    
    exec flrig --rig-file="$SDR_DIR/config/flrig_g90.xml" --xml-enable --auto-connect "$@"
}

case "${1:-}" in
    --help|-h)
        echo "FlRig G90 Launcher"
        echo "Launches FlRig with G90 configuration"
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac
FLRIG_EOF

echo "  ✓ g90-flrig wrapper created"

# Install wrappers
echo ""
echo "Installing wrappers to /usr/local/bin/..."

if [ "$EUID" -eq 0 ]; then
    # Already root
    cp "$TEMP_DIR/g90-sdr" /usr/local/bin/
    cp "$TEMP_DIR/g90-flrig" /usr/local/bin/
    chmod +x /usr/local/bin/g90-sdr
    chmod +x /usr/local/bin/g90-flrig
else
    # Use sudo
    sudo cp "$TEMP_DIR/g90-sdr" /usr/local/bin/
    sudo cp "$TEMP_DIR/g90-flrig" /usr/local/bin/
    sudo chmod +x /usr/local/bin/g90-sdr
    sudo chmod +x /usr/local/bin/g90-flrig
fi

echo "  ✓ g90-sdr installed"
echo "  ✓ g90-flrig installed"

# Update desktop launchers
echo ""
echo "Updating desktop launchers..."

LAUNCHER_DIR="$HOME/.local/share/applications"

# Update FlRig launcher
if [ -f "$LAUNCHER_DIR/flrig-g90.desktop" ]; then
    sed -i 's|Exec=.*flrig.*|Exec=g90-flrig|' "$LAUNCHER_DIR/flrig-g90.desktop"
    echo "  ✓ Updated flrig-g90.desktop"
fi

# Update G90-SDR launcher
if [ -f "$LAUNCHER_DIR/g90-sdr.desktop" ]; then
    sed -i 's|Exec=.*|Exec=g90-sdr|' "$LAUNCHER_DIR/g90-sdr.desktop"
    echo "  ✓ Updated g90-sdr.desktop"
fi

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$LAUNCHER_DIR" 2>/dev/null
    echo "  ✓ Desktop database updated"
fi

# Test installation
echo ""
echo "Testing installation..."
if command -v g90-sdr &> /dev/null; then
    echo "  ✓ g90-sdr command available"
    g90-sdr --find || echo "  (Installation will be detected at runtime)"
else
    echo "  ✗ g90-sdr command not found in PATH"
fi

if command -v g90-flrig &> /dev/null; then
    echo "  ✓ g90-flrig command available"
else
    echo "  ✗ g90-flrig command not found in PATH"
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  Installation Complete!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Universal commands installed:"
echo "  • g90-sdr        - Start complete G90-SDR system"
echo "  • g90-flrig      - Start FlRig with G90 config"
echo ""
echo "These commands work from:"
echo "  • Terminal"
echo "  • Desktop launchers"
echo "  • Any directory"
echo "  • Any user (after they install G90-SDR)"
echo ""
echo "Test commands:"
echo "  g90-sdr --help"
echo "  g90-sdr --find"
echo "  g90-flrig"
echo ""
echo "The system auto-detects G90-SDR installation location!"
echo ""
