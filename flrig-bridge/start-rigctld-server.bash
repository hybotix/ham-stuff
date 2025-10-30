#!/bin/bash

# Move into the script directory - set this in your ~/.bashrc to the directory
#   where you store executable scripts. This might be $HOME/bin, for example.
cd $L_SCRIPT_DIR

# Start FlRig first
flrig  --config-dir ~/.flrig/g90-sdr &
sleep 3

# Start GQRX. GQRX must have remote control set TRUE and set to connect to
#   localhost:4532. You might have to manually edit $HOME/.config/gqrx/default.conf

gqrx &
sleep 3

# Start GQRX with the the Universal Bridge.
# This bridges from GQRX on port 4532 to FlRig on port 12345

./flrig-universal_bridge.py
