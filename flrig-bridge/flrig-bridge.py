#!/usr/bin/env python3
"""
FlRig to rigctld protocol bridge
Allows GQRX (or other rigctld clients) to control rigs via FlRig
"""

import socket
import xmlrpc.client
import threading
import time

FLRIG_HOST = "127.0.0.1"
FLRIG_PORT = 12345
LISTEN_HOST = "127.0.0.1"
LISTEN_PORT = 4532

class FlRigBridge:
    def __init__(self):
        self.flrig = xmlrpc.client.ServerProxy(f"http://{FLRIG_HOST}:{FLRIG_PORT}")
        self.running = True

    def get_frequency(self):
        """Get current frequency from FlRig"""
        try:
            freq = self.flrig.rig.get_vfo()
            return int(freq)
        except Exception as e:
            print(f"Error getting frequency: {e}")
            return None

    def set_frequency(self, freq):
        """Set frequency via FlRig"""
        try:
            self.flrig.rig.set_vfo(int(freq))
            return True
        except Exception as e:
            print(f"Error setting frequency: {e}")
            return False

    def get_mode(self):
        """Get current mode from FlRig"""
        try:
            mode = self.flrig.rig.get_mode()
            # Map FlRig modes to Hamlib modes
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

    def set_mode(self, mode, passband=0):
        """Set mode via FlRig"""
        try:
            self.flrig.rig.set_mode(mode)
            return True
        except Exception as e:
            print(f"Error setting mode: {e}")
            return False

    def handle_client(self, conn, addr):
        """Handle rigctld protocol commands from client"""
        print(f"Client connected from {addr}")

        try:
            while self.running:
                data = conn.recv(1024)
                if not data:
                    break

                cmd = data.decode().strip()
                print(f"Received: {cmd}")

                # Parse rigctld commands
                parts = cmd.split()
                if not parts:
                    continue

                command = parts[0].lower()
                response = ""

                if command == 'f':
                    # Get frequency
                    freq = self.get_frequency()
                    if freq:
                        response = f"{freq}\n"
                    else:
                        response = "RPRT -1\n"

                elif command == 'F' and len(parts) > 1:
                    # Set frequency
                    try:
                        freq = int(parts[1])
                        if self.set_frequency(freq):
                            response = "RPRT 0\n"
                        else:
                            response = "RPRT -1\n"
                    except ValueError:
                        response = "RPRT -1\n"

                elif command == 'm':
                    # Get mode
                    mode = self.get_mode()
                    response = f"{mode}\n0\n"  # mode and passband

                elif command == 'M' and len(parts) > 1:
                    # Set mode
                    mode = parts[1]
                    if self.set_mode(mode):
                        response = "RPRT 0\n"
                    else:
                        response = "RPRT -1\n"
                elif command == 'q':
                    # Quit
                    response = "RPRT 0\n"
                    conn.sendall(response.encode())
                    break
                elif command == 't':
                    # Get PTT status (always return 0 = RX)
                    response = "0\n"
                elif command == 'T':
                    # Set PTT - ignore it!
                    response = "RPRT 0\n"
                elif command == '\\dump_state':
                    # Return minimal rig state
                    response = "0\n2\n2\n150000.000000 30000000.000000 0x900 -1 -1 0x10000003 0x3\n"
                    response += "0 0 0 0 0 0 0\n"
                else:
                    # Unknown command
                    response = "RPRT -1\n"

                conn.sendall(response.encode())

        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            conn.close()
            print(f"Client disconnected from {addr}")

    def run(self):
        """Start the bridge server"""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((LISTEN_HOST, LISTEN_PORT))
        server.listen(5)

        print(f"FlRig bridge listening on {LISTEN_HOST}:{LISTEN_PORT}")
        print(f"Connecting to FlRig at {FLRIG_HOST}:{FLRIG_PORT}")
        print("Press Ctrl+C to stop")

        try:
            while self.running:
                server.settimeout(1.0)
                try:
                    conn, addr = server.accept()
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(conn, addr)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                except socket.timeout:
                    continue
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            self.running = False
            server.close()

if __name__ == "__main__":
    bridge = FlRigBridge()
    bridge.run()
