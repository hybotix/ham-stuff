#!/usr/bin/env python3
"""
Start rigctld Server
Replaces: start-rigctld-server.bash

Provides Hamlib-compatible server on port 4533
Can optionally start FlRig if not already running
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
import shutil
import socket
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

def main():
    """Main startup routine"""
    parser = argparse.ArgumentParser(
        description='Start rigctld server for FlRig',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Assumes FlRig already running
  %(prog)s --start-flrig      # Start FlRig first
  %(prog)s --config g90-sdr   # Start FlRig with specific config
        """
    )
    parser.add_argument(
        '--start-flrig',
        action='store_true',
        help='Start FlRig before starting rigctld server'
    )
    parser.add_argument(
        '--config',
        default='g90-sdr',
        help='FlRig config directory name (default: g90-sdr)'
    )

    args = parser.parse_args()

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
    bridge_script = home_path / "flrig-rigctld-server.py"
    if not check_file_exists(bridge_script, "rigctld server script"):
        return 1

    # Check if port 4533 is already in use
    if is_port_in_use(4533):
        print("Error: Port 4533 is already in use", file=sys.stderr)
        print("       Another rigctld server may be running", file=sys.stderr)
        print("       Check with: sudo lsof -i :4533", file=sys.stderr)
        print("       Kill with: kill <PID>", file=sys.stderr)
        return 1

    # If starting FlRig, check and start it
    if args.start_flrig:
        if not check_command_exists('flrig'):
            print("       Install with: sudo apt install flrig", file=sys.stderr)
            return 1

        # Check FlRig config directory
        config_dir = home_path / ".flrig" / args.config
        if not check_directory_exists(config_dir, f"FlRig config directory '{args.config}'"):
            return 1

        # Check for required config files (warnings only)
        flrig_prefs = config_dir / "flrig.prefs"
        if not flrig_prefs.exists():
            print(f"Warning: FlRig preferences file not found: {flrig_prefs}", file=sys.stderr)
            print(f"         FlRig will use defaults and may need manual configuration", file=sys.stderr)

        print(f"Starting FlRig with config: {args.config}")
        try:
            subprocess.Popen(['flrig', '--config-dir', str(config_dir)])
            print("Waiting for FlRig to initialize...")
            import time
            time.sleep(3)
        except FileNotFoundError:
            print("Error: FlRig command not found", file=sys.stderr)
            print("       Install with: sudo apt install flrig", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"Error: Failed to start FlRig", file=sys.stderr)
            print(f"       Reason: {e}", file=sys.stderr)
            return 1
    else:
        print("Note: Assuming FlRig is already running")
        print("      Use --start-flrig to start FlRig automatically")

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
