#!/bin/bash
# Filename: check_env.bash
# Check if L_SDR_DIR environment variable is properly set

echo "════════════════════════════════════════════════════════════════"
echo "  G90-SDR Environment Check"
echo "════════════════════════════════════════════════════════════════"
echo ""

if [ -z "$L_SDR_DIR" ]; then
    echo "✗ L_SDR_DIR is NOT set"
    echo ""
    echo "To set it, add this to your ~/.bashrc:"
    echo "  export L_SDR_DIR=\$HOME/Virtual/G90-SDR"
    echo ""
    echo "Then run:"
    echo "  source ~/.bashrc"
    echo ""
    exit 1
else
    echo "✓ L_SDR_DIR is set to: $L_SDR_DIR"
    echo ""
    
    # Check if directory exists
    if [ -d "$L_SDR_DIR" ]; then
        echo "✓ Directory exists"
        
        # Check structure
        if [ -d "$L_SDR_DIR/scripts" ] && [ -d "$L_SDR_DIR/tests" ]; then
            echo "✓ Directory structure is correct"
            echo ""
            echo "Contents:"
            ls -la "$L_SDR_DIR" | grep -E "scripts|tests|config|logs"
            echo ""
            echo "✓ Environment is properly configured!"
        else
            echo "✗ Directory structure is incorrect"
            echo "  Missing scripts/ or tests/ directory"
        fi
    else
        echo "✗ Directory does not exist: $L_SDR_DIR"
        echo ""
        echo "Please check your L_SDR_DIR setting in ~/.bashrc"
    fi
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
