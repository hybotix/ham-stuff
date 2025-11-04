#!/usr/bin/env python3
# Filename: tests/DebugUsb.py
# Debug USB device detection to identify your specific hardware

import serial.tools.list_ports
import subprocess

print("=" * 70)
print("  USB Device Debug Information")
print("=" * 70)

# Method 1: pyserial list_ports
print("\n[Method 1] PySerial Port Detection:")
print("-" * 70)
ports = serial.tools.list_ports.comports()

if not ports:
    print("No serial ports found!")
else:
    for i, port in enumerate(ports, 1):
        print(f"\nDevice {i}:")
        print(f"  device:       {port.device}")
        print(f"  name:         {port.name}")
        print(f"  description:  {port.description}")
        print(f"  hwid:         {port.hwid}")
        print(f"  vid:          {port.vid}")
        print(f"  pid:          {port.pid}")
        print(f"  serial_number: {port.serial_number}")
        print(f"  location:     {port.location}")
        print(f"  manufacturer: {port.manufacturer}")
        print(f"  product:      {port.product}")
        print(f"  interface:    {port.interface}")

# Method 2: lsusb command
print("\n" + "=" * 70)
print("[Method 2] lsusb Output:")
print("-" * 70)
try:
    result = subprocess.run(['lsusb'], capture_output=True, text=True)
    print(result.stdout)
except Exception as e:
    print(f"Could not run lsusb: {e}")

# Method 3: Check /dev/ttyUSB* devices
print("=" * 70)
print("[Method 3] /dev/ttyUSB* Devices:")
print("-" * 70)
try:
    result = subprocess.run(['ls', '-la', '/dev/ttyUSB*'], 
                          capture_output=True, text=True, shell=False)
    if result.returncode == 0:
        print(result.stdout)
    else:
        print("No /dev/ttyUSB* devices found")
except Exception as e:
    print(f"Could not list devices: {e}")

# Method 4: dmesg for recent USB events
print("=" * 70)
print("[Method 4] Recent USB Connection Events (dmesg):")
print("-" * 70)
try:
    result = subprocess.run(['dmesg', '|', 'grep', '-i', 'usb', '|', 'tail', '-20'],
                          capture_output=True, text=True, shell=True)
    print(result.stdout)
except Exception as e:
    print(f"Could not run dmesg: {e}")

# Analysis
print("\n" + "=" * 70)
print("  Analysis")
print("=" * 70)

if ports:
    print(f"\n✓ Found {len(ports)} serial port(s)")
    
    # Look for common USB-Serial chips
    keywords = {
        'DE-19 (CH340/CH341)': ['CH340', 'CH341', '1a86:7523', 'QinHeng'],
        'FTDI': ['FTDI', '0403:6001'],
        'Prolific': ['Prolific', 'PL2303'],
        'CP210x': ['CP210', 'Silicon Labs'],
    }
    
    print("\nDetected adapters:")
    for port in ports:
        port_info = f"{port.description} {port.hwid}".upper()
        for adapter_name, search_terms in keywords.items():
            if any(term.upper() in port_info for term in search_terms):
                print(f"  ✓ {adapter_name} detected on {port.device}")
                break
        else:
            print(f"  ? Unknown adapter on {port.device}")
    
    print("\nRecommendation:")
    print("  If FlRig connects successfully, your adapter is working correctly")
    print("  even if not specifically identified as DE-19.")
else:
    print("\n✗ No serial ports detected")
    print("\nTroubleshooting:")
    print("  1. Check USB cable connection")
    print("  2. Ensure G90 is powered on")
    print("  3. Try a different USB port")
    print("  4. Check if DE-19 LED is lit")

print("\n" + "=" * 70)
print("  End of Debug Report")
print("=" * 70)
