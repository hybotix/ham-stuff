#!/bin/bash
# Filename: utils/build_gqrx.bash
# Build GQRX from source - always pulls latest stable release

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
echo "  GQRX Source Build Script"
echo "  Builds latest stable GQRX from source"
echo "████████████████████████████████████████████████████████████████████████"
echo ""

# Check if already installed
if command -v gqrx &> /dev/null; then
    CURRENT_VERSION=$(gqrx --version 2>&1 | head -1)
    print_info "Currently installed: $CURRENT_VERSION"
    echo ""
    read -p "Rebuild GQRX from latest source? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Build cancelled"
        exit 0
    fi
else
    print_info "GQRX not currently installed"
fi

# Check for existing build
print_header "Checking for Previous Builds"

if [ -d "/tmp/gqrx" ]; then
    print_warning "Found existing GQRX source in /tmp/gqrx"
    read -p "Remove and start fresh? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf /tmp/gqrx
        print_success "Cleaned up old source"
    fi
fi

# Install dependencies
print_header "Installing Build Dependencies"

print_info "This will install required development packages..."
sudo apt update

print_info "Installing Qt5 and GNU Radio dependencies..."
sudo apt install -y \
    git \
    cmake \
    build-essential \
    qtbase5-dev \
    qtchooser \
    qt5-qmake \
    qtbase5-dev-tools \
    libqt5svg5-dev \
    libgnuradio-dev \
    gr-osmosdr \
    libpulse-dev \
    portaudio19-dev \
    libsndfile1-dev \
    libvolk2-dev \
    liblog4cpp5-dev \
    libboost-all-dev

print_success "Dependencies installed"

# Clone repository
print_header "Downloading GQRX Source"

cd /tmp

print_info "Cloning GQRX repository from GitHub..."
if [ -d "gqrx" ]; then
    print_info "Removing old source directory..."
    rm -rf gqrx
fi

git clone https://github.com/gqrx-sdr/gqrx.git
cd gqrx

# Get latest stable release tag (not beta/rc)
print_info "Fetching latest stable release..."
git fetch --tags

# Get the latest non-prerelease tag
LATEST_TAG=$(git tag --sort=-v:refname | grep -v -E 'beta|rc|alpha' | head -1)

if [ -z "$LATEST_TAG" ]; then
    print_error "Could not determine latest stable release"
    exit 1
fi

print_success "Latest stable release: $LATEST_TAG"

# Checkout latest stable
print_info "Checking out $LATEST_TAG..."
git checkout $LATEST_TAG

BUILD_VERSION=$LATEST_TAG

# Configure build
print_header "Configuring Build"

if [ -d "build" ]; then
    print_info "Cleaning previous build directory..."
    rm -rf build
fi

mkdir build
cd build

print_info "Running cmake..."
cmake .. -DCMAKE_INSTALL_PREFIX=/usr/local

print_success "Build configured"

# Build
print_header "Compiling GQRX"

print_info "This will take 10-20 minutes on Raspberry Pi 5..."
print_info "Using $(nproc) CPU cores for compilation"
echo ""

# Show compilation progress
make -j$(nproc)

print_success "Compilation complete"

# Install
print_header "Installing GQRX"

print_info "Installing to /usr/local/bin/..."
sudo make install

print_info "Updating library cache..."
sudo ldconfig

# Create desktop entry if it doesn't exist
if [ ! -f "/usr/local/share/applications/gqrx.desktop" ]; then
    print_info "Creating desktop entry..."
    sudo mkdir -p /usr/local/share/applications
    
    sudo tee /usr/local/share/applications/gqrx.desktop > /dev/null << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=GQRX
GenericName=Software Defined Radio
Comment=SDR receiver using GNU Radio
Icon=gqrx
Exec=gqrx
Terminal=false
Categories=HamRadio;Network;
Keywords=sdr;radio;receiver;
EOF
    
    print_success "Desktop entry created"
fi

print_success "GQRX installed"

# Verify installation
print_header "Verifying Installation"

if command -v gqrx &> /dev/null; then
    INSTALLED_VERSION=$(gqrx --version 2>&1 | head -1)
    print_success "GQRX is installed and available"
    print_info "Version: $INSTALLED_VERSION"
    print_info "Location: $(which gqrx)"
else
    print_error "GQRX command not found after installation"
    print_warning "You may need to log out and back in, or reboot"
fi

# Clean up
print_header "Cleanup"

read -p "Remove source files from /tmp/gqrx? (y/n) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    cd /tmp
    rm -rf gqrx
    print_success "Source files removed"
else
    print_info "Source files kept in /tmp/gqrx"
fi

# Summary
print_header "Build Complete!"

echo ""
echo "GQRX has been built and installed from source"
echo ""
echo "Built version: $BUILD_VERSION"
echo "Installed to: /usr/local/bin/gqrx"
echo ""
echo "To run GQRX:"
echo "  • From terminal: gqrx"
echo "  • From applications menu: Look for 'GQRX'"
echo "  • Use G90-SDR launcher: g90-sdr"
echo ""
echo "Benefits of source build:"
echo "  ✓ Latest features and bug fixes"
echo "  ✓ Optimized for your system"
echo "  ✓ Full control over version"
echo "  ✓ No package manager conflicts"
echo ""
echo "To rebuild in the future:"
echo "  bash build_gqrx.bash"
echo ""
