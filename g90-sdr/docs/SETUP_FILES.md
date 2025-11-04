# G90-SDR File Setup Guide

Complete checklist for creating all project files in the correct locations.

## Directory Structure to Create

```bash
mkdir -p ~/G90-SDR
cd ~/G90-SDR
mkdir -p config scripts tests docs logs
touch logs/.gitkeep
```

## Files to Create

### Root Directory Files

#### 1. requirements.txt
```
Location: ~/G90-SDR/requirements.txt
Content: Plain text list of Python packages
```

**Content:**
```
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
```

#### 2. install.sh
```
Location: ~/G90-SDR/install.sh
Permissions: chmod +x install.sh
Content: Bash script for installation
```

#### 3. update.sh
```
Location: ~/G90-SDR/update.sh
Permissions: chmod +x update.sh
Content: Bash script for updates
```

#### 4. .gitignore
```
Location: ~/G90-SDR/.gitignore
Content: Git ignore rules
```

#### 5. LICENSE
```
Location: ~/G90-SDR/LICENSE
Content: MIT license text
```

#### 6. README.md
```
Location: ~/G90-SDR/README.md
Content: Project documentation
```

#### 7. INSTALL.md
```
Location: ~/G90-SDR/INSTALL.md
Content: Installation instructions
```

#### 8. QUICK_REFERENCE.md
```
Location: ~/G90-SDR/QUICK_REFERENCE.md
Content: Quick command reference
```

---

### scripts/ Directory

#### 9. scripts/rig_control.py
```
Location: ~/G90-SDR/scripts/rig_control.py
Content: FlRig interface code
```

#### 10. scripts/frequency_sync.py
```
Location: ~/G90-SDR/scripts/frequency_sync.py
Content: Frequency synchronization
```

#### 11. scripts/audio_router.py
```
Location: ~/G90-SDR/scripts/audio_router.py
Content: Audio device management
```

#### 12. scripts/config_manager.py
```
Location: ~/G90-SDR/scripts/config_manager.py
Content: Configuration management
```

#### 13. scripts/device_monitor.py
```
Location: ~/G90-SDR/scripts/device_monitor.py
Content: Hardware monitoring
```

#### 14. scripts/start_sdr.py
```
Location: ~/G90-SDR/scripts/start_sdr.py
Content: System startup script
```

#### 15. scripts/stop_sdr.py
```
Location: ~/G90-SDR/scripts/stop_sdr.py
Content: System shutdown script
```

---

### tests/ Directory

#### 16. tests/TestConnection.py
```
Location: ~/G90-SDR/tests/TestConnection.py
Content: Connection testing
```

#### 17. tests/TestAudio.py
```
Location: ~/G90-SDR/tests/TestAudio.py
Content: Audio testing
```

#### 18. tests/TestCatControl.py
```
Location: ~/G90-SDR/tests/TestCatControl.py
Content: CAT control testing
```

#### 19. tests/DiagnoseSystem.py
```
Location: ~/G90-SDR/tests/DiagnoseSystem.py
Content: System diagnostics
```

#### 20. tests/CalibrateAudio.py
```
Location: ~/G90-SDR/tests/CalibrateAudio.py
Content: Audio calibration
```

---

### docs/ Directory

#### 21. docs/USER_GUIDE.md
```
Location: ~/G90-SDR/docs/USER_GUIDE.md
Content: Complete user guide
```

#### 22. docs/TROUBLESHOOTING.md
```
Location: ~/G90-SDR/docs/TROUBLESHOOTING.md
Content: Troubleshooting guide
```

#### 23. docs/PROJECT_STRUCTURE.md
```
Location: ~/G90-SDR/docs/PROJECT_STRUCTURE.md
Content: Project organization
```

---

## Quick Setup Commands

### Step 1: Create Directory Structure
```bash
cd ~
mkdir -p G90-SDR/{config,scripts,tests,docs,logs}
cd G90-SDR
touch logs/.gitkeep
```

### Step 2: Create requirements.txt First
```bash
cat > requirements.txt << 'EOF'
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
EOF
```

