#!/usr/bin/env python3
"""
Complete Ham Radio Station Setup
Replaces: start-ham-radio-setup.bash

Starts everything: FlRig, GQRX, both bridges
- GQRX panadapter with sync
- rigctld server for other software
"""

import os
import sys
import subprocess
import time
import argparse
import shutil
import socket
from pathlib import Path
from config import find_script, get_flrig_config_dir

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

def is_port_in_use(port):
    """Check if a port is already in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('127.0.0.1', port))
            return False
        except OSError:
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

def cleanup_processes(processes):
    """Terminate all background processes"""
    for name, process in processes.items():
        if process and process.poll() is None:
            print(f"Terminating {name}...")
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print(f"Force killing {name}...")
                process.kill()
            except Exception as e:
                print(f"Warning: Error terminating {name}: {e}", file=sys.stderr)

def main():
    """Main startup routine"""
    parser = argparse.ArgumentParser(
        description='Start complete ham radio station setup',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This script starts:
  - FlRig (rig control)
  - GQRX (SDR panadapter)
  - GQRX bridge (synchronization)
  - rigctld server (for other software)

Example:
  %(prog)s --config g90-sdr
        """
    )
    parser.add_argument(
        '--config',
        default='g90-sdr',
        help='FlRig config directory name (default: g90-sdr)'
    )

    args = parser.parse_args()

    print("=" * 60)
    print("Complete Ham Radio Station Setup")
    print("Replaces: start-ham-radio-setup.bash")
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

    commands_needed = ['flrig', 'gqrx']
    for cmd in commands_needed:
        if not check_command_exists(cmd):
            if cmd == 'flrig':
                print("       Install with: sudo apt install flrig", file=sys.stderr)
            elif cmd == 'gqrx':
                print("       Install with: sudo apt install gqrx-sdr", file=sys.stderr)
            return 1

    # Check FlRig config directory
    config_dir = get_flrig_config_dir(args.config)
    if not check_directory_exists(config_dir, f"FlRig config directory '{args.config}'"):
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

    # Check bridge scripts
    gqrx_bridge = find_script("flrig-gqrx-bridge.py")
    if not gqrx_bridge:
        print("Error: flrig-gqrx-bridge.py not found in any search location", file=sys.stderr)
        print("       Searched $L_SCRIPT_DIR, ~/.local/scripts, $PATH, etc.", file=sys.stderr)
        return 1

    if not check_file_exists(gqrx_bridge, "GQRX bridge script"):
        return 1

    rigctld_server = find_script("flrig-rigctld-server.py")
    if not rigctld_server:
        print("Error: flrig-rigctld-server.py not found in any search location", file=sys.stderr)
        print("       Searched $L_SCRIPT_DIR, ~/.local/scripts, $PATH, etc.", file=sys.stderr)
        return 1

    if not check_file_exists(rigctld_server, "rigctld server script"):
        return 1

    # Check if port 4533 is already in use
    if is_port_in_use(4533):
        print("Error: Port 4533 is already in use", file=sys.stderr)
        print("       Another rigctld server may be running", file=sys.stderr)
        print("       Check with: sudo lsof -i :4533", file=sys.stderr)
        print("       Kill with: kill <PID>", file=sys.stderr)
        return 1

    print("All prerequisites OK")
    print()

    # Track all background processes for cleanup
    processes = {}

    try:
        # Start FlRig
        flrig_process = start_process(
            'flrig',
            ['--config-dir', str(config_dir)],
            "FlRig"
        )
        if not flrig_process:
            return 1
        processes['FlRig'] = flrig_process

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
            raise RuntimeError("Failed to start GQRX")
        processes['GQRX'] = gqrx_process

        print("Waiting for GQRX to initialize...")
        time.sleep(3)

        # Check if GQRX is still running
        if gqrx_process.poll() is not None:
            exit_code = gqrx_process.returncode
            print(f"Error: GQRX exited unexpectedly with code {exit_code}", file=sys.stderr)
            print(f"       Check GQRX configuration", file=sys.stderr)
            print(f"       Run GQRX manually to see error messages", file=sys.stderr)
            raise RuntimeError("GQRX failed to start")

        # Start GQRX bridge (background)
        print("Starting GQRX bridge...")
        bridge_process = start_process(
            str(gqrx_bridge),
            [],
            "GQRX bridge"
        )
        if not bridge_process:
            raise RuntimeError("Failed to start GQRX bridge")
        processes['GQRX bridge'] = bridge_process

        print("Waiting for GQRX bridge to initialize...")
        time.sleep(2)

        # Check if bridge is still running
        if bridge_process.poll() is not None:
            exit_code = bridge_process.returncode
            print(f"Error: GQRX bridge exited unexpectedly with code {exit_code}", file=sys.stderr)
            print(f"       Check bridge script: {gqrx_bridge}", file=sys.stderr)
            print(f"       Run bridge manually to see error messages", file=sys.stderr)
            raise RuntimeError("GQRX bridge failed to start")

        # Start rigctld server (foreground)
        print()
        print("Starting rigctld server (foreground - Ctrl+C to stop all)...")
        print("=" * 60)
        print()

        result = subprocess.run([str(rigctld_server)])
        return result.returncode

    except KeyboardInterrupt:
        print("\n\nShutting down gracefully...")
        cleanup_processes(processes)
        return 0

    except Exception as e:
        print(f"\nError: Setup failed", file=sys.stderr)
        print(f"       Reason: {e}", file=sys.stderr)
        print("Cleaning up background processes...", file=sys.stderr)
        cleanup_processes(processes)
        return 1

if __name__ == "__main__":
    sys.exit(main())