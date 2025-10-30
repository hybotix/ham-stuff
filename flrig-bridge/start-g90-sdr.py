#!/usr/bin/env python3
"""
Start G90 SDR Panadapter Setup
Replaces: start-g90-sdr.bash

- FlRig for rig control
- GQRX for waterfall display
- Bridge for synchronization
"""

import os
import sys
import subprocess
import time
import shutil
from pathlib import Path

def check_command_exists(command):
    """Check if a command exists in PATH"""
    if not shutil.which(command):
        print(f"Error: Command '{command}' not found in PATH", file=sys.stderr)
        return False
    return True

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

def check_directory_exists(dirpath, description):
    """Check if a directory exists and is readable"""
    if not dirpath.exists():
        print(f"Error: {description} does not exist", file=sys.stderr)
        print(f"       Expected location: {dirpath}", file=sys.stderr)
        print(f"       Create with: mkdir -p {dirpath}", file=sys.stderr)
        return False
    if not dirpath.is_dir():
        print(f"Error: {description} exists but is not a directory", file=sys.stderr)
        print(f"       Path: {dirpath}", file=sys.stderr)
        return False
    if not os.access(dirpath, os.R_OK):
        print(f"Error: {description} is not readable", file=sys.stderr)
        print(f"       Fix with: chmod +r {dirpath}", file=sys.stderr)
        return False
    return True

def start_process(command, args, description):
    """Start a background process with error handling"""
    try:
        print(f"Starting {description}...")
        process = subprocess.Popen([command] + args)
        return process
    except FileNotFoundError:
        print(f"Error: Command '{command}' not found", file=sys.stderr)
        print(f"       Install with: sudo apt install {command}", file=sys.stderr)
        return None
    except PermissionError:
        print(f"Error: Permission denied executing '{command}'", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error: Failed to start {description}", file=sys.stderr)
        print(f"       Reason: {e}", file=sys.stderr)
        return None

def main():
    """Main startup routine"""
    print("=" * 60)
    print("G90 SDR Panadapter Setup")
    print("Replaces: start-g90-sdr.bash")
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
    if not check_command_exists('flrig'):
        print("       Install with: sudo apt install flrig", file=sys.stderr)
        return 1

    if not check_command_exists('gqrx'):
        print("       Install with: sudo apt install gqrx-sdr", file=sys.stderr)
        return 1

    # Check FlRig config directory
    config_dir = home_path / ".flrig" / "g90-sdr"
    if not check_directory_exists(config_dir, "FlRig config directory"):
        return 1

    # Check for required config files (warnings only)
    flrig_prefs = config_dir / "flrig.prefs"
    if not flrig_prefs.exists():
        print(f"Warning: FlRig preferences file not found: {flrig_prefs}", file=sys.stderr)
        print(f"         FlRig will use defaults and may need manual configuration", file=sys.stderr)

    g90_prefs = config_dir / "Xiegu-G90.prefs"
    if not g90_prefs.exists():
        print(f"Warning: G90 preferences file not found: {g90_prefs}", file=sys.stderr)
        print(f"         FlRig will need to be configured for the G90", file=sys.stderr)

    # Check bridge script
    bridge_script = home_path / "flrig-gqrx-bridge.py"
    if not check_file_exists(bridge_script, "GQRX bridge script"):
        return 1

    print("All prerequisites OK")
    print()

    # Start FlRig
    flrig_process = start_process(
        'flrig',
        ['--config-dir', str(config_dir)],
        "FlRig"
    )
    if not flrig_process:
        return 1

    print("Waiting for FlRig to initialize...")
    time.sleep(3)

    # Check if FlRig is still running
    if flrig_process.poll() is not None:
        exit_code = flrig_process.returncode
        print(f"Error: FlRig exited unexpectedly with code {exit_code}", file=sys.stderr)
        print(f"       Check FlRig configuration in: {config_dir}", file=sys.stderr)
        print(f"       Run FlRig manually to see error messages", file=sys.stderr)
        return 1

    # Start GQRX
    gqrx_process = start_process('gqrx', [], "GQRX")
    if not gqrx_process:
        print("Terminating FlRig...", file=sys.stderr)
        flrig_process.terminate()
        return 1

    print("Waiting for GQRX to initialize...")
    time.sleep(3)

    # Check if GQRX is still running
    if gqrx_process.poll() is not None:
        exit_code = gqrx_process.returncode
        print(f"Error: GQRX exited unexpectedly with code {exit_code}", file=sys.stderr)
        print(f"       Check GQRX configuration", file=sys.stderr)
        print(f"       Run GQRX manually to see error messages", file=sys.stderr)
        print("Terminating FlRig...", file=sys.stderr)
        flrig_process.terminate()
        return 1

    # Start GQRX bridge (foreground)
    print()
    print("Starting GQRX bridge (foreground - Ctrl+C to stop)...")
    print("=" * 60)
    print()

    try:
        result = subprocess.run([str(bridge_script)])
        return result.returncode
    except KeyboardInterrupt:
        print("\n\nShutting down gracefully...")
        return 0
    except Exception as e:
        print(f"\nError: GQRX bridge failed to start", file=sys.stderr)
        print(f"       Reason: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