### Step 3: Create Each Python File
For each script, use:
```bash
nano scripts/filename.py
# Paste content
# Save: Ctrl+O, Enter
# Exit: Ctrl+X
```

### Step 4: Create Shell Scripts
```bash
nano install.sh
# Paste content
# Save and exit
chmod +x install.sh

nano update.sh
# Paste content
# Save and exit
chmod +x update.sh
```

### Step 5: Create Documentation
```bash
nano README.md
# Paste content and save

nano INSTALL.md
# Paste content and save

# Repeat for other docs
```

---

## Verification Checklist

After creating all files, verify:

```bash
cd ~/G90-SDR

# Check directory structure
tree -L 2  # or: ls -R

# Verify requirements.txt exists and has content
cat requirements.txt

# Check shell scripts are executable
ls -la *.sh

# Count Python files
find scripts/ tests/ -name "*.py" | wc -l
# Should show 12 files

# Check documentation
ls -la docs/
ls -la *.md
```

---

## Expected File Count

- **Root directory**: 8 files
- **scripts/**: 7 Python files
- **tests/**: 5 Python files
- **docs/**: 3 Markdown files
- **config/**: 0 files initially (created by install.sh)
- **logs/**: 1 file (.gitkeep)

**Total: 24 files**

---

## Installation Order

1. ✅ Create directory structure
2. ✅ Create `requirements.txt` (CRITICAL - needed by install.sh)
3. ✅ Create `install.sh` and make executable
4. ✅ Create all Python files in `scripts/`
5. ✅ Create all Python files in `tests/`
6. ✅ Create all documentation files
7. ✅ Create supporting files (.gitignore, LICENSE, etc.)
8. ✅ Run `bash install.sh`

---

## Common File Creation Methods

### Method 1: Using nano (recommended for beginners)
```bash
nano filename
# Paste content
# Ctrl+O to save
# Ctrl+X to exit
```

### Method 2: Using cat with heredoc
```bash
cat > filename << 'EOF'
# Paste all content here
EOF
```

### Method 3: Using echo for small files
```bash
echo "content" > filename
```

### Method 4: Download from repository (if available)
```bash
git clone https://github.com/yourusername/G90-SDR.git
```

---

## File-by-File Creation Script

To automate creation, you can use this helper script:

```bash
#!/bin/bash
# create_structure.sh - Creates directory structure

cd ~
mkdir -p G90-SDR/{config,scripts,tests,docs,logs}
cd G90-SDR
touch logs/.gitkeep

echo "Directory structure created!"
echo "Now create requirements.txt:"
echo "  nano requirements.txt"
echo ""
echo "Then create each Python file in scripts/ and tests/"
echo "Then run: bash install.sh"
```

---

## Troubleshooting File Creation

### Problem: "File not found" during install
**Solution**: Check that requirements.txt exists in root directory
```bash
ls -la ~/G90-SDR/requirements.txt
```

### Problem: "Permission denied" on shell scripts
**Solution**: Make scripts executable
```bash
chmod +x ~/G90-SDR/*.sh
```

### Problem: Python import errors
**Solution**: Ensure files have correct naming and are in right directories
```bash
# Check script locations
ls ~/G90-SDR/scripts/*.py
ls ~/G90-SDR/tests/*.py
```

---

## Quick File Content Extraction

If you need to get file contents from the AI conversation, ask for specific files:

Example:
- "Show me the content of requirements.txt"
- "Give me the install.sh script"
- "What goes in rig_control.py?"

Then copy and paste into the appropriate file.

---

## After All Files Are Created

```bash
cd ~/G90-SDR

# Verify structure
echo "=== Directory Structure ==="
tree -L 2

# Verify requirements.txt
echo -e "\n=== requirements.txt ==="
cat requirements.txt

# Make scripts executable
echo -e "\n=== Making scripts executable ==="
chmod +x *.sh

# Ready to install
echo -e "\n=== Ready to Install ==="
echo "Run: bash install.sh"
```

---

**Remember: requirements.txt MUST be created before running install.sh!**
