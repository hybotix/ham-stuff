#!/bin/bash
# Filename: create_all_files.bash
# Master script to create ALL G90-SDR files at once

set -e

echo "Creating G90-SDR project structure..."
echo ""

# Create base directory
mkdir -p ~/G90-SDR
cd ~/G90-SDR

# Create subdirectories
mkdir -p config scripts tests docs logs
touch logs/.gitkeep

echo "✓ Directory structure created"

# Create requirements.txt
cat > requirements.txt << 'REQUIREMENTS_EOF'
pyserial>=3.5
requests>=2.31.0
pyyaml>=6.0.1
pyaudio>=0.2.14
sounddevice>=0.4.6
numpy>=1.26.0
psutil>=5.9.8
colorlog>=6.8.2
python-dateutil>=2.9.0
typing-extensions>=4.12.0
REQUIREMENTS_EOF

echo "✓ requirements.txt created"

# Create .gitignore
cat > .gitignore << 'GITIGNORE_EOF'
__pycache__/
*.py[cod]
venv/
*.log
logs/*.log
*.bak
.vscode/
.idea/
*.swp
.DS_Store
*.tar.gz
config/audio_calibration.json
GITIGNORE_EOF

echo "✓ .gitignore created"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  G90-SDR project structure created at: ~/G90-SDR"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "IMPORTANT: This script only creates the directory structure and"
echo "basic files. You still need to create the Python scripts and"
echo "documentation by copying them from the conversation."
echo ""
echo "Next steps:"
echo "  1. Copy each Python file from the chat artifacts"
echo "  2. Copy documentation files"
echo "  3. Run: bash install.sh"
echo ""
echo "Files you need to copy (23 total):"
echo ""
echo "Root directory:"
echo "  - README.md"
echo "  - INSTALL.md"
echo "  - LICENSE"
echo "  - QUICK_REFERENCE.md"
echo "  - install.sh (make executable: chmod +x install.sh)"
echo "  - update.sh (make executable: chmod +x update.sh)"
echo ""
echo "scripts/ directory (7 files):"
echo "  - rig_control.py"
echo "  - frequency_sync.py"
echo "  - audio_router.py"
echo "  - config_manager.py"
echo "  - device_monitor.py"
echo "  - start_sdr.py"
echo "  - stop_sdr.py"
echo ""
echo "tests/ directory (5 files):"
echo "  - TestConnection.py"
echo "  - TestAudio.py"
echo "  - TestCatControl.py"
echo "  - DiagnoseSystem.py"
echo "  - CalibrateAudio.py"
echo ""
echo "docs/ directory (3 files):"
echo "  - USER_GUIDE.md"
echo "  - TROUBLESHOOTING.md"
echo "  - PROJECT_STRUCTURE.md"
echo ""
