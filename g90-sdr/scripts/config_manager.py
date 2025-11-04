#!/usr/bin/env python3
# Filename: scripts/config_manager.py
# Configuration management for G90-SDR system

import os
import yaml
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class FlRigConfig:
    """FlRig configuration settings"""
    host: str = '127.0.0.1'
    port: int = 12345
    device: str = '/dev/ttyUSB0'
    baudrate: int = 19200
    timeout: int = 200
    retries: int = 5


@dataclass
class GQRXConfig:
    """GQRX configuration settings"""
    host: str = '127.0.0.1'
    port: int = 7356
    sample_rate: int = 48000
    fft_size: int = 4096
    fft_rate: int = 25
    waterfall_span: int = 48000


@dataclass
class AudioConfig:
    """Audio routing configuration"""
    input_device: Optional[int] = None
    output_device: Optional[int] = None
    sample_rate: int = 48000
    latency_ms: int = 50
    use_pulseaudio: bool = True


@dataclass
class SyncConfig:
    """Frequency synchronization configuration"""
    enabled: bool = True
    interval: float = 0.5  # seconds
    sync_mode: bool = True
    sync_bandwidth: bool = False


@dataclass
class SystemConfig:
    """Complete system configuration"""
    flrig: FlRigConfig
    gqrx: GQRXConfig
    audio: AudioConfig
    sync: SyncConfig
    
    def __init__(self):
        self.flrig = FlRigConfig()
        self.gqrx = GQRXConfig()
        self.audio = AudioConfig()
        self.sync = SyncConfig()


class ConfigManager:
    """Manage G90-SDR configuration files"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize configuration manager
        
        Args:
            config_dir: Configuration directory path (default: ../config)
        """
        if config_dir is None:
            # Default to config directory relative to script
            script_dir = Path(__file__).parent
            config_dir = script_dir.parent / 'config'
        
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.config_file = self.config_dir / 'g90_sdr.yaml'
        self.config: SystemConfig = SystemConfig()
    
    def load(self) -> bool:
        """
        Load configuration from file
        
        Returns:
            True if loaded successfully, False otherwise
        """
        if not self.config_file.exists():
            logger.warning(f"Config file not found: {self.config_file}")
            logger.info("Using default configuration")
            return False
        
        try:
            with open(self.config_file, 'r') as f:
                data = yaml.safe_load(f)
            
            if not data:
                logger.warning("Config file is empty")
                return False
            
            # Load FlRig config
            if 'flrig' in data:
                self.config.flrig = FlRigConfig(**data['flrig'])
            
            # Load GQRX config
            if 'gqrx' in data:
                self.config.gqrx = GQRXConfig(**data['gqrx'])
            
            # Load Audio config
            if 'audio' in data:
                self.config.audio = AudioConfig(**data['audio'])
            
            # Load Sync config
            if 'sync' in data:
                self.config.sync = SyncConfig(**data['sync'])
            
            logger.info(f"Configuration loaded from {self.config_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return False
    
    def save(self) -> bool:
        """
        Save configuration to file
        
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Convert config to dict
            data = {
                'flrig': asdict(self.config.flrig),
                'gqrx': asdict(self.config.gqrx),
                'audio': asdict(self.config.audio),
                'sync': asdict(self.config.sync)
            }
            
            # Save to YAML file
            with open(self.config_file, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(f"Configuration saved to {self.config_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """
        Reset configuration to default values
        
        Returns:
            True if reset successfully
        """
        self.config = SystemConfig()
        logger.info("Configuration reset to defaults")
        return self.save()
    
    def get_flrig_config(self) -> FlRigConfig:
        """Get FlRig configuration"""
        return self.config.flrig
    
    def get_gqrx_config(self) -> GQRXConfig:
        """Get GQRX configuration"""
        return self.config.gqrx
    
    def get_audio_config(self) -> AudioConfig:
        """Get audio configuration"""
        return self.config.audio
    
    def get_sync_config(self) -> SyncConfig:
        """Get sync configuration"""
        return self.config.sync
    
    def set_flrig_config(self, **kwargs):
        """Update FlRig configuration"""
        for key, value in kwargs.items():
            if hasattr(self.config.flrig, key):
                setattr(self.config.flrig, key, value)
    
    def set_gqrx_config(self, **kwargs):
        """Update GQRX configuration"""
        for key, value in kwargs.items():
            if hasattr(self.config.gqrx, key):
                setattr(self.config.gqrx, key, value)
    
    def set_audio_config(self, **kwargs):
        """Update audio configuration"""
        for key, value in kwargs.items():
            if hasattr(self.config.audio, key):
                setattr(self.config.audio, key, value)
    
    def set_sync_config(self, **kwargs):
        """Update sync configuration"""
        for key, value in kwargs.items():
            if hasattr(self.config.sync, key):
                setattr(self.config.sync, key, value)
    
    def export_json(self, filepath: Path) -> bool:
        """
        Export configuration to JSON file
        
        Args:
            filepath: Output JSON file path
            
        Returns:
            True if exported successfully
        """
        try:
            data = {
                'flrig': asdict(self.config.flrig),
                'gqrx': asdict(self.config.gqrx),
                'audio': asdict(self.config.audio),
                'sync': asdict(self.config.sync)
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Configuration exported to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting configuration: {e}")
            return False
    
    def import_json(self, filepath: Path) -> bool:
        """
        Import configuration from JSON file
        
        Args:
            filepath: Input JSON file path
            
        Returns:
            True if imported successfully
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Load configurations
            if 'flrig' in data:
                self.config.flrig = FlRigConfig(**data['flrig'])
            if 'gqrx' in data:
                self.config.gqrx = GQRXConfig(**data['gqrx'])
            if 'audio' in data:
                self.config.audio = AudioConfig(**data['audio'])
            if 'sync' in data:
                self.config.sync = SyncConfig(**data['sync'])
            
            logger.info(f"Configuration imported from {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error importing configuration: {e}")
            return False
    
    def print_config(self):
        """Print current configuration"""
        print("\nCurrent Configuration:")
        print("=" * 50)
        
        print("\nFlRig:")
        for key, value in asdict(self.config.flrig).items():
            print(f"  {key:15} {value}")
        
        print("\nGQRX:")
        for key, value in asdict(self.config.gqrx).items():
            print(f"  {key:15} {value}")
        
        print("\nAudio:")
        for key, value in asdict(self.config.audio).items():
            print(f"  {key:15} {value}")
        
        print("\nSync:")
        for key, value in asdict(self.config.sync).items():
            print(f"  {key:15} {value}")


def main():
    """Test configuration manager"""
    print("G90-SDR Configuration Manager Test")
    print("=" * 50)
    
    # Create config manager
    config_mgr = ConfigManager()
    
    # Try to load existing config
    print("\nLoading configuration...")
    if config_mgr.load():
        print("✓ Loaded existing configuration")
    else:
        print("✓ Using default configuration")
    
    # Print current config
    config_mgr.print_config()
    
    # Test save
    print("\n\nSaving configuration...")
    if config_mgr.save():
        print(f"✓ Configuration saved to {config_mgr.config_file}")
    
    # Test modification
    print("\nModifying sync interval to 1.0 seconds...")
    config_mgr.set_sync_config(interval=1.0)
    config_mgr.save()
    
    # Test export
    export_file = config_mgr.config_dir / 'g90_sdr_export.json'
    print(f"\nExporting to JSON: {export_file}")
    if config_mgr.export_json(export_file):
        print("✓ Exported successfully")
    
    print("\n✓ Configuration manager test complete")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
