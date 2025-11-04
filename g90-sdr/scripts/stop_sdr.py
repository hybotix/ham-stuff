#!/usr/bin/env python3
# Filename: scripts/stop_sdr.py
# Stop all G90-SDR system components

import sys
import psutil
import signal
import time


def print_header(title: str):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def find_process_by_name(name: str) -> list:
    """
    Find all processes matching name
    
    Args:
        name: Process name to search for
        
    Returns:
        List of matching Process objects
    """
    processes = []
    for proc in psutil.process_iter(['name', 'pid', 'cmdline']):
        try:
            proc_name = proc.info['name'].lower()
            cmdline = ' '.join(proc.info['cmdline'] or []).lower()
            
            if name.lower() in proc_name or name.lower() in cmdline:
                processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    return processes


def stop_process(proc, timeout: int = 5):
    """
    Stop a process gracefully, force kill if necessary
    
    Args:
        proc: Process object
        timeout: Seconds to wait before force kill
        
    Returns:
        True if stopped successfully
    """
    try:
        proc_name = proc.name()
        pid = proc.pid
        
        print(f"  Stopping {proc_name} (PID: {pid})...", end=" ")
        
        # Try graceful termination
        proc.terminate()
        
        # Wait for process to terminate
        try:
            proc.wait(timeout=timeout)
            print("✓")
            return True
        except psutil.TimeoutExpired:
            # Force kill if still running
            print("(force killing)...", end=" ")
            proc.kill()
            proc.wait(timeout=2)
            print("✓")
            return True
            
    except psutil.NoSuchProcess:
        print("(already stopped)")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def stop_flrig():
    """Stop FlRig process"""
    processes = find_process_by_name('flrig')
    
    if not processes:
        print("  FlRig is not running")
        return True
    
    success = True
    for proc in processes:
        if not stop_process(proc):
            success = False
    
    return success


def stop_gqrx():
    """Stop GQRX process"""
    processes = find_process_by_name('gqrx')
    
    if not processes:
        print("  GQRX is not running")
        return True
    
    success = True
    for proc in processes:
        if not stop_process(proc):
            success = False
    
    return success


def stop_sync_script():
    """Stop any running frequency sync scripts"""
    processes = find_process_by_name('frequency_sync')
    
    if not processes:
        # Also check for start_sdr.py
        processes = find_process_by_name('start_sdr')
    
    if not processes:
        print("  No sync scripts running")
        return True
    
    success = True
    for proc in processes:
        if not stop_process(proc):
            success = False
    
    return success


def verify_stopped():
    """Verify all processes are stopped"""
    print_header("Verification")
    
    processes_to_check = ['flrig', 'gqrx', 'frequency_sync', 'start_sdr']
    all_stopped = True
    
    for proc_name in processes_to_check:
        processes = find_process_by_name(proc_name)
        if processes:
            print(f"  ⚠ {proc_name} still running ({len(processes)} instance(s))")
            all_stopped = False
        else:
            print(f"  ✓ {proc_name} stopped")
    
    return all_stopped


def main():
    """Main stop routine"""
    print("\n" + "█" * 60)
    print("  G90-SDR System Shutdown")
    print("█" * 60)
    
    print_header("Stopping Services")
    
    # Stop in reverse order of startup
    print("\n[1/3] Stopping frequency synchronization...")
    stop_sync_script()
    
    print("\n[2/3] Stopping GQRX...")
    stop_gqrx()
    
    print("\n[3/3] Stopping FlRig...")
    stop_flrig()
    
    # Wait a moment for processes to fully terminate
    time.sleep(1)
    
    # Verify
    if verify_stopped():
        print("\n" + "=" * 60)
        print("  ✓ G90-SDR System Stopped Successfully")
        print("=" * 60)
        return 0
    else:
        print("\n" + "=" * 60)
        print("  ⚠ Some processes may still be running")
        print("  Use 'pkill -9 flrig' or 'pkill -9 gqrx' if needed")
        print("=" * 60)
        return 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nShutdown cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError during shutdown: {e}")
        sys.exit(1)
