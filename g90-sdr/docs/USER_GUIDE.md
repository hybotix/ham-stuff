# G90-SDR User Guide

Complete guide to operating your Xiegu G90 as a software-defined radio.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Daily Operation](#daily-operation)
3. [Features and Functions](#features-and-functions)
4. [Configuration](#configuration)
5. [Tips and Best Practices](#tips-and-best-practices)
6. [Advanced Usage](#advanced-usage)

---

## Quick Start

### First Time Setup

1. **Hardware Connection**
   ```bash
   G90 → DE-19 → USB → Raspberry Pi
   ```
   - Connect DE-19 to G90's data port
   - Connect USB cable to Raspberry Pi
   - Power on G90

2. **Software Startup**
   ```bash
   cd ~/G90-SDR
   source venv/bin/activate
   python3 scripts/start_sdr.py
   ```

3. **What You'll See**
   - FlRig opens (rig control interface)
   - GQRX opens (waterfall display)
   - Frequency automatically syncs

### Basic Operation

**Tuning**: Change frequency on G90 → GQRX follows automatically

**Mode Selection**: Change mode on G90 → GQRX switches mode

**Waterfall Display**: Real-time spectrum view in GQRX

---

## Daily Operation

### Starting the System

```bash
# Navigate to project directory
cd ~/G90-SDR

# Activate Python environment
source venv/bin/activate

# Start G90-SDR
python3 scripts/start_sdr.py
```

**Expected startup sequence:**
1. FlRig starts (3 seconds)
2. GQRX starts (5 seconds)
3. Frequency sync starts
4. System ready message

### Stopping the System

**Method 1: Graceful Shutdown**
```bash
# Press Ctrl+C in terminal running start_sdr.py
```

**Method 2: Stop Script**
```bash
python3 scripts/stop_sdr.py
```

**Method 3: Manual**
- Close GQRX window
- Close FlRig window
- Press Ctrl+C in terminal

---

## Features and Functions

### FlRig Functions

**Frequency Control**
- Direct frequency entry
- VFO A/B switching
- Memory channels
- Band selection

**Mode Selection**
- USB, LSB, CW, AM, FM
- Bandwidth adjustment
- Filter selection

**Power Control**
- Adjustable 0-10W output
- SWR monitoring
- Power meter

### GQRX Functions

**Waterfall Display**
- Real-time spectrum
- Adjustable color maps
- Zoom and pan
- Center frequency tracking

**Receiver Controls**
- RF gain
- SQL threshold
- AGC settings
- Audio recording

**Signal Analysis**
- FFT display
- Signal strength
- Frequency markers
- Bandwidth visualization

### Frequency Synchronization

**Automatic Features:**
- G90 frequency → GQRX (every 0.5s)
- Mode changes synchronized
- Bandwidth tracking (optional)

**Configuration:**
```bash
# Edit sync interval
nano config/g90_sdr.yaml

sync:
  enabled: true
  interval: 0.5  # seconds
  sync_mode: true
  sync_bandwidth: false
```

---

## Configuration

### Main Configuration File

Location: `config/g90_sdr.yaml`

```yaml
flrig:
  host: 127.0.0.1      # FlRig server
  port: 12345          # XML-RPC port
  device: /dev/ttyUSB0 # Serial device
  baudrate: 19200      # G90 baud rate

gqrx:
  host: 127.0.0.1      # GQRX server
  port: 7356           # Remote control port
  sample_rate: 48000   # Audio sample rate
  fft_size: 4096       # FFT resolution

audio:
  sample_rate: 48000   # Audio sample rate
  latency_ms: 50       # Audio latency

sync:
  enabled: true        # Enable sync
  interval: 0.5        # Sync interval
```

### Audio Configuration

**Find Audio Devices:**
```bash
python3 tests/TestAudio.py
```

**Set Default Device:**
Edit `config/g90_sdr.yaml`:
```yaml
audio:
  input_device: 2   # Device number
  output_device: 2
```

### FlRig Configuration

**G90 Settings in FlRig:**
1. Open FlRig
2. Config → Setup → Transceiver
3. Select: Xiegu G90
4. Serial Port: /dev/ttyUSB0
5. Baud Rate: 19200
6. Click "Init"

**XML-RPC Server:**
1. Config → Setup → Server
2. Enable "Use XML-RPC"
3. Port: 12345
4. Address: 127.0.0.1

### GQRX Configuration

**Remote Control:**
1. Tools → Remote Control
2. Check "Enable remote control"
3. Port: 7356

**Audio Device:**
1. Configure I/O Devices
2. Input: Select your DE-19/sound card
3. Sample Rate: 48000 Hz
4. Decimation: None

---

## Tips and Best Practices

### Audio Levels

**Optimal Settings:**
- Peak: -12 to -6 dB
- RMS: -20 to -15 dB
- Headroom: Minimum 6 dB

**Calibration:**
```bash
python3 tests/CalibrateAudio.py
```

**Adjust on G90:**
- Use G90's AF gain control
- Start low, increase gradually
- Monitor waterfall for clipping

### Performance Optimization

**Reduce CPU Usage:**
```yaml
# In config/g90_sdr.yaml
gqrx:
  fft_size: 2048  # Lower = less CPU
  fft_rate: 15    # Lower = less CPU
```

**Reduce Latency:**
```yaml
audio:
  latency_ms: 25  # Lower = less latency
sync:
  interval: 0.25  # Faster sync
```

**Improve Stability:**
- Use USB 3.0 ports
- Avoid USB hubs
- Keep cables short
- Use ferrite cores

### Operating Tips

**For CW:**
- Set narrow bandwidth (500 Hz)
- Use CW mode in both G90 and GQRX
- Adjust audio for comfortable tone

**For SSB:**
- Use 2.4-3.0 kHz bandwidth
- Monitor audio levels carefully
- Adjust RF gain for strong signals

**For Digital Modes:**
- Keep audio levels moderate
- Use USB mode for RTTY/PSK
- Monitor waterfall for proper centering

**For Weak Signal Work:**
- Reduce RF gain on strong signals
- Use narrower IF bandwidth
- Enable AGC in GQRX

---

## Advanced Usage

### Multiple Display Windows

**Run GQRX on separate monitor:**
```bash
DISPLAY=:0.1 gqrx &
```

### Remote Operation

**Access from another computer:**
1. Change FlRig host to Pi's IP
2. Change GQRX host to Pi's IP
3. Forward ports 12345 and 7356

### Custom Scripts

**Create frequency presets:**
```python
from scripts.rig_control import RigControl

rig = RigControl()
rig.connect()

# Set to 14.074 MHz (FT8)
rig.set_frequency(14074000)
rig.set_mode('USB')
```

**Automate band scanning:**
```python
for freq in range(14000000, 14350000, 1000):
    rig.set_frequency(freq)
    time.sleep(0.5)
```

### Integration with Other Software

**WSJT-X Configuration:**
1. File → Settings → Radio
2. Rig: Hamlib NET rigctl
3. Network Server: localhost:12345
4. Data Mode: USB

**fldigi Configuration:**
1. Configure → Rig Control → Hamlib
2. Device: NET rigctl
3. Device: localhost:12345

### Logging

**View System Logs:**
```bash
tail -f logs/g90_sdr.log
```

**Debug Mode:**
```bash
# Edit scripts, change logging level:
logging.basicConfig(level=logging.DEBUG)
```

### Backup Configuration

**Save Settings:**
```bash
tar -czf g90_backup.tar.gz config/ logs/
```

**Restore Settings:**
```bash
tar -xzf g90_backup.tar.gz
```

---

## Keyboard Shortcuts

### GQRX Shortcuts

- **F**: Toggle full screen
- **Space**: Toggle receiver
- **M**: Toggle demodulator
- **S**: Take screenshot
- **L**: Toggle signal lock
- **Ctrl+W**: Close window
- **Mouse wheel**: Tune frequency

### FlRig Shortcuts

- **Ctrl+Q**: Quit
- **Up/Down**: Frequency up/down
- **Left/Right**: Band up/down

---

## Monitoring Performance

### Check System Health

```bash
python3 tests/DiagnoseSystem.py
```

### Monitor Connection

```bash
python3 scripts/device_monitor.py
```

### Check Audio Quality

```bash
python3 tests/TestAudio.py
```

---

## Common Workflows

### Contest Operation

1. Start G90-SDR
2. Set bandwidth to 2.4 kHz
3. Enable AGC in GQRX
4. Use waterfall to find stations
5. Click on signals to tune

### DX Hunting

1. Enable wide bandwidth (5+ kHz)
2. Watch waterfall for activity
3. Use zoom for precise tuning
4. Record interesting signals

### Digital Mode Operation

1. Connect WSJT-X or fldigi
2. Set appropriate mode
3. Monitor waterfall for decoding
4. Let G90-SDR handle frequency control

---

## Getting Help

**System Diagnostics:**
```bash
python3 tests/DiagnoseSystem.py
```

**Check Logs:**
```bash
cat logs/g90_sdr.log
```

**Test Components:**
- Connection: `python3 tests/TestConnection.py`
- Audio: `python3 tests/TestAudio.py`
- CAT: `python3 tests/TestCatControl.py`

**Community Support:**
- Project documentation
- Amateur radio forums
- GitHub issues

---

## Safety and Regulations

- Always follow your local amateur radio regulations
- Ensure proper licensing for transmit operations
- Monitor power output to prevent equipment damage
- Use proper antenna for frequency range
- Follow good amateur practice

---

**73 and enjoy your G90-SDR!**
