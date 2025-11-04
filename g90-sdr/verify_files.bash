#!/bin/bash
# Filename: verify_files.bash
# Verify all required files are present before installation

# Use L_SDR_DIR environment variable or fall back to script location
if [ -n "$L_SDR_DIR" ]; then
    SCRIPT_DIR="$L_SDR_DIR"
else
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
fi

cd "$SCRIPT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "════════════════════════════════════════════════════════════════"
echo "  G90-SDR File Verification"
echo "  Working in: $SCRIPT_DIR"
echo "════════════════════════════════════════════════════════════════"
echo ""

MISSING=0
PRESENT=0

check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1"
        ((PRESENT++))
    else
        echo -e "${RED}✗${NC} $1 ${YELLOW}(MISSING)${NC}"
        ((MISSING++))
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $1/"
    else
        echo -e "${RED}✗${NC} $1/ ${YELLOW}(MISSING)${NC}"
        ((MISSING++))
    fi
}

echo "Checking Directory Structure:"
echo "─────────────────────────────────────────────────────────────────"
check_dir "config"
check_dir "scripts"
check_dir "tests"
check_dir "docs"
check_dir "logs"

echo ""
echo "Checking Root Files:"
echo "─────────────────────────────────────────────────────────────────"
check_file "requirements.txt"
check_file "install.sh"
check_file "update.sh"
check_file "README.md"
check_file "INSTALL.md"
check_file "LICENSE"
check_file "QUICK_REFERENCE.md"
check_file ".gitignore"

echo ""
echo "Checking scripts/ Files:"
echo "─────────────────────────────────────────────────────────────────"
check_file "scripts/rig_control.py"
check_file "scripts/frequency_sync.py"
check_file "scripts/audio_router.py"
check_file "scripts/config_manager.py"
check_file "scripts/device_monitor.py"
check_file "scripts/start_sdr.py"
check_file "scripts/stop_sdr.py"

echo ""
echo "Checking tests/ Files:"
echo "─────────────────────────────────────────────────────────────────"
check_file "tests/TestConnection.py"
check_file "tests/TestAudio.py"
check_file "tests/TestCatControl.py"
check_file "tests/DiagnoseSystem.py"
check_file "tests/CalibrateAudio.py"

echo ""
echo "Checking docs/ Files:"
echo "─────────────────────────────────────────────────────────────────"
check_file "docs/USER_GUIDE.md"
check_file "docs/TROUBLESHOOTING.md"
check_file "docs/PROJECT_STRUCTURE.md"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  Summary"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "  Present: $PRESENT files"
echo "  Missing: $MISSING files"
echo ""

if [ $MISSING -eq 0 ]; then
    echo -e "${GREEN}✓ All files present! Ready to install.${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Make scripts executable: chmod +x *.sh"
    echo "  2. Run installation: bash install.sh"
    exit 0
else
    echo -e "${YELLOW}⚠ $MISSING file(s) missing!${NC}"
    echo ""
    echo "Please create missing files before running install.sh"
    echo "See SETUP_FILES.md for instructions"
    exit 1
fi
