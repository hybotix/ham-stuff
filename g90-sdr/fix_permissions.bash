#!/bin/bash
# Filename: fix_permissions.bash
# Comprehensive permission fixing for all G90-SDR files

set -e

# Use L_SDR_DIR environment variable or fall back to script location
if [ -n "$L_SDR_DIR" ]; then
    SCRIPT_DIR="$L_SDR_DIR"
else
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
fi

cd "$SCRIPT_DIR" || { echo "Error: Could not cd to $SCRIPT_DIR"; exit 1; }

echo "════════════════════════════════════════════════════════════════"
echo "  G90-SDR Permission Fixer"
echo "  Working in: $SCRIPT_DIR"
echo "════════════════════════════════════════════════════════════════"
echo ""

COUNT=0

# Fix all shell scripts
echo "[1] Shell Scripts (.sh):"
echo "────────────────────────────────────────────────────────────────"
while IFS= read -r -d '' file; do
    chmod +x "$file"
    echo "  ✓ $file"
    ((COUNT++))
done < <(find . -maxdepth 1 -type f -name "*.sh" -print0)

if [ $COUNT -eq 0 ]; then
    echo "  No .sh files found in root"
fi

# Fix all Python scripts in scripts/
echo ""
echo "[2] Python Scripts in scripts/:"
echo "────────────────────────────────────────────────────────────────"
COUNT=0
if [ -d "scripts" ]; then
    while IFS= read -r -d '' file; do
        chmod +x "$file"
        echo "  ✓ $(basename $file)"
        ((COUNT++))
    done < <(find scripts/ -type f -name "*.py" -print0)
    
    if [ $COUNT -eq 0 ]; then
        echo "  No .py files found in scripts/"
    fi
else
    echo "  scripts/ directory not found"
fi

# Fix all Python scripts in tests/
echo ""
echo "[3] Python Scripts in tests/:"
echo "────────────────────────────────────────────────────────────────"
COUNT=0
if [ -d "tests" ]; then
    while IFS= read -r -d '' file; do
        chmod +x "$file"
        echo "  ✓ $(basename $file)"
        ((COUNT++))
    done < <(find tests/ -type f -name "*.py" -print0)
    
    if [ $COUNT -eq 0 ]; then
        echo "  No .py files found in tests/"
    fi
else
    echo "  tests/ directory not found"
fi

# Verify permissions
echo ""
echo "[4] Verification:"
echo "────────────────────────────────────────────────────────────────"

EXEC_COUNT=$(find . -type f \( -name "*.py" -o -name "*.sh" \) -executable | wc -l)
TOTAL_COUNT=$(find . -type f \( -name "*.py" -o -name "*.sh" \) | wc -l)

echo "  Executable scripts: $EXEC_COUNT"
echo "  Total scripts:      $TOTAL_COUNT"

if [ "$EXEC_COUNT" -eq "$TOTAL_COUNT" ]; then
    echo "  ✓ All scripts are executable"
else
    echo "  ⚠ Some scripts may not be executable"
fi

# Show summary by directory
echo ""
echo "[5] Summary by Directory:"
echo "────────────────────────────────────────────────────────────────"

for dir in . scripts tests; do
    if [ -d "$dir" ]; then
        count=$(find "$dir" -maxdepth 1 -type f \( -name "*.py" -o -name "*.sh" \) -executable | wc -l)
        total=$(find "$dir" -maxdepth 1 -type f \( -name "*.py" -o -name "*.sh" \) | wc -l)
        echo "  $dir: $count/$total executable"
    fi
done

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  ✓ Permission fix complete!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "You can now run scripts directly:"
echo "  ./scripts/start_sdr.py"
echo "  ./scripts/safe_start.py"
echo "  ./tests/TestConnection.py"
echo "  ./tests/DiagnoseCrash.py"
echo ""
