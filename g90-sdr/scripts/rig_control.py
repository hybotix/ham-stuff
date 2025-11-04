#!/usr/bin/env python3
# Filename: scripts/rig_control.py
# FlRig interface and CAT control wrapper for Xiegu G90

import xmlrpc.client
import logging
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class RigState:
    """Current state of the radio"""
    frequency: int  # Hz
    mode: str  # USB, LSB, CW, AM, FM
    bandwidth: int  # Hz
    power: float  # Watts
    connected: bool


class RigControl:
    """Interface to control Xiegu G90 via FlRig XML-RPC"""
    
    def __init__(self, host: str = '127.0.0.1', port: int = 12345):
        """
        Initialize rig control interface
        
        Args:
            host: FlRig server IP address
            port: FlRig XML-RPC port (default 12345)
        """
        self.host = host
        self.port = port
        self.server_url = f'http://{host}:{port}'
        self.proxy: Optional[xmlrpc.client.ServerProxy] = None
        self._connected = False
        
    def connect(self) -> bool:
        """
        Connect to FlRig server
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.proxy = xmlrpc.client.ServerProxy(self.server_url)
            # Test connection
            xcvr = self.proxy.rig.get_xcvr()
            logger.info(f"Connected to FlRig - Transceiver: {xcvr}")
            self._connected = True
            return True
        except Exception as e:
            logger.error(f"Failed to connect to FlRig: {e}")
            self._connected = False
            return False
    
    def disconnect(self):
        """Disconnect from FlRig server"""
        self.proxy = None
        self._connected = False
        logger.info("Disconnected from FlRig")
    
    def is_connected(self) -> bool:
        """Check if connected to FlRig"""
        return self._connected and self.proxy is not None
    
    def get_frequency(self) -> Optional[int]:
        """
        Get current VFO frequency
        
        Returns:
            Frequency in Hz, or None if error
        """
        if not self.is_connected():
            logger.error("Not connected to FlRig")
            return None
        
        try:
            freq_str = self.proxy.rig.get_vfo()
            frequency = int(float(freq_str))
            return frequency
        except Exception as e:
            logger.error(f"Error getting frequency: {e}")
            return None
    
    def set_frequency(self, frequency: int) -> bool:
        """
        Set VFO frequency
        
        Args:
            frequency: Frequency in Hz
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected():
            logger.error("Not connected to FlRig")
            return False
        
        try:
            self.proxy.rig.set_vfo(float(frequency))
            logger.info(f"Set frequency to {frequency} Hz")
            return True
        except Exception as e:
            logger.error(f"Error setting frequency: {e}")
            return False
    
    def get_mode(self) -> Optional[str]:
        """
        Get current operating mode
        
        Returns:
            Mode string (USB, LSB, CW, AM, FM) or None if error
        """
        if not self.is_connected():
            logger.error("Not connected to FlRig")
            return None
        
        try:
            mode = self.proxy.rig.get_mode()
            return mode
        except Exception as e:
            logger.error(f"Error getting mode: {e}")
            return None
    
    def set_mode(self, mode: str) -> bool:
        """
        Set operating mode
        
        Args:
            mode: Mode string (USB, LSB, CW, AM, FM)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected():
            logger.error("Not connected to FlRig")
            return False
        
        valid_modes = ['USB', 'LSB', 'CW', 'AM', 'FM', 'CW-R', 'RTTY', 'RTTY-R']
        if mode.upper() not in valid_modes:
            logger.error(f"Invalid mode: {mode}")
            return False
        
        try:
            self.proxy.rig.set_mode(mode.upper())
            logger.info(f"Set mode to {mode}")
            return True
        except Exception as e:
            logger.error(f"Error setting mode: {e}")
            return False
    
    def get_bandwidth(self) -> Optional[int]:
        """
        Get current bandwidth
        
        Returns:
            Bandwidth in Hz, or None if error
        """
        if not self.is_connected():
            logger.error("Not connected to FlRig")
            return None
        
        try:
            bw_result = self.proxy.rig.get_bw()
            
            # FlRig sometimes returns a list, sometimes a string
            if isinstance(bw_result, list):
                if len(bw_result) > 0:
                    bw_str = str(bw_result[0])
                else:
                    logger.warning("Bandwidth list is empty")
                    return None
            else:
                bw_str = str(bw_result)
            
            bandwidth = int(float(bw_str))
            return bandwidth
        except Exception as e:
            logger.error(f"Error getting bandwidth: {e}")
            return None
    
    def set_bandwidth(self, bandwidth: int) -> bool:
        """
        Set bandwidth
        
        Args:
            bandwidth: Bandwidth in Hz
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected():
            logger.error("Not connected to FlRig")
            return False
        
        try:
            # Some rigs expect bandwidth as index, others as Hz
            # Try sending as float first
            result = self.proxy.rig.set_bw(float(bandwidth))
            logger.info(f"Set bandwidth to {bandwidth} Hz")
            return True
        except Exception as e:
            logger.error(f"Error setting bandwidth: {e}")
            return False
    
    def get_power(self) -> Optional[float]:
        """
        Get transmit power level
        
        Returns:
            Power in Watts, or None if error
        """
        if not self.is_connected():
            logger.error("Not connected to FlRig")
            return None
        
        try:
            power = float(self.proxy.rig.get_power())
            return power
        except Exception as e:
            logger.error(f"Error getting power: {e}")
            return None
    
    def set_power(self, power: float) -> bool:
        """
        Set transmit power level
        
        Args:
            power: Power in Watts (0-10 for G90)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected():
            logger.error("Not connected to FlRig")
            return False
        
        if not 0 <= power <= 10:
            logger.error(f"Invalid power level: {power} (must be 0-10W)")
            return False
        
        try:
            self.proxy.rig.set_power(power)
            logger.info(f"Set power to {power}W")
            return True
        except Exception as e:
            logger.error(f"Error setting power: {e}")
            return False
    
    def get_state(self) -> Optional[RigState]:
        """
        Get complete rig state
        
        Returns:
            RigState object or None if error
        """
        if not self.is_connected():
            return None
        
        try:
            frequency = self.get_frequency()
            mode = self.get_mode()
            bandwidth = self.get_bandwidth()
            power = self.get_power()
            
            if None in [frequency, mode, bandwidth, power]:
                return None
            
            return RigState(
                frequency=frequency,
                mode=mode,
                bandwidth=bandwidth,
                power=power,
                connected=True
            )
        except Exception as e:
            logger.error(f"Error getting rig state: {e}")
            return None
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get rig information
        
        Returns:
            Dictionary with rig info
        """
        if not self.is_connected():
            return {'connected': False}
        
        try:
            info = {
                'connected': True,
                'xcvr': self.proxy.rig.get_xcvr(),
                'frequency': self.get_frequency(),
                'mode': self.get_mode(),
                'bandwidth': self.get_bandwidth(),
                'power': self.get_power()
            }
            return info
        except Exception as e:
            logger.error(f"Error getting rig info: {e}")
            return {'connected': False, 'error': str(e)}


def main():
    """Test rig control functionality"""
    print("G90-SDR Rig Control Test")
    print("=" * 50)
    
    # Create rig control instance
    rig = RigControl()
    
    # Connect to FlRig
    print("\nConnecting to FlRig...")
    if not rig.connect():
        print("ERROR: Could not connect to FlRig")
        print("Make sure FlRig is running and listening on port 12345")
        return
    
    print("✓ Connected to FlRig")
    
    # Get rig info
    print("\nRig Information:")
    info = rig.get_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # Get current state
    print("\nCurrent State:")
    state = rig.get_state()
    if state:
        print(f"  Frequency: {state.frequency / 1e6:.6f} MHz")
        print(f"  Mode: {state.mode}")
        print(f"  Bandwidth: {state.bandwidth} Hz")
        print(f"  Power: {state.power}W")
    
    # Test frequency change
    print("\nTesting frequency control...")
    print("  Current frequency:", rig.get_frequency())
    
    # Disconnect
    print("\nDisconnecting...")
    rig.disconnect()
    print("✓ Disconnected")


if __name__ == '__main__':
    main()
