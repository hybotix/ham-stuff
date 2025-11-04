#!/bin/bash
# Filename: fix_all.bash
# Simple permission fixer - no fancy stuff

# Use L_SDR_DIR environment variable or fall back to script location
if [ -n "$L_SDR_DIR" ]; then
    SCRIPT_DIR="$L_SDR_DIR"
else
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
fi

cd "$SCRIPT_DIR"

echo "Working in: $SCRIPT_DIR"
echo "Fixing all permissions..."

# Root directory shell scripts
chmod +x *.sh 2>/dev/null
echo "✓ Root .sh files"

# All Python in scripts/
chmod +x scripts/*.py 2>/dev/null
echo "✓ scripts/*.py files"

# All Python in tests/
chmod +x tests/*.py 2>/dev/null
echo "✓ tests/*.py files"

echo ""
echo "Done! Listing files:"
echo ""
echo "Root scripts:"
ls -lh *.sh 2>/dev/null | awk '{print $1, $9}'

echo ""
echo "scripts/ directory:"
ls -lh scripts/*.py 2>/dev/null | awk '{print $1, $9}'

echo ""
echo "tests/ directory:"
ls -lh tests/*.py 2>/dev/null | awk '{print $1, $9}'

echo ""
echo "If you see 'rwx' in the permissions, they are executable."
