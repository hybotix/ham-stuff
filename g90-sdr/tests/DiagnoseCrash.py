#!/usr/bin/env python3
# Filename: tests/DiagnoseCrash.py
# Diagnose why the system crashed

import subprocess
import os
import sys

print("=" * 70)
print("  G90-SDR Crash Diagnosis")
print("=" * 70)

# Check for crash logs
print("\n[1] Checking System Logs:")
print("-" * 70)

# Check dmesg for errors
try:
    result = subprocess.run(['dmesg', '|', 'tail', '-50'], 
                          capture_output=True, text=True, shell=True)
    errors = [line for line in result.stdout.split('\n') 
              if any(word in line.lower() for word in ['error', 'fail', 'crash', 'killed'])]
    
    if errors:
        print("Recent errors found:")
        for error in errors[-10:]:  # Show last 10 errors
            print(f"  {error}")
    else:
        print("  No obvious errors in dmesg")
except Exception as e:
    print(f"  Could not check dmesg: {e}")

# Check application log
print("\n[2] Checking G90-SDR Log:")
print("-" * 70)

# Use L_SDR_DIR environment variable or find relative to script
if 'L_SDR_DIR' in os.environ:
    project_dir = os.environ['L_SDR_DIR']
else:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)

log_file = os.path.join(project_dir, "logs", "g90_sdr.log")

if os.path.exists(log_file):
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
            # Show last 20 lines
            print("Last 20 log entries:")
            for line in lines[-20:]:
                print(f"  {line.rstrip()}")
    except Exception as e:
        print(f"  Could not read log: {e}")
else:
    print(f"  No log file found at: {log_file}")

# Check for killed processes
print("\n[3] Checking for OOM (Out of Memory) Kills:")
print("-" * 70)

try:
    result = subprocess.run(['dmesg', '|', 'grep', '-i', 'killed'], 
                          capture_output=True, text=True, shell=True)
    if result.stdout.strip():
        print("Processes killed by OOM:")
        print(result.stdout)
    else:
        print("  No OOM kills detected")
except Exception as e:
    print(f"  Could not check: {e}")

# Check audio device status
print("\n[4] Checking Audio Devices:")
print("-" * 70)

try:
    # Check if audio devices are in use
    result = subprocess.run(['fuser', '/dev/snd/*'], 
                          capture_output=True, text=True, shell=True)
    if result.stdout.strip():
        print("Processes using audio devices:")
        print(result.stdout)
    else:
        print("  No processes currently using audio")
except Exception as e:
    print(f"  Could not check audio: {e}")

# Check PulseAudio status
try:
    result = subprocess.run(['systemctl', '--user', 'status', 'pulseaudio'], 
                          capture_output=True, text=True)
    if 'active (running)' in result.stdout:
        print("  ✓ PulseAudio is running")
    else:
        print("  ✗ PulseAudio is not running")
except Exception as e:
    print(f"  Could not check PulseAudio: {e}")

# Check GQRX-specific issues
print("\n[5] Checking GQRX Status:")
print("-" * 70)

try:
    # Check if GQRX is running
    result = subprocess.run(['pgrep', '-a', 'gqrx'], 
                          capture_output=True, text=True)
    if result.stdout.strip():
        print("GQRX processes:")
        print(result.stdout)
    else:
        print("  GQRX is not running (crashed or stopped)")
except Exception as e:
    print(f"  Could not check: {e}")

# Check for GQRX config issues
gqrx_config = os.path.expanduser("~/.config/gqrx/default.conf")
if os.path.exists(gqrx_config):
    print(f"  ✓ GQRX config exists: {gqrx_config}")
else:
    print(f"  ⚠ GQRX config not found")

# Check memory usage
print("\n[6] Checking System Resources:")
print("-" * 70)

try:
    result = subprocess.run(['free', '-h'], 
                          capture_output=True, text=True)
    print(result.stdout)
except Exception as e:
    print(f"  Could not check memory: {e}")

# Common issues and solutions
print("\n" + "=" * 70)
print("  Common Crash Causes & Solutions")
print("=" * 70)

print("""
1. AUDIO DEVICE CONFLICT
   Symptom: Crashes when starting GQRX
   Solution: 
   - Close other audio applications
   - Restart PulseAudio: systemctl --user restart pulseaudio
   - Check: fuser -v /dev/snd/*

2. OUT OF MEMORY
   Symptom: System freezes, processes killed
   Solution:
   - Close other applications
   - Reduce GQRX FFT size
   - Add swap space

3. GQRX CONFIGURATION ISSUE
   Symptom: GQRX crashes immediately
   Solution:
   - Delete GQRX config: rm -rf ~/.config/gqrx
   - Restart GQRX and reconfigure

4. REMOTE CONTROL NOT ENABLED
   Symptom: Frequency sync fails
   Solution:
   - In GQRX: Tools → Remote Control → Enable

5. PERMISSIONS ISSUE
   Symptom: Cannot access devices
   Solution:
   - Check groups: groups
   - Add to groups: sudo usermod -a -G dialout,audio $USER
   - Reboot

6. USB DISCONNECTION
   Symptom: CAT control stops working
   Solution:
   - Check USB cable
   - Check dmesg for USB errors
   - Try different USB port
""")

print("\n" + "=" * 70)
print("  Recovery Steps")
print("=" * 70)

print("""
1. Kill all processes:
   pkill -9 gqrx
   pkill -9 flrig
   pkill -9 -f start_sdr

2. Reset audio:
   systemctl --user restart pulseaudio
   pulseaudio -k
   pulseaudio --start

3. Clear GQRX config (if needed):
   rm -rf ~/.config/gqrx

4. Check logs:
   tail -f ~/G90-SDR/logs/g90_sdr.log

5. Restart system:
   python3 ~/G90-SDR/scripts/start_sdr.py
""")

print("\n" + "=" * 70)
print("  Next Steps")
print("=" * 70)

print("""
If crashes continue:
1. Run with verbose logging
2. Start components individually to isolate issue
3. Check system temperature: vcgencmd measure_temp
4. Monitor resources: htop
5. Report issue with log file
""")

print("=" * 70)
