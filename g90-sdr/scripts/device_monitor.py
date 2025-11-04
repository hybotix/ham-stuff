#!/usr/bin/env python3
# Filename: scripts/device_monitor.py
# Monitor hardware connections and system health

import time
import logging
import threading
import serial.tools.list_ports
from typing import Callable, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class DeviceMonitor:
    """Monitor hardware device connections"""
    
    def __init__(self, check_interval: float = 2.0):
        """
        Initialize device monitor
        
        Args:
            check_interval: Check interval in seconds
        """
        self.check_interval = check_interval
        self.running = False
        self.thread: Optional[threading.Thread] = None
        
        # Callbacks
        self.on_device_connected: Optional[Callable] = None
        self.on_device_disconnected: Optional[Callable] = None
        
        # Tracked devices
        self.known_devices: List[str] = []
        
        # Statistics
        self.start_time: Optional[datetime] = None
        self.connection_events = 0
        self.disconnection_events = 0
    
    def get_connected_devices(self) -> List[str]:
        """
        Get list of currently connected serial devices
        
        Returns:
            List of device paths
        """
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]
    
    def detect_de19(self) -> Optional[str]:
        """
        Detect DE-19 interface
        
        Returns:
            Device path if found, None otherwise
        """
        ports = serial.tools.list_ports.comports()
        
        for port in ports:
            # DE-19 uses CH340 USB-to-serial chip
            if 'CH340' in port.description or '1a86:7523' in port.hwid:
                return port.device
        
        return None
    
    def check_devices(self):
        """Check for device connection changes"""
        current_devices = self.get_connected_devices()
        
        # Check for new devices
        new_devices = set(current_devices) - set(self.known_devices)
        if new_devices:
            for device in new_devices:
                logger.info(f"Device connected: {device}")
                self.connection_events += 1
                
                if self.on_device_connected:
                    try:
                        self.on_device_connected(device)
                    except Exception as e:
                        logger.error(f"Error in connection callback: {e}")
        
        # Check for removed devices
        removed_devices = set(self.known_devices) - set(current_devices)
        if removed_devices:
            for device in removed_devices:
                logger.warning(f"Device disconnected: {device}")
                self.disconnection_events += 1
                
                if self.on_device_disconnected:
                    try:
                        self.on_device_disconnected(device)
                    except Exception as e:
                        logger.error(f"Error in disconnection callback: {e}")
        
        # Update known devices
        self.known_devices = current_devices
    
    def monitor_loop(self):
        """Main monitoring loop"""
        logger.info("Device monitoring started")
        self.start_time = datetime.now()
        
        # Initial device scan
        self.known_devices = self.get_connected_devices()
        logger.info(f"Initial devices: {self.known_devices}")
        
        while self.running:
            try:
                self.check_devices()
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
                time.sleep(self.check_interval)
        
        logger.info("Device monitoring stopped")
    
    def start(self):
        """Start device monitoring"""
        if self.running:
            logger.warning("Monitor already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.thread.start()
        logger.info("Device monitor started")
    
    def stop(self):
        """Stop device monitoring"""
        if not self.running:
            return
        
        self.running = False
        if self.thread:
            self.thread.join(timeout=self.check_interval + 1)
        logger.info("Device monitor stopped")
    
    def get_statistics(self) -> dict:
        """
        Get monitoring statistics
        
        Returns:
            Dictionary with statistics
        """
        uptime = None
        if self.start_time:
            uptime = (datetime.now() - self.start_time).total_seconds()
        
        return {
            'running': self.running,
            'uptime_seconds': uptime,
            'connected_devices': len(self.known_devices),
            'connection_events': self.connection_events,
            'disconnection_events': self.disconnection_events,
            'devices': self.known_devices
        }
    
    def print_status(self):
        """Print current monitoring status"""
        stats = self.get_statistics()
        
        print("\nDevice Monitor Status:")
        print("=" * 60)
        print(f"  Running: {stats['running']}")
        
        if stats['uptime_seconds']:
            uptime_str = f"{stats['uptime_seconds']:.0f} seconds"
            print(f"  Uptime: {uptime_str}")
        
        print(f"  Connected devices: {stats['connected_devices']}")
        print(f"  Connection events: {stats['connection_events']}")
        print(f"  Disconnection events: {stats['disconnection_events']}")
        
        if stats['devices']:
            print("\n  Current devices:")
            for device in stats['devices']:
                print(f"    {device}")
        
        # Check for DE-19
        de19 = self.detect_de19()
        if de19:
            print(f"\n  ✓ DE-19 detected at: {de19}")
        else:
            print("\n  ⚠ DE-19 not detected")


class SystemHealthMonitor:
    """Monitor overall system health"""
    
    def __init__(self):
        self.device_monitor = DeviceMonitor()
        self.alerts: List[str] = []
    
    def check_health(self) -> dict:
        """
        Perform complete health check
        
        Returns:
            Dictionary with health status
        """
        health = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'checks': {}
        }
        
        # Check DE-19 connection
        de19 = self.device_monitor.detect_de19()
        health['checks']['de19_connected'] = de19 is not None
        if de19:
            health['de19_device'] = de19
        
        # Check serial devices
        devices = self.device_monitor.get_connected_devices()
        health['checks']['serial_devices'] = len(devices) > 0
        health['serial_device_count'] = len(devices)
        
        # Determine overall status
        if not health['checks']['de19_connected']:
            health['overall_status'] = 'warning'
            self.alerts.append("DE-19 not connected")
        
        if not health['checks']['serial_devices']:
            health['overall_status'] = 'critical'
            self.alerts.append("No serial devices detected")
        
        return health
    
    def print_health_report(self):
        """Print health report"""
        health = self.check_health()
        
        print("\nSystem Health Report")
        print("=" * 60)
        print(f"  Timestamp: {health['timestamp']}")
        print(f"  Overall Status: {health['overall_status'].upper()}")
        
        print("\n  Checks:")
        for check, status in health['checks'].items():
            symbol = "✓" if status else "✗"
            print(f"    {symbol} {check.replace('_', ' ').title()}")
        
        if self.alerts:
            print("\n  Alerts:")
            for alert in self.alerts:
                print(f"    ⚠ {alert}")
            self.alerts.clear()


