# G90-SDR Installation Guide

Complete step-by-step installation instructions for Ubuntu 24.04 on Raspberry Pi 5.

## Prerequisites

### Hardware Setup

1. **Raspberry Pi 5 Preparation**
   - Install Ubuntu 24.04 LTS (64-bit) on microSD card or NVMe
   - Recommended: 8GB RAM model for best performance
   - Ensure adequate cooling (heatsinks or active cooling)
   - Connect to network (Ethernet or WiFi)
   - Connect monitor, keyboard, and mouse

2. **Xiegu G90 Setup**
   - Power off the G90
   - Connect antenna
   - Ensure radio is in good working condition

3. **DE-19 Connection**
   - Connect DE-19 to G90's data port (6-pin connector on rear)
   - Connect USB cable from DE-19 to Raspberry Pi USB 3.0 port
   - Verify DE-19 power LED is lit when G90 is on

### Software Prerequisites

1. **Update System**
```bash
sudo apt update
sudo apt upgrade -y
sudo reboot
```

2. **Install Build Tools**
```bash
sudo apt install -y \
    build-essential \
    git \
    cmake \
    pkg-config \
    libusb-1.0-0-dev \
    libasound2-dev \
    portaudio19-dev \
    python3.13 \
    python3.13-dev \
    python3-pip \
    python3-venv
```

## Step 1: System Configuration

### 1.1 Configure Serial Port Access

```bash
# Add current user to dialout group for serial port access
sudo usermod -a -G dialout $USER

# Add user to audio group
sudo usermod -a -G audio $USER

# Reboot for changes to take effect
sudo reboot
```

### 1.2 Disable Serial Console (if needed)

Ubuntu 24.04 may use the serial port for console. Disable it:

```bash
sudo systemctl stop serial-getty@ttyUSB0.service
sudo systemctl disable serial-getty@ttyUSB0.service
```

### 1.3 Configure USB Permissions

Create udev rule for DE-19:

```bash
sudo nano /etc/udev/rules.d/99-xiegu.rules
```

Add the following line:
```
SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", MODE="0666", GROUP="dialout"
```

Reload udev rules:
```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

## Step 2: Install FlRig

### 2.1 Download and Install FlRig

```bash
# Install dependencies
sudo apt install -y \
    libfltk1.3-dev \
    libfltk-images1.3 \
    libfltk-forms1.3 \
    libx11-dev \
    libxinerama-dev \
    libxft-dev \
    libxcursor-dev

# Download FlRig (version 2.0.03 or later)
cd ~/Downloads
wget https://sourceforge.net/projects/fldigi/files/flrig/flrig-2.0.03.tar.gz
tar -xzf flrig-2.0.03.tar.gz
cd flrig-2.0.03

# Build and install
./configure --prefix=/usr/local
make -j4
sudo make install
```

### 2.2 Verify FlRig Installation

```bash
flrig --version
```

## Step 3: Install GQRX

### 3.1 Install GQRX and Dependencies

```bash
sudo apt install -y \
    gqrx-sdr \
    libvolk2-dev \
    librtlsdr-dev \
    libhackrf-dev \
    gnuradio \
    gr-osmosdr
```

### 3.2 Configure PulseAudio

```bash
# Install PulseAudio utilities
sudo apt install -y \
    pulseaudio \
    pulseaudio-utils \
    pavucontrol

# Ensure PulseAudio is running
systemctl --user enable pulseaudio
systemctl --user start pulseaudio
```

## Step 4: Install Python Dependencies

### 4.1 Create Project Directory

```bash
cd ~
mkdir -p G90-SDR
cd G90-SDR
```

### 4.2 Create Virtual Environment

```bash
# Create virtual environment with Python 3.13
python3.13 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

### 4.3 Install Python Packages

Create `requirements.txt`:

```bash
cat > requirements.txt << 'EOF'
# Filename: requirements.txt
# G90-SDR Python Dependencies

# Serial communication
pyserial>=3.5

# XML-RPC for FlRig control
xmlrpc>=1.0.1

# Network communication
requests>=2.31.0

# Configuration file handling
pyyaml>=6.0.1
configparser>=6.0.0

# Audio processing
pyaudio>=0.2.14
sounddevice>=0.4.6

# System monitoring
psutil>=5.9.8

# Logging enhancements
colorlog>=6.8.2

# Date/time utilities
python-dateutil>=2.9.0

# Type checking
typing-extensions>=4.9.0
EOF
```

Install dependencies:

```bash
# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install requirements
pip install -r requirements.txt
```

## Step 5: Install G90-SDR Software

### 5.1 Create Directory Structure

```bash
mkdir -p config scripts tests docs logs
```

### 5.2 Copy Configuration Files

Create FlRig configuration:

```bash
cat > config/flrig_g90.xml << 'EOF'
<?xml version="1.0"?>
<FLRIG>
  <RIG>
    <XCVR>Xiegu G90</XCVR>
    <DEVICE>/dev/ttyUSB0</DEVICE>
    <BAUDRATE>19200</BAUDRATE>
    <RETRIES>5</RETRIES>
    <TIMEOUT>200</TIMEOUT>
    <WRITE_DELAY>0</WRITE_DELAY>
    <INIT_DELAY>0</INIT_DELAY>
    <RESTORE_TTY>1</RESTORE_TTY>
    <CAT_COMMANDS>1</CAT_COMMANDS>
    <RTS_CTS_FLOW>0</RTS_CTS_FLOW>
    <RTSptt>0</RTSptt>
    <DTRptt>0</DTRptt>
  </RIG>
  <SERVER>
    <USE_XML_RPC>1</USE_XML_RPC>
    <PORT>12345</PORT>
    <ADDRESS>127.0.0.1</ADDRESS>
  </SERVER>
</FLRIG>
EOF
```

