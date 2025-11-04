#!/usr/bin/env python3
# Filename: tests/TestAudio.py
# Audio device detection and testing

import sys
import sounddevice as sd
import numpy as np


def print_header(title: str):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def list_audio_devices():
    """List all available audio devices"""
    print_header("Audio Device Detection")
    
    devices = sd.query_devices()
    
    print(f"\nFound {len(devices)} audio device(s):\n")
    
    for idx, device in enumerate(devices):
        print(f"Device {idx}: {device['name']}")
        print(f"  Max Input Channels: {device['max_input_channels']}")
        print(f"  Max Output Channels: {device['max_output_channels']}")
        print(f"  Default Sample Rate: {device['default_samplerate']} Hz")
        
        # Highlight potential radio interface
        if any(keyword in device['name'].lower() for keyword in ['usb', 'audio', 'codec']):
            print("  >>> Possible radio interface")
        print()
    
    return devices


def test_input_device(device_id: int = None, duration: float = 2.0):
    """Test audio input device"""
    print_header(f"Audio Input Test (Device {device_id})")
    
    try:
        # Record audio
        print(f"\n  Recording for {duration} seconds...")
        sample_rate = 48000
        recording = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            device=device_id,
            dtype='float32'
        )
        sd.wait()
        
        # Analyze recording
        rms = np.sqrt(np.mean(recording**2))
        peak = np.max(np.abs(recording))
        
        print(f"  ✓ Recording complete")
        print(f"\n  Audio Analysis:")
        print(f"    RMS Level: {20 * np.log10(rms + 1e-10):.1f} dB")
        print(f"    Peak Level: {20 * np.log10(peak + 1e-10):.1f} dB")
        
        if peak < 0.001:
            print("\n  ⚠ Warning: Very low audio level detected")
            print("    Possible issues:")
            print("      - No audio signal present")
            print("      - Input gain too low")
            print("      - Wrong input device selected")
            return False
        else:
            print("\n  ✓ Audio signal detected")
            return True
            
    except Exception as e:
        print(f"\n  ✗ Error testing input: {e}")
        return False


def test_output_device(device_id: int = None, duration: float = 1.0):
    """Test audio output device"""
    print_header(f"Audio Output Test (Device {device_id})")
    
    try:
        # Generate 1 kHz test tone
        sample_rate = 48000
        frequency = 1000  # Hz
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        tone = 0.3 * np.sin(2 * np.pi * frequency * t)
        
        print(f"\n  Playing {frequency} Hz test tone for {duration} seconds...")
        print("  Listen for a clear tone on your output device.")
        
        sd.play(tone, samplerate=sample_rate, device=device_id)
        sd.wait()
        
        print("  ✓ Playback complete")
        return True
        
    except Exception as e:
        print(f"\n  ✗ Error testing output: {e}")
        return False


def test_loopback(input_device: int = None, output_device: int = None):
    """Test audio loopback"""
    print_header("Audio Loopback Test")
    
    print("\n  This test requires a loopback cable connecting")
    print("  the output to the input.")
    print()
    
    response = input("  Do you have a loopback cable connected? (y/n): ")
    if response.lower() != 'y':
        print("\n  ⚠ Skipping loopback test")
        return None
    
    try:
        sample_rate = 48000
        duration = 2.0
        frequency = 1000  # Hz
        
        # Generate test tone
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        tone = 0.3 * np.sin(2 * np.pi * frequency * t)
        
        print("\n  Playing tone and recording simultaneously...")
        
        # Play and record
        recording = sd.playrec(
            tone,
            samplerate=sample_rate,
            channels=1,
            input_device=input_device,
            output_device=output_device,
            dtype='float32'
        )
        sd.wait()
        
        # Analyze recording
        rms_out = np.sqrt(np.mean(tone**2))
        rms_in = np.sqrt(np.mean(recording**2))
        correlation = np.corrcoef(tone.flatten(), recording.flatten())[0, 1]
        
        print(f"  ✓ Test complete")
        print(f"\n  Results:")
        print(f"    Output RMS: {20 * np.log10(rms_out):.1f} dB")
        print(f"    Input RMS: {20 * np.log10(rms_in + 1e-10):.1f} dB")
        print(f"    Correlation: {correlation:.3f}")
        
        if correlation > 0.7:
            print("\n  ✓ Strong correlation - loopback working well")
            return True
        elif correlation > 0.3:
            print("\n  ⚠ Moderate correlation - check connections")
            return False
        else:
            print("\n  ✗ Poor correlation - loopback may not be working")
            return False
            
    except Exception as e:
        print(f"\n  ✗ Error in loopback test: {e}")
        return False


def main():
    """Run audio tests"""
    print("\n" + "█" * 60)
    print("  G90-SDR Audio Test Suite")
    print("  Version 1.0")
    print("█" * 60)
    
    # List devices
    devices = list_audio_devices()
    
    # Get default devices
    default_input = sd.default.device[0]
    default_output = sd.default.device[1]
    
    print(f"\nDefault input device: {default_input}")
    print(f"Default output device: {default_output}")
    
    # Interactive device selection
    print("\nYou can test specific devices or use defaults.")
    response = input("\nSelect input device number (or press Enter for default): ")
    
    if response.strip():
        try:
            input_device = int(response)
        except ValueError:
            input_device = default_input
    else:
        input_device = default_input
    
    response = input("Select output device number (or press Enter for default): ")
    
    if response.strip():
        try:
            output_device = int(response)
        except ValueError:
            output_device = default_output
    else:
        output_device = default_output
    
    # Run tests
    results = {}
    
    # Test input
    print("\n\nMake some noise or speak into the microphone...")
    input("Press Enter when ready to test input...")
    results['input'] = test_input_device(input_device, duration=2.0)
    
    # Test output
    input("\n\nPress Enter when ready to test output...")
    results['output'] = test_output_device(output_device, duration=1.0)
    
    # Test loopback (optional)
    results['loopback'] = test_loopback(input_device, output_device)
    
    # Summary
    print_header("Test Summary")
    
    print("\n  Results:")
    for test, result in results.items():
        if result is None:
            status = "⊘ SKIP"
        elif result:
            status = "✓ PASS"
        else:
            status = "✗ FAIL"
        print(f"    {test.upper():15} {status}")
    
    passed = sum(1 for r in results.values() if r is True)
    total = sum(1 for r in results.values() if r is not None)
    
    print(f"\n  Overall: {passed}/{total} tests passed")
    
    if passed == total and total > 0:
        print("\n  🎉 All audio tests passed!")
        return 0
    else:
        print("\n  ⚠ Some tests failed or were skipped.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
