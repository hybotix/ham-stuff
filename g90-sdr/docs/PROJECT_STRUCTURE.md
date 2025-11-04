# G90-SDR Project Structure

Complete overview of the project organization and file purposes.

## Directory Tree

```
G90-SDR/
├── README.md                    # Project overview and features
├── INSTALL.md                   # Installation instructions
├── LICENSE                      # MIT License
├── requirements.txt             # Python dependencies
├── install.sh                   # Automated installation script
│
├── config/                      # Configuration files
│   ├── g90_sdr.yaml            # Main configuration
│   ├── flrig_g90.xml           # FlRig configuration template
│   ├── gqrx_config.conf        # GQRX configuration template
│   └── audio_routing.conf      # Audio configuration
│
├── scripts/                     # Main application scripts
│   ├── rig_control.py          # FlRig interface and CAT control
│   ├── frequency_sync.py       # Frequency synchronization
│   ├── audio_router.py         # Audio device management
│   ├── config_manager.py       # Configuration management
│   ├── device_monitor.py       # Hardware monitoring
│   ├── start_sdr.py            # System startup script
│   └── stop_sdr.py             # System shutdown script
│
├── tests/                       # Diagnostic and test scripts
│   ├── TestConnection.py       # Connection and hardware test
│   ├── TestAudio.py            # Audio device testing
│   ├── TestCatControl.py       # CAT command testing
│   ├── DiagnoseSystem.py       # Complete system diagnostics
│   └── CalibrateAudio.py       # Audio level calibration
│
├── docs/                        # Documentation
│   ├── USER_GUIDE.md           # Complete user guide
│   ├── TROUBLESHOOTING.md      # Problem solving guide
│   ├── API_REFERENCE.md        # API documentation
│   └── PROJECT_STRUCTURE.md    # This file
│
├── logs/                        # Log files
│   ├── .gitkeep                # Keep directory in git
│   └── g90_sdr.log             # Main application log
│
└── venv/                        # Python virtual environment
    └── (virtual environment files)
```

---

## File Descriptions

### Root Directory

#### README.md
- **Purpose**: Project overview, features, quick start
- **Audience**: All users
- **Content**: System architecture, features, installation overview

#### INSTALL.md
- **Purpose**: Detailed installation instructions
- **Audience**: New users, system administrators
- **Content**: Step-by-step setup, dependencies, configuration

#### LICENSE
- **Purpose**: Software license and terms
- **Audience**: All users, developers
- **Content**: MIT license, amateur radio requirements

#### requirements.txt
- **Purpose**: Python package dependencies
- **Format**: pip-compatible package list
- **Usage**: `pip install -r requirements.txt`

#### install.sh
- **Purpose**: Automated installation script
- **Type**: Bash shell script
- **Usage**: `bash install.sh`
- **Functions**:
  - System updates
  - Dependency installation
  - FlRig compilation
  - GQRX installation
  - Python environment setup
  - Permission configuration

---

### config/ Directory

Configuration files for all system components.

#### g90_sdr.yaml
- **Format**: YAML configuration file
- **Purpose**: Main system configuration
- **Sections**:
  - FlRig settings (host, port, device, baud rate)
  - GQRX settings (sample rate, FFT parameters)
  - Audio settings (devices, sample rate, latency)
  - Sync settings (interval, mode sync)

#### flrig_g90.xml
- **Format**: XML configuration
- **Purpose**: FlRig configuration template
- **Content**: G90-specific rig settings

#### gqrx_config.conf
- **Format**: INI-style configuration
- **Purpose**: GQRX configuration template
- **Content**: SDR receiver settings

#### audio_routing.conf
- **Format**: INI configuration
- **Purpose**: Audio device configuration
- **Content**: PulseAudio settings, device mappings

---

### scripts/ Directory

Core application code for G90-SDR system.

#### rig_control.py
- **Purpose**: FlRig XML-RPC interface
- **Class**: `RigControl`
- **Functions**:
  - `connect()` - Connect to FlRig
  - `get_frequency()` - Read VFO frequency
  - `set_frequency()` - Set VFO frequency
  - `get_mode()` - Read operating mode
  - `set_mode()` - Set operating mode
  - `get_power()` - Read TX power
  - `set_power()` - Set TX power
  - `get_state()` - Complete rig state
- **Dependencies**: xmlrpc.client

#### frequency_sync.py
- **Purpose**: Synchronize G90 and GQRX
- **Classes**: 
  - `GQRXControl` - GQRX remote control
  - `FrequencySync` - Synchronization engine