def main():
    """Test device monitoring"""
    print("G90-SDR Device Monitor Test")
    print("=" * 60)
    
    # Create device monitor
    monitor = DeviceMonitor(check_interval=2.0)
    
    # Set up callbacks
    def on_connect(device):
        print(f"\n>>> Device CONNECTED: {device}")
    
    def on_disconnect(device):
        print(f"\n>>> Device DISCONNECTED: {device}")
    
    monitor.on_device_connected = on_connect
    monitor.on_device_disconnected = on_disconnect
    
    # Start monitoring
    print("\nStarting device monitor...")
    monitor.start()
    
    print("✓ Monitor running")
    print("\nMonitoring for device changes...")
    print("Try unplugging/plugging the DE-19 USB cable")
    print("Press Ctrl+C to stop\n")
    
    try:
        # Monitor for 30 seconds
        for i in range(15):
            time.sleep(2)
            
            # Print status every 10 seconds
            if i % 5 == 0:
                monitor.print_status()
            
            print(".", end="", flush=True)
        
        print("\n\n30 seconds elapsed")
        
    except KeyboardInterrupt:
        print("\n\nStopped by user")
    
    # Stop monitoring
    print("\nStopping monitor...")
    monitor.stop()
    
    # Final statistics
    print("\nFinal Statistics:")
    monitor.print_status()
    
    # Health check
    print("\n")
    health_monitor = SystemHealthMonitor()
    health_monitor.print_health_report()
    
    print("\n✓ Device monitor test complete")


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    main()
