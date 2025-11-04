#!/bin/bash
# Filename: set_path.bash
# Configure the correct G90-SDR installation path

echo "════════════════════════════════════════════════════════════════"
echo "  G90-SDR Path Configuration"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Get current directory
CURRENT_DIR="$(pwd)"
echo "Current directory: $CURRENT_DIR"
echo ""

# Detect if we're in G90-SDR directory
if [[ "$CURRENT_DIR" == *"G90-SDR"* ]]; then
    echo "✓ You appear to be in the G90-SDR directory"
    G90_DIR="$CURRENT_DIR"
else
    echo "⚠ Current directory doesn't contain 'G90-SDR'"
    echo ""
    echo "Please enter the full path to your G90-SDR installation:"
    echo "Example: /home/username/Virtual/G90-SDR"
    echo ""
    read -p "Path: " G90_DIR
fi

echo ""
echo "G90-SDR directory: $G90_DIR"
echo ""

# Verify directory exists and has expected structure
if [ ! -d "$G90_DIR" ]; then
    echo "✗ Directory does not exist: $G90_DIR"
    exit 1
fi

if [ ! -d "$G90_DIR/scripts" ] || [ ! -d "$G90_DIR/tests" ]; then
    echo "✗ Directory doesn't have expected structure (missing scripts/ or tests/)"
    exit 1
fi

echo "✓ Directory structure looks good"
echo ""

# Create a .g90path file
cat > "$G90_DIR/.g90path" << EOF
# G90-SDR Installation Path
# This file is used by scripts to find the correct installation directory
G90_SDR_PATH=$G90_DIR
EOF

echo "✓ Created configuration file: $G90_DIR/.g90path"
echo ""
echo "All scripts will now use: $G90_DIR"
echo ""
echo "To verify, run:"
echo "  cd $G90_DIR"
echo "  cat .g90path"
echo ""