- **Functions**:
  - Automatic frequency tracking
  - Mode synchronization
  - Bandwidth sync (optional)
- **Threading**: Background sync thread
- **Dependencies**: socket, threading

#### audio_router.py
- **Purpose**: Audio device management
- **Classes**:
  - `AudioDevice` - Device representation
  - `AudioRouter` - Device detection and routing
- **Functions**:
  - `scan_devices()` - Detect audio devices
  - `detect_radio_interface()` - Auto-detect DE-19
  - `configure_pulseaudio_loopback()` - Set up audio routing
- **Dependencies**: sounddevice, subprocess

#### config_manager.py
- **Purpose**: Configuration file management
- **Classes**:
  - `FlRigConfig` - FlRig settings
  - `GQRXConfig` - GQRX settings
  - `AudioConfig` - Audio settings
  - `SyncConfig` - Sync settings
  - `SystemConfig` - Complete configuration
  - `ConfigManager` - Config file operations
- **Functions**:
  - Load/save YAML configuration
  - Import/export JSON
  - Reset to defaults
- **Dependencies**: yaml, json

#### device_monitor.py
- **Purpose**: Hardware connection monitoring
- **Classes**:
  - `DeviceMonitor` - USB device monitoring
  - `SystemHealthMonitor` - System health checks
- **Functions**:
  - Real-time device detection
  - Connection event callbacks
  - Health status reporting
- **Threading**: Background monitoring thread
- **Dependencies**: serial, threading

#### start_sdr.py
- **Purpose**: System startup orchestration
- **Class**: `SDRSystem`
- **Functions**:
  - Start FlRig
  - Start GQRX
  - Start frequency sync
  - Handle shutdown signals
- **Usage**: `python3 scripts/start_sdr.py`

#### stop_sdr.py
- **Purpose**: Graceful system shutdown
- **Functions**:
  - Stop all processes
  - Clean up resources
  - Verify shutdown
- **Usage**: `python3 scripts/stop_sdr.py`

---

### tests/ Directory

Diagnostic and testing utilities.

#### TestConnection.py
- **Purpose**: Hardware and connection testing
- **Tests**:
  - USB device detection
  - Serial port access
  - FlRig connectivity
  - Permission verification
- **Usage**: `python3 tests/TestConnection.py`
- **Exit Codes**: 0 = pass, 1 = fail

#### TestAudio.py
- **Purpose**: Audio system testing
- **Tests**:
  - Audio device detection
  - Input device testing
  - Output device testing
  - Loopback testing (optional)
- **Usage**: `python3 tests/TestAudio.py`
- **Interactive**: User selects devices

#### TestCatControl.py
- **Purpose**: CAT command testing
- **Tests**:
  - Connection establishment
  - Frequency get/set
  - Mode get/set
  - Power reading
  - Bandwidth reading
  - Rapid command sequence
- **Usage**: `python3 tests/TestCatControl.py`
- **Note**: May change radio settings temporarily

#### DiagnoseSystem.py
- **Purpose**: Complete system diagnostics
- **Checks**:
  - System information
  - Software dependencies
  - Python modules
  - Hardware detection
  - Permissions
  - Running processes
  - Network services
  - FlRig connection
  - GQRX connection
- **Usage**: `python3 tests/DiagnoseSystem.py`
- **Output**: Detailed diagnostic report

#### CalibrateAudio.py
- **Purpose**: Audio level calibration
- **Functions**:
  - Measure audio levels
  - Continuous monitoring
  - Visual level meters
  - Calibration recommendations
- **Usage**: `python3 tests/CalibrateAudio.py`
- **Interactive**: User adjusts levels

---

### docs/ Directory

Comprehensive documentation.

#### USER_GUIDE.md
- **Audience**: End users
- **Content**:
  - Quick start guide
  - Daily operation
  - Features and functions
  - Configuration
  - Tips and best practices
  - Advanced usage

#### TROUBLESHOOTING.md
- **Audience**: Users experiencing problems
- **Content**:
  - Quick diagnostics
  - Common problems and solutions
  - Connection issues
  - Audio issues
  - Performance issues
  - Emergency recovery

#### API_REFERENCE.md
- **Audience**: Developers
- **Content**:
  - Class documentation
  - Function reference
  - Usage examples
  - Integration guide

#### PROJECT_STRUCTURE.md
- **Audience**: Developers, contributors
- **Content**: This file - complete project organization

---

### logs/ Directory

Application and system logs.

#### g90_sdr.log
- **Format**: Text log file
- **Content**: 
  - Application events
  - Error messages
  - Debug information
  - Timestamps
