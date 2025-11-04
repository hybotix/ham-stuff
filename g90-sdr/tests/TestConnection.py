#!/usr/bin/env python3
# Filename: tests/TestConnection.py
# Verify DE-19 and G90 connectivity

import sys
import os
import serial
import serial.tools.list_ports
import time

# Add parent directory to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from rig_control import RigControl


def print_header(title: str):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_usb_devices():
    """Test for USB device presence"""
    print_header("USB Device Detection")
    
    ports = list(serial.tools.list_ports.comports())
    
    if not ports:
        print("✗ No serial devices found")
        return False
    
    print(f"✓ Found {len(ports)} serial device(s):")
    
    de19_found = False
    for port in ports:
        print(f"\n  Port: {port.device}")
        print(f"  Description: {port.description}")
        print(f"  Hardware ID: {port.hwid}")
        
        # Check for CH340 (DE-19 uses this chip)
        # Also check for various CH34x variants and QinHeng Electronics
        if any(keyword in str(port.description).upper() for keyword in ['CH340', 'CH341', 'QINHENG', 'HL-340']):
            print("  >>> This appears to be the DE-19 interface!")
            de19_found = True
        elif '1a86:7523' in str(port.hwid).lower() or '1a86:7523' in str(port.hwid):
            print("  >>> This appears to be the DE-19 interface!")
            de19_found = True
        elif 'USB' in str(port.description).upper() and 'SERIAL' in str(port.description).upper():
            print("  >>> This could be the DE-19 interface (USB-Serial adapter)")
            de19_found = True
    
    if not de19_found:
        print("\n  ⚠ Note: DE-19 not specifically identified, but serial port exists")
        print("  This is OK if FlRig can connect to the radio")
        # Return True anyway since we have a working serial port
        return True
    
    return de19_found


def test_serial_connection(port: str = '/dev/ttyUSB0', baud: int = 19200):
    """Test serial port connection"""
    print_header(f"Serial Port Test: {port}")
    
    try:
        # Try to open serial port
        ser = serial.Serial(
            port=port,
            baudrate=baud,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1.0
        )
        
        print(f"✓ Successfully opened {port} at {baud} baud")
        print(f"  Settings: {ser}")
        
        # Send a test command (Kenwood/ICOM style frequency query)
        print("\n  Sending test command (FA;)...")
        ser.write(b'FA;')
        time.sleep(0.1)
        
        # Try to read response
        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting)
            print(f"  ✓ Received response: {response}")
        else:
            print("  ⚠ No response received (radio may be off or not in CAT mode)")
        
        ser.close()
        return True
        
    except serial.SerialException as e:
        print(f"✗ Could not open serial port: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


def test_flrig_connection():
    """Test FlRig connection"""
    print_header("FlRig Connection Test")
    
    rig = RigControl()
    
    print("  Attempting to connect to FlRig at 127.0.0.1:12345...")
    
    if rig.connect():
        print("  ✓ Successfully connected to FlRig")
        
        # Get rig info
        info = rig.get_info()
        print(f"\n  Transceiver: {info.get('xcvr', 'Unknown')}")
        print(f"  Frequency: {info.get('frequency', 0) / 1e6:.6f} MHz")
        print(f"  Mode: {info.get('mode', 'Unknown')}")
        
        rig.disconnect()
        return True
    else:
        print("  ✗ Could not connect to FlRig")
        print("\n  Troubleshooting:")
        print("    1. Make sure FlRig is running")
        print("    2. Check that FlRig is configured for Xiegu G90")
        print("    3. Verify XML-RPC server is enabled (port 12345)")
        print("    4. Ensure G90 is powered on and connected")
        return False


def test_permissions():
    """Test serial port permissions"""
    print_header("Permission Check")
    
    import grp
    import pwd
    
    username = pwd.getpwuid(os.getuid()).pw_name
    print(f"  Current user: {username}")
    
    # Check dialout group membership
    try:
        dialout_group = grp.getgrnam('dialout')
        user_groups = [g.gr_name for g in grp.getgrall() if username in g.gr_mem]
        
        if 'dialout' in user_groups:
            print("  ✓ User is in 'dialout' group")
            return True
        else:
            print("  ✗ User is NOT in 'dialout' group")
            print("\n  To fix this, run:")
            print(f"    sudo usermod -a -G dialout {username}")
            print("    sudo reboot")
            return False
    except KeyError:
        print("  ⚠ 'dialout' group not found on this system")
        return True


def main():
    """Run all connection tests"""
    print("\n" + "█" * 60)
    print("  G90-SDR Connection Test Suite")
    print("  Version 1.0")
    print("█" * 60)
    
    results = {}
    
    # Test 1: USB devices
    results['usb'] = test_usb_devices()
    time.sleep(1)
    
    # Test 2: Permissions
    results['permissions'] = test_permissions()
    time.sleep(1)
    
    # Test 3: Serial connection
    ports = [port.device for port in serial.tools.list_ports.comports()]
    if ports:
        results['serial'] = test_serial_connection(ports[0])
    else:
        print_header("Serial Port Test")
        print("  ⚠ Skipped - no serial ports found")
        results['serial'] = False
    time.sleep(1)
    
    # Test 4: FlRig connection
    results['flrig'] = test_flrig_connection()
    
    # Summary
    print_header("Test Summary")
    
    print("\n  Results:")
    for test, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"    {test.upper():15} {status}")
    
    total = len(results)
    passed = sum(results.values())
    
    print(f"\n  Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n  🎉 All tests passed! Your system is ready.")
        return 0
    else:
        print("\n  ⚠ Some tests failed. Please address the issues above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
