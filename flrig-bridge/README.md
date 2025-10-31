# FlRig Bridge - Universal Rig Control for Xiegu G90

A Python bridge system that enables the Xiegu G90 to work reliably with any Hamlib-compatible software by using FlRig as a backend. Solves the critical issue where Hamlib's native G90 driver causes unwanted transmit triggering.

## Features

- **Fast GQRX Panadapter**: Dedicated bridge provides responsive bidirectional sync between GQRX and your G90
- **Universal rigctld Server**: Hamlib-compatible server that any rigctld client can connect to
- **Multi-Radio Ready**: Organized configuration structure supports multiple radios easily
- **PTT Protection**: Ignores all PTT commands to prevent accidental transmit
- **No Transmit Bug**: Bypasses Hamlib's buggy G90 driver by using FlRig's reliable CAT implementation
- **Lightweight**: Pure Python with minimal dependencies
- **Modular Design**: Separate specialized bridges instead of one monolithic solution

## The Problem This Solves

The Xiegu G90's implementation in Hamlib (model 3088) has a critical bug where certain CAT commands trigger transmit mode unexpectedly. This makes it dangerous to use with rigctld-based applications like GQRX, fldigi, and logging software.

This bridge system solves the problem by routing all rig control through FlRig, which implements G90 CAT control correctly, while providing standard interfaces for other software.

## Architecture

```
┌──────────────────────────────────────────────┐
│                   FlRig                       │
│            (XML-RPC: 12345)                   │
│          Single source of truth               │
└─────────┬──────────────────┬─────────────────┘
          │                  │
    ┌─────▼────────┐   ┌─────▼──────────────┐
    │ GQRX Bridge  │   │ rigctld Server     │
    │ (Fast sync)  │   │ (Port 4533)        │
    └─────┬────────┘   └─────┬──────────────┘
          │                  │
    ┌─────▼────────┐   ┌─────▼──────────────┐
    │    GQRX      │   │  fldigi, logging,  │
    │ Panadapter   │   │  other Hamlib SW   │
    └──────────────┘   └────────────────────┘
```

**Two specialized bridges:**
- **flrig-gqrx-bridge.py**: Handles GQRX ↔ FlRig synchronization only
- **flrig-rigctld-server.py**: Provides rigctld server for other software only

Each bridge does one job well, resulting in better performance and reliability than a monolithic solution.

## Hardware Requirements

- **Xiegu G90** HF transceiver
- **Audio Interface** for IF/audio output (e.g., SignaLink USB, any USB sound card)
- **Computer** running Linux (tested on Raspberry Pi 5 with Ubuntu 24.04)
- **USB connection** from G90 to computer for CAT control

## Software Prerequisites

