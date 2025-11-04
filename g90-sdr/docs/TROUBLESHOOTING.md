# G90-SDR Troubleshooting Guide

Solutions to common issues and problems.

## Quick Diagnostic

**Run this first:**
```bash
cd ~/G90-SDR
source venv/bin/activate
python3 tests/DiagnoseSystem.py
```

This will identify most common issues automatically.

---

## Connection Issues

### Problem: "No serial devices found"

**Symptoms:**
- TestConnection.py shows no devices
- /dev/ttyUSB0 doesn't exist

**Solutions:**

1. **Check USB Connection**
   ```bash
   lsusb
   ```
   Look for: `QinHeng Electronics CH340` or similar

2. **Check dmesg**
   ```bash
   dmesg | grep ttyUSB
   ```
   Should show device attachment

3. **Try Different USB Port**
   - Use USB 3.0 ports (blue)
   - Avoid USB hubs
   - Try different cable

4. **Check DE-19 Power**
   - Power LED should be lit
   - G90 must be powered on
   - Check 6-pin data cable connection

### Problem: "Permission denied" on /dev/ttyUSB0

**Symptoms:**
- Device exists but can't open it
- "Permission denied" error

**Solutions:**

1. **Check Group Membership**
   ```bash
   groups
   ```
   Should include `dialout`

2. **Add User to dialout Group**
   ```bash
   sudo usermod -a -G dialout $USER
   sudo reboot
   ```

3. **Temporary Fix (not recommended)**
   ```bash
   sudo chmod 666 /dev/ttyUSB0
   ```

4. **Verify udev Rules**
   ```bash
   cat /etc/udev/rules.d/99-xiegu.rules
   ```
   Should contain CH340 rule

### Problem: FlRig won't connect to G90

**Symptoms:**
- FlRig shows "Not Connected"
- Red status indicator
- No response to commands

**Solutions:**

1. **Check G90 Settings**
   - Ensure G90 is in CAT control mode
   - Check menu settings for serial enable
   - Verify baud rate is 19200

2. **FlRig Configuration**
   - Config → Setup → Transceiver
   - Select: Xiegu G90
   - Device: /dev/ttyUSB0
   - Baud: 19200
   - Click "Init"

3. **Test Serial Connection**
   ```bash
   python3 tests/TestConnection.py
   ```

4. **Restart Everything**
   ```bash
   # Close FlRig
   # Power cycle G90
   # Restart FlRig
   ```

5. **Check for Conflicting Software**
   ```bash
   lsof /dev/ttyUSB0
   ```
   Kill any processes using the port

---

## Audio Issues

### Problem: No audio in GQRX

**Symptoms:**
- Waterfall is flat/empty
- No audio levels
- Silent reception

**Solutions:**

1. **Check Audio Device**
   ```bash
   python3 tests/TestAudio.py
   ```

2. **Verify PulseAudio**
   ```bash
   systemctl --user status pulseaudio
   ```
   Should be running

3. **Check Device Selection in GQRX**
   - Configure I/O Devices
   - Ensure correct input device selected
   - Sample rate: 48000 Hz

4. **Test Audio Loopback**
   ```bash
   pactl list sources short
   pactl list sinks short
   ```

5. **Restart PulseAudio**
   ```bash
   systemctl --user restart pulseaudio
   ```

6. **Check G90 Audio Output**
   - Verify AF gain is not zero
   - Check volume on DE-19
   - Test with headphones first

### Problem: Audio is distorted/clipping

**Symptoms:**
- Harsh, distorted audio
- Flat-topped waveforms
- Red clipping indicators

**Solutions:**

1. **Run Audio Calibration**
   ```bash
   python3 tests/CalibrateAudio.py
   ```

2. **Reduce Input Level**
   - Lower G90 AF gain
   - Reduce volume on DE-19
   - Check computer input level

3. **Target Levels**
   - Peak: -12 to -6 dB
   - RMS: -20 to -15 dB
   - Maintain 6+ dB headroom

4. **Check for Ground Loops**
   - Use ferrite cores
   - Isolate power supplies
   - Check cable shielding

