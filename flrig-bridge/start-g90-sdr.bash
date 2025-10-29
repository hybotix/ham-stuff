#!/bin/bash

# Move into the script directory
cd $L_SCRIPT_DIR

# Start FlRig first
flrig &
sleep 2

# Start GQRX
gqrx &
sleep 2

# Start the bridge
./flrig-gqrx-bridge.py
