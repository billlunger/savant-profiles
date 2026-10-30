#!/usr/bin/env python3
"""
Barco WME-50 REST API Debug Server

Captures all incoming HTTP/HTTPS requests and logs them with full details.
This helps diagnose what the Savant profile is actually sending.

Usage:
    python3 debug_server.py

Then update your profile to use: 127.0.0.1 (DeviceIP state variable)
The server will run on HTTPS port 443 (or 8443 if you don't have root)
"""

import http.server
import ssl
import json
import socket
from datetime import datetime
from pathlib import Path
import sys
import os

class DebugRequestHandler(http.server.BaseHTTPRequestHandler):
    """HTTP request handler that logs everything"""

    # Color codes for terminal output
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

    def log_message(self, format, *args):
        """Override to customize logging"""
        pass  # We'll do custom logging instead

    def do_POST(self):
        """Handle POST requests"""
        self.log_full_request("POST")

    def do_GET(self):
        """Handle GET requests"""
        self.log_full_request("GET")

    def log_full_request(self, method):
        """Log the full request details"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        print(f"\n{self.BOLD}{'='*80}{self.RESET}")
        print(f"{self.GREEN}[{timestamp}] {method} Request Received{self.RESET}")
        print(f"{self.BOLD}{'='*80}{self.RESET}")

        # Request line
        print(f"\n{self.BOLD}REQUEST LINE:{self.RESET}")
        print(f"  {method} {self.path} {self.request_version}")

        # Headers
        print(f"\n{self.BOLD}HEADERS:{self.RESET}")
        for header, value in self.headers.items():
            # Mask sensitive data
            if header.lower() in ['authorization', 'cookie', 'api_key']:
                value = f"***{value[-4:]}" if len(value) > 4 else "***"
            print(f"  {header}: {value}")

        # Body
        content_length = int(self.headers.get('Content-Length', 0))
        body = ""
        if content_length > 0:
            body = self.rfile.read(content_length).decode('utf-8', errors='replace')
            print(f"\n{self.BOLD}BODY ({content_length} bytes):{self.RESET}")
            print(f"  {body}")

            # Try to parse as JSON
            try:
                json_data = json.loads(body)
                print(f"\n{self.BOLD}PARSED JSON:{self.RESET}")
                print(f"  {json.dumps(json_data, indent=2)}")
            except:
                pass
        else:
            print(f"\n{self.BOLD}BODY:{self.RESET} (no body)")

        # Raw bytes
        print(f"\n{self.BOLD}RAW REQUEST (as sent):{self.RESET}")
        raw_request = f"{method} {self.path} {self.request_version}\r\n"
        for header, value in self.headers.items():
            raw_request += f"{header}: {value}\r\n"
        raw_request += "\r\n"
        if body:
            raw_request += body

        # Display raw with visible special characters
        print(f"  {repr(raw_request)}")

        # Send response based on endpoint
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Set-Cookie', 'sid=debug_session_12345; Path=/; Max-Age=1800')

        # Generate appropriate response
        if '/api/v1/auth/key' in self.path:
            response = {
                "expiresIn": 1800,
                "kind": "auth#token",
                "scope": "API"
            }
            print(f"\n{self.YELLOW}→ Sending AUTH response (session created){self.RESET}")
        elif '/api/v1/wall/power' in self.path:
            if method == 'POST':
                response = {
                    "actionId": "debug123",
                    "issuedBy": "groups#wall#cbm",
                    "kind": "action#response",
                    "result": "accepted"
                }
                print(f"\n{self.YELLOW}→ Sending POWER response (accepted){self.RESET}")
            else:
                response = {
                    "kind": "groups#wall#state",
                    "power": "on"
                }
                print(f"\n{self.YELLOW}→ Sending POWER GET response{self.RESET}")
        elif '/api/v1/wall/brightness' in self.path:
            if method == 'POST':
                response = {
                    "actionId": "debug124",
                    "issuedBy": "groups#wall#cbm",
                    "kind": "action#response",
                    "result": "accepted"
                }
                print(f"\n{self.YELLOW}→ Sending BRIGHTNESS response (accepted){self.RESET}")
            else:
                response = {
                    "kind": "groups#wall#cbm",
                    "brightness": 50,
                    "minimum": 0,
                    "maximum": 100
                }
                print(f"\n{self.YELLOW}→ Sending BRIGHTNESS GET response{self.RESET}")
        elif '/api/v1/wall/preset' in self.path:
            response = {
                "actionId": "debug125",
                "issuedBy": "groups#wall#cbm",
                "kind": "action#response",
                "result": "accepted"
            }
            print(f"\n{self.YELLOW}→ Sending PRESET response (accepted){self.RESET}")
        else:
            response = {
                "kind": "debug#response",
                "status": "ok",
                "endpoint": self.path
            }
            print(f"\n{self.YELLOW}→ Sending generic response{self.RESET}")

        response_body = json.dumps(response).encode('utf-8')
        self.send_header('Content-Length', len(response_body))
        self.end_headers()
        self.wfile.write(response_body)

        print(f"\n{self.BLUE}Response sent: {json.dumps(response)}{self.RESET}\n")


def create_self_signed_cert():
    """Create a self-signed certificate if it doesn't exist"""
    cert_file = Path('debug_cert.pem')
    key_file = Path('debug_key.pem')

    if cert_file.exists() and key_file.exists():
        print(f"✓ Using existing certificate: {cert_file}")
        return cert_file, key_file

    print("Creating self-signed certificate...")
    print("(This may take a moment...)")

    try:
        import subprocess
        subprocess.run([
            'openssl', 'req', '-x509', '-newkey', 'rsa:2048',
            '-keyout', str(key_file),
            '-out', str(cert_file),
            '-days', '365',
            '-nodes',
            '-subj', '/CN=localhost'
        ], check=True, capture_output=True)

        print(f"✓ Certificate created: {cert_file}")
        print(f"✓ Key created: {key_file}")
        return cert_file, key_file
    except Exception as e:
        print(f"✗ Error creating certificate: {e}")
        print("\nTo create manually, run:")
        print("  openssl req -x509 -newkey rsa:2048 -keyout debug_key.pem -out debug_cert.pem -days 365 -nodes -subj '/CN=localhost'")
        sys.exit(1)


