#!/bin/bash
# Filename: utils/build_flrig.bash
# Build FlRig from source - always pulls latest stable release

set -e

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

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
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
echo "  FlRig Source Build Script"
echo "  Builds latest stable FlRig from source"
echo "████████████████████████████████████████████████████████████████████████"
echo ""

# Check current version
if command -v flrig &> /dev/null; then
    CURRENT_VERSION=$(flrig --version 2>&1 | head -1 || echo "unknown")
    print_info "Currently installed: $CURRENT_VERSION"
else
    print_info "FlRig not currently installed"
fi

# Install dependencies
print_header "Installing Build Dependencies"

print_info "Installing FlRig build dependencies..."
sudo apt update
sudo apt install -y \
    build-essential \
    libfltk1.3-dev \
    libfltk-images1.3 \
    libfltk-forms1.3 \
    libx11-dev \
    libxinerama-dev \
    libxft-dev \
    libxcursor-dev \
    wget \
    curl

print_success "Dependencies installed"

# Get latest version from SourceForge
print_header "Finding Latest FlRig Release"

print_info "Querying SourceForge for latest release..."

# Scrape SourceForge to find latest version
LATEST_VERSION=$(curl -s "https://sourceforge.net/projects/fldigi/files/flrig/" | \
    grep -oP 'flrig-\d+\.\d+\.\d+\.tar\.gz' | \
    sort -V | \
    tail -1 | \
    sed 's/flrig-//;s/.tar.gz//')

if [ -z "$LATEST_VERSION" ]; then
    print_error "Could not determine latest version from SourceForge"
    print_info "Defaulting to known stable version 2.0.03"
    LATEST_VERSION="2.0.03"
fi

print_success "Latest stable release: $LATEST_VERSION"

# Download source
print_header "Downloading FlRig Source"

cd /tmp

TARBALL="flrig-${LATEST_VERSION}.tar.gz"
DOWNLOAD_URL="https://sourceforge.net/projects/fldigi/files/flrig/${TARBALL}/download"

print_info "Downloading: $TARBALL"

if [ -f "$TARBALL" ]; then
    print_info "Removing old tarball..."
    rm "$TARBALL"
fi

wget -O "$TARBALL" "$DOWNLOAD_URL"

print_success "Downloaded successfully"

# Extract
print_header "Extracting Source"

EXTRACT_DIR="flrig-${LATEST_VERSION}"

if [ -d "$EXTRACT_DIR" ]; then
    print_info "Removing old source directory..."
    rm -rf "$EXTRACT_DIR"
fi

tar -xzf "$TARBALL"

if [ ! -d "$EXTRACT_DIR" ]; then
    print_error "Extraction failed or unexpected directory name"
    exit 1
fi

cd "$EXTRACT_DIR"

print_success "Source extracted"

# Configure
print_header "Configuring Build"

print_info "Running configure script..."
./configure --prefix=/usr/local

print_success "Configuration complete"

# Build
print_header "Compiling FlRig"

print_info "Building with $(nproc) CPU cores..."
print_info "This will take ~5 minutes on Raspberry Pi 5..."

make -j$(nproc)

print_success "Compilation complete"

# Install
print_header "Installing FlRig"

print_info "Installing to /usr/local/bin/..."
sudo make install

print_success "FlRig installed"

# Verify
print_header "Verifying Installation"

if command -v flrig &> /dev/null; then
    INSTALLED_VERSION=$(flrig --version 2>&1 | head -1)
    print_success "FlRig is installed and available"
    print_info "Version: $INSTALLED_VERSION"
    print_info "Location: $(which flrig)"
else
    print_error "FlRig command not found after installation"
    print_warning "You may need to log out and back in"
fi

# Cleanup
print_header "Cleanup"

read -p "Remove source files from /tmp? (y/n) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    cd /tmp
    rm -rf "$EXTRACT_DIR" "$TARBALL"
    print_success "Source files removed"
else
    print_info "Source files kept in /tmp/$EXTRACT_DIR"
fi

# Summary
print_header "Build Complete!"

echo ""
echo "FlRig has been built and installed from source"
echo ""
echo "Built version: $LATEST_VERSION"
echo "Installed to: /usr/local/bin/flrig"
echo ""
echo "To run FlRig:"
echo "  • From terminal: flrig"
echo "  • With G90 config: g90-flrig"
echo "  • Use G90-SDR launcher: g90-sdr"
echo ""
echo "To rebuild in the future:"
echo "  bash utils/build_flrig.bash"
echo ""
