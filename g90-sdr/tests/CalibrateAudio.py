#!/usr/bin/env python3
# Filename: tests/CalibrateAudio.py
# Audio level calibration tool for optimal SDR performance

import sys
import numpy as np
import sounddevice as sd
import time


def print_header(title: str):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_bar(level: float, width: int = 50):
    """Print a visual bar for audio level"""
    filled = int(level * width)
    bar = "█" * filled + "░" * (width - filled)
    return bar


def measure_audio_level(device_id: int, duration: float = 1.0) -> dict:
    """
    Measure audio level from device
    
    Args:
        device_id: Audio device ID
        duration: Measurement duration in seconds
        
    Returns:
        Dictionary with level measurements
    """
    sample_rate = 48000
    
    # Record audio
    recording = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        device=device_id,
        dtype='float32'
    )
    sd.wait()
    
    # Calculate levels
    rms = np.sqrt(np.mean(recording**2))
    peak = np.max(np.abs(recording))
    
    # Convert to dB
    rms_db = 20 * np.log10(rms + 1e-10)
    peak_db = 20 * np.log10(peak + 1e-10)
    
    # Calculate headroom
    headroom_db = 0 - peak_db  # dB below full scale
    
    return {
        'rms': rms,
        'peak': peak,
        'rms_db': rms_db,
        'peak_db': peak_db,
        'headroom_db': headroom_db
    }


def continuous_level_monitor(device_id: int, duration: int = 30):
    """
    Continuously monitor and display audio levels
    
    Args:
        device_id: Audio device ID
        duration: Monitor duration in seconds
    """
    print("\n  Monitoring audio levels...")
    print("  Adjust your radio's audio output for optimal level")
    print("  Target: Peak around -6 to -10 dB (for headroom)\n")
    
    chunk_duration = 0.5  # Update every 0.5 seconds
    iterations = int(duration / chunk_duration)
    
    max_peak_seen = -100.0
    min_peak_seen = 0.0
    
    try:
        for i in range(iterations):
            # Measure levels
            levels = measure_audio_level(device_id, chunk_duration)
            
            # Track peaks
            if levels['peak_db'] > max_peak_seen:
                max_peak_seen = levels['peak_db']
            if levels['peak_db'] < min_peak_seen and levels['peak_db'] > -80:
                min_peak_seen = levels['peak_db']
            
            # Display
            print(f"\r  RMS: {levels['rms_db']:6.1f} dB  " +
                  f"Peak: {levels['peak_db']:6.1f} dB  " +
                  f"Headroom: {levels['headroom_db']:6.1f} dB  " +
                  f"[{print_bar(min(levels['peak'], 1.0), 30)}]  " +
                  f"Time: {i*chunk_duration:.0f}s", end="", flush=True)
            
    except KeyboardInterrupt:
        print("\n\n  Monitoring stopped by user")
    
    print(f"\n\n  Statistics:")
    print(f"    Maximum peak: {max_peak_seen:.1f} dB")
    print(f"    Minimum peak: {min_peak_seen:.1f} dB")
    
    # Provide recommendations
    print("\n  Recommendations:")
    if max_peak_seen > -3:
        print("    ⚠ Audio level too high - risk of clipping!")
        print("    → Reduce audio output from G90 or DE-19")
    elif max_peak_seen > -6:
        print("    ✓ Audio level is good (slight headroom)")
    elif max_peak_seen > -12:
        print("    ✓ Audio level is optimal (good headroom)")
    elif max_peak_seen > -20:
        print("    ⚠ Audio level is low")
        print("    → Increase audio output from G90 or DE-19")
    else:
        print("    ✗ Audio level too low")
        print("    → Significantly increase audio output")


