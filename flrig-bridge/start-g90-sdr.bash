#!/bin/bash

# Change to home directory where scripts are
cd ~

# Start FlRig with G90 config
flrig --config-dir ~/.flrig/g90-sdr &
sleep 3

# Start GQRX
gqrx &
sleep 3

# Start GQRX bridge
./flrig-gqrx-bridge.py
