#!/bin/bash
# Filename: create_universal_launchers.bash
# Create universal desktop launchers that work for any user

echo "════════════════════════════════════════════════════════════════"
echo "  Creating Universal G90-SDR Launchers"
echo "════════════════════════════════════════════════════════════════"
echo ""

LAUNCHER_DIR="$HOME/.local/share/applications"
mkdir -p "$LAUNCHER_DIR"

echo "Creating universal desktop launchers..."
echo ""

# 1. Universal FlRig Launcher
cat > "$LAUNCHER_DIR/flrig-g90.desktop" << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=FlRig for G90
GenericName=Rig Control
Comment=FlRig CAT Control for Xiegu G90 (Auto-configured)
Icon=flrig
Exec=g90-flrig
Terminal=false
Categories=HamRadio;Network;AudioVideo;
Keywords=ham;radio;rig;control;CAT;transceiver;g90;xiegu;
StartupNotify=true
EOF
chmod +x "$LAUNCHER_DIR/flrig-g90.desktop"
echo "  ✓ FlRig G90 launcher (universal)"

# 2. Universal GQRX Launcher
cat > "$LAUNCHER_DIR/gqrx-g90.desktop" << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=GQRX for G90
GenericName=SDR Receiver
Comment=GQRX SDR Receiver with Waterfall Display
Icon=gqrx
Exec=gqrx
Terminal=false
Categories=HamRadio;Network;AudioVideo;
Keywords=sdr;radio;receiver;waterfall;spectrum;g90;
StartupNotify=true
EOF
chmod +x "$LAUNCHER_DIR/gqrx-g90.desktop"
echo "  ✓ GQRX G90 launcher"

# 3. Universal G90-SDR System Launcher
cat > "$LAUNCHER_DIR/g90-sdr.desktop" << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=G90-SDR System
GenericName=SDR System
Comment=Complete G90 SDR System (FlRig + GQRX + Sync)
Icon=radio
Exec=g90-sdr
Terminal=true
Categories=HamRadio;Network;AudioVideo;
Keywords=sdr;g90;xiegu;ham;radio;amateur;
StartupNotify=true
EOF
chmod +x "$LAUNCHER_DIR/g90-sdr.desktop"
echo "  ✓ G90-SDR System launcher (universal)"

# 4. Safe Start Launcher
cat > "$LAUNCHER_DIR/g90-sdr-safe.desktop" << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=G90-SDR Safe Start
GenericName=SDR Safe Mode
Comment=Start G90-SDR with troubleshooting steps
Icon=dialog-warning
Exec=bash -c 'SDR=$(g90-sdr --find 2>/dev/null); if [ -n "$SDR" ]; then cd "$SDR" && source venv/bin/activate && python3 scripts/safe_start.py; else echo "G90-SDR not found"; read -p "Press Enter"; fi'
Terminal=true
Categories=HamRadio;System;
Keywords=sdr;g90;troubleshoot;safe;debug;
StartupNotify=true
EOF
chmod +x "$LAUNCHER_DIR/g90-sdr-safe.desktop"
echo "  ✓ Safe Start launcher"

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$LAUNCHER_DIR" 2>/dev/null
    echo ""
    echo "  ✓ Desktop database updated"
fi

# Refresh MATE panel if present
if command -v mate-panel &> /dev/null; then
    killall -HUP mate-panel 2>/dev/null || true
    echo "  ✓ MATE menu refreshed"
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  Universal Launchers Created!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "IMPORTANT: These launchers require wrapper scripts!"
echo ""
echo "To complete setup, run:"
echo "  sudo bash install_wrappers.bash"
echo ""
echo "This installs:"
echo "  • /usr/local/bin/g90-sdr      (system launcher)"
echo "  • /usr/local/bin/g90-flrig    (FlRig launcher)"
echo ""
echo "Benefits:"
echo "  ✅ Works for ANY user on this system"
echo "  ✅ Works with ANY installation location"
echo "  ✅ Auto-detects G90-SDR directory"
echo "  ✅ No hardcoded paths"
echo "  ✅ Ready for public distribution"
echo ""
echo "After installing wrappers, launchers will appear in:"
echo "  • Applications Menu"
echo "  • Desktop Environment menus"
echo "  • Can be run from terminal: g90-sdr"
echo ""
