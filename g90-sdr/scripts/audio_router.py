#!/usr/bin/env python3
# Filename: scripts/audio_router.py
# Audio device detection and PulseAudio routing configuration

import subprocess
import logging
import sounddevice as sd
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class AudioDevice:
    """Represents an audio device"""
    
    def __init__(self, index: int, name: str, inputs: int, outputs: int, 
                 sample_rate: float, is_default_input: bool = False, 
                 is_default_output: bool = False):
        self.index = index
        self.name = name
        self.inputs = inputs
        self.outputs = outputs
        self.sample_rate = sample_rate
        self.is_default_input = is_default_input
        self.is_default_output = is_default_output
    
    def __repr__(self):
        return (f"AudioDevice(index={self.index}, name='{self.name}', "
                f"in={self.inputs}, out={self.outputs})")


class AudioRouter:
    """Manage audio device detection and routing"""
    
    def __init__(self):
        self.devices: List[AudioDevice] = []
        self.radio_input: Optional[AudioDevice] = None
        self.radio_output: Optional[AudioDevice] = None
        
    def scan_devices(self) -> List[AudioDevice]:
        """
        Scan for all available audio devices
        
        Returns:
            List of AudioDevice objects
        """
        try:
            devices_info = sd.query_devices()
            default_in, default_out = sd.default.device
            
            self.devices = []
            
            for idx, dev in enumerate(devices_info):
                device = AudioDevice(
                    index=idx,
                    name=dev['name'],
                    inputs=dev['max_input_channels'],
                    outputs=dev['max_output_channels'],
                    sample_rate=dev['default_samplerate'],
                    is_default_input=(idx == default_in),
                    is_default_output=(idx == default_out)
                )
                self.devices.append(device)
            
            logger.info(f"Found {len(self.devices)} audio devices")
            return self.devices
            
        except Exception as e:
            logger.error(f"Error scanning audio devices: {e}")
            return []
    
    def detect_radio_interface(self) -> Tuple[Optional[AudioDevice], Optional[AudioDevice]]:
        """
        Attempt to automatically detect radio interface
        
        Returns:
            Tuple of (input_device, output_device) or (None, None)
        """
        if not self.devices:
            self.scan_devices()
        
        # Keywords that might indicate a radio interface
        radio_keywords = [
            'usb audio',
            'codec',
            'signalink',
            'digirig',
            'tigertronics',
            'usb sound',
            'audio adapter'
        ]
        
        candidates = []
        
        for device in self.devices:
            device_name_lower = device.name.lower()
            
            # Check if device name contains radio-related keywords
            for keyword in radio_keywords:
                if keyword in device_name_lower:
                    candidates.append(device)
                    break
        
        if candidates:
            # Prefer device with both input and output
            for dev in candidates:
                if dev.inputs > 0 and dev.outputs > 0:
                    logger.info(f"Auto-detected radio interface: {dev.name}")
                    self.radio_input = dev
                    self.radio_output = dev
                    return (dev, dev)
            
            # Otherwise use first candidate
            dev = candidates[0]
            logger.info(f"Detected possible radio interface: {dev.name}")
            
            if dev.inputs > 0:
                self.radio_input = dev
            if dev.outputs > 0:
                self.radio_output = dev
            
            return (self.radio_input, self.radio_output)
        
        logger.warning("Could not auto-detect radio interface")
        return (None, None)
    
    def list_devices(self):
        """Print list of all audio devices"""
        if not self.devices:
            self.scan_devices()
        
        print("\nAvailable Audio Devices:")
        print("=" * 70)
        
        for dev in self.devices:
            print(f"\nDevice {dev.index}: {dev.name}")
            print(f"  Input channels:  {dev.inputs}")
            print(f"  Output channels: {dev.outputs}")
            print(f"  Sample rate:     {dev.sample_rate} Hz")
            
            if dev.is_default_input:
                print("  >>> Default INPUT device")
            if dev.is_default_output:
                print("  >>> Default OUTPUT device")
    
    def set_default_device(self, device_index: int, 
                          device_type: str = 'both') -> bool:
        """
        Set default audio device
        
        Args:
            device_index: Device index
            device_type: 'input', 'output', or 'both'
            
        Returns:
            True if successful
        """
        try:
            if device_type in ['input', 'both']:
                sd.default.device[0] = device_index
                logger.info(f"Set default input to device {device_index}")
            
            if device_type in ['output', 'both']:
                sd.default.device[1] = device_index
                logger.info(f"Set default output to device {device_index}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error setting default device: {e}")
            return False
    
    def configure_pulseaudio_loopback(self, 
                                      source_device: int,
                                      sink_device: int,
                                      latency_ms: int = 50) -> bool:
        """
        Configure PulseAudio loopback module
        
        Args:
            source_device: Source (input) device index
            sink_device: Sink (output) device index
            latency_ms: Latency in milliseconds
            
        Returns:
            True if successful
        """
        try:
            # Get device names
            devices = sd.query_devices()
            source_name = devices[source_device]['name']
            sink_name = devices[sink_device]['name']
            
            # Unload existing loopback modules
            subprocess.run(['pactl', 'unload-module', 'module-loopback'],
                         stderr=subprocess.DEVNULL)
            
            # Load loopback module
            cmd = [
                'pactl', 'load-module', 'module-loopback',
                f'source={source_name}',
                f'sink={sink_name}',
                f'latency_msec={latency_ms}'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Configured PulseAudio loopback: {source_name} -> {sink_name}")
                return True
            else:
                logger.error(f"Failed to configure loopback: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error configuring PulseAudio loopback: {e}")
            return False
    
    def get_pulseaudio_info(self) -> Dict:
        """
        Get PulseAudio system information
        
        Returns:
            Dictionary with PulseAudio info
        """
        info = {
            'running': False,
            'sinks': [],
            'sources': [],
            'modules': []
        }
        
        try:
            # Check if PulseAudio is running
            result = subprocess.run(['pactl', 'info'], 
                                  capture_output=True, text=True)
            info['running'] = (result.returncode == 0)
            
            if not info['running']:
                return info
            
            # List sinks
            result = subprocess.run(['pactl', 'list', 'short', 'sinks'],
                                  capture_output=True, text=True)
            info['sinks'] = result.stdout.strip().split('\n') if result.stdout else []
            
            # List sources
            result = subprocess.run(['pactl', 'list', 'short', 'sources'],
                                  capture_output=True, text=True)
            info['sources'] = result.stdout.strip().split('\n') if result.stdout else []
            
            # List modules
            result = subprocess.run(['pactl', 'list', 'short', 'modules'],
                                  capture_output=True, text=True)
            info['modules'] = result.stdout.strip().split('\n') if result.stdout else []
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting PulseAudio info: {e}")
            return info
    
    def print_pulseaudio_status(self):
        """Print PulseAudio status"""
        info = self.get_pulseaudio_info()
        
        print("\nPulseAudio Status:")
        print("=" * 70)
        
        if not info['running']:
            print("  ✗ PulseAudio is not running")
            return
        
        print("  ✓ PulseAudio is running")
        print(f"\n  Sinks (outputs): {len(info['sinks'])}")
        for sink in info['sinks'][:5]:  # Show first 5
            print(f"    {sink}")
        
        print(f"\n  Sources (inputs): {len(info['sources'])}")
        for source in info['sources'][:5]:  # Show first 5
            print(f"    {source}")
        
        # Check for loopback modules
        loopback_count = sum(1 for m in info['modules'] if 'loopback' in m)
        print(f"\n  Active loopback modules: {loopback_count}")


def main():
    """Test audio router functionality"""
    print("G90-SDR Audio Router Test")
    print("=" * 70)
    
    # Create audio router
    router = AudioRouter()
    
    # Scan devices
    print("\n[1/4] Scanning audio devices...")
    router.scan_devices()
    router.list_devices()
    
    # Auto-detect radio interface
    print("\n\n[2/4] Auto-detecting radio interface...")
    radio_in, radio_out = router.detect_radio_interface()
    
    if radio_in or radio_out:
        print("✓ Radio interface detected:")
        if radio_in:
            print(f"  Input:  {radio_in.name}")
        if radio_out:
            print(f"  Output: {radio_out.name}")
    else:
        print("⚠ No radio interface auto-detected")
        print("  You may need to manually specify devices")
    
    # Check PulseAudio
    print("\n\n[3/4] Checking PulseAudio...")
    router.print_pulseaudio_status()
    
    # Show recommendations
    print("\n\n[4/4] Recommendations:")
    print("=" * 70)
    
    default_in, default_out = sd.default.device
    print(f"  Current default input:  Device {default_in}")
    print(f"  Current default output: Device {default_out}")
    
    if radio_in and radio_in.index != default_in:
        print(f"\n  Consider setting radio interface as default input:")
        print(f"    Device {radio_in.index}: {radio_in.name}")
    
    print("\n✓ Audio router test complete")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