- **Rotation**: Manual (not automated)
- **Size**: Can grow large - monitor regularly

#### .gitkeep
- **Purpose**: Maintain empty directory in git
- **Content**: Empty file

---

## File Naming Conventions

### Python Scripts

**Format**: `lowercase_with_underscores.py`
- **Example**: `frequency_sync.py`
- **Rationale**: Python PEP 8 standard

**Test Scripts**: `CapitalizedWordTest.py`
- **Example**: `TestConnection.py`
- **Rationale**: Project standard for test files

### Configuration Files

**Format**: `lowercase.extension`
- **Example**: `g90_sdr.yaml`
- **Extensions**: `.yaml`, `.conf`, `.xml`

### Documentation

**Format**: `UPPERCASE.md` or `CAPITALIZED.md`
- **Example**: `README.md`, `USER_GUIDE.md`
- **Rationale**: High visibility for important docs

---

## Code Organization

### Module Structure

Each Python module follows this structure:

```python
# Filename: path/to/file.py
# Description of module purpose

# Imports
import standard_library
import third_party
from local_module import LocalClass

# Constants
CONSTANT_NAME = value

# Classes
class ClassName:
    """Class docstring"""
    
    def __init__(self):
        """Constructor"""
        pass
    
    def method_name(self):
        """Method docstring"""
        pass

# Functions
def function_name():
    """Function docstring"""
    pass

# Main execution
def main():
    """Main function"""
    pass

if __name__ == '__main__':
    main()
```

### Naming Conventions

- **Classes**: `PascalCase`
- **Functions**: `snake_case`
- **Variables**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private members**: `_leading_underscore`

---

## Dependencies

### System Dependencies

```
build-essential     # Compilation tools
git                 # Version control
cmake              # Build system
python3.13         # Python interpreter
libusb-1.0-0-dev   # USB library
libasound2-dev     # ALSA library
portaudio19-dev    # PortAudio library
pulseaudio         # Audio server
flrig              # Rig control
gqrx-sdr           # SDR receiver
```

### Python Dependencies

```
pyserial           # Serial communication
requests           # HTTP requests
pyyaml             # YAML parsing
pyaudio            # Audio I/O
sounddevice        # Audio device access
numpy              # Numerical computing
psutil             # System monitoring
colorlog           # Colored logging
python-dateutil    # Date/time utilities
typing-extensions  # Type hints
```

---

## Version Control

### Git Structure

```
.gitignore         # Ignored files
- venv/            # Virtual environment
- __pycache__/     # Python cache
- *.pyc            # Compiled Python
- *.log            # Log files
- .DS_Store        # macOS files
```

### Branching Strategy

- `main` - Stable releases
- `develop` - Development branch
- `feature/*` - Feature branches
- `bugfix/*` - Bug fix branches

---

## Testing Strategy

### Test Levels

1. **Unit Tests**: Individual function testing
2. **Integration Tests**: Component interaction testing
3. **System Tests**: Complete system testing
4. **Hardware Tests**: Physical device testing

### Test Execution

```bash
# All tests
python3 tests/TestConnection.py
python3 tests/TestAudio.py
python3 tests/TestCatControl.py

# System diagnostic
python3 tests/DiagnoseSystem.py
```

---

## Build and Deployment

### Installation Process

1. System update
2. Dependency installation
3. FlRig compilation
4. GQRX installation
5. Python environment setup
6. Configuration file creation
7. Permission setup
8. System testing

### Deployment Target

- **Platform**: Raspberry Pi 5
- **OS**: Ubuntu 24.04 LTS
- **Python**: 3.13+
- **Architecture**: ARM64

---

## Maintenance

### Regular Tasks

- **Weekly**: Check logs, test connections
- **Monthly**: Update dependencies, backup config
- **Quarterly**: System updates, documentation review

### Backup Strategy

```bash
# Configuration backup
tar -czf g90_backup.tar.gz config/ logs/

# Full backup
tar -czf g90_full_backup.tar.gz \
    config/ scripts/ tests/ docs/ logs/
```

---

## Contributing

### Code Style

- Follow PEP 8 for Python
- Use type hints
- Document all functions
- Include docstrings
- Add comments for complex logic

### Commit Messages

```
Format: [Type] Short description

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation
- test: Tests
- refactor: Code refactoring
```

---

## Support Files

### Additional Files (Not in Repository)

- `venv/` - Python virtual environment
- `*.log` - Log files
- `__pycache__/` - Python cache
- `*.pyc` - Compiled Python files

---

**This structure supports a maintainable, testable, and well-documented amateur radio SDR system!**