### Problem: Audio is too quiet

**Symptoms:**
- Very low levels
- Barely audible
- Weak signals in waterfall

**Solutions:**

1. **Increase G90 Output**
   - Raise AF gain
   - Check menu audio settings
   - Verify data port audio level

2. **Check GQRX Settings**
   - Increase RF gain
   - Adjust audio gain slider
   - Enable AGC

3. **Verify Device**
   ```bash
   python3 tests/TestAudio.py
   ```
   Check that correct device is selected

---

## GQRX Issues

### Problem: GQRX won't start

**Symptoms:**
- Application crashes
- Error on startup
- Window doesn't appear

**Solutions:**

1. **Check Installation**
   ```bash
   which gqrx
   gqrx --version
   ```

2. **Delete Configuration**
   ```bash
   rm -rf ~/.config/gqrx
   ```
   Restart GQRX

3. **Check Audio Device Conflicts**
   ```bash
   # Kill processes using audio
   fuser -k /dev/snd/*
   ```

4. **Run from Terminal**
   ```bash
   gqrx 2>&1 | tee gqrx_error.log
   ```
   Check error messages

5. **Check Graphics**
   - Ensure X server is running
   - Verify display settings
   - Update graphics drivers

### Problem: Remote control not working

**Symptoms:**
- Can't connect to port 7356
- Frequency sync not working
- Commands ignored

**Solutions:**

1. **Enable Remote Control in GQRX**
   - Tools → Remote Control
   - Check "Enable remote control"
   - Port: 7356

2. **Test Connection**
   ```bash
   telnet localhost 7356
   # Type: f
   # Should return frequency
   ```

3. **Check Firewall**
   ```bash
   sudo ufw status
   # If active, allow port:
   sudo ufw allow 7356
   ```

4. **Restart GQRX**
   Close and reopen GQRX

---

## Frequency Sync Issues

### Problem: GQRX not following G90 frequency

**Symptoms:**
- Changing G90 frequency doesn't update GQRX
- Manual sync works, automatic doesn't
- Sync seems delayed

**Solutions:**

1. **Check Sync Status**
   ```bash
   # Look for sync messages in logs
   tail -f logs/g90_sdr.log
   ```

2. **Verify FlRig Connection**
   - FlRig must be connected
   - XML-RPC server must be enabled
   - Port 12345 must be accessible

3. **Verify GQRX Remote Control**
   - Must be enabled
   - Port 7356 must be accessible

4. **Adjust Sync Interval**
   ```yaml
   # In config/g90_sdr.yaml
   sync:
     interval: 0.5  # Try 1.0 for slower systems
   ```

5. **Restart Sync Service**
   ```bash
   python3 scripts/stop_sdr.py
   python3 scripts/start_sdr.py
   ```

### Problem: Mode doesn't sync

**Symptoms:**
- Frequency syncs but not mode
- Mode changes ignored

**Solutions:**

1. **Check Mode Sync Setting**
   ```yaml
   # In config/g90_sdr.yaml
   sync:
     sync_mode: true  # Must be true
   ```

2. **Verify Mode Compatibility**
   - Some modes may not map directly
   - Check FlRig mode display
   - Manually set mode in GQRX

---

## Performance Issues

### Problem: System is slow/laggy

**Symptoms:**
- High CPU usage
- Delayed response
- Choppy waterfall

**Solutions:**

1. **Check CPU Usage**
   ```bash
   top
   ```
   Look for high CPU processes

2. **Optimize GQRX Settings**
   ```yaml
   gqrx:
     fft_size: 2048   # Lower value
     fft_rate: 15     # Lower value
   ```

3. **Close Unnecessary Programs**
   - Close web browsers
   - Stop background services
   - Kill unused processes

4. **Check System Resources**
   ```bash
   python3 tests/DiagnoseSystem.py
   ```

5. **Cooling**
   - Ensure adequate cooling
   - Check CPU temperature
   - Add heatsinks/fan

### Problem: High memory usage

**Symptoms:**
- System becomes unresponsive
- Out of memory errors
- Swap usage high

