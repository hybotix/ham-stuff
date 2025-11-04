#!/bin/bash
# Filename: update.bash
# G90-SDR System Update Script

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

# Welcome message
clear
echo "████████████████████████████████████████████████████████████████████████"
echo "  G90-SDR Update Script"
echo "  Version 1.0"
echo "████████████████████████████████████████████████████████████████████████"
echo ""

print_info "This script will update G90-SDR and its dependencies"
echo ""

# Backup configuration
print_header "Step 1: Backing Up Configuration"

BACKUP_DIR="backups"
mkdir -p "$BACKUP_DIR"

BACKUP_FILE="$BACKUP_DIR/g90_backup_$(date +%Y%m%d_%H%M%S).tar.gz"

if [ -d "config" ]; then
    print_info "Creating backup: $BACKUP_FILE"
    tar -czf "$BACKUP_FILE" config/ logs/ 2>/dev/null || true
    print_success "Configuration backed up"
else
    print_warning "No configuration directory found"
fi

# Update system packages
print_header "Step 2: Updating System Packages"

print_info "Updating package lists..."
sudo apt update

print_info "Upgrading packages..."
sudo apt upgrade -y

print_success "System packages updated"

# Update Python packages
print_header "Step 3: Updating Python Packages"

if [ -d "venv" ]; then
    print_info "Activating virtual environment..."
    source venv/bin/activate
    
    print_info "Upgrading pip..."
    pip install --upgrade pip setuptools wheel
    
    print_info "Updating Python packages..."
    pip install --upgrade -r requirements.txt
    
    print_success "Python packages updated"
else
    print_warning "Virtual environment not found"
    print_info "Creating new virtual environment..."
    
    if command -v python3.13 &> /dev/null; then
        python3.13 -m venv venv
    else
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    pip install --upgrade pip setuptools wheel
    pip install -r requirements.txt
    
    print_success "Virtual environment created"
fi

# Check FlRig version
print_header "Step 4: Checking FlRig"

if command -v flrig &> /dev/null; then
    FLRIG_VERSION=$(flrig --version 2>&1 | head -n 1 || echo "unknown")
    print_info "Current FlRig version: $FLRIG_VERSION"
    print_info "To update FlRig, visit: https://sourceforge.net/projects/fldigi/"
else
    print_warning "FlRig not found"
fi

# Check GQRX version
print_header "Step 5: Checking GQRX"

if command -v gqrx &> /dev/null; then
    print_info "GQRX is installed"
    print_info "To update GQRX: sudo apt upgrade gqrx-sdr"
else
    print_warning "GQRX not found"
fi

# Update permissions
print_header "Step 6: Checking Permissions"

print_info "Verifying udev rules..."
if [ -f "/etc/udev/rules.d/99-xiegu.rules" ]; then
    print_success "udev rules present"
else
    print_warning "udev rules missing - recreating..."
    sudo tee /etc/udev/rules.d/99-xiegu.rules > /dev/null << 'EOF'
SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", MODE="0666", GROUP="dialout"
EOF
    sudo udevadm control --reload-rules
    sudo udevadm trigger
    print_success "udev rules created"
fi

# Verify group membership
USERNAME=$(whoami)
if groups | grep -q dialout; then
    print_success "User in dialout group"
else
    print_warning "User not in dialout group - adding..."
    sudo usermod -a -G dialout "$USERNAME"
    print_warning "Reboot required for group changes"
fi

# Run system diagnostics
print_header "Step 7: System Diagnostics"

print_info "Running diagnostic tests..."
if [ -f "tests/DiagnoseSystem.py" ]; then
    python3 tests/DiagnoseSystem.py
else
    print_warning "Diagnostic script not found"
fi

# Check for updates
print_header "Step 8: Checking for G90-SDR Updates"

if [ -d ".git" ]; then
    print_info "Checking for updates from git repository..."
    git fetch
    
    LOCAL=$(git rev-parse @)
    REMOTE=$(git rev-parse @{u})
    
    if [ "$LOCAL" = "$REMOTE" ]; then
        print_success "G90-SDR is up to date"
    else
        print_warning "Updates available in repository"
        print_info "To update: git pull origin main"
    fi
else
    print_info "Not a git repository - manual updates only"
fi

# Summary
print_header "Update Summary"

echo ""
echo "Update completed successfully!"
echo ""
echo "What was updated:"
echo "  ✓ System packages"
echo "  ✓ Python packages"
echo "  ✓ Permissions verified"
echo "  ✓ Configuration backed up to: $BACKUP_FILE"
echo ""

# Check if reboot needed
if [ -f /var/run/reboot-required ]; then
    echo -e "${YELLOW}⚠ System reboot recommended${NC}"
    echo ""
    read -p "Reboot now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Rebooting..."
        sudo reboot
    else
        print_warning "Remember to reboot when convenient"
    fi
fi

print_success "Update complete!"
echo ""
echo "To start G90-SDR:"
echo "  cd ~/G90-SDR"
echo "  source venv/bin/activate"
echo "  python3 scripts/start_sdr.py"
echo ""