def main():
    # Determine port (use 8443 if no root, otherwise 443)
    port = 443
    if os.getuid() != 0:
        port = 8443
        print(f"ℹ Running without root, using port {port} instead of 443")

    # Create certificate
    cert_file, key_file = create_self_signed_cert()

    # Setup HTTPS
    server_address = ('0.0.0.0', port)
    httpd = http.server.HTTPServer(server_address, DebugRequestHandler)

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(str(cert_file), str(key_file))
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

    # Get local IP for user reference
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except:
        local_ip = "127.0.0.1"

    print("\n" + "="*80)
    print("🚀 DEBUG SERVER STARTED")
    print("="*80)
    print(f"\nListening on: https://0.0.0.0:{port}")
    print(f"Local IP (for profile): {local_ip}")
    print(f"Localhost: https://127.0.0.1:{port}")
    print("\n" + "-"*80)
    print("CONFIGURATION FOR YOUR PROFILE:")
    print("-"*80)

    if port == 443:
        print(f"\nDeviceIP state variable: {local_ip}")
        print("Port: 443 (HTTPS)")
    else:
        print(f"\nDeviceIP state variable: {local_ip}:{port}")
        print(f"Port: {port} (HTTPS)")

    print("\n" + "-"*80)
    print("CERTIFICATE INFO:")
    print("-"*80)
    print(f"Certificate: {cert_file}")
    print(f"Key: {key_file}")
    print("\nNote: This is a self-signed certificate.")
    print("Your profile/client should accept it without validation for testing.")

    print("\n" + "-"*80)
    print("ENDPOINTS AVAILABLE:")
    print("-"*80)
    print("  POST /api/v1/auth/key         - Authentication")
    print("  POST /api/v1/wall/power       - Set power state")
    print("  GET  /api/v1/wall/power       - Get power state")
    print("  POST /api/v1/wall/brightness  - Set brightness")
    print("  GET  /api/v1/wall/brightness  - Get brightness")
    print("  POST /api/v1/wall/preset      - Set preset")
    print("  POST /api/v1/* (any)          - Any other endpoint")

    print("\n" + "-"*80)
    print("Ready to receive requests. Press Ctrl+C to stop.")
    print("-"*80 + "\n")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped")
        sys.exit(0)


if __name__ == '__main__':
    main()
