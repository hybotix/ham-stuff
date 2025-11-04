#!/bin/bash
# Filename: install.bash
# G90-SDR System Installation Script for Ubuntu 24.04 on Raspberry Pi 5

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Use L_SDR_DIR environment variable or fall back to script location
if [ -n "$L_SDR_DIR" ]; then
    SCRIPT_DIR="$L_SDR_DIR"
else
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
fi

cd "$SCRIPT_DIR"

# Function to print colored messages
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

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_error "Please do not run this script as root"
    print_info "Run as normal user: bash install.sh"
    exit 1
fi

# Welcome message
clear
echo "████████████████████████████████████████████████████████████████████████"
echo "  G90-SDR Installation Script"
echo "  Xiegu G90 Software Defined Radio Interface"
echo "  Version 1.0 - For Ubuntu 24.04 on Raspberry Pi 5"
echo "████████████████████████████████████████████████████████████████████████"
echo ""

# Confirm installation
read -p "This will install G90-SDR and its dependencies. Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_info "Installation cancelled"
    exit 0
fi

# Step 1: Update system
print_header "Step 1: Updating System"
print_info "Updating package lists..."
sudo apt update

print_info "Upgrading packages (this may take a while)..."
sudo apt upgrade -y

print_success "System updated"

# Step 2: Install system dependencies
print_header "Step 2: Installing System Dependencies"

print_info "Installing build tools..."
sudo apt install -y \
    build-essential \
    git \
    cmake \
    pkg-config \
    wget \
    curl

print_info "Installing Python 3.13..."
# Check if Python 3.13 is available
if ! command -v python3.13 &> /dev/null; then
    print_warning "Python 3.13 not found, installing Python 3..."
    sudo apt install -y python3 python3-dev python3-pip python3-venv
else
    print_success "Python 3.13 found"
fi

print_info "Installing USB and serial libraries..."
sudo apt install -y \
    libusb-1.0-0-dev \
    python3-serial

print_success "System dependencies installed"

# Step 3: Install audio dependencies
print_header "Step 3: Installing Audio Dependencies"

print_info "Installing PulseAudio..."
sudo apt install -y \
    pulseaudio \
    pulseaudio-utils \
    pavucontrol \
    libasound2-dev \
    portaudio19-dev

print_info "Installing Python audio libraries dependencies..."
sudo apt install -y \
    python3-pyaudio \
    libportaudio2 \
    libportaudiocpp0

print_success "Audio dependencies installed"

# Step 4: Install FlRig from source (latest version)
print_header "Step 4: Building FlRig from Source"

if command -v flrig &> /dev/null; then
    FLRIG_VERSION=$(flrig --version 2>&1 | head -1 || echo "unknown")
    print_info "FlRig already installed: $FLRIG_VERSION"
    read -p "Rebuild FlRig from latest source? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_success "Using existing FlRig"
    else
        REBUILD_FLRIG=true
    fi
else
    REBUILD_FLRIG=true
fi

if [ "$REBUILD_FLRIG" = true ]; then
    print_info "Installing FlRig dependencies..."
    sudo apt install -y \
        libfltk1.3-dev \
        libfltk-images1.3 \
        libfltk-forms1.3 \
        libx11-dev \
        libxinerama-dev \
        libxft-dev \
        libxcursor-dev \
        wget \
        curl
    
    print_info "Finding latest FlRig release..."
    cd /tmp
    
    # Get latest version from SourceForge
    LATEST_VERSION=$(curl -s "https://sourceforge.net/projects/fldigi/files/flrig/" | \
        grep -oP 'flrig-\d+\.\d+\.\d+\.tar\.gz' | \
        sort -V | \
        tail -1 | \
        sed 's/flrig-//;s/.tar.gz//')
    
    if [ -z "$LATEST_VERSION" ]; then
        print_warning "Could not auto-detect latest version, using 2.0.03"
        LATEST_VERSION="2.0.03"
    fi
    
    print_info "Building FlRig version: $LATEST_VERSION"
    
    # Download
    TARBALL="flrig-${LATEST_VERSION}.tar.gz"
    wget -O "$TARBALL" "https://sourceforge.net/projects/fldigi/files/flrig/${TARBALL}/download"
    
    # Extract
    tar -xzf "$TARBALL"
    cd "flrig-${LATEST_VERSION}"
    
    # Build
    print_info "Compiling FlRig (this will take ~5 minutes)..."
    ./configure --prefix=/usr/local
    make -j$(nproc)
    
    print_info "Installing FlRig..."
    sudo make install
    
    # Clean up
    cd /tmp
    rm -rf "flrig-${LATEST_VERSION}" "$TARBALL"
    
    cd "$SCRIPT_DIR"
    print_success "FlRig built and installed: version $LATEST_VERSION"
fi

# Step 5: Install GQRX from source (latest version)
print_header "Step 5: Building GQRX from Source"

if command -v gqrx &> /dev/null; then
    GQRX_VERSION=$(gqrx --version 2>&1 | head -1 || echo "unknown")
    print_info "GQRX already installed: $GQRX_VERSION"
    read -p "Rebuild GQRX from latest source? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_success "Using existing GQRX"
    else
        REBUILD_GQRX=true
    fi
else
    REBUILD_GQRX=true
fi