Create GQRX configuration template:

```bash
cat > config/gqrx_config.conf << 'EOF'
[General]
configversion=2

[input]
device="audio_source=pulse"
sample_rate=48000
bandwidth=1000000
corr=0

[receiver]
offset=0
mode="USB"
sql_level=-150.0
agc=1

[fft]
fft_size=4096
fft_rate=25
averaging=75

[waterfall]
waterfall_span=48000

[remote_control]
enabled=true
port=7356
EOF
```

## Step 6: Configure Audio Routing

### 6.1 Identify Audio Devices

```bash
# List audio devices
aplay -l
arecord -l

# List PulseAudio sinks and sources
pactl list sinks short
pactl list sources short
```

### 6.2 Create Audio Configuration

Create `config/audio_routing.conf`:

```bash
cat > config/audio_routing.conf << 'EOF'
# Filename: config/audio_routing.conf
# Audio routing configuration

[devices]
# Radio input device (from DE-19)
radio_input = default

# Radio output device (to DE-19)
radio_output = default

# Sample rate (Hz)
sample_rate = 48000

# Latency (ms)
latency = 50

[pulseaudio]
# PulseAudio module loading
load_loopback = true
loopback_latency = 50
EOF
```

## Step 7: Hardware Detection and Testing

### 7.1 Detect DE-19 Interface

```bash
# List USB devices
lsusb

# Check for serial devices
ls -l /dev/ttyUSB*

# Monitor device connection
dmesg | grep ttyUSB
```

Expected output should show CH340 USB-to-serial adapter (DE-19).

### 7.2 Test Serial Connection

```bash
# Install screen for serial testing
sudo apt install -y screen

# Connect to radio (press Ctrl+A then K to exit)
screen /dev/ttyUSB0 19200
```

## Step 8: Configure System Services

### 8.1 Create Systemd Service (Optional)

For automatic startup:

```bash
sudo nano /etc/systemd/system/g90-sdr.service
```

Add:
```ini
[Unit]
Description=G90 SDR Interface
After=network.target sound.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/G90-SDR
ExecStart=/home/YOUR_USERNAME/G90-SDR/venv/bin/python3 /home/YOUR_USERNAME/G90-SDR/scripts/start_sdr.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable g90-sdr.service
```

## Step 9: Initial Testing

### 9.1 Test System Components

```bash
# Activate virtual environment
cd ~/G90-SDR
source venv/bin/activate

# Test connection (will create this script next)
python3 tests/TestConnection.py

# Test audio
python3 tests/TestAudio.py

# Test CAT control
python3 tests/TestCatControl.py

# Run full diagnostics
python3 tests/DiagnoseSystem.py
```

## Step 10: First Run

### 10.1 Start FlRig

```bash
flrig &
```

Configure FlRig:
1. Click **Config** → **Setup** → **Transceiver**
2. Select: **Xiegu G90**
3. Set serial port: **/dev/ttyUSB0**
4. Set baud rate: **19200**
5. Click **Init**
6. Click **Close**

### 10.2 Start GQRX

```bash
gqrx &
```

Configure GQRX:
1. Select device string: **other**
2. Set input rate: **48000**
3. Click **OK**
4. Enable **Remote Control** under **Tools**

### 10.3 Start G90-SDR

```bash
cd ~/G90-SDR
source venv/bin/activate
python3 scripts/start_sdr.py
```

## Troubleshooting Installation

### Serial Port Permission Denied

```bash
sudo chmod 666 /dev/ttyUSB0
# Or add user to dialout group and reboot
sudo usermod -a -G dialout $USER
sudo reboot
```

### FlRig Won't Connect

1. Verify G90 is powered on
2. Check DE-19 USB connection
3. Verify serial device: `ls -l /dev/ttyUSB*`
4. Try different baud rates: 19200, 9600

### GQRX Audio Issues

```bash
# Reset PulseAudio
systemctl --user restart pulseaudio

# Check audio devices
pavucontrol
```

### Python Module Import Errors

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall requirements
pip install --force-reinstall -r requirements.txt
```

### USB Device Not Detected

```bash
# Check USB devices
lsusb

# Check dmesg for errors
dmesg | tail -50

# Try different USB port
```

## Performance Optimization

### Raspberry Pi 5 Tweaks

```bash
# Increase GPU memory
sudo nano /boot/firmware/config.txt
# Add: gpu_mem=256

# Set CPU governor to performance
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
```

### Audio Latency Optimization

```bash
# Edit PulseAudio configuration
sudo nano /etc/pulse/daemon.conf

# Uncomment and set:
# default-fragments = 4
# default-fragment-size-msec = 5
```

Restart PulseAudio:
```bash
systemctl --user restart pulseaudio
```

## Post-Installation

### Backup Configuration

```bash
cd ~/G90-SDR
tar -czf g90-sdr-backup.tar.gz config/ scripts/ tests/
```

### Update Software

```bash
cd ~/G90-SDR
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

## Next Steps

1. Read `docs/USER_GUIDE.md` for usage instructions
2. Calibrate audio levels: `python3 tests/CalibrateAudio.py`
3. Configure frequency memory channels
4. Install digital mode software (WSJT-X, fldigi)
5. Optimize for your specific operating preferences

## Support

If you encounter issues:
1. Run `python3 tests/DiagnoseSystem.py`
2. Check `logs/` directory for error messages
3. Consult `docs/TROUBLESHOOTING.md`
4. Post detailed error reports to project issue tracker

## Installation Complete!

Your G90-SDR system is now ready. Enjoy your software-defined radio experience!

73 and happy operating!
