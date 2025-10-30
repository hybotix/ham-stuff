#!/usr/bin/env python3
"""
FlRig rigctld Server
Pure rigctld server for FlRig - no GQRX sync
Use this alongside the GQRX bridge for best performance
"""

import socket
import xmlrpc.client
import threading

FLRIG_HOST = "127.0.0.1"
FLRIG_PORT = 12345
RIGCTLD_HOST = "127.0.0.1"
RIGCTLD_PORT = 4533

class FlRigRigctldServer:
    def __init__(self):
        self.flrig = xmlrpc.client.ServerProxy(f"http://{FLRIG_HOST}:{FLRIG_PORT}")
        self.running = True

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

    def handle_rigctld_client(self, conn, addr):
        """Handle rigctld protocol commands from client"""
        print(f"Client connected from {addr}")

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
            print(f"Client error: {e}")
        finally:
            conn.close()
            print(f"Client disconnected from {addr}")

    def run(self):
        """Start the rigctld server"""
        print("=" * 60)
        print("FlRig rigctld Server")
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
        print(f"rigctld server listening on {RIGCTLD_HOST}:{RIGCTLD_PORT}")
        print("Any Hamlib-compatible software can connect here")
        print()
        print("Press Ctrl+C to stop")
        print("=" * 60)
        print()

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((RIGCTLD_HOST, RIGCTLD_PORT))
        server.listen(5)
        server.settimeout(1.0)

        print("✓ Server ready")

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
        except KeyboardInterrupt:
            print("\n\nShutting down...")
        finally:
            self.running = False
            server.close()

if __name__ == "__main__":
    server = FlRigRigctldServer()
    server.run()
