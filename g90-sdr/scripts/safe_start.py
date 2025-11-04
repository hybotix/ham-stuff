#!/usr/bin/env python3
# Filename: scripts/safe_start.py
# Safe startup with audio device checking and recovery

import sys
import os
import subprocess
import time

sys.path.insert(0, os.path.dirname(__file__))

def print_header(msg):
    print("\n" + "=" * 60)
    print(f"  {msg}")
    print("=" * 60)

def check_audio_available():
    """Check if audio device is available"""
    try:
        result = subprocess.run(['fuser', '/dev/snd/pcmC0D0c'], 
                              capture_output=True, text=True)
        if result.stdout.strip():
            print("⚠ Audio device in use by:")
            print(result.stdout)
            return False
        return True
    except:
        return True  # Assume available if can't check

def reset_audio():
    """Reset PulseAudio"""
    print("\nResetting audio system...")
    try:
        subprocess.run(['systemctl', '--user', 'restart', 'pulseaudio'],
                      capture_output=True)
        time.sleep(2)
        print("✓ Audio system reset")
        return True
    except Exception as e:
        print(f"✗ Could not reset audio: {e}")
        return False

def kill_existing():
    """Kill any existing instances"""
    print("\nCleaning up existing processes...")
    for proc in ['gqrx', 'flrig', 'start_sdr']:
        try:
            subprocess.run(['pkill', '-9', proc], 
                         stderr=subprocess.DEVNULL)
        except:
            pass
    time.sleep(1)
    print("✓ Cleanup complete")

def main():
    print_header("G90-SDR Safe Startup")
    
    print("\nThis script performs safety checks before starting.")
    
    # Step 1: Kill existing
    kill_existing()
    
    # Step 2: Check audio
    print_header("Audio Device Check")
    if not check_audio_available():
        print("\n⚠ Audio device is in use!")
        response = input("Try to reset audio? (y/n): ")
        if response.lower() == 'y':
            if not reset_audio():
                print("\n✗ Could not reset audio")
                print("Please close other audio applications and try again")
                return 1
        else:
            print("Proceeding anyway...")
    else:
        print("✓ Audio device available")
    
    # Step 3: Verify files exist
    print_header("File Check")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    required = ['rig_control.py', 'frequency_sync.py']
    
    for file in required:
        path = os.path.join(script_dir, file)
        if os.path.exists(path):
            print(f"✓ {file}")
        else:
            print(f"✗ {file} missing!")
            return 1
    
    # Step 4: Start FlRig manually
    print_header("Starting FlRig")
    print("\n1. FlRig will open")
    print("2. Wait for it to connect to G90")
    print("3. Ensure 'Connected' status is shown")
    
    input("\nPress Enter to start FlRig...")
    
    try:
        flrig_proc = subprocess.Popen(['flrig'], 
                                     stdout=subprocess.DEVNULL,
                                     stderr=subprocess.DEVNULL)
        print("✓ FlRig started (PID: {})".format(flrig_proc.pid))
        print("\nWaiting 5 seconds for FlRig to initialize...")
        time.sleep(5)
    except Exception as e:
        print(f"✗ Could not start FlRig: {e}")
        return 1
    
    # Verify FlRig is running
    try:
        from rig_control import RigControl
        rig = RigControl()
        if rig.connect():
            print("✓ FlRig is responding")
            rig.disconnect()
        else:
            print("⚠ FlRig not responding yet")
            print("  Wait a moment and check FlRig shows 'Connected'")
            input("  Press Enter when FlRig is connected...")
    except Exception as e:
        print(f"⚠ Could not verify FlRig: {e}")
    
    # Step 5: Start GQRX manually
    print_header("Starting GQRX")
    print("\n1. GQRX will open")
    print("2. Configure audio device if prompted")
    print("3. Click 'OK' on any configuration dialogs")
    print("4. Enable: Tools → Remote Control")
    
    input("\nPress Enter to start GQRX...")
    
    try:
        gqrx_proc = subprocess.Popen(['gqrx'],
                                     stdout=subprocess.DEVNULL,
                                     stderr=subprocess.DEVNULL)
        print("✓ GQRX started (PID: {})".format(gqrx_proc.pid))
        print("\nWaiting 8 seconds for GQRX to initialize...")
        time.sleep(8)
    except Exception as e:
        print(f"✗ Could not start GQRX: {e}")
        return 1
    
    print("\nIMPORTANT: In GQRX, go to Tools → Remote Control and enable it")
    input("Press Enter when Remote Control is enabled...")
    
    # Step 6: Start frequency sync
    print_header("Starting Frequency Sync")
    
    try:
        from frequency_sync import FrequencySync
        sync = FrequencySync(sync_interval=0.5)
        
        print("Connecting to FlRig and GQRX...")
        if not sync.connect():
            print("✗ Could not connect")
            print("  Make sure:")
            print("  - FlRig shows 'Connected'")
            print("  - GQRX Remote Control is enabled")
            return 1
        
        print("✓ Connected to both")
        
        if not sync.start():
            print("✗ Could not start sync")
            return 1
        
        print("✓ Frequency synchronization started")
        
        print_header("System Running")
        print("\n✓ All components started successfully!")
        print("\nYou can now:")
        print("  - Use FlRig to control the G90")
        print("  - Watch the waterfall in GQRX")
        print("  - Change frequency on G90 to see sync")
        print("\nPress Ctrl+C to stop")
        
        # Keep running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\nShutting down...")
            sync.stop()
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print("\n✓ Shutdown complete")
    return 0

if __name__ == '__main__':
    sys.exit(main())
