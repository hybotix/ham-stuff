#!/usr/bin/env python3
# Filename: scripts/frequency_sync.py
# Synchronizes GQRX frequency with Xiegu G90 via FlRig

import socket
import time
import logging
import threading
from typing import Optional
from rig_control import RigControl

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GQRXControl:
    """Interface to control GQRX via TCP remote control"""
    
    def __init__(self, host: str = '127.0.0.1', port: int = 7356):
        """
        Initialize GQRX control interface
        
        Args:
            host: GQRX server IP address
            port: GQRX remote control port (default 7356)
        """
        self.host = host
        self.port = port
        self.sock: Optional[socket.socket] = None
        self._connected = False
    
    def connect(self) -> bool:
        """
        Connect to GQRX remote control interface
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(5.0)
            self.sock.connect((self.host, self.port))
            self._connected = True
            logger.info(f"Connected to GQRX at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to GQRX: {e}")
            self._connected = False
            return False
    
    def disconnect(self):
        """Disconnect from GQRX"""
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
        self.sock = None
        self._connected = False
        logger.info("Disconnected from GQRX")
    
    def is_connected(self) -> bool:
        """Check if connected to GQRX"""
        return self._connected and self.sock is not None
    
    def send_command(self, command: str) -> Optional[str]:
        """
        Send command to GQRX and get response
        
        Args:
            command: Command string
            
        Returns:
            Response string or None if error
        """
        if not self.is_connected():
            logger.error("Not connected to GQRX")
            return None
        
        try:
            # Send command (must end with newline)
            self.sock.sendall(f"{command}\n".encode('ascii'))
            
            # Receive response
            response = self.sock.recv(1024).decode('ascii').strip()
            return response
        except Exception as e:
            logger.error(f"Error sending command to GQRX: {e}")
            self._connected = False
            return None
    
    def set_frequency(self, frequency: int) -> bool:
        """
        Set GQRX frequency
        
        Args:
            frequency: Frequency in Hz
            
        Returns:
            True if successful, False otherwise
        """
        response = self.send_command(f"F {frequency}")
        if response and "RPRT 0" in response:
            logger.debug(f"Set GQRX frequency to {frequency} Hz")
            return True
        return False
    
    def get_frequency(self) -> Optional[int]:
        """
        Get current GQRX frequency
        
        Returns:
            Frequency in Hz, or None if error
        """
        response = self.send_command("f")
        if response:
            try:
                return int(response)
            except ValueError:
                logger.error(f"Invalid frequency response: {response}")
        return None
    
    def set_mode(self, mode: str) -> bool:
        """
        Set GQRX demodulator mode
        
        Args:
            mode: Mode string (USB, LSB, CW, AM, FM, etc.)
            
        Returns:
            True if successful, False otherwise
        """
        response = self.send_command(f"M {mode}")
        if response and "RPRT 0" in response:
            logger.debug(f"Set GQRX mode to {mode}")
            return True
        return False


class FrequencySync:
    """Synchronizes frequency between G90 and GQRX"""
    
    def __init__(self, 
                 flrig_host: str = '127.0.0.1', 
                 flrig_port: int = 12345,
                 gqrx_host: str = '127.0.0.1',
                 gqrx_port: int = 7356,
                 sync_interval: float = 0.5):
        """
        Initialize frequency synchronization
        
        Args:
            flrig_host: FlRig server address
            flrig_port: FlRig XML-RPC port
            gqrx_host: GQRX server address
            gqrx_port: GQRX remote control port
            sync_interval: Sync interval in seconds (default 0.5)
        """
        self.rig = RigControl(flrig_host, flrig_port)
        self.gqrx = GQRXControl(gqrx_host, gqrx_port)
        self.sync_interval = sync_interval
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.last_frequency = 0
        self.last_mode = ""
    
    def connect(self) -> bool:
        """
        Connect to both FlRig and GQRX
        
        Returns:
            True if both connections successful, False otherwise
        """
        logger.info("Connecting to FlRig and GQRX...")
        
        rig_ok = self.rig.connect()
        gqrx_ok = self.gqrx.connect()
        
        if rig_ok and gqrx_ok:
            logger.info("✓ Connected to both FlRig and GQRX")
            return True
        else:
            if not rig_ok:
                logger.error("✗ Failed to connect to FlRig")
            if not gqrx_ok:
                logger.error("✗ Failed to connect to GQRX")
            return False
    
    def disconnect(self):
        """Disconnect from both FlRig and GQRX"""
        self.stop()
        self.rig.disconnect()
        self.gqrx.disconnect()
    
    def sync_once(self) -> bool:
        """
        Perform one synchronization cycle
        
        Returns:
            True if sync successful, False otherwise
        """
        # Get frequency and mode from G90
        frequency = self.rig.get_frequency()
        mode = self.rig.get_mode()
        
        if frequency is None or mode is None:
            logger.warning("Could not get rig state")
            return False
        
        # Only update if changed
        frequency_changed = (frequency != self.last_frequency)
        mode_changed = (mode != self.last_mode)
        
        if frequency_changed:
            if self.gqrx.set_frequency(frequency):
                self.last_frequency = frequency
                logger.info(f"Synced frequency: {frequency / 1e6:.6f} MHz")
            else:
                return False
        
        if mode_changed:
            if self.gqrx.set_mode(mode):
                self.last_mode = mode
                logger.info(f"Synced mode: {mode}")
            else:
                return False
        
        return True
    
    def sync_loop(self):
        """Main synchronization loop (runs in thread)"""
        logger.info("Frequency sync loop started")
        
        while self.running:
            try:
                self.sync_once()
                time.sleep(self.sync_interval)
            except Exception as e:
                logger.error(f"Error in sync loop: {e}")
                time.sleep(1.0)
        
        logger.info("Frequency sync loop stopped")
    
    def start(self) -> bool:
        """
        Start frequency synchronization thread
        
        Returns:
            True if started successfully, False otherwise
        """
        if self.running:
            logger.warning("Sync already running")
            return False
        
        if not self.rig.is_connected() or not self.gqrx.is_connected():
            logger.error("Not connected to FlRig and/or GQRX")
            return False
        
        # Perform initial sync
        if not self.sync_once():
            logger.warning("Initial sync failed, but continuing...")
        
        # Start sync thread
        self.running = True
        self.thread = threading.Thread(target=self.sync_loop, daemon=True)
        self.thread.start()
        
        logger.info("Frequency synchronization started")
        return True
    
    def stop(self):
        """Stop frequency synchronization thread"""
        if self.running:
            self.running = False
            if self.thread:
                self.thread.join(timeout=2.0)
            logger.info("Frequency synchronization stopped")


def main():
    """Test frequency synchronization"""
    print("G90-SDR Frequency Synchronization Test")
    print("=" * 50)
    
    # Create sync instance
    sync = FrequencySync(sync_interval=1.0)
    
    # Connect
    print("\nConnecting to FlRig and GQRX...")
    if not sync.connect():
        print("ERROR: Could not connect")
        print("\nMake sure:")
        print("  1. FlRig is running and connected to G90")
        print("  2. GQRX is running with remote control enabled")
        return
    
    print("✓ Connected")
    
    # Start sync
    print("\nStarting frequency sync...")
    if not sync.start():
        print("ERROR: Could not start sync")
        sync.disconnect()
        return
    
    print("✓ Sync running")
    print("\nMonitoring for 30 seconds...")
    print("Change frequency on G90 to see sync in action")
    print("Press Ctrl+C to stop")
    
    try:
        # Run for 30 seconds
        for i in range(30):
            time.sleep(1)
            print(".", end="", flush=True)
    except KeyboardInterrupt:
        print("\n\nStopped by user")
    
    # Stop and disconnect
    print("\nStopping sync...")
    sync.disconnect()
    print("✓ Stopped")


if __name__ == '__main__':
    main()
