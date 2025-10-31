#!/usr/bin/env python3
"""
Universal Application Launcher
Launch any ham radio application with optional FlRig and bridge support

Can be used as a template for specific application launchers
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

def start_process(command, args, description, foreground=False):
    """Start a process with error handling"""
    try:
        print(f"Starting {description}...")
        if foreground:
            return subprocess.run([command] + args)
        else:
            return subprocess.Popen([command] + args)
    except FileNotFoundError:
        print(f"Error: Command '{command}' not found", file=sys.stderr)
        print(f"       Check if it's installed", file=sys.stderr)
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
        if process and hasattr(process, 'poll') and process.poll() is None:
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
    """Main launcher routine"""
    parser = argparse.ArgumentParser(
        description='Universal ham radio application launcher',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Launch app only (assumes FlRig/bridges already running)
  %(prog)s --app wsjt-x

  # Launch with FlRig
  %(prog)s --app fldigi --start-flrig --config g90-sdr

  # Launch with FlRig and rigctld bridge
  %(prog)s --app fldigi --start-flrig --start-bridge --config g90-sdr

  # Launch app in foreground (wait for it to exit)
  %(prog)s --app wsjt-x --foreground

  # Pass arguments to the application
  %(prog)s --app gqrx --app-args "--help"
        """
    )

    # Application options
    parser.add_argument(
        '--app',
        required=True,
        help='Application command to launch (e.g., wsjt-x, fldigi, gqrx)'
    )
    parser.add_argument(
        '--app-args',
        default='',
        help='Arguments to pass to the application (quote if multiple)'
    )
    parser.add_argument(
        '--foreground',
        action='store_true',
        help='Run application in foreground (wait for exit)'
    )

    # FlRig options
    parser.add_argument(
        '--start-flrig',
        action='store_true',
        help='Start FlRig before launching application'
    )
    parser.add_argument(
        '--config',
        default='g90-sdr',
        help='FlRig config directory name (default: g90-sdr)'
    )
    parser.add_argument(
        '--flrig-delay',
        type=int,
        default=3,
        help='Seconds to wait for FlRig to initialize (default: 3)'
    )

    # Bridge options
    parser.add_argument(
        '--start-bridge',
        action='store_true',
        help='Start rigctld bridge (requires --start-flrig or FlRig running)'
    )
    parser.add_argument(
        '--bridge-delay',
        type=int,
        default=2,
        help='Seconds to wait for bridge to initialize (default: 2)'
    )

    args = parser.parse_args()

    print("=" * 60)
    print("Universal Application Launcher")
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

    # Check if application exists
    if not check_command_exists(args.app):
        print(f"       Application '{args.app}' not found", file=sys.stderr)
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

            print(f"Waiting {args.flrig_delay} seconds for FlRig to initialize...")
            time.sleep(args.flrig_delay)

            # Check if FlRig is still running
            if flrig_process.poll() is not None:
                exit_code = flrig_process.returncode
                print(f"Error: FlRig exited unexpectedly with code {exit_code}", file=sys.stderr)
                print(f"       Check FlRig configuration in: {config_dir}", file=sys.stderr)
                return 1

        # Start rigctld bridge if requested
        if args.start_bridge:
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

            print(f"Waiting {args.bridge_delay} seconds for bridge to initialize...")
            time.sleep(args.bridge_delay)

            # Check if bridge is still running
            if bridge_process.poll() is not None:
                exit_code = bridge_process.returncode
                print(f"Error: Bridge exited unexpectedly with code {exit_code}", file=sys.stderr)
                raise RuntimeError("Bridge failed to start")

        print("All prerequisites OK")
        print()

        # Parse application arguments
        app_args_list = args.app_args.split() if args.app_args else []

        # Launch the application
        print(f"Launching {args.app}...")
        if args.app_args:
            print(f"  with arguments: {args.app_args}")
        print("=" * 60)
        print()

        app_result = start_process(
            args.app,
            app_args_list,
            args.app,
            foreground=args.foreground
        )

        if not app_result:
            raise RuntimeError(f"Failed to start {args.app}")

        # If foreground, wait for app to exit
        if args.foreground:
            return app_result.returncode
        else:
            print(f"{args.app} started successfully")
            if processes:
                print("\nBackground processes running:")
                for name in processes.keys():
                    print(f"  - {name}")
                print("\nNote: Background processes will continue after this script exits")
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