if [ "$REBUILD_GQRX" = true ]; then
    print_info "Installing GQRX build dependencies..."
    sudo apt install -y \
        git \
        cmake \
        qtbase5-dev \
        qtchooser \
        libqt5svg5-dev \
        libgnuradio-dev \
        gr-osmosdr \
        libpulse-dev \
        portaudio19-dev \
        libsndfile1-dev \
        libvolk2-dev \
        liblog4cpp5-dev \
        libboost-all-dev
    
    print_info "Cloning GQRX repository..."
    cd /tmp
    
    if [ -d "gqrx" ]; then
        rm -rf gqrx
    fi
    
    git clone https://github.com/gqrx-sdr/gqrx.git
    cd gqrx
    
    # Get latest stable (non-beta/rc) tag
    print_info "Finding latest stable release..."
    git fetch --tags
    LATEST_TAG=$(git tag --sort=-v:refname | grep -v -E 'beta|rc|alpha' | head -1)
    
    if [ -z "$LATEST_TAG" ]; then
        print_error "Could not determine latest stable release"
        LATEST_TAG="v2.17.5"  # Fallback to known good version
        print_warning "Using fallback version: $LATEST_TAG"
    fi
    
    print_info "Building GQRX version: $LATEST_TAG"
    git checkout "$LATEST_TAG"
    
    print_info "Configuring GQRX build..."
    mkdir build
    cd build
    cmake ..
    
    print_info "Compiling GQRX (this will take 10-20 minutes on Raspberry Pi 5)..."
    make -j$(nproc)
    
    print_info "Installing GQRX..."
    sudo make install
    sudo ldconfig
    
    # Clean up
    cd /tmp
    rm -rf gqrx
    
    cd "$SCRIPT_DIR"
    
    # Verify installation
    if command -v gqrx &> /dev/null; then
        GQRX_VERSION=$(gqrx --version 2>&1 | head -1)
        print_success "GQRX built and installed: $GQRX_VERSION"
    else
        print_error "GQRX build succeeded but command not found in PATH"
        print_warning "This may resolve after reboot"
    fi
fi

# Step 6: Create Python virtual environment
print_header "Step 6: Setting Up Python Environment"

print_info "Creating virtual environment..."
if [ -d "venv" ]; then
    print_warning "Virtual environment already exists, recreating..."
    rm -rf venv
fi

# Try Python 3.13, fall back to python3
if command -v python3.13 &> /dev/null; then
    python3.13 -m venv venv
else
    python3 -m venv venv
fi

print_info "Activating virtual environment..."
source venv/bin/activate

print_info "Upgrading pip..."
pip install --upgrade pip setuptools wheel

print_info "Installing Python dependencies..."
pip install -r requirements.txt

print_success "Python environment configured"

# Step 7: Configure system permissions
print_header "Step 7: Configuring System Permissions"

print_info "Adding user to dialout group (for serial port access)..."
sudo usermod -a -G dialout "$USER"

print_info "Adding user to audio group..."
sudo usermod -a -G audio "$USER"

print_info "Creating udev rules for DE-19 interface..."
sudo tee /etc/udev/rules.d/99-xiegu.rules > /dev/null << 'EOF'
# Xiegu DE-19 Data Interface (CH340 USB-to-serial)
SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", MODE="0666", GROUP="dialout"
EOF

print_info "Reloading udev rules..."
sudo udevadm control --reload-rules
sudo udevadm trigger

print_success "System permissions configured"

# Step 8: Create configuration files
print_header "Step 8: Creating Configuration Files"

print_info "Creating configuration directory..."
mkdir -p config

print_info "Creating default configuration..."
cat > config/g90_sdr.yaml << 'EOF'
# G90-SDR Configuration File

flrig:
  host: 127.0.0.1
  port: 12345
  device: /dev/ttyUSB0
  baudrate: 19200
  timeout: 200
  retries: 5

gqrx:
  host: 127.0.0.1
  port: 7356
  sample_rate: 48000
  fft_size: 4096
  fft_rate: 25
  waterfall_span: 48000

audio:
  input_device: null
  output_device: null
  sample_rate: 48000
  latency_ms: 50
  use_pulseaudio: true

sync:
  enabled: true
  interval: 0.5
  sync_mode: true
  sync_bandwidth: false
EOF

print_success "Configuration files created"

# Step 9: Create log directory
print_header "Step 9: Creating Log Directory"

mkdir -p logs
touch logs/.gitkeep

print_success "Log directory created"

# Step 10: Test installation
print_header "Step 10: Testing Installation"

print_info "Testing Python imports..."
source venv/bin/activate

python3 << 'EOF'
import sys
try:
    import serial
    import sounddevice
    import numpy
    import yaml
    import psutil
    print("✓ All Python modules imported successfully")
    sys.exit(0)
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)
EOF

if [ $? -eq 0 ]; then
    print_success "Python environment test passed"
else
    print_error "Python environment test failed"
    exit 1
fi

# Final message
print_header "Installation Complete!"

echo ""
echo -e "${GREEN}✓ G90-SDR has been installed successfully!${NC}"
echo ""
echo "IMPORTANT: Group membership changes require a reboot to take effect."
echo ""
echo "Next steps:"
echo "  1. Reboot your Raspberry Pi: sudo reboot"
echo "  2. After reboot, connect your G90 and DE-19"
echo "  3. Run connection test: python3 tests/TestConnection.py"
echo "  4. Run audio test: python3 tests/TestAudio.py"
echo "  5. Run system diagnostics: python3 tests/DiagnoseSystem.py"
echo "  6. Start G90-SDR: python3 scripts/start_sdr.py"
echo ""
echo "Documentation:"
echo "  README.md     - Project overview and features"
echo "  INSTALL.md    - Detailed installation guide"
echo "  config/       - Configuration files"
echo ""
echo "Support:"
echo "  Check logs in: $SCRIPT_DIR/logs/"
echo "  Report issues: https://github.com/yourusername/G90-SDR"
echo ""
echo -e "${YELLOW}Please reboot now: sudo reboot${NC}"
echo ""

# Ask if user wants to reboot now
read -p "Reboot now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Rebooting..."
    sudo reboot
else
    print_warning "Remember to reboot before using G90-SDR!"
fi
