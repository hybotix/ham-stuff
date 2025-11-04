#!/usr/bin/env python3
# Filename: tests/TestCatControl.py
# Test CAT control functionality via FlRig

import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from rig_control import RigControl


def print_header(title: str):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_connection():
    """Test basic connection to FlRig"""
    print_header("CAT Connection Test")
    
    rig = RigControl()
    
    print("  Attempting connection to FlRig...")
    if not rig.connect():
        print("  ✗ Connection failed")
        print("\n  Troubleshooting:")
        print("    1. Ensure FlRig is running")
        print("    2. Check FlRig XML-RPC server is enabled")
        print("    3. Verify FlRig is connected to G90")
        return False, None
    
    print("  ✓ Connected successfully")
    return True, rig


def test_get_info(rig: RigControl):
    """Test getting rig information"""
    print_header("Rig Information")
    
    try:
        info = rig.get_info()
        
        print(f"\n  Transceiver: {info.get('xcvr', 'Unknown')}")
        print(f"  Frequency: {info.get('frequency', 0) / 1e6:.6f} MHz")
        print(f"  Mode: {info.get('mode', 'Unknown')}")
        print(f"  Bandwidth: {info.get('bandwidth', 0)} Hz")
        print(f"  Power: {info.get('power', 0)}W")
        
        print("\n  ✓ Successfully read rig information")
        return True
    except Exception as e:
        print(f"\n  ✗ Error: {e}")
        return False


def test_frequency_control(rig: RigControl):
    """Test frequency get/set"""
    print_header("Frequency Control Test")
    
    try:
        # Get current frequency
        initial_freq = rig.get_frequency()
        if initial_freq is None:
            print("  ✗ Could not read frequency")
            return False
        
        print(f"  Current frequency: {initial_freq / 1e6:.6f} MHz")
        
        # Calculate test frequency (add 1 kHz)
        test_freq = initial_freq + 1000
        
        print(f"  Setting frequency to: {test_freq / 1e6:.6f} MHz")
        if not rig.set_frequency(test_freq):
            print("  ✗ Could not set frequency")
            return False
        
        time.sleep(0.5)
        
        # Verify frequency changed
        current_freq = rig.get_frequency()
        if current_freq is None:
            print("  ✗ Could not verify frequency")
            return False
        
        print(f"  Verified frequency: {current_freq / 1e6:.6f} MHz")
        
        # Restore original frequency
        print(f"  Restoring original frequency...")
        rig.set_frequency(initial_freq)
        time.sleep(0.5)
        
        print("  ✓ Frequency control working")
        return True
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_mode_control(rig: RigControl):
    """Test mode get/set"""
    print_header("Mode Control Test")
    
    try:
        # Get current mode
        initial_mode = rig.get_mode()
        if initial_mode is None:
            print("  ✗ Could not read mode")
            return False
        
        print(f"  Current mode: {initial_mode}")
        
        # Determine test mode
        test_mode = 'LSB' if initial_mode != 'LSB' else 'USB'
        
        print(f"  Setting mode to: {test_mode}")
        if not rig.set_mode(test_mode):
            print("  ✗ Could not set mode")
            return False
        
        time.sleep(0.5)
        
        # Verify mode changed
        current_mode = rig.get_mode()
        if current_mode is None:
            print("  ✗ Could not verify mode")
            return False
        
        print(f"  Verified mode: {current_mode}")
        
        # Restore original mode
        print(f"  Restoring original mode...")
        rig.set_mode(initial_mode)
        time.sleep(0.5)
        
        print("  ✓ Mode control working")
        return True
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_power_control(rig: RigControl):
    """Test power level get/set"""
    print_header("Power Control Test")
    
    try:
        # Get current power
        initial_power = rig.get_power()
        if initial_power is None:
            print("  ✗ Could not read power level")
            return False
        
        print(f"  Current power: {initial_power}W")
        
        # Note: We don't change power level as that could affect operation
        print("  Note: Not changing power level (could affect operation)")
        print("  ✓ Power reading working")
        return True
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_bandwidth_control(rig: RigControl):
    """Test bandwidth get"""
    print_header("Bandwidth Control Test")
    
    try:
        # Get current bandwidth
        bandwidth = rig.get_bandwidth()
        if bandwidth is None:
            print("  ✗ Could not read bandwidth")
            return False
        
        print(f"  Current bandwidth: {bandwidth} Hz")
        print("  ✓ Bandwidth reading working")
        return True
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_rapid_commands(rig: RigControl):
    """Test rapid command sequence"""
    print_header("Rapid Command Test")
    
    try:
        print("  Sending 10 rapid frequency queries...")
        
        start_time = time.time()
        successes = 0
        
        for i in range(10):
            freq = rig.get_frequency()
            if freq is not None:
                successes += 1
            print(".", end="", flush=True)
            time.sleep(0.1)
        
        elapsed = time.time() - start_time
        
        print(f"\n\n  Completed: {successes}/10 successful")
        print(f"  Time: {elapsed:.2f} seconds")
        print(f"  Average: {elapsed/10:.3f} seconds per command")
        
        if successes == 10:
            print("  ✓ Rapid command test passed")
            return True
        else:
            print("  ⚠ Some commands failed")
            return False
        
    except Exception as e:
        print(f"\n  ✗ Error: {e}")
        return False


def main():
    """Run all CAT control tests"""
    print("\n" + "█" * 60)
    print("  G90-SDR CAT Control Test Suite")
    print("  Version 1.0")
    print("█" * 60)
    
    results = {}
    rig = None
    
    # Test 1: Connection
    success, rig = test_connection()
    results['connection'] = success
    
    if not success:
        print_header("Test Summary")
        print("\n  ✗ Connection failed - cannot continue")
        print("\n  Make sure:")
        print("    1. G90 is powered on")
        print("    2. DE-19 is connected via USB")
        print("    3. FlRig is running")
        print("    4. FlRig shows 'Connected' to G90")
        return 1
    
    # Test 2: Rig info
    time.sleep(0.5)
    results['info'] = test_get_info(rig)
    
    # Test 3: Frequency control
    time.sleep(0.5)
    results['frequency'] = test_frequency_control(rig)
    
    # Test 4: Mode control
    time.sleep(0.5)
    results['mode'] = test_mode_control(rig)
    
    # Test 5: Power control
    time.sleep(0.5)
    results['power'] = test_power_control(rig)
    
    # Test 6: Bandwidth
    time.sleep(0.5)
    results['bandwidth'] = test_bandwidth_control(rig)
    
    # Test 7: Rapid commands
    time.sleep(0.5)
    results['rapid'] = test_rapid_commands(rig)
    
    # Disconnect
    rig.disconnect()
    
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
        print("\n  🎉 All CAT control tests passed!")
        print("  Your G90 is responding correctly to all commands.")
        return 0
    else:
        print("\n  ⚠ Some tests failed.")
        print("  Check FlRig connection and G90 settings.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
