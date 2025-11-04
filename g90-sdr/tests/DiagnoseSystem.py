#!/usr/bin/env python3
# Filename: tests/DiagnoseSystem.py
# Complete system health check and diagnostics

import sys
import os
import subprocess
import psutil
import socket
import serial.tools.list_ports

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from rig_control import RigControl
from frequency_sync import GQRXControl


def print_header(title: str, char: str = "="):
    """Print formatted header"""
    print("\n" + char * 60)
    print(f"  {title}")
    print(char * 60)


def check_system_info():
    """Check system information"""
    print_header("System Information")
    
    try:
        # OS info
        with open('/etc/os-release', 'r') as f:
            os_info = f.read()
            for line in os_info.split('\n'):
                if line.startswith('PRETTY_NAME'):
                    print(f"  OS: {line.split('=')[1].strip('\"')}")
        
        # Python version
        print(f"  Python: {sys.version.split()[0]}")
        
        # CPU info
        cpu_count = psutil.cpu_count()
        cpu_percent = psutil.cpu_percent(interval=1)
        print(f"  CPU: {cpu_count} cores, {cpu_percent}% usage")
        
        # Memory info
        mem = psutil.virtual_memory()
        print(f"  Memory: {mem.total / (1024**3):.1f} GB total, {mem.percent}% used")
        
        # Disk info
        disk = psutil.disk_usage('/')
        print(f"  Disk: {disk.total / (1024**3):.1f} GB total, {disk.percent}% used")
        
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def check_dependencies():
    """Check required software dependencies"""
    print_header("Software Dependencies")
    
    dependencies = {
        'flrig': 'FlRig (rig control)',
        'gqrx': 'GQRX (SDR receiver)',
        'pactl': 'PulseAudio (audio routing)',
        'python3': 'Python 3'
    }
    
    results = {}
    for cmd, desc in dependencies.items():
        try:
            result = subprocess.run(
                ['which', cmd],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                path = result.stdout.strip()
                print(f"  ✓ {desc:30} {path}")
                results[cmd] = True
            else:
                print(f"  ✗ {desc:30} NOT FOUND")
                results[cmd] = False
        except Exception as e:
            print(f"  ✗ {desc:30} Error: {e}")
            results[cmd] = False
    
    return all(results.values())


def check_python_modules():
    """Check Python module dependencies"""
    print_header("Python Module Dependencies")
    
    modules = [
        'serial',
        'sounddevice',
        'numpy',
        'psutil',
        'yaml'
    ]
    
    results = {}
    for module in modules:
        try:
            __import__(module)
            print(f"  ✓ {module}")
            results[module] = True
        except ImportError:
            print(f"  ✗ {module} - NOT INSTALLED")
            results[module] = False
    
    return all(results.values())


def check_hardware():
    """Check hardware connections"""
    print_header("Hardware Detection")
    
    # Serial ports
    ports = list(serial.tools.list_ports.comports())
    print(f"\n  Serial Ports: {len(ports)} found")
    
    de19_found = False
    for port in ports:
        print(f"\n    {port.device}")
        print(f"      Description: {port.description}")
        if 'CH340' in port.description or '1a86:7523' in port.hwid:
            print("      >>> DE-19 interface detected!")
            de19_found = True
    
    if not de19_found:
        print("\n  ⚠ DE-19 interface not detected")
        print("    Check USB connection and G90 power")
    
    # Audio devices
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        print(f"\n  Audio Devices: {len(devices)} found")
        
        for idx, device in enumerate(devices):
            if device['max_input_channels'] > 0 or device['max_output_channels'] > 0:
                print(f"    [{idx}] {device['name']}")
    except Exception as e:
        print(f"\n  ✗ Error detecting audio devices: {e}")
    
    return de19_found


def check_processes():
    """Check for running processes"""
    print_header("Running Processes")
    
    processes_to_check = ['flrig', 'gqrx']
    results = {}
    
    for proc_name in processes_to_check:
        found = False
        for proc in psutil.process_iter(['name', 'pid']):
            try:
                if proc_name in proc.info['name'].lower():
                    print(f"  ✓ {proc_name:10} running (PID: {proc.info['pid']})")
                    found = True
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        if not found:
            print(f"  ○ {proc_name:10} not running")
        
        results[proc_name] = found
    
    return results


def check_network_services():
    """Check network services"""
    print_header("Network Services")
    
    services = {
        'FlRig XML-RPC': ('127.0.0.1', 12345),
        'GQRX Remote': ('127.0.0.1', 7356)
    }
    
    results = {}
    for name, (host, port) in services.items():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                print(f"  ✓ {name:20} listening on {host}:{port}")
                results[name] = True
            else:
                print(f"  ✗ {name:20} not reachable at {host}:{port}")
                results[name] = False
        except Exception as e:
            print(f"  ✗ {name:20} Error: {e}")
            results[name] = False
    
    return all(results.values())


def check_flrig_connection():
    """Test FlRig connection"""
    print_header("FlRig Connection Test")
    
    rig = RigControl()
    if rig.connect():
        info = rig.get_info()
        print(f"  ✓ Connected to FlRig")
        print(f"    Transceiver: {info.get('xcvr', 'Unknown')}")
        print(f"    Frequency: {info.get('frequency', 0) / 1e6:.6f} MHz")
        print(f"    Mode: {info.get('mode', 'Unknown')}")
        rig.disconnect()
        return True
    else:
        print(f"  ✗ Could not connect to FlRig")
        return False


def check_gqrx_connection():
    """Test GQRX connection"""
    print_header("GQRX Connection Test")
    
    gqrx = GQRXControl()
    if gqrx.connect():
        freq = gqrx.get_frequency()
        print(f"  ✓ Connected to GQRX")
        if freq:
            print(f"    Current Frequency: {freq / 1e6:.6f} MHz")
        gqrx.disconnect()
        return True
    else:
        print(f"  ✗ Could not connect to GQRX")
        return False


def check_permissions():
    """Check file and device permissions"""
    print_header("Permission Check")
    
    import pwd
    import grp
    
    username = pwd.getpwuid(os.getuid()).pw_name
    user_groups = [g.gr_name for g in grp.getgrall() if username in g.gr_mem]
    
    print(f"  User: {username}")
    print(f"  Groups: {', '.join(user_groups)}")
    
    required_groups = ['dialout', 'audio']
    missing = [g for g in required_groups if g not in user_groups]
    
    if missing:
        print(f"\n  ⚠ Missing group memberships: {', '.join(missing)}")
        return False
    else:
        print(f"\n  ✓ All required group memberships present")
        return True


def generate_report():
    """Generate diagnostic report"""
    print("\n" + "█" * 60)
    print("  G90-SDR System Diagnostic Report")
    print("  Version 1.0")
    print("█" * 60)
    
    results = {}
    
    # Run all checks
    results['system'] = check_system_info()
    results['dependencies'] = check_dependencies()
    results['python_modules'] = check_python_modules()
    results['hardware'] = check_hardware()
    results['permissions'] = check_permissions()
    
    process_status = check_processes()
    results['services'] = check_network_services()
    
    # Only test connections if processes are running
    if process_status.get('flrig', False):
        results['flrig'] = check_flrig_connection()
    else:
        results['flrig'] = None
    
    if process_status.get('gqrx', False):
        results['gqrx'] = check_gqrx_connection()
    else:
        results['gqrx'] = None
    
    # Summary
    print_header("Diagnostic Summary", char="█")
    
    print("\n  Core System:")
    for check in ['system', 'dependencies', 'python_modules', 'hardware', 'permissions']:
        status = "✓ PASS" if results[check] else "✗ FAIL"
        print(f"    {check.replace('_', ' ').title():20} {status}")
    
    print("\n  Services:")
    for check in ['services', 'flrig', 'gqrx']:
        result = results[check]
        if result is None:
            status = "⊘ SKIP (not running)"
        elif result:
            status = "✓ PASS"
        else:
            status = "✗ FAIL"
        print(f"    {check.upper():20} {status}")
    
    # Count results
    total = sum(1 for v in results.values() if v is not None)
    passed = sum(1 for v in results.values() if v is True)
    
    print(f"\n  Overall Status: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n  🎉 System is healthy and ready!")
        return 0
    else:
        print("\n  ⚠ Some issues detected. Please review above.")
        
        print("\n  Common Solutions:")
        if not results['dependencies']:
            print("    - Install missing software with: sudo apt install <package>")
        if not results['python_modules']:
            print("    - Install Python modules with: pip install -r requirements.txt")
        if not results['hardware']:
            print("    - Check USB connection and G90 power")
        if not results['permissions']:
            print("    - Add user to groups and reboot")
        
        return 1


def main():
    """Run complete system diagnosis"""
    try:
        return generate_report()
    except KeyboardInterrupt:
        print("\n\nDiagnostic cancelled by user")
        return 1
    except Exception as e:
        print(f"\n\nFatal error during diagnosis: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
