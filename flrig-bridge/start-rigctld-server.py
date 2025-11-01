#!/usr/bin/env python3
"""
Start rigctld Server
Replaces: start-rigctld-server.bash

Provides Hamlib-compatible server on port 4533
Assumes FlRig is already running
"""

import os
import sys
import subprocess
from pathlib import Path
import shutil
from config import find_script

def check_file_exists(filepath, description):
    """Check if a file exists and is readable/executable"""
    if not filepath.exists():
        print(f"Error: {description} does not exist", file=sys.stderr)
        print(f"       Expected location: {filepath}", file=sys.stderr)
        return False
    if not filepath.is_file():
        print(f"Error: {description} exists but is not a regular file", file=sys.stderr)
        print(f"       Path: {filepath}", file=sys.stderr)
        return False
    if not os.access(filepath, os.R_OK):
        print(f"Error: {description} is not readable", file=sys.stderr)
        print(f"       Fix with: chmod +r {filepath}", file=sys.stderr)
        return False
    if not os.access(filepath, os.X_OK):
        print(f"Error: {description} is not executable", file=sys.stderr)
        print(f"       Fix with: chmod +x {filepath}", file=sys.stderr)
        return False
    return True

def main():
    """Main startup routine"""
    print("=" * 60)
    print("rigctld Server Startup")
    print("Replaces: start-rigctld-server.bash")
    print("=" * 60)
    print()

    # Get HOME from environment
    home = os.environ.get('HOME')
    if not home:
        print("Error: HOME environment variable is not set", file=sys.stderr)
        print("       This script requires HOME to be defined", file=sys.stderr)
        print("       Check with: echo $HOME", file=sys.stderr)
        return 1

    home_path = Path(home)
    if not home_path.exists():
        print(f"Error: HOME directory does not exist: {home}", file=sys.stderr)
        print(f"       This indicates a serious system configuration problem", file=sys.stderr)
        return 1

    # Check required commands
    print("Checking prerequisites...")

    # Check bridge script
    bridge_script = find_script("flrig-rigctld-server.py")
    if not bridge_script:
        print("Error: flrig-rigctld-server.py not found in any search location", file=sys.stderr)
        print("       Searched:", file=sys.stderr)
        print("         - $L_SCRIPT_DIR (if set)", file=sys.stderr)
        print("         - ~/.local/scripts", file=sys.stderr)
        print("         - ~/.local/bin", file=sys.stderr)
        print("         - ~/bin", file=sys.stderr)
        print("         - $PATH", file=sys.stderr)
        print("         - ~ (home directory)", file=sys.stderr)
        print("       Install script or set L_SCRIPT_DIR environment variable", file=sys.stderr)
        return 1

    if not check_file_exists(bridge_script, "rigctld server script"):
        return 1

    print("All prerequisites OK")
    print()

    # Start rigctld server (foreground)
    print("Starting rigctld server (foreground - Ctrl+C to stop)...")
    print("=" * 60)
    print()

    try:
        result = subprocess.run([str(bridge_script)])
        return result.returncode
    except KeyboardInterrupt:
        print("\n\nShutting down gracefully...")
        return 0
    except Exception as e:
        print(f"\nError: rigctld server failed to start", file=sys.stderr)
        print(f"       Reason: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())