- **Python 3** (3.7 or newer)
- **FlRig** - Rig control software ([http://www.w1hkj.com/](http://www.w1hkj.com/))
- **GQRX** (optional) - SDR software for waterfall display ([https://gqrx.dk/](https://gqrx.dk/))

### Installing Prerequisites

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 flrig gqrx-sdr
```

**Raspberry Pi OS:**
```bash
sudo apt update
sudo apt install python3 flrig gqrx-sdr
```

## Installation

1. Clone this repository:
```bash
git clone git@github.com:hybotix/ham-stuff.git
cd ham-stuff/flrig-bridge
```

2. Make the scripts executable:
```bash
chmod +x flrig-gqrx-bridge.py
chmod +x flrig-rigctld-server.py
chmod +x start-*.bash
```

3. Copy scripts to your home directory (or run from repo):
```bash
cp flrig-gqrx-bridge.py ~/
cp flrig-rigctld-server.py ~/
cp start-*.bash ~/
```

## Configuration

### FlRig Setup

FlRig configurations are organized by radio/purpose in `~/.flrig/`:

```
~/.flrig/
├── g90-sdr/          # G90 SDR panadapter config
│   ├── flrig.prefs
│   └── Xiegu-G90.prefs
├── g90-portable/     # (Future) Portable ops config
└── ic7300-main/      # (Future) Different radio
```

**Initial setup:**

1. Create config directory:
```bash
mkdir -p ~/.flrig/g90-sdr
```

2. Start FlRig with this config:
```bash
flrig --config-dir ~/.flrig/g90-sdr --xmlrpc-server-port 12345
```

3. Configure FlRig for Xiegu G90:
   - **Config → Setup → Transceiver**
   - Select "Xiegu G90"
   - Set serial port (usually `/dev/ttyUSB0`)
   - Set baud rate: 19200
   - Test connection

4. Verify XML-RPC server:
   - **Config → Setup → Server**
   - Should show XML-RPC enabled on port 12345

5. Close FlRig - configuration is saved automatically

### GQRX Setup (Optional, for panadapter)

1. Start GQRX
2. Configure audio input device (your USB sound card/interface)
3. Enable remote control:
   - **Tools → Remote Control**
   - Note the port (usually 4532)

Or edit `~/.config/gqrx/default.conf`:
```ini
[remote_control]
allowed_hosts=127.0.0.1
enabled=true
port=4532
```

## Usage

### Quick Start - SDR Panadapter Only

For GQRX waterfall display with rig control:

```bash
./start-g90-sdr.bash
```

This starts:
- FlRig (with G90-SDR config)
- GQRX (SDR waterfall)
- GQRX bridge (synchronization)

### Quick Start - Complete Station Setup

For GQRX panadapter PLUS rigctld server for other software:

```bash
./start-ham-radio-setup.bash
```

This starts:
- FlRig
- GQRX + GQRX bridge
- rigctld server (port 4533)

### Advanced - Individual Components

**Start just FlRig:**
```bash
flrig --config-dir ~/.flrig/g90-sdr --xmlrpc-server-port 12345 &
```

**Start GQRX bridge (assumes FlRig and GQRX running):**
```bash
./flrig-gqrx-bridge.py
```

**Start rigctld server (assumes FlRig running):**
```bash
./start-rigctld-server.bash
```

## Port Reference

| Port  | Service        | Description                                    |
|-------|----------------|------------------------------------------------|
| 4532  | GQRX           | GQRX remote control (bridge connects as client)|
| 4533  | rigctld Server | Hamlib rigctld server (clients connect here)   |
| 12345 | FlRig          | FlRig XML-RPC server (bridges connect here)    |

## Compatible Software

**Tested and working:**

- **GQRX** - SDR software with waterfall display (via dedicated bridge)
- **WSJT-X** - FT8/FT4 digital modes (can use FlRig directly or rigctld server)
- **JTDX** - Enhanced WSJT-X fork (can use FlRig directly or rigctld server)
- **fldigi** - Digital modes software (connect to rigctld server on port 4533)
- **CubicSDR** - Alternative SDR software (connect to rigctld server on port 4533)
- **Logging software** - CQRLOG, Xlog, etc. (use Hamlib NET rigctl, port 4533)

Any software that supports "Hamlib NET rigctl" should work by connecting to `localhost:4533`.

## Multi-Radio Setup

The configuration structure makes it easy to support multiple radios:

**1. Create a new config directory:**
```bash
mkdir -p ~/.flrig/ic7300-main
```

**2. Start FlRig with different port:**
```bash
flrig --config-dir ~/.flrig/ic7300-main --xmlrpc-server-port 12346 &
```

**3. Configure the radio through FlRig's GUI**

**4. Create dedicated bridge instances:**

For the second radio, you'd either:
- Modify the bridge scripts to use port 12346
- Create separate bridge scripts for each radio
- Add command-line arguments to bridges (future enhancement)

**Example directory structure:**
```
~/.flrig/
├── g90-sdr/          # Xiegu G90 for SDR panadapter
├── g90-portable/     # Same G90, portable config
├── ic7300-main/      # Icom IC-7300 shack radio
└── ft991a-mobile/    # Yaesu FT-991A mobile config
```

Each radio gets its own:
- Configuration directory
- XML-RPC port (12345, 12346, 12347...)
- Bridge instances
- Startup scripts

## Troubleshooting

### Bridge won't start - "Address already in use"

**Problem:** Port 4533 is already in use.

**Solution:**
```bash
# Find what's using the port
sudo lsof -i :4533

# Kill the process
kill <PID>

# Or kill all Python processes (careful!)
killall python3
```

### Bridge can't connect to FlRig

**Problem:** `Cannot connect to FlRig: [Errno 111] Connection refused`

**Solution:**
- Make sure FlRig is running
- Check that FlRig's XML-RPC server is enabled
- Verify correct port (default 12345)
- Check config directory path is correct

### GQRX bridge can't connect

**Problem:** `Cannot connect to GQRX`

**Solution:**
- Make sure GQRX is running first
- Check GQRX remote control is enabled (Tools → Remote Control)
- Verify `~/.config/gqrx/default.conf` has `enabled=true` and `port=4532`
- Try restarting GQRX

### G90 goes into transmit mode

**Problem:** G90 randomly transmits.

**Solution:**
- You should NOT be using Hamlib/rigctld directly with the G90
- Make sure you're using THESE bridges, which route through FlRig
- The bridges ignore all PTT commands for safety
- If using rigctld directly (not these bridges), that's the bug this project fixes!

### Frequency changes are slow or don't sync

**Problem:** Changing frequency in one application doesn't update others quickly.

**Solution:**
- GQRX bridge polls every 0.1 seconds (fast but not instant)
- Check that all components are running (FlRig, bridges)
- Make sure FlRig is actually connected to the G90
- Watch bridge output for errors

### Permission denied on serial port

**Problem:** FlRig can't access `/dev/ttyUSB0`

**Solution:**
```bash
# Add your user to dialout group
sudo usermod -a -G dialout $USER

# Log out and back in for changes to take effect
```

## Technical Details

### Supported rigctld Commands

The rigctld server implements:

- `f` - Get frequency
- `F <freq>` - Set frequency
- `m` - Get mode
- `M <mode> <passband>` - Set mode
- `t` - Get PTT status (always returns 0/RX)
- `T <0|1>` - Set PTT (ignored for safety)
- `\dump_state` - Return rig capabilities

### FlRig XML-RPC Methods Used

- `rig.get_vfo()` - Get current frequency
- `rig.set_frequency(freq)` - Set frequency
- `rig.get_mode()` - Get current mode
- `rig.set_mode(mode)` - Set mode

### GQRX Bridge Design

The GQRX bridge uses a polling approach:
- Polls GQRX and FlRig every 0.1 seconds (configurable)
- Compares frequencies to detect changes
- Syncs the one that changed to the other
- Uses debounce logic to prevent mid-typing updates

### Why Two Bridges Instead of One?

Originally, a "universal" bridge tried to do both GQRX sync AND rigctld server. This caused:
- Performance issues (polling overhead affected rigctld response)
- Timing conflicts (GQRX sync interfered with other clients)
- Complexity (harder to debug and maintain)

**The two-bridge solution:**
- Each bridge optimized for its specific task
- GQRX bridge: fast polling for responsive panadapter
- rigctld server: event-driven, responds instantly to client commands
- No interference between the two
- Easier to understand and maintain

This follows the Unix philosophy: "Do one thing and do it well."

## Known Limitations

- **No actual SDR hardware**: Uses G90's IF output through audio interface, not a true SDR. Bandwidth limited to G90's IF bandwidth.
- **GQRX sync is polling-based**: Updates every 0.1 seconds, not instant (fast enough for practical use)
- **PTT is disabled**: Bridges ignore all PTT commands as a safety measure
- **Mode changes**: Limited to modes supported by both FlRig and the G90
- **Single client assumption**: While rigctld server supports multiple clients, they may conflict if changing frequency simultaneously

## Future Enhancements

Potential improvements (contributions welcome!):

- Command-line arguments for ports and config paths
- Automatic FlRig instance detection
- Configuration file for bridges (YAML/JSON)
- Web interface for monitoring/control
- Integration with other SDR software
- Support for more rigctld commands
- Logging and diagnostics modes

## Support This Project

If you find this project useful and it helps with your ham radio setup, please consider sponsoring my work! Your support helps me afford parts, tools, and learning resources to keep creating and sharing open-source projects.

**GitHub Sponsors:** (Pending approval - coming soon!)

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

Some areas that could use help:
- Testing with other radios (X5105, X6100, etc.)
- Testing with more Hamlib-compatible software
- Documentation improvements
- Performance optimizations
- Additional features

## License

MIT License - See LICENSE file for details

## Acknowledgments

This bridge system was developed collaboratively with Claude (Anthropic AI) to solve the Xiegu G90's incompatibility with Hamlib's rigctld, which caused unwanted transmit triggering. The solution uses FlRig as a reliable CAT control backend with specialized bridge software for different use cases.

Special thanks to:
- The FlRig developers for creating reliable rig control software
- The Hamlib project for the rigctld protocol specification
- The GQRX developers for excellent SDR software
- The ham radio open-source community

## Support

For questions or issues:
- Open an issue on GitHub: https://github.com/hybotix/ham-stuff
- Contact: hybotix on GitHub

## Author

**hybotix** - Amateur radio enthusiast, electronics tinkerer, and robotics builder

73 and happy operating!

---

**Project Status:** Active and working. Tested on Raspberry Pi 5 with Ubuntu 24.04, Xiegu G90, and SignaLink USB interface.
