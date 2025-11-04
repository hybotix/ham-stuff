#!/bin/bash
# Filename: make_executable.bash
# Make all Python scripts and shell scripts executable

# Use L_SDR_DIR environment variable or fall back to script location
if [ -n "$L_SDR_DIR" ]; then
    SCRIPT_DIR="$L_SDR_DIR"
else
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
fi

cd "$SCRIPT_DIR" || exit 1

echo "Working directory: $SCRIPT_DIR"
echo "Making all scripts executable..."
echo ""

# Make shell scripts executable
echo "Shell scripts:"
if ls *.bash 1> /dev/null 2>&1; then
    chmod +x *.bash
    for script in *.bash; do
        if [ -f "$script" ]; then
            echo "  ✓ $script"
        fi
    done
fi

# Also check for .sh files (legacy)
if ls *.sh 1> /dev/null 2>&1; then
    chmod +x *.sh
    for script in *.sh; do
        if [ -f "$script" ]; then
            echo "  ✓ $script"
        fi
    done
fi

# Make Python scripts executable in scripts/
echo ""
echo "Python scripts in scripts/:"
if [ -d "scripts" ]; then
    if ls scripts/*.py 1> /dev/null 2>&1; then
        chmod +x scripts/*.py
        for script in scripts/*.py; do
            if [ -f "$script" ]; then
                echo "  ✓ $(basename $script)"
            fi
        done
    else
        echo "  No Python scripts found in scripts/"
    fi
else
    echo "  scripts/ directory not found"
fi

# Make Python scripts executable in tests/
echo ""
echo "Python scripts in tests/:"
if [ -d "tests" ]; then
    if ls tests/*.py 1> /dev/null 2>&1; then
        chmod +x tests/*.py
        for script in tests/*.py; do
            if [ -f "$script" ]; then
                echo "  ✓ $(basename $script)"
            fi
        done
    else
        echo "  No Python scripts found in tests/"
    fi
else
    echo "  tests/ directory not found"
fi

echo ""
echo "✓ All scripts are now executable"
echo ""
echo "You can now run scripts directly:"
echo "  ./scripts/start_sdr.py"
echo "  ./tests/TestConnection.py"
echo "  etc."
