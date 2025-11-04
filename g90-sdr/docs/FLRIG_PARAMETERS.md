# FlRig Command Line Parameters

Complete guide to starting FlRig with parameters for GUI launchers.

---

## Basic FlRig Command

```bash
flrig
```

This starts FlRig with default settings.

---

## Important Command Line Parameters

### Configuration File
```bash
flrig --rig-file=/path/to/config.xml
```
Loads a specific rig configuration file.

### Debug Mode
```bash
flrig --debug-level=4
```
Debug levels: 0 (none), 1 (errors), 2 (warnings), 3 (info), 4 (verbose)

### XML-RPC Server Port
```bash
flrig --xml-port=12345
```
Set the XML-RPC server port (default is 12345).

### Enable XML-RPC Server
```bash
flrig --xml-enable
```
Start with XML-RPC server enabled.

### Auto-connect
```bash
flrig --auto-connect
```
Automatically connect to rig on startup.

---

## G90-Specific Command

For the G90-SDR project:

```bash
flrig --rig-file=$L_SDR_DIR/config/flrig_g90.xml --xml-enable --auto-connect
```

**Or with full path:**
```bash
flrig --rig-file=/home/hybotix/Virtual/G90-SDR/config/flrig_g90.xml --xml-enable --auto-connect
```

---

## Common Parameter Combinations

### 1. Basic Auto-start
```bash
flrig --auto-connect
```
Simple - just connects automatically.

### 2. Full Automation
```bash
flrig --rig-file=$L_SDR_DIR/config/flrig_g90.xml --xml-enable --auto-connect --debug-level=1
```
Best for automated startup.

### 3. Development/Debug Mode
```bash
flrig --rig-file=$L_SDR_DIR/config/flrig_g90.xml --xml-enable --auto-connect --debug-level=4
```
Shows detailed debug information.

---

## Desktop Launcher Files

### Create Desktop Shortcut

**Location:** `~/.local/share/applications/flrig-g90.desktop`

**Content:**
```ini
[Desktop Entry]
Version=1.0
Type=Application
Name=FlRig for G90
Comment=FlRig CAT Control for Xiegu G90
Icon=flrig
Exec=/usr/local/bin/flrig --rig-file=/home/hybotix/Virtual/G90-SDR/config/flrig_g90.xml --xml-enable --auto-connect
Terminal=false
Categories=HamRadio;Network;
Keywords=ham;radio;rig;control;CAT;transceiver;
```

### Install Desktop Launcher

```bash
cd $L_SDR_DIR

# Create the desktop file
cat > flrig-g90.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=FlRig for G90
Comment=FlRig CAT Control for Xiegu G90
Icon=flrig
Exec=/usr/local/bin/flrig --rig-file=$L_SDR_DIR/config/flrig_g90.xml --xml-enable --auto-connect
Terminal=false
Categories=HamRadio;Network;
Keywords=ham;radio;rig;control;CAT;transceiver;
EOF

# Install it
desktop-file-install --dir=$HOME/.local/share/applications flrig-g90.desktop

# Update desktop database
update-desktop-database $HOME/.local/share/applications
```

---

## GQRX Desktop Launcher

**Location:** `~/.local/share/applications/gqrx-g90.desktop`

**Content:**
```ini
[Desktop Entry]
Version=1.0
Type=Application
Name=GQRX for G90
Comment=GQRX SDR Receiver for G90
Icon=gqrx
Exec=/usr/bin/gqrx
Terminal=false
Categories=HamRadio;Network;
Keywords=sdr;radio;receiver;waterfall;
```

---

## Complete G90-SDR Launcher

Create a single launcher that starts everything:

**Location:** `~/.local/share/applications/g90-sdr.desktop`

**Content:**
```ini
[Desktop Entry]
Version=1.0
Type=Application
Name=G90-SDR System
Comment=Complete G90 SDR System (FlRig + GQRX + Sync)
Icon=radio
Exec=/home/hybotix/Virtual/G90-SDR/scripts/start_sdr.py
Terminal=true
Categories=HamRadio;Network;
Keywords=sdr;g90;xiegu;ham;radio;
```