def calibrate_input_level(device_id: int):
    """
    Guide user through input calibration
    
    Args:
        device_id: Audio device ID
    """
    print_header("Input Level Calibration")
    
    print("\n  This will help you set optimal audio levels from your G90.")
    print("\n  Setup:")
    print("    1. Tune to a station with a strong signal")
    print("    2. Set G90 to SSB or AM mode")
    print("    3. Adjust G90 volume to comfortable listening level")
    
    input("\n  Press Enter when ready...")
    
    # Baseline measurement
    print("\n  Taking baseline measurement...")
    baseline = measure_audio_level(device_id, 2.0)
    
    print(f"\n  Baseline levels:")
    print(f"    RMS:  {baseline['rms_db']:6.1f} dB")
    print(f"    Peak: {baseline['peak_db']:6.1f} dB")
    
    if baseline['peak_db'] < -40:
        print("\n  ⚠ Very low signal detected!")
        print("    Check:")
        print("      - G90 volume is turned up")
        print("      - DE-19 connections are secure")
        print("      - Audio routing is correct")
        return
    
    # Start continuous monitoring
    print("\n  Starting continuous monitoring for 30 seconds...")
    print("  Speak into the microphone or tune to different signals")
    continuous_level_monitor(device_id, duration=30)


def test_output_level(device_id: int):
    """
    Test audio output level
    
    Args:
        device_id: Audio device ID
    """
    print_header("Output Level Test")
    
    print("\n  This will test audio output to your G90.")
    print("\n  CAUTION: Start with low volume on G90!")
    
    response = input("\n  Generate test tone? (y/n): ")
    if response.lower() != 'y':
        print("  Skipped")
        return
    
    # Generate test tones at different levels
    sample_rate = 48000
    duration = 2.0
    frequency = 1000  # Hz
    
    levels = [0.1, 0.3, 0.5]
    
    for level in levels:
        print(f"\n  Playing test tone at {level*100:.0f}% level...")
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        tone = level * np.sin(2 * np.pi * frequency * t)
        
        sd.play(tone, samplerate=sample_rate, device=device_id)
        sd.wait()
        
        time.sleep(0.5)
    
    print("\n  ✓ Output test complete")
    print("  Did you hear the tones clearly?")


def save_calibration(device_id: int, settings: dict):
    """
    Save calibration settings
    
    Args:
        device_id: Audio device ID
        settings: Calibration settings
    """
    import json
    from pathlib import Path
    
    config_dir = Path(__file__).parent.parent / 'config'
    config_file = config_dir / 'audio_calibration.json'
    
    data = {
        'device_id': device_id,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'settings': settings
    }
    
    with open(config_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n  ✓ Calibration saved to {config_file}")


def main():
    """Run audio calibration"""
    print("\n" + "█" * 70)
    print("  G90-SDR Audio Calibration Tool")
    print("  Version 1.0")
    print("█" * 70)
    
    # List devices
    print("\nAvailable Audio Devices:")
    print("=" * 70)
    
    devices = sd.query_devices()
    for idx, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            print(f"  [{idx}] {device['name']}")
            print(f"      Input channels: {device['max_input_channels']}")
    
    # Select device
    print("\n")
    device_str = input("Select audio input device number: ")
    
    try:
        device_id = int(device_str)
    except ValueError:
        print("Invalid device number")
        return 1
    
    # Verify device
    if device_id < 0 or device_id >= len(devices):
        print("Device number out of range")
        return 1
    
    device = devices[device_id]
    if device['max_input_channels'] == 0:
        print("Selected device has no input channels")
        return 1
    
    print(f"\n✓ Selected: {device['name']}")
    
    # Run calibration
    calibrate_input_level(device_id)
    
    # Optional output test
    if device['max_output_channels'] > 0:
        print("\n")
        response = input("Test output levels? (y/n): ")
        if response.lower() == 'y':
            test_output_level(device_id)
    
    # Summary
    print_header("Calibration Complete")
    
    print("\n  Optimal settings for G90 SDR operation:")
    print("    • Peak levels: -12 to -6 dB")
    print("    • RMS levels: -20 to -15 dB")
    print("    • Minimum headroom: 6 dB")
    
    print("\n  Tips:")
    print("    • Lower levels = more headroom, less distortion")
    print("    • Higher levels = better SNR, but risk clipping")
    print("    • Adjust G90 volume, not computer volume")
    print("    • Test with various signal strengths")
    
    print("\n✓ Calibration session complete")
    return 0


if __name__ == '__main__':
    sys.exit(main())
