#!/usr/bin/env python3
"""
Configuration helper for FlRig Bridge System
Handles environment variables and fallback paths
"""

import os
import sys
import shutil
from pathlib import Path

def get_script_dir():
    """
    Get script directory with intelligent fallback
    
    Priority:
    1. L_SCRIPT_DIR environment variable
    2. Common installation locations
    3. Current user's home directory
    """
    # First priority: explicit environment variable
    script_dir = os.environ.get('L_SCRIPT_DIR')
    if script_dir:
        path = Path(script_dir)
        if path.exists() and path.is_dir():
            return path
        else:
            print(f"Warning: L_SCRIPT_DIR set to '{script_dir}' but path doesn't exist", file=sys.stderr)
    
    # Second priority: common installation locations
    fallback_paths = [
        Path.home() / ".local" / "scripts",
        Path.home() / ".local" / "bin",
        Path.home() / "bin",
        Path.home(),
    ]
    
    for path in fallback_paths:
        if path.exists() and path.is_dir():
            return path
    
    # Last resort: home directory
    return Path.home()

def find_script(script_name):
    """
    Find a script file intelligently
    
    Search order:
    1. L_SCRIPT_DIR environment variable
    2. Common script directories
    3. Directories in $PATH
    4. Current directory
    
    Args:
        script_name: Name of the script to find (e.g., 'flrig-gqrx-bridge.py')
    
    Returns:
        Path object if found, None otherwise
    """
    # Priority 1: L_SCRIPT_DIR environment variable
    script_dir = os.environ.get('L_SCRIPT_DIR')
    if script_dir:
        script_path = Path(script_dir) / script_name
        if script_path.exists() and script_path.is_file():
            return script_path
    
    # Priority 2: Common script locations
    common_paths = [
        Path.home() / ".local" / "scripts",
        Path.home() / ".local" / "bin",
        Path.home() / "bin",
        Path.home(),
    ]
    
    for directory in common_paths:
        script_path = directory / script_name
        if script_path.exists() and script_path.is_file():
            return script_path
    
    # Priority 3: Search $PATH
    # Use shutil.which() which searches PATH for executables
    found_in_path = shutil.which(script_name)
    if found_in_path:
        return Path(found_in_path)
    
    # Priority 4: Current directory (last resort)
    script_path = Path.cwd() / script_name
    if script_path.exists() and script_path.is_file():
        return script_path
    
    # Not found anywhere
    return None

def get_config_dir():
    """
    Get configuration directory
    
    Priority:
    1. L_CONFIG_DIR environment variable
    2. XDG_CONFIG_HOME environment variable
    3. ~/.config (standard)
    """
    # First priority: explicit environment variable
    config_dir = os.environ.get('L_CONFIG_DIR')
    if config_dir:
        path = Path(config_dir)
        if path.exists() and path.is_dir():
            return path
    
    # Second priority: XDG standard
    xdg_config = os.environ.get('XDG_CONFIG_HOME')
    if xdg_config:
        path = Path(xdg_config)
        if path.exists() and path.is_dir():
            return path
    
    # Default: ~/.config
    return Path.home() / ".config"

def get_flrig_config_dir(config_name="g90-sdr"):
    """
    Get FlRig configuration directory for a specific config
    
    Args:
        config_name: Name of the FlRig configuration (default: g90-sdr)
    
    Returns:
        Path to FlRig config directory
    """
    base_config = get_config_dir()
    return base_config.parent / ".flrig" / config_name

def get_share_dir():
    """
    Get share/data directory
    
    Priority:
    1. L_SHARE_DIR environment variable
    2. XDG_DATA_HOME environment variable
    3. ~/.local/share (standard)
    """
    # First priority: explicit environment variable
    share_dir = os.environ.get('L_SHARE_DIR')
    if share_dir:
        path = Path(share_dir)
        if path.exists() and path.is_dir():
            return path
    
    # Second priority: XDG standard
    xdg_data = os.environ.get('XDG_DATA_HOME')
    if xdg_data:
        path = Path(xdg_data)
        if path.exists() and path.is_dir():
            return path
    
    # Default: ~/.local/share
    return Path.home() / ".local" / "share"

def get_usb_port():
    """
    Get USB serial port for rig connection
    
    Priority:
    1. USB_PORT environment variable
    2. Common default (/dev/ttyUSB0)
    """
    usb_port = os.environ.get('USB_PORT')
    if usb_port:
        return usb_port
    
    # Default
    return '/dev/ttyUSB0'

# Convenience function for validation
def validate_environment():
    """
    Validate environment and print useful information
    Returns True if everything looks good
    """
    import sys
    
    issues = []
    
    # Check script directory
    script_dir = get_script_dir()
    if not script_dir.exists():
        issues.append(f"Script directory does not exist: {script_dir}")
    
    # Check config directory
    config_dir = get_config_dir()
    if not config_dir.exists():
        issues.append(f"Config directory does not exist: {config_dir}")
    
    if issues:
        print("Environment validation found issues:", file=sys.stderr)
        for issue in issues:
            print(f"  - {issue}", file=sys.stderr)
        return False
    
    return True

def print_environment_info():
    """Print current environment configuration"""
    print("FlRig Bridge System Configuration:")
    print(f"  Script Directory: {get_script_dir()}")
    print(f"  Config Directory: {get_config_dir()}")
    print(f"  Share Directory:  {get_share_dir()}")
    print(f"  USB Port:         {get_usb_port()}")
    print()
    print("Environment Variables (if set):")
    env_vars = ['L_SCRIPT_DIR', 'L_CONFIG_DIR', 'L_SHARE_DIR', 'USB_PORT']
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            print(f"  {var} = {value}")
        else:
            print(f"  {var} = (not set)")

if __name__ == "__main__":
    # Test/debug mode
    import sys
    print_environment_info()
    print()
    
    # Test script finding
    test_scripts = [
        'flrig-gqrx-bridge.py',
        'flrig-rigctld-server.py',
        'start-g90-sdr.py',
    ]
    
    print("Script Search Results:")
    for script in test_scripts:
        found = find_script(script)
        if found:
            print(f"  ✓ {script}: {found}")
        else:
            print(f"  ✗ {script}: NOT FOUND")
