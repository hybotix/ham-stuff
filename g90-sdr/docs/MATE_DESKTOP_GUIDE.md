# G90-SDR MATE Desktop Integration Guide

Complete guide for using G90-SDR with MATE Desktop Environment.

---

## Quick Setup

```bash
cd $L_SDR_DIR
./install_launchers.bash
```

This creates launchers optimized for MATE.

---

## MATE-Specific Features

### 1. Application Menu Integration

Launchers automatically appear in:
- **Applications Menu** → **Internet**
- **Applications Menu** → **AudioVideo**
- Search bar (press `Alt+F2`, type "G90")

### 2. Panel Shortcuts

**Add to Top Panel:**
1. Right-click MATE panel
2. **Add to Panel**
3. **Custom Application Launcher**
4. Click **Browse**
5. Navigate to: `~/.local/share/applications/`
6. Select: `flrig-g90.desktop` or `g90-sdr.desktop`
7. Click **Add**

**Quick Command Option:**
1. Right-click panel → **Add to Panel**
2. Select **Custom Application Launcher**
3. In Command field, enter:
   ```bash
   flrig --rig-file=$L_SDR_DIR/config/flrig_g90.xml --xml-enable --auto-connect
   ```
4. Name it "FlRig G90"
5. Choose icon (optional)

### 3. Desktop Shortcuts

**Create Desktop Icon:**
1. Run `install_launchers.bash` (answer "y" when prompted)
2. Icons appear on desktop
3. Double-click to launch

**Or manually:**
```bash
cp ~/.local/share/applications/g90-sdr.desktop ~/Desktop/
gio set ~/Desktop/g90-sdr.desktop "metadata::trusted" true
```

### 4. Keyboard Shortcuts

**Create Custom Shortcuts:**
1. **System** → **Preferences** → **Hardware** → **Keyboard Shortcuts**
2. Click **Add**
3. Name: "Start G90-SDR"
4. Command: 
   ```bash
   mate-terminal -e "bash -c 'cd $L_SDR_DIR && source venv/bin/activate && python3 scripts/start_sdr.py'"
   ```
5. Click **Add**
6. Click on **Disabled**, press your desired key combo (e.g., `Ctrl+Alt+G`)

---

## MATE Terminal Integration

### Launch with MATE Terminal

The G90-SDR launcher uses `mate-terminal` for proper terminal display:

```bash
mate-terminal --title="G90-SDR System" -e "bash -c 'cd $L_SDR_DIR && source venv/bin/activate && python3 scripts/start_sdr.py'"
```

### Terminal Preferences

**Optimize Terminal for G90-SDR:**
1. Open MATE Terminal
2. **Edit** → **Profiles**
3. Select profile → **Edit**
4. **Scrolling**: Set scrollback to 5000 lines
5. **Colors**: Choose readable color scheme
6. Save

---

## MATE Menu Configuration

### Add HamRadio Category

If HamRadio category doesn't appear:

1. Install menu editor:
   ```bash
   sudo apt install mozo
   ```

2. Open menu editor:
   ```bash
   mozo
   ```

3. Right-click → **New Menu**
4. Name: "Ham Radio"
5. Drag launchers into new category

### Customize Launcher Icons

```bash
# Find available radio icons
ls /usr/share/pixmaps/ | grep -i radio
ls /usr/share/icons/hicolor/48x48/apps/ | grep -i radio

# Edit launcher
nano ~/.local/share/applications/g90-sdr.desktop

# Change Icon= line to one of:
Icon=radio
Icon=network-transmit-receive
Icon=applications-multimedia
```

---

## MATE Autostart (Optional)

**Start G90-SDR at Login:**

1. Create autostart directory:
   ```bash
   mkdir -p ~/.config/autostart
   ```

2. Create autostart entry:
   ```bash
   cat > ~/.config/autostart/g90-sdr.desktop << EOF
   [Desktop Entry]
   Type=Application
   Name=G90-SDR System
   Comment=Start G90-SDR at login
   Exec=bash -c 'sleep 10 && cd $L_SDR_DIR && source venv/bin/activate && python3 scripts/start_sdr.py'
   Hidden=false
   NoDisplay=false
   X-MATE-Autostart-enabled=true
   EOF
   ```

3. Disable if needed:
   - **System** → **Preferences** → **Startup Applications**
   - Uncheck "G90-SDR System"

---

## MATE Panel Applet Ideas

### 1. Quick Launch Panel

Create a custom panel with all radio apps:

1. Right-click panel → **New Panel**
2. Add launchers:
   - FlRig for G90
   - GQRX for G90
   - G90-SDR System
3. Add system monitor (shows CPU/memory usage)

### 2. Command Buttons

**FlRig Only:**
```bash
flrig --rig-file=$L_SDR_DIR/config/flrig_g90.xml --xml-enable --auto-connect
```

