# FlRig Bridge - Universal Rig Control for Xiegu G90

A Python bridge that enables the Xiegu G90 to work reliably with any Hamlib-compatible software by using FlRig as a backend. Solves the critical issue where Hamlib's native G90 driver causes unwanted transmit triggering.

## Features

- **Universal rigctld Server**: Acts as a Hamlib-compatible server that any rigctld client can connect to
- **GQRX Bidirectional Sync**: Automatically syncs frequency changes between GQRX and your G90
- **Multi-Client Support**: Multiple applications can connect simultaneously and stay synchronized
- **PTT Protection**: Ignores all PTT commands to prevent accidental transmit
- **No Transmit Bug**: Bypasses Hamlib's buggy G90 driver by using FlRig's reliable CAT implementation
- **Lightweight**: Pure Python with minimal dependencies

## The Problem This Solves

The Xiegu G90's implementation in Hamlib (model 3088) has a critical bug where certain CAT commands trigger transmit mode unexpectedly. This makes it dangerous to use with rigctld-based applications like GQRX, fldigi, and logging software.

This bridge solves the problem by routing all rig control through FlRig, which implements G90 CAT control correctly, while providing standard rigctld and GQRX interfaces for other software.

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

2. Make the bridge script executable:
```bash
chmod +x universal-flrig-bridge.py
```

3. (Optional) Copy to a convenient location:
```bash
cp universal-flrig-bridge.py ~/
```

## Configuration

### FlRig Setup

1. Start FlRig
2. Configure for Xiegu G90:
   - **Config → Setup → Transceiver**
   - Select "Xiegu G90"
   - Set serial port (usually `/dev/ttyUSB0`)
   - Set baud rate: 19200
3. Enable XML-RPC server:
   - **Config → Setup → Server**
   - Enable XML-RPC server on port 12345

### GQRX Setup (Optional)

1. Start GQRX
2. Configure audio input device (your USB sound card/interface)
3. Enable remote control:
   - **Tools → Remote Control**
   - The dialog should show port 4532

Alternatively, edit `~/.config/gqrx/default.conf`:
```ini
[remote_control]
allowed_hosts=127.0.0.1
enabled=true
port=4532
```

## Usage

### Starting the Bridge

1. **Start FlRig first** and connect to your G90
2. **(Optional)** Start GQRX with your audio interface configured
3. **Start the bridge:**
```bash
./universal-flrig-bridge.py
```

You should see output like:
```
============================================================
Universal FlRig Bridge
============================================================
✓ FlRig connected at 127.0.0.1:12345
  Current frequency: 14074000 Hz

Services:
  • rigctld server: 127.0.0.1:4533
    Any Hamlib-compatible software can connect here
  • GQRX sync: 127.0.0.1:4532
    Bidirectional frequency sync with GQRX

Press Ctrl+C to stop
============================================================
```

### Automated Startup Script

Create a startup script to launch everything at once:

```bash
#!/bin/bash
# start-g90-sdr.sh

# Start FlRig
flrig &
sleep 3

# Start GQRX (optional)
gqrx &
sleep 3

# Start the bridge
~/universal-flrig-bridge.py
```

Make it executable:
```bash
chmod +x start-g90-sdr.sh
```

## Port Reference

| Port  | Service         | Description                                    |
|-------|-----------------|------------------------------------------------|
| 4532  | GQRX            | GQRX remote control (bridge connects as client)|
| 4533  | Bridge (rigctld)| Hamlib rigctld server (clients connect here)   |
| 12345 | FlRig           | FlRig XML-RPC server (bridge connects here)    |

## Compatible Software

The bridge has been tested with:

- **GQRX** - SDR software with waterfall display (bidirectional sync)
- **WSJT-X** - FT8/FT4 digital modes (can use FlRig directly or bridge)
- **JTDX** - Enhanced WSJT-X fork (can use FlRig directly or bridge)
- **fldigi** - Digital modes software (connect to port 4533)
- **CubicSDR** - Alternative SDR software (connect to port 4533)

Any software that supports "Hamlib NET rigctl" should work by connecting to `localhost:4533`.

## How It Works

