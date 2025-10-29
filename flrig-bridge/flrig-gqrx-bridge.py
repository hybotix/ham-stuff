#!/usr/bin/env python3
"""
Universal FlRig Bridge for Xiegu G90
Enables panadapter operation and fixes Hamlib CAT issues

Author:   Dale Weber/N7PKT <dalew@n7pkt.org>
Created:  October, 2025
License:  MIT
Developed with assistance from Anthropic's Claude AI

This bridge provides:
- rigctld-compatible server for any Hamlib compatible software
- Bidirectional sync with GQRX
- Reliable CAT control via FlRig (bypasses buggy Hamlib G90 driver)
"""
```
MIT License

Copyright (c) 2025 Dale Weber

Permission is hereby granted, free of charge, to any person obtaining a copy...
```

"""
Bidirectional bridge between GQRX and FlRig
- Connects to GQRX's remote control (port 4532)
- Connects to FlRig's XML-RPC (port 12345)
- Syncs frequency changes both ways
"""

import socket
import xmlrpc.client
import time
import threading

GQRX_HOST = "127.0.0.1"
GQRX_PORT = 4532
FLRIG_HOST = "127.0.0.1"
FLRIG_PORT = 12345
POLL_INTERVAL = 0.5  # seconds

class GQRXFlRigBridge:
    def __init__(self):
        self.flrig = xmlrpc.client.ServerProxy(f"http://{FLRIG_HOST}:{FLRIG_PORT}")
        self.gqrx_sock = None
        self.running = True
        self.last_freq = None
        
    def connect_gqrx(self):
        """Connect to GQRX's remote control port"""
        max_retries = 10
        retry_count = 0
        
        while retry_count < max_retries and self.running:
            try:
                print(f"Attempting to connect to GQRX at {GQRX_HOST}:{GQRX_PORT}...")
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2.0)
                sock.connect((GQRX_HOST, GQRX_PORT))
                print("Connected to GQRX!")
                return sock
            except (ConnectionRefusedError, socket.timeout) as e:
                retry_count += 1
                print(f"Connection attempt {retry_count}/{max_retries} failed. Is GQRX running with remote control enabled?")
                if retry_count < max_retries:
                    time.sleep(2)
        
        print("Failed to connect to GQRX after multiple attempts.")
        return None
    
    def send_gqrx_command(self, cmd):
        """Send command to GQRX and get response"""
        if not self.gqrx_sock:
            return None
        
        try:
            self.gqrx_sock.sendall(f"{cmd}\n".encode())
            response = self.gqrx_sock.recv(1024).decode().strip()
            return response
        except Exception as e:
            print(f"Error sending GQRX command: {e}")
            return None
    
    def get_gqrx_frequency(self):
        """Get current frequency from GQRX"""
        response = self.send_gqrx_command("f")
        if response and response != "RPRT 1":
            try:
                return int(response)
            except ValueError:
                return None
        return None
    
    def set_gqrx_frequency(self, freq):
        """Set GQRX frequency"""
        response = self.send_gqrx_command(f"F {freq}")
        return response == "RPRT 0"
    
    def get_flrig_frequency(self):
        """Get current frequency from FlRig"""
        try:
            freq = self.flrig.rig.get_vfo()
            return int(freq)
        except Exception as e:
            print(f"Error getting FlRig frequency: {e}")
            return None
    
    def set_flrig_frequency(self, freq):
        """Set FlRig frequency"""
        try:
            self.flrig.rig.set_frequency(float(freq))
            return True
        except Exception as e:
            print(f"Error setting FlRig frequency: {e}")
            return False
    
    def sync_frequencies(self):
        """Main sync loop - monitors both and syncs changes"""
        print("Starting frequency sync loop...")
        
        while self.running:
            try:
                # Get frequencies from both
                gqrx_freq = self.get_gqrx_frequency()
                flrig_freq = self.get_flrig_frequency()
                
                if gqrx_freq is None or flrig_freq is None:
                    time.sleep(POLL_INTERVAL)
                    continue
                
                # Check if they're different (allow 1 Hz tolerance)
                if abs(gqrx_freq - flrig_freq) > 1:
                    # Determine which changed since last check
                    if self.last_freq is None:
                        # First run, sync GQRX to FlRig
                        print(f"Initial sync: GQRX {gqrx_freq} <- FlRig {flrig_freq}")
                        self.set_gqrx_frequency(flrig_freq)
                        self.last_freq = flrig_freq
                    elif abs(gqrx_freq - self.last_freq) > abs(flrig_freq - self.last_freq):
                        # GQRX changed more, sync FlRig to GQRX
                        print(f"GQRX changed: {self.last_freq} -> {gqrx_freq}, updating FlRig")
                        if self.set_flrig_frequency(gqrx_freq):
                            self.last_freq = gqrx_freq
                    else:
                        # FlRig changed more, sync GQRX to FlRig
                        print(f"FlRig changed: {self.last_freq} -> {flrig_freq}, updating GQRX")
                        if self.set_gqrx_frequency(flrig_freq):
                            self.last_freq = flrig_freq
                else:
                    # They match, update last known
                    self.last_freq = gqrx_freq
                
                time.sleep(POLL_INTERVAL)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error in sync loop: {e}")
                time.sleep(POLL_INTERVAL)
    
    def run(self):
        """Start the bridge"""
        print("GQRX-FlRig Bridge Starting...")
        print(f"Connecting to FlRig at {FLRIG_HOST}:{FLRIG_PORT}")
        print(f"Will connect to GQRX at {GQRX_HOST}:{GQRX_PORT}")
        print("Make sure GQRX is running with Remote Control enabled (Tools → Remote Control)")
        print("Press Ctrl+C to stop\n")
        
        # Test FlRig connection
        try:
            freq = self.flrig.rig.get_vfo()
            print(f"✓ FlRig connected, current frequency: {freq} Hz")
        except Exception as e:
            print(f"✗ Cannot connect to FlRig: {e}")
            print("Make sure FlRig is running!")
            return
        
        # Connect to GQRX
        self.gqrx_sock = self.connect_gqrx()
        if not self.gqrx_sock:
            print("\nCannot connect to GQRX.")
            print("In GQRX: Go to Tools → Remote Control")
            print("The port shown there should match this script's GQRX_PORT")
            return
        
        try:
            self.sync_frequencies()
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            self.running = False
            if self.gqrx_sock:
                self.gqrx_sock.close()

if __name__ == "__main__":
    bridge = GQRXFlRigBridge()
    bridge.run()