**GQRX Only:**
```bash
gqrx
```

**Diagnostics:**
```bash
mate-terminal -e "bash -c 'cd $L_SDR_DIR && python3 tests/DiagnoseSystem.py; read -p \"Press Enter to close\"'"
```

---

## MATE File Manager Integration

### Open Terminal Here

Right-click in Caja (MATE file manager):

1. Navigate to `$L_SDR_DIR`
2. Right-click → **Open in Terminal**
3. Terminal opens with correct path
4. Run: `source venv/bin/activate`
5. Run scripts directly

### Bookmark G90-SDR

1. Open Caja
2. Navigate to `~/Virtual/G90-SDR`
3. **Bookmarks** → **Add Bookmark**
4. Quick access from sidebar

---

## MATE System Tray Integration

### FlRig in System Tray

FlRig can minimize to system tray:
1. Start FlRig
2. **Configure** → **UI** → **Minimize to tray**
3. Check the option
4. Click X to minimize (doesn't quit)

---

## Notification Integration

### Desktop Notifications

Create notification script:

```bash
#!/bin/bash
# Filename: notify_g90.bash
# Send MATE notification when G90-SDR starts

notify-send "G90-SDR" "System starting..." -i radio
sleep 5
notify-send "G90-SDR" "System ready!" -i dialog-information
```

Add to start_sdr.py or launcher.

---

## MATE Theme Compatibility

### Recommended Themes for Readability

Good themes for radio applications:
- **Ambiant-MATE** (default)
- **BlackMATE**
- **TraditionalOK** (high contrast)

Change theme:
- **System** → **Preferences** → **Look and Feel** → **Appearance**

---

## Troubleshooting MATE Integration

### Launcher Doesn't Appear

```bash
# Update desktop database
update-desktop-database ~/.local/share/applications

# Restart MATE panel
killall -HUP mate-panel

# Log out and back in
```

### Icon Not Showing

```bash
# Check icon cache
gtk-update-icon-cache ~/.local/share/icons 2>/dev/null

# Use generic icon
Icon=radio
```

### Terminal Doesn't Stay Open

Edit launcher, change `Terminal=false` to `Terminal=true` or use:
```bash
Exec=mate-terminal --disable-factory -e "command here"
```

---

## MATE Workspace Management

### Dedicated SDR Workspace

1. Create 4 workspaces (right-click workspace switcher)
2. Dedicate Workspace 4 to radio:
   - FlRig on left half
   - GQRX on right half
3. Use `Ctrl+Alt+Down` to switch

### Window Tiling

**Manual Tiling:**
- `Super+Left` - Tile window left
- `Super+Right` - Tile window right
- `Super+Up` - Maximize window

**For G90-SDR:**
1. Start FlRig → Tile left (`Super+Left`)
2. Start GQRX → Tile right (`Super+Right`)
3. Perfect split-screen view!

---

## Example MATE Panel Layout

```
┌─────────────────────────────────────────────────────────────┐
│ [Menu] [FlRig] [GQRX] [G90-SDR]    [Network] [Volume] [Clock]│
└─────────────────────────────────────────────────────────────┘
```

**Create this:**
1. Add Custom Application Launchers for each app
2. Use small icons (16x16 or 24x24)
3. Add separators between sections

---

## Quick Commands for MATE

### Open Terminal at G90-SDR

```bash
mate-terminal --working-directory=$L_SDR_DIR
```

### Run Command in New Window

```bash
mate-terminal --title="Test" -e "python3 tests/TestConnection.py"
```

### Multiple Tabs

```bash
mate-terminal \
  --tab -e "bash -c 'cd $L_SDR_DIR && python3 scripts/start_sdr.py'" \
  --tab -e "bash -c 'cd $L_SDR_DIR && tail -f logs/g90_sdr.log'"
```

---

## MATE + G90-SDR Best Practices

1. **Use Panel Launchers** - Quick access without menu navigation
2. **Dedicated Workspace** - Keep SDR apps organized
3. **Tile Windows** - FlRig left, GQRX right
4. **Bookmark Directory** - Quick Caja access
5. **Custom Shortcuts** - `Ctrl+Alt+G` for quick start
6. **System Tray** - Minimize FlRig when not adjusting

---

## Summary

**Essential Command for MATE Launchers:**
```bash
flrig --rig-file=$L_SDR_DIR/config/flrig_g90.xml --xml-enable --auto-connect
```

**Install All Launchers:**
```bash
cd $L_SDR_DIR
./install_launchers.bash
```

**Access Launchers:**
- Applications Menu → Internet
- Panel shortcuts
- Desktop icons
- Keyboard shortcuts

MATE makes G90-SDR integration simple and efficient! 🖥️📻✨
