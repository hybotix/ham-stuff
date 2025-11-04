# G90-SDR Quick Reference Card

Fast reference for common commands and operations.

---

## 🔧 Environment Setup

**L_SDR_DIR Environment Variable:**
```bash
# Add to ~/.bashrc:
export L_SDR_DIR=$HOME/Virtual/G90-SDR

# Apply changes:
source ~/.bashrc

# Verify it's set:
echo $L_SDR_DIR
./check_env.sh
```

All scripts use `$L_SDR_DIR` to find the installation directory.

---

## 🚀 Quick Start Commands

```bash
# Navigate to project (uses L_SDR_DIR)
cd $L_SDR_DIR

# Activate environment
source venv/bin/activate

# Start system
python3 scripts/start_sdr.py

# Stop system
python3 scripts/stop_sdr.py
# OR press Ctrl+C
```

---

## 🔧 Diagnostic Commands

```bash
# Complete system check
python3 tests/DiagnoseSystem.py

# Test hardware connection
python3 tests/TestConnection.py

# Test audio devices
python3 tests/TestAudio.py

# Test CAT control
python3 tests/TestCatControl.py

# Calibrate audio levels
python3 tests/CalibrateAudio.py

# Monitor device connections
python3 scripts/device_monitor.py
```

---

## 📁 Important Files

```
config/g90_sdr.yaml          # Main configuration
logs/g90_sdr.log             # Application logs
requirements.txt              # Python dependencies
install.sh                    # Installation script
```

---

## 🎛️ Configuration Locations

**FlRig Settings:**
- File: `config/flrig_g90.xml`
- GUI: Config → Setup → Transceiver

**GQRX Settings:**
- File: `config/gqrx_config.conf`
- GUI: Configure I/O Devices

**System Config:**
- File: `config/g90_sdr.yaml`
- Edit: `nano config/g90_sdr.yaml`

---

## 🔌 Hardware Troubleshooting

**Check USB Connection:**
```bash
lsusb                        # List USB devices
ls -l /dev/ttyUSB*          # List serial ports
dmesg | grep ttyUSB          # Check device messages
```

**Check Permissions:**
```bash
groups                       # Check group membership
sudo usermod -a -G dialout $USER  # Add to dialout
sudo usermod -a -G audio $USER    # Add to audio
sudo reboot                  # Reboot required
```

**Fix Serial Port:**
```bash
sudo chmod 666 /dev/ttyUSB0  # Temporary fix
```

---

## 🔊 Audio Troubleshooting

**List Audio Devices:**
```bash
aplay -l                     # List playback devices
arecord -l                   # List capture devices
pactl list sinks short       # PulseAudio sinks
pactl list sources short     # PulseAudio sources
```

**Restart Audio:**
```bash
systemctl --user restart pulseaudio
```

**Check Audio Levels:**
```bash
pavucontrol                  # GUI volume control
```

---

## 📡 FlRig Commands

**Start FlRig:**
```bash
flrig &
```

**FlRig Configuration:**
1. Config → Setup → Transceiver
2. Select: Xiegu G90
3. Device: /dev/ttyUSB0
4. Baud: 19200
5. Click "Init"

**Enable XML-RPC:**
1. Config → Setup → Server
2. Enable "Use XML-RPC"
3. Port: 12345

---

## 📺 GQRX Commands

**Start GQRX:**
```bash
gqrx &
```

**GQRX Configuration:**
1. Configure I/O Devices
2. Device: Select audio device
3. Sample Rate: 48000
4. Click OK

**Enable Remote Control:**
1. Tools → Remote Control
2. Check "Enable remote control"
3. Port: 7356

---

## 🔍 System Information

**Check System Status:**
```bash
# CPU usage
top

# Memory usage
free -h

# Disk usage
df -h

# Temperature
vcgencmd measure_temp

# Running processes
ps aux | grep -E 'flrig|gqrx|python'
```

---

## 📊 Log Management

**View Logs:**
```bash
# Real-time log viewing
tail -f logs/g90_sdr.log

# View last 50 lines
tail -n 50 logs/g90_sdr.log

# Search logs
grep ERROR logs/g90_sdr.log

# Clear logs
> logs/g90_sdr.log
```

---

## 💾 Backup and Restore

**Backup Configuration:**
```bash
tar -czf g90_backup.tar.gz config/ logs/
```

**Restore Configuration:**
```bash
tar -xzf g90_backup.tar.gz
```