```
┌──────────┐         ┌─────────────────────┐         ┌────────────┐
│  GQRX    │◄───────►│  Universal Bridge   │◄────────┤  fldigi    │
│ (4532)   │  sync   │  (rigctld server)   │ client  │  CubicSDR  │
└──────────┘         │  Port 4533          │         │  etc.      │
                     └─────────────────────┘         └────────────┘
                              │
                              ▼
                     ┌─────────────────┐
                     │     FlRig       │
                     │   XML-RPC       │
                     │   Port 12345    │
                     └─────────────────┘
                              │
                              ▼
                     ┌─────────────────┐
                     │   Xiegu G90     │
                     │   (USB Serial)  │
                     └─────────────────┘
```

The bridge:
1. Connects to FlRig's XML-RPC server (port 12345)
2. Connects to GQRX's remote control (port 4532) for bidirectional sync
3. Provides a rigctld-compatible server (port 4533) for other applications
4. Synchronizes frequency changes across all clients
5. Routes all CAT commands through FlRig to avoid Hamlib's G90 bugs

## Troubleshooting

### Bridge won't start - "Address already in use"

**Problem:** Port 4533 is already in use.

**Solution:**
```bash
# Find what's using the port
sudo lsof -i :4533

# Kill the process
kill <PID>
```

### Bridge can't connect to FlRig

**Problem:** `Cannot connect to FlRig: [Errno 111] Connection refused`

**Solution:**
- Make sure FlRig is running
- Check that FlRig's XML-RPC server is enabled (Config → Setup → Server)
- Verify port 12345 is correct

### Bridge can't connect to GQRX

**Problem:** `Cannot connect to GQRX`

**Solution:**
- This is optional - the bridge works without GQRX
- If you want GQRX sync, make sure GQRX is running first
- Check GQRX remote control is enabled (Tools → Remote Control)
- Verify `~/.config/gqrx/default.conf` has `enabled=true` and `port=4532`

### G90 goes into transmit mode

**Problem:** G90 randomly transmits when using the bridge.

**Solution:**
- You should NOT be using Hamlib/rigctld directly with the G90
- Make sure you're using THIS bridge, which routes through FlRig
- The bridge ignores all PTT commands for safety
- If using rigctld directly (not this bridge), that's the bug this project fixes!

### Frequency changes don't sync

**Problem:** Changing frequency in one application doesn't update others.

**Solution:**
- Check that all applications are connected (look at bridge output)
- GQRX sync polls every 0.5 seconds, so there may be a slight delay
- Make sure FlRig is actually connected to the G90

### Other software can't connect to port 4533

**Problem:** Software reports "Connection refused" when trying to connect to rigctld.

**Solution:**
- Make sure the bridge is running
- Check you're connecting to `localhost` or `127.0.0.1` on port `4533`
- Some software might need "Hamlib NET rigctl" or "Network rig" selected

## Technical Details

### Supported rigctld Commands

The bridge implements the following Hamlib rigctld protocol commands:

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

### Thread Safety

The bridge uses thread locks to prevent race conditions when multiple clients modify frequency simultaneously. All frequency changes are atomic and properly synchronized.

## Known Limitations

- **No actual SDR hardware**: This uses the G90's IF output through an audio interface, not a true SDR. Bandwidth is limited to the G90's IF bandwidth.
- **GQRX sync is polling-based**: Updates every 0.5 seconds, not instant
- **PTT is disabled**: The bridge ignores all PTT commands as a safety measure
- **Mode changes**: Limited to modes supported by both FlRig and the G90

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT License - See LICENSE file for details

## Acknowledgments

This bridge was developed collaboratively with Claude (Anthropic AI) to solve the Xiegu G90's incompatibility with Hamlib's rigctld, which caused unwanted transmit triggering. The solution uses FlRig as a reliable CAT control backend.

Special thanks to:
- The FlRig developers for creating reliable rig control software
- The Hamlib project for the rigctld protocol specification
- The GQRX developers for excellent SDR software
- The ham radio open-source community

## Support

For questions or issues:
- Open an issue on GitHub: https://github.com/hybotix/ham-stuff
- Contact: hybotix on GitHub

73 and happy operating!
