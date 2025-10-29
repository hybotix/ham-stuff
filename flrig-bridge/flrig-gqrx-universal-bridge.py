#!/usr/bin/env python3
"""
Universal FlRig Bridge
- Acts as rigctld server (port 4533) for any Hamlib-compatible software
- Syncs bidirectionally with GQRX (port 4532)
- Connects to FlRig's XML-RPC (port 12345)
- All frequency changes sync across all clients
"""

import socket
import xmlrpc.client
import time
import threading
import select

FLRIG_HOST = "127.0.0.1"
FLRIG_PORT = 12345
GQRX_HOST = "127.0.0.1"
GQRX_PORT = 4532
RIGCTLD_HOST = "127.0.0.1"
RIGCTLD_PORT = 4533
POLL_INTERVAL = 0.5  # seconds

class UniversalFlRigBridge:
    def __init__(self):
        self.flrig = xmlrpc.client.ServerProxy(f"http://{FLRIG_HOST}:{FLRIG_PORT}")
        self.gqrx_sock = None
        self.running = True
        self.last_freq = None
        self.freq_lock = threading.Lock()
        
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
            with self.freq_lock:
                self.last_freq = freq
            return True
        except Exception as e:
            print(f"Error setting FlRig frequency: {e}")
            return False
    
    def get_flrig_mode(self):
        """Get current mode from FlRig"""
        try:
            mode = self.flrig.rig.get_mode()
            mode_map = {
                'USB': 'USB',
                'LSB': 'LSB',
                'CW': 'CW',
                'CWR': 'CWR',
                'AM': 'AM',
                'FM': 'FM',
                'RTTY': 'RTTY',
                'RTTYR': 'RTTYR'
            }
            return mode_map.get(mode, 'USB')
        except Exception as e:
            print(f"Error getting mode: {e}")
            return 'USB'
    
    def set_flrig_mode(self, mode):
        """Set mode via FlRig"""
        try:
            self.flrig.rig.set_mode(mode)
            return True
        except Exception as e:
            print(f"Error setting mode: {e}")
            return False
    
    # ========== GQRX Sync Functions ==========
    
    def connect_gqrx(self):
        """Connect to GQRX's remote control port"""
        try:
            print(f"Connecting to GQRX at {GQRX_HOST}:{GQRX_PORT}...")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2.0)
            sock.connect((GQRX_HOST, GQRX_PORT))
            print("✓ Connected to GQRX!")
            return sock
        except Exception as e:
            print(f"Cannot connect to GQRX: {e}")
            print("  GQRX sync will be disabled. Make sure GQRX is running if you want sync.")
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
            print(f"GQRX connection lost: {e}")
            self.gqrx_sock = None
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
    
    def gqrx_sync_loop(self):
        """Continuously sync with GQRX"""
        print("Starting GQRX sync thread...")
        
        while self.running:
            if not self.gqrx_sock:
                time.sleep(5)
                self.gqrx_sock = self.connect_gqrx()
                continue
            
            try:
                gqrx_freq = self.get_gqrx_frequency()
                flrig_freq = self.get_flrig_frequency()
                
                if gqrx_freq and flrig_freq and abs(gqrx_freq - flrig_freq) > 1:
                    with self.freq_lock:
                        if self.last_freq is None:
                            self.set_gqrx_frequency(flrig_freq)
                            self.last_freq = flrig_freq
                        elif abs(gqrx_freq - self.last_freq) > abs(flrig_freq - self.last_freq):
                            print(f"GQRX: {self.last_freq} → {gqrx_freq}")
                            if self.set_flrig_frequency(gqrx_freq):
                                self.last_freq = gqrx_freq
                        else:
                            print(f"FlRig: {self.last_freq} → {flrig_freq}")
                            if self.set_gqrx_frequency(flrig_freq):
                                self.last_freq = flrig_freq
                else:
                    with self.freq_lock:
                        self.last_freq = gqrx_freq if gqrx_freq else flrig_freq
                
                time.sleep(POLL_INTERVAL)
            except Exception as e:
                print(f"GQRX sync error: {e}")
                time.sleep(POLL_INTERVAL)
    
    # ========== rigctld Server Functions ==========
    
    def handle_rigctld_client(self, conn, addr):
        """Handle rigctld protocol commands from client"""
        print(f"rigctld client connected from {addr}")
        
        try:
            while self.running:
                data = conn.recv(1024)
                if not data:
                    break
                
                cmd = data.decode().strip()
                parts = cmd.split()
                if not parts:
                    continue
                
                command = parts[0]
                response = ""
                
                if command == 'f' or command == 'F':
                    if len(parts) == 1:
                        # Get frequency
                        freq = self.get_flrig_frequency()
                        if freq:
                            response = f"{freq}\n"
                        else:
                            response = "RPRT -1\n"
                    else:
                        # Set frequency
                        try:
                            freq = int(parts[1])
                            if self.set_flrig_frequency(freq):
                                response = "RPRT 0\n"
                            else:
                                response = "RPRT -1\n"
                        except ValueError:
                            response = "RPRT -1\n"
                
                elif command == 'm' or command == 'M':
                    if len(parts) == 1:
                        # Get mode
                        mode = self.get_flrig_mode()
                        response = f"{mode}\n0\n"
                    else:
                        # Set mode
                        mode = parts[1]
                        if self.set_flrig_mode(mode):
                            response = "RPRT 0\n"
                        else:
                            response = "RPRT -1\n"
                
                elif command == 'q' or command == 'Q':
                    response = "RPRT 0\n"
                    conn.sendall(response.encode())
                    break
                
                elif command == 't' or command == 'T':
                    # PTT - always ignore and return success
                    if len(parts) == 1:
                        response = "0\n"  # Always RX
                    else:
                        response = "RPRT 0\n"  # Pretend we set it
                
                elif command == '\\dump_state':
                    response = "0\n2\n2\n150000.000000 30000000.000000 0x900 -1 -1 0x10000003 0x3\n"
                    response += "0 0 0 0 0 0 0\n"
                
                else:
                    response = "RPRT -1\n"
                
                conn.sendall(response.encode())
        
        except Exception as e:
            print(f"rigctld client error: {e}")
        finally:
            conn.close()
            print(f"rigctld client disconnected from {addr}")
    
    def rigctld_server_loop(self):
        """Run rigctld-compatible server"""
        print(f"Starting rigctld server on {RIGCTLD_HOST}:{RIGCTLD_PORT}...")
        
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((RIGCTLD_HOST, RIGCTLD_PORT))
        server.listen(5)
        server.settimeout(1.0)
        
        print(f"✓ rigctld server ready - other software can connect to port {RIGCTLD_PORT}")
        
        try:
            while self.running:
                try:
                    conn, addr = server.accept()
                    client_thread = threading.Thread(
                        target=self.handle_rigctld_client,
                        args=(conn, addr),
                        daemon=True
                    )
                    client_thread.start()
                except socket.timeout:
                    continue
        finally:
            server.close()
    
    def run(self):
        """Start the universal bridge"""
        print("=" * 60)
        print("Universal FlRig Bridge")
        print("=" * 60)
        
        # Test FlRig connection
        try:
            freq = self.flrig.rig.get_vfo()
            print(f"✓ FlRig connected at {FLRIG_HOST}:{FLRIG_PORT}")
            print(f"  Current frequency: {freq} Hz")
        except Exception as e:
            print(f"✗ Cannot connect to FlRig: {e}")
            print("  Make sure FlRig is running!")
            return
        
        print()
        print("Services:")
        print(f"  • rigctld server: {RIGCTLD_HOST}:{RIGCTLD_PORT}")
        print(f"    Any Hamlib-compatible software can connect here")
        print(f"  • GQRX sync: {GQRX_HOST}:{GQRX_PORT}")
        print(f"    Bidirectional frequency sync with GQRX")
        print()
        print("Press Ctrl+C to stop")
        print("=" * 60)
        print()
        
        # Start GQRX sync thread
        gqrx_thread = threading.Thread(target=self.gqrx_sync_loop, daemon=True)
        gqrx_thread.start()
        
        # Start rigctld server thread
        rigctld_thread = threading.Thread(target=self.rigctld_server_loop, daemon=True)
        rigctld_thread.start()
        
        # Keep main thread alive
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\nShutting down...")
        finally:
            self.running = False
            if self.gqrx_sock:
                self.gqrx_sock.close()
            time.sleep(1)

if __name__ == "__main__":
    bridge = UniversalFlRigBridge()
    bridge.run()