**Backup Entire Project:**
```bash
cd ~
tar -czf g90_full_backup.tar.gz G90-SDR/
```

---

## ⚙️ Common Configuration Changes

**Change Sync Interval:**
```yaml
# Edit config/g90_sdr.yaml
sync:
  interval: 1.0  # Change from 0.5 to 1.0
```

**Change FlRig Port:**
```yaml
flrig:
  port: 12345  # Default port
```

**Change GQRX Sample Rate:**
```yaml
gqrx:
  sample_rate: 48000  # Or 96000 for higher quality
```

---

## 🐛 Emergency Fixes

**Kill All Processes:**
```bash
pkill -9 flrig
pkill -9 gqrx
pkill -9 -f start_sdr.py
```

**Reset Configuration:**
```bash
cd ~/G90-SDR
rm -rf config/
bash install.sh  # Recreate config
```

**Reset PulseAudio:**
```bash
systemctl --user restart pulseaudio
pulseaudio -k
pulseaudio --start
```

**Reset USB Device:**
```bash
# Unplug USB cable, wait 5 seconds, replug
# Or reset USB bus (advanced):
sudo sh -c "echo 0 > /sys/bus/usb/devices/1-1/authorized"
sudo sh -c "echo 1 > /sys/bus/usb/devices/1-1/authorized"
```

---

## 📞 Help Resources

**Documentation:**
```bash
cat README.md                # Project overview
cat INSTALL.md               # Installation guide
cat docs/USER_GUIDE.md       # User guide
cat docs/TROUBLESHOOTING.md  # Troubleshooting
```

**System Diagnostics:**
```bash
python3 tests/DiagnoseSystem.py > diagnostic.txt
cat diagnostic.txt
```

---

## 🎯 Optimal Settings

**Audio Levels:**
- Peak: -12 to -6 dB
- RMS: -20 to -15 dB
- Headroom: 6+ dB

**Performance:**
- FFT Size: 4096 (standard) or 2048 (lower CPU)
- FFT Rate: 25 (standard) or 15 (lower CPU)
- Sample Rate: 48000 Hz

**Sync:**
- Interval: 0.5 seconds (fast) or 1.0 (slower systems)

---

## 🔑 Keyboard Shortcuts

**GQRX:**
- `F` - Full screen
- `Space` - Start/stop receiver
- `M` - Change mode
- `S` - Screenshot
- Mouse wheel - Tune frequency

**Terminal:**
- `Ctrl+C` - Stop current process
- `Ctrl+Z` - Suspend process
- `Ctrl+L` - Clear screen

---

## 🌐 Network Ports

```
12345  # FlRig XML-RPC server
7356   # GQRX remote control
```

**Test Connectivity:**
```bash
telnet localhost 12345       # Test FlRig
telnet localhost 7356        # Test GQRX
```

---

## 📋 Checklist Before Use

- [ ] G90 powered on
- [ ] DE-19 connected via USB
- [ ] USB device detected (`lsusb`)
- [ ] Serial port exists (`ls /dev/ttyUSB*`)
- [ ] User in dialout group (`groups`)
- [ ] Audio device detected (`aplay -l`)
- [ ] FlRig installed (`which flrig`)
- [ ] GQRX installed (`which gqrx`)
- [ ] Python environment activated (`source venv/bin/activate`)

---

## 🚨 Common Error Messages

| Error | Solution |
|-------|----------|
| "Permission denied" | `sudo chmod 666 /dev/ttyUSB0` |
| "No module named..." | `pip install -r requirements.txt` |
| "Connection refused" | Start FlRig/GQRX first |
| "Device not found" | Check USB connection |
| "Import error" | Activate venv: `source venv/bin/activate` |

---

## 📖 Quick Links

- **Installation**: `INSTALL.md`
- **User Guide**: `docs/USER_GUIDE.md`
- **Troubleshooting**: `docs/TROUBLESHOOTING.md`
- **Project Structure**: `docs/PROJECT_STRUCTURE.md`

---

## 💡 Pro Tips

1. **Always activate venv** before running scripts
2. **Check logs first** when troubleshooting
3. **Run diagnostics** regularly
4. **Backup config** before major changes
5. **Use quality USB cables** for reliability
6. **Monitor CPU temperature** during long sessions
7. **Keep system updated** but test after updates
8. **Document custom changes** in config comments

---

**Print this card or save as bookmark for quick reference!**

**73 and happy operating! 📻✨**
