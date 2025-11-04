#!/bin/bash
# Filename: utils/rebuild_all.bash
# Rebuild all source-built components to latest versions

set -e

# Use L_SDR_DIR or script location
if [ -n "$L_SDR_DIR" ]; then
    UTILS_DIR="$L_SDR_DIR/utils"
else
    UTILS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
fi

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_header() {
    echo ""
    echo "========================================================================"
    echo "  $1"
    echo "========================================================================"
}

# Welcome
clear
echo "████████████████████████████████████████████████████████████████████████"
echo "  G90-SDR Source Rebuild"
echo "  Rebuild all components to latest stable versions"
echo "████████████████████████████████████████████████████████████████████████"
echo ""

# Show current versions
print_header "Current Versions"

echo "FlRig:"
if command -v flrig &> /dev/null; then
    flrig --version 2>&1 | head -1
else
    echo "  Not installed"
fi

echo ""
echo "GQRX:"
if command -v gqrx &> /dev/null; then
    gqrx --version 2>&1 | head -1
else
    echo "  Not installed"
fi

echo ""
read -p "Rebuild both FlRig and GQRX to latest versions? (y/n) " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_info "Rebuild cancelled"
    exit 0
fi

# Build FlRig
print_header "Building FlRig"

if [ -f "$UTILS_DIR/build_flrig.bash" ]; then
    bash "$UTILS_DIR/build_flrig.bash"
else
    print_error "build_flrig.bash not found in $UTILS_DIR"
    exit 1
fi

echo ""
read -p "Continue to GQRX build? (y/n) " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_info "Stopping after FlRig"
    exit 0
fi

# Build GQRX
print_header "Building GQRX"

if [ -f "$UTILS_DIR/build_gqrx.bash" ]; then
    bash "$UTILS_DIR/build_gqrx.bash"
else
    print_error "build_gqrx.bash not found in $UTILS_DIR"
    exit 1
fi

# Summary
print_header "Rebuild Complete!"

echo ""
echo "All components rebuilt to latest stable versions"
echo ""
echo "New versions:"
echo "  FlRig: $(flrig --version 2>&1 | head -1)"
echo "  GQRX:  $(gqrx --version 2>&1 | head -1)"
echo ""
echo "Changes take effect immediately"
echo "No restart required"
echo ""
echo "To test:"
echo "  g90-flrig     # Test FlRig"
echo "  gqrx          # Test GQRX"
echo "  g90-sdr       # Test complete system"
echo ""
