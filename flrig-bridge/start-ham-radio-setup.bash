#!/bin/bash

# Complete Ham Radio Station Setup
# Starts everything: FlRig, GQRX, both bridges
# - GQRX panadapter with sync
# - rigctld server for other software

cd ~

echo "Starting complete ham radio station setup..."
echo ""

# Start FlRig with G90-SDR config
echo "Starting FlRig..."
flrig --config-dir ~/.flrig/g90-sdr --xmlrpc-server-port 12345 &
sleep 3

# Start GQRX
echo "Starting GQRX..."
gqrx &
sleep 3

# Start GQRX bridge in background
echo "Starting GQRX bridge..."
./flrig-gqrx-bridge.py &
sleep 2

# Start rigctld server (foreground - see output)
echo "Starting rigctld server..."
echo ""
./flrig-rigctld-server.py
