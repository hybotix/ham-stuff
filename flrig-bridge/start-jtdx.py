#!/usr/bin/env python3
"""
Start JTDX
Launch JTDX with optional FlRig and bridge support

JTDX can connect to FlRig directly or use the rigctld bridge
"""

import os
import sys
import subprocess
import argparse
import time
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
        description='Start JTDX with optional FlRig and bridge',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                              # Launch JTDX only
  %(prog)s --start-flrig                # Launch with FlRig
  %(prog)s --start-flrig --start-bridge # Launch with FlRig and rigctld bridge
  %(prog)s --config g90-portable        # Use different config

Note: JTDX can use FlRig directly (recommended) or connect to rigctld bridge
      Configure rig control in JTDX settings
        """
    )

    parser.add_argument(
        '--start-flrig',
        action='store_true',
        help='Start FlRig before launching JTDX'
    )
    parser.add_argument(
        '--config',
        default='g90-sdr',
        help='FlRig config directory name (default: g90-sdr)'
    )
    parser.add_argument(
        '--start-bridge',
        action='store_true',
        help='Start rigctld bridge (for Hamlib compatibility)'
    )

    args = parser.parse_args()

    print("=" * 60)
    print("JTDX Launcher")
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

    # Check prerequisites
    print("Checking prerequisites...")

    if not check_command_exists('jtdx'):
        print("       JTDX not found", file=sys.stderr)
        print("       Install from: https://jtdx.tech/", file=sys.stderr)
        return 1

    # Track background processes for cleanup
    processes = {}

    try:
        # Start FlRig if requested
        if args.start_flrig:
            if not check_command_exists('flrig'):
                print("       Install with: sudo apt install flrig", file=sys.stderr)
                return 1

            # Check FlRig config directory
            config_dir = home_path / ".flrig" / args.config
            if not check_directory_exists(config_dir, f"FlRig config directory '{args.config}'"):
                return 1

            # Check for config files (warnings only)
            flrig_prefs = config_dir / "flrig.prefs"
            if not flrig_prefs.exists():
                print(f"Warning: FlRig preferences file not found: {flrig_prefs}", file=sys.stderr)
                print(f"         FlRig will use defaults and may need manual configuration", file=sys.stderr)

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
                return 1

        # Start rigctld bridge if requested
        if args.start_bridge:
            if not args.start_flrig:
                print("Warning: --start-bridge requires FlRig to be running", file=sys.stderr)
                print("         Use --start-flrig or start FlRig manually", file=sys.stderr)

            # Check if port is available
            if is_port_in_use(4533):
                print("Error: Port 4533 is already in use", file=sys.stderr)
                print("       Another rigctld server may be running", file=sys.stderr)
                print("       Check with: sudo lsof -i :4533", file=sys.stderr)
                raise RuntimeError("Port conflict")

            bridge_script = home_path / "flrig-rigctld-server.py"
            if not check_file_exists(bridge_script, "rigctld server script"):
                raise RuntimeError("Bridge script not found")

            bridge_process = start_process(
                str(bridge_script),
                [],
                "rigctld bridge"
            )
            if not bridge_process:
                raise RuntimeError("Failed to start bridge")
            processes['rigctld bridge'] = bridge_process

            print("Waiting for bridge to initialize...")
            time.sleep(2)

            # Check if bridge is still running
            if bridge_process.poll() is not None:
                exit_code = bridge_process.returncode
                print(f"Error: Bridge exited unexpectedly with code {exit_code}", file=sys.stderr)
                raise RuntimeError("Bridge failed to start")

        print("All prerequisites OK")
        print()

        # Launch JTDX
        print("Launching JTDX...")
        print("=" * 60)
        print()
        print("Configure rig control in JTDX:")
        if args.start_flrig and not args.start_bridge:
            print("  - Radio: Flrig")
            print("  - Network Server: 127.0.0.1:12345")
        elif args.start_bridge:
            print("  - Radio: Hamlib NET rigctl")
            print("  - Network Server: 127.0.0.1:4533")
        print()

        jtdx_process = start_process('jtdx', [], "JTDX")
        if not jtdx_process:
            raise RuntimeError("Failed to start JTDX")

        print("JTDX started successfully")
        if processes:
            print("\nBackground processes running:")
            for name in processes.keys():
                print(f"  - {name}")
            print("\nNote: Close JTDX to stop this script")

        # Wait for JTDX to exit
        jtdx_process.wait()
        print("\nJTDX exited")

        return 0

    except KeyboardInterrupt:
        print("\n\nShutting down gracefully...")
        cleanup_processes(processes)
        return 0

    except Exception as e:
        print(f"\nError: Launcher failed", file=sys.stderr)
        print(f"       Reason: {e}", file=sys.stderr)
        if processes:
            print("Cleaning up background processes...", file=sys.stderr)
            cleanup_processes(processes)
        return 1

if __name__ == "__main__":
    sys.exit(main())
