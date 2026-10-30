#!/usr/bin/env python3
import http.server
import ssl
import json
import sys
import argparse
from urllib.parse import urlparse, parse_qs

# Mock State
DEVICE_STATE = {
    "power": "standby",
    "brightness": 50,
    "input": "HDMI",
    "presets": [
        {"name": "HDMI", "id": "1"},
        {"name": "DisplayPort", "id": "2"},
        {"name": "Profile3", "id": "3"},
        {"name": "Profile4", "id": "4"},
        {"name": "Profile5", "id": "5"},
        {"name": "Profile6", "id": "6"},
        {"name": "Profile7", "id": "7"}
    ]
}

class BarcoMockHandler(http.server.BaseHTTPRequestHandler):
    def _set_response(self, code=200, content_type='application/json'):
        self.send_response(code)
        self.send_header('Content-type', content_type)
        if code == 200 and self.path.endswith('/auth/key'):
             self.send_header('Set-Cookie', 'sid=mock_session_id; Path=/; HttpOnly')
        self.end_headers()

    def do_GET(self):
        self._log_request()
        
        parsed_path = urlparse(self.path)
        
        response_data = {}
        
        if parsed_path.path.endswith('/wall/power'):
            response_data = {"power": DEVICE_STATE["power"]}
        elif parsed_path.path.endswith('/wall/brightness'):
            response_data = {"brightness": DEVICE_STATE["brightness"]}
        elif parsed_path.path.endswith('/wall/presets'):
             response_data = {"presets": DEVICE_STATE["presets"]}
        else:
             self._set_response(404)
             self.wfile.write(json.dumps({"error": "Not Found"}).encode('utf-8'))
             return

        self._set_response()
        self.wfile.write(json.dumps(response_data).encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        body_json = {}
        try:
            body_json = json.loads(post_data.decode('utf-8'))
        except:
            pass

        self._log_request(body=post_data.decode('utf-8'))
        
        parsed_path = urlparse(self.path)
        response_data = {}

        if parsed_path.path.endswith('/auth/key'):
            # Always succeed auth
            response_data = {"status": "ok", "token": "mock_token"}
            
        elif parsed_path.path.endswith('/wall/power'):
            if 'power' in body_json:
                DEVICE_STATE['power'] = body_json['power']
                response_data = {"power": DEVICE_STATE['power']}
            else:
                 self._set_response(400)
                 return
                 
        elif parsed_path.path.endswith('/wall/brightness'):
            if 'brightness' in body_json:
                DEVICE_STATE['brightness'] = int(body_json['brightness'])
                response_data = {"brightness": DEVICE_STATE['brightness']}
            else:
                 self._set_response(400)
                 return

        elif parsed_path.path.endswith('/wall/preset'):
             if 'name' in body_json:
                 DEVICE_STATE['input'] = body_json['name']
                 response_data = {"status": "ok", "selected": DEVICE_STATE['input']}
             else:
                 self._set_response(400)
                 return

        else:
             self._set_response(404)
             self.wfile.write(json.dumps({"error": "Not Found"}).encode('utf-8'))
             return
             
        self._set_response()
        self.wfile.write(json.dumps(response_data).encode('utf-8'))

    def _log_request(self, body=None):
        print("\n" + "="*50)
        print(f"RECEIVED REQUEST: {self.command} {self.path}")
        print("-" * 20)
        print("HEADERS:")
        print(self.headers)
        if body:
            print("-" * 20)
            print("BODY:")
            print(body)
        print("="*50 + "\n")

    def log_message(self, format, *args):
        # Override to silence default logging if desired, or keep it.
        # Keeping it for now but redirecting to stderr to separate from our custom logs
        sys.stderr.write("%s - - [%s] %s\n" %
                         (self.client_address[0],
                          self.log_date_time_string(),
                          format%args))

def run(server_class=http.server.HTTPServer, handler_class=BarcoMockHandler, port=443):
    server_address = ('0.0.0.0', port)
    httpd = server_class(server_address, handler_class)
    
    # SSL Context
    # We use the generated server.pem for both certificate and key
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile='./server.pem', keyfile='./server.pem')
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

    print(f"Starting Barco Mock Server on https://0.0.0.0:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        httpd.server_close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Barco Mock Server")
    parser.add_argument('port', type=int, nargs='?', default=443, help='Port to listen on (default: 443)')
    args = parser.parse_args()
    
    run(port=args.port)
