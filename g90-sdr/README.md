# G90-SDR: Xiegu G90 Software Defined Radio Interface

## Project Overview

G90-SDR transforms your Xiegu G90 HF transceiver into a fully-functional software-defined radio by interfacing it with a Raspberry Pi 5 and GQRX. This project enables waterfall displays, advanced filtering, digital mode operation, and spectrum analysis capabilities.

## Hardware Requirements

- **Radio**: Xiegu G90 HF Transceiver
- **Interface**: Xiegu DE-19 Data Interface Expansion Adapter
- **Computer**: Raspberry Pi 5 (4GB or 8GB recommended)
- **Operating System**: Ubuntu 24.04 LTS
- **Audio Interface**: USB sound card (if not using DE-19's internal audio)
- **Cables**: 
  - USB cable (Raspberry Pi to DE-19)
  - Audio cables (DE-19 to sound card if needed)
  - CAT control cable (included with DE-19)

## Features

- **Full CAT Control**: Frequency, mode, and power control via FlRig
- **SDR Reception**: Real-time waterfall and spectrum display in GQRX
- **Digital Modes**: Ready for WSJT-X, fldigi, and other digital mode software
- **Audio Routing**: Automatic audio pipeline management
- **Diagnostic Tools**: Built-in testing and calibration utilities
- **Automated Setup**: One-command installation and configuration

## System Architecture

```
┌─────────────────┐
│   Xiegu G90     │
│   HF Radio      │
└────────┬────────┘
         │ CAT (Serial)
         │ Audio I/O
┌────────┴────────┐
│  DE-19 Data     │
│  Interface      │
└────────┬────────┘
         │ USB
┌────────┴────────────┐
│  Raspberry Pi 5     │
│  Ubuntu 24.04       │
│                     │
│  ┌──────────────┐   │
│  │   FlRig      │   │
│  │ (Rig Control)│   │
│  └──────┬───────┘   │
│         │           │
│  ┌──────┴───────┐   │
│  │    GQRX      │   │
│  │  (SDR Rx)    │   │
│  └──────────────┘   │
│                     │
│  ┌──────────────┐   │
│  │  G90-SDR     │   │
│  │  Scripts     │   │
│  └──────────────┘   │
└─────────────────────┘
```

## Software Components

### Core Applications
- **FlRig**: CAT control and rig interface (v2.0.03+)
- **GQRX**: SDR receiver and waterfall display (v2.17+)
- **PulseAudio**: Audio routing and management

### Python Scripts (v3.13+)
- `rig_control.py`: FlRig interface and command wrapper
- `audio_router.py`: Automatic audio device configuration
- `frequency_sync.py`: Synchronizes GQRX with G90 frequency
- `config_manager.py`: Settings and configuration management
- `device_monitor.py`: Hardware connection monitoring

### Diagnostic Tools
- `TestConnection.py`: Verify DE-19 and G90 connectivity
- `TestAudio.py`: Audio loopback and quality testing
- `TestCatControl.py`: CAT command verification
- `DiagnoseSystem.py`: Complete system health check
- `CalibrateAudio.py`: Audio level calibration

## Directory Structure

```
G90-SDR/
├── README.md                 # This file
├── INSTALL.md               # Detailed installation guide
├── requirements.txt         # Python dependencies
├── config/
│   ├── flrig_g90.xml       # FlRig G90 configuration
│   ├── gqrx_config.conf    # GQRX settings
│   └── audio_routing.conf  # PulseAudio configuration
├── scripts/
│   ├── rig_control.py
│   ├── audio_router.py
│   ├── frequency_sync.py
│   ├── config_manager.py
│   └── device_monitor.py
├── tests/
│   ├── TestConnection.py
│   ├── TestAudio.py
│   ├── TestCatControl.py
│   ├── DiagnoseSystem.py
│   └── CalibrateAudio.py
├── docs/
│   ├── USER_GUIDE.md
│   ├── TROUBLESHOOTING.md
│   └── API_REFERENCE.md
└── logs/
    └── .gitkeep
```

## Quick Start

```bash
# Clone the repository
git clone <repository-url> G90-SDR
cd G90-SDR

# Run installation
sudo bash install.sh

# Test the connection
python3 tests/TestConnection.py

# Start the SDR system
python3 scripts/start_sdr.py
```

## Usage

### Starting the System
```bash
cd G90-SDR
python3 scripts/start_sdr.py
```

This will:
1. Detect and configure the DE-19 interface
2. Start FlRig with G90 settings
3. Configure audio routing
4. Launch GQRX synchronized to the G90
5. Start frequency synchronization service

### Manual Control

**FlRig**: Opens automatically, use for frequency/mode control
**GQRX**: SDR receiver with waterfall display
**Frequency Sync**: Automatically keeps GQRX tuned to G90 frequency

### Stopping the System
```bash
python3 scripts/stop_sdr.py
```

## Configuration

Edit `config/config_manager.py` to customize:
- Audio device selection
- FlRig network port (default: 12345)
- GQRX remote control port (default: 7356)
- Frequency sync interval
- Audio sample rate
- Waterfall settings

## Troubleshooting

### No Audio
Run `python3 tests/TestAudio.py` to diagnose audio routing issues.

### CAT Control Not Working
1. Check USB connection to DE-19
2. Run `python3 tests/TestCatControl.py`
3. Verify FlRig is running
4. Check serial port permissions: `sudo usermod -a -G dialout $USER`

### GQRX Won't Start
1. Run `python3 tests/DiagnoseSystem.py`
2. Check that audio device is not in use
3. Verify GQRX configuration in `config/gqrx_config.conf`

For detailed troubleshooting, see `docs/TROUBLESHOOTING.md`

## Supported Operating Modes

- **SSB** (USB/LSB): Voice operation with waterfall
- **CW**: Morse code with narrow filters
- **AM/FM**: Broadcast monitoring
- **Digital**: RTTY, PSK31, FT8, etc. (requires additional software)

## Performance Notes

- **Latency**: ~50-100ms typical
- **Sample Rate**: 48kHz (adjustable)
- **CPU Usage**: ~15-25% on Raspberry Pi 5
- **Memory**: ~500MB typical usage

## Contributing

Contributions welcome! Please:
1. Follow the coding standards (PEP 8 for Python)
2. Use underscores for file naming
3. Test with Python 3.13+
4. Document all functions
5. Add diagnostic tests for new features

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Acknowledgments

- Xiegu for the excellent G90 radio and DE-19 interface
- FlRig development team
- GQRX development team
- Amateur radio community for testing and feedback

## Support

- **Issues**: Use GitHub issue tracker
- **Documentation**: See `docs/` directory
- **Discussion**: Amateur radio forums and communities

## Version History

- **v1.0.0** (Initial Release)
  - Basic SDR functionality
  - FlRig integration
  - GQRX waterfall display
  - Frequency synchronization
  - Diagnostic tools

## Author

Created for the amateur radio community. 73!

## Warning

Always follow your local amateur radio regulations and licensing requirements. This software is provided as-is for licensed amateur radio operators.