**Solutions:**

1. **Check Memory**
   ```bash
   free -h
   ```

2. **Restart Services**
   ```bash
   python3 scripts/stop_sdr.py
   python3 scripts/start_sdr.py
   ```

3. **Reduce Buffer Sizes**
   - Lower FFT size
   - Reduce waterfall history
   - Disable recording

---

## Installation Issues

### Problem: Python module import errors

**Symptoms:**
- ImportError messages
- ModuleNotFoundError
- Missing dependencies

**Solutions:**

1. **Activate Virtual Environment**
   ```bash
   source venv/bin/activate
   ```

2. **Reinstall Requirements**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Check Python Version**
   ```bash
   python3 --version
   # Should be 3.13 or later
   ```

4. **Install System Packages**
   ```bash
   sudo apt install python3-dev portaudio19-dev
   ```

### Problem: FlRig compile errors

**Symptoms:**
- Build fails
- Missing dependencies
- Configuration errors

**Solutions:**

1. **Install Build Dependencies**
   ```bash
   sudo apt install -y \
       libfltk1.3-dev \
       libfltk-images1.3 \
       libx11-dev
   ```

2. **Clean Build**
   ```bash
   cd /tmp/flrig-2.0.03
   make clean
   ./configure
   make
   ```

3. **Check Configure Output**
   Look for missing dependencies

---

## Hardware Issues

### Problem: DE-19 not detected

**Symptoms:**
- No CH340 device found
- USB device not recognized
- Power LED off

**Solutions:**

1. **Check Connections**
   - 6-pin cable to G90
   - USB cable to Pi
   - All connections secure

2. **Check G90 Power**
   - G90 must be on
   - DE-19 powered from G90

3. **Try Different Cable**
   - Use quality USB cable
   - Check for damage
   - Try different USB port

4. **Check USB Power**
   ```bash
   lsusb -v | grep MaxPower
   ```

### Problem: Intermittent disconnections

**Symptoms:**
- Device randomly disconnects
- Connection drops during use
- Frequent reconnections

**Solutions:**

1. **Check Cable Quality**
   - Use shielded cables
   - Avoid long cables
   - Add ferrite cores

2. **Check USB Power**
   - Use powered USB hub
   - Check Pi power supply
   - Monitor voltage

3. **Monitor Connections**
   ```bash
   python3 scripts/device_monitor.py
   ```

4. **Check for Interference**
   - Move away from RF sources
   - Use ferrite cores
   - Ground properly

---

## Emergency Recovery

### System Won't Boot

1. **Boot to Recovery**
   - Hold Shift during boot
   - Select recovery mode

2. **Check SD Card**
   - Test on another device
   - Check for corruption
   - Backup and reimage

### Complete Reset

```bash
# Backup configuration
tar -czf backup.tar.gz config/

# Remove installation
rm -rf ~/G90-SDR

# Reinstall
git clone <repository> G90-SDR
cd G90-SDR
bash install.sh

# Restore config
tar -xzf backup.tar.gz
```

---

## Getting More Help

### Collect Diagnostic Information

```bash
# Run diagnostics
python3 tests/DiagnoseSystem.py > diagnostic.txt

# Collect logs
tar -czf g90_logs.tar.gz logs/ diagnostic.txt

# Check system info
uname -a >> diagnostic.txt
lsusb >> diagnostic.txt
```

### Before Asking for Help

1. Run `DiagnoseSystem.py`
2. Check logs in `logs/g90_sdr.log`
3. Note exact error messages
4. List what you've tried
5. Provide system information

### Support Channels

- GitHub Issues
- Amateur radio forums
- Documentation in `docs/`
- System logs in `logs/`

---

## Preventive Maintenance

**Weekly:**
- Check connections
- Verify audio levels
- Review logs

**Monthly:**
- Update software
- Backup configuration
- Test all functions

**As Needed:**
- Update Ubuntu
- Upgrade Python packages
- Clean dust from Pi

---

**Remember: Most issues are connection or configuration related. Start with the basics!**