---

## FlRig Configuration File Format

Example `flrig_g90.xml`:

```xml
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
  <UI>
    <XCVR_AUTO_ON>1</XCVR_AUTO_ON>
    <XCVR_AUTO_OFF>1</XCVR_AUTO_OFF>
  </UI>
</FLRIG>
```

---

## Verify FlRig Parameters

### Check Available Parameters
```bash
flrig --help
```

### Check FlRig Version
```bash
flrig --version
```

### Test Launch
```bash
# Test from terminal first
flrig --rig-file=$L_SDR_DIR/config/flrig_g90.xml --xml-enable --auto-connect --debug-level=2
```

---

## Troubleshooting Launchers

### Launcher Doesn't Work

1. **Check FlRig Path**
   ```bash
   which flrig
   # Should show: /usr/local/bin/flrig
   ```

2. **Check Config File Exists**
   ```bash
   ls -la $L_SDR_DIR/config/flrig_g90.xml
   ```

3. **Test Command Manually**
   ```bash
   /usr/local/bin/flrig --rig-file=$L_SDR_DIR/config/flrig_g90.xml
   ```

4. **Check Desktop File Syntax**
   ```bash
   desktop-file-validate ~/.local/share/applications/flrig-g90.desktop
   ```

### Icon Not Showing

Copy FlRig icon:
```bash
sudo cp /usr/local/share/pixmaps/flrig.xpm /usr/share/pixmaps/
```

Or use generic icon:
```ini
Icon=radio
# or
Icon=network-transmit-receive
```

---

## Creating Launchers Script

Create an automated script to install all launchers:

```bash
#!/bin/bash
# Filename: install_launchers.bash
# Install desktop launcher files

LAUNCHER_DIR="$HOME/.local/share/applications"
mkdir -p "$LAUNCHER_DIR"

# FlRig Launcher
cat > "$LAUNCHER_DIR/flrig-g90.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=FlRig for G90
Comment=FlRig CAT Control for Xiegu G90
Icon=flrig
Exec=/usr/local/bin/flrig --rig-file=$L_SDR_DIR/config/flrig_g90.xml --xml-enable --auto-connect
Terminal=false
Categories=HamRadio;Network;
Keywords=ham;radio;rig;control;CAT;transceiver;
EOF

# GQRX Launcher
cat > "$LAUNCHER_DIR/gqrx-g90.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=GQRX for G90
Comment=GQRX SDR Receiver
Icon=gqrx
Exec=/usr/bin/gqrx
Terminal=false
Categories=HamRadio;Network;
Keywords=sdr;radio;receiver;waterfall;
EOF

# G90-SDR Complete System Launcher
cat > "$LAUNCHER_DIR/g90-sdr.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=G90-SDR System
Comment=Complete G90 SDR System
Icon=radio
Exec=$L_SDR_DIR/scripts/start_sdr.py
Terminal=true
Categories=HamRadio;Network;
Keywords=sdr;g90;xiegu;ham;radio;
Path=$L_SDR_DIR
EOF

# Make executable
chmod +x "$LAUNCHER_DIR"/*.desktop

# Update desktop database
update-desktop-database "$LAUNCHER_DIR"

echo "✓ Desktop launchers installed"
echo "  - FlRig for G90"
echo "  - GQRX for G90"
echo "  - G90-SDR System"
echo ""
echo "Look for them in your application menu!"
```

---

## Summary

### Minimum Command
```bash
flrig
```

### Recommended for G90-SDR
```bash
flrig --rig-file=$L_SDR_DIR/config/flrig_g90.xml --xml-enable --auto-connect
```

### Full Desktop Launcher
Use the `.desktop` file format with the recommended command in the `Exec=` line.

---

**The key parameters you need:**
1. `--rig-file` - Points to your G90 config
2. `--xml-enable` - Enables remote control for frequency sync
3. `--auto-connect` - Automatically connects to radio on startup

These three parameters make FlRig fully automated and ready for G90-SDR! 📻✨
