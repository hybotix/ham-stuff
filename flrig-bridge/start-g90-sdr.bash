#!/bin/bash

# Start G90 SDR Panadapter Setup
# - FlRig for rig control
# - GQRX for waterfall display
# - Bridge for synchronization

cd ~

# Start FlRig with G90-SDR config
flrig --config-dir ~/.flrig/g90-sdr --xmlrpc-server-port 12345 &
sleep 3

# Start GQRX
gqrx &
sleep 3

# Start GQRX bridge (foreground - see output)
./flrig-gqrx-bridge.py
