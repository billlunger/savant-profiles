#!/usr/bin/env python3
"""
Barco Video Wall Manager REST API Relay Server
Runs on localhost:5000 to relay Savant profile commands to the Barco VwM REST API.

This server acts as an intermediary between Savant (which cannot handle dynamic headers)
and the Barco REST API (which requires session cookies). The relay server:
1. Receives JSON commands from Savant over raw TCP
2. Authenticates with Barco using the provided API key
3. Relays the command using the obtained session cookie
4. Returns the response to Savant
5. Forgets the session cookie (stateless per-request)

Minimal dependencies - uses only Python standard library (socket, json, urllib).
"""

import json
import ssl
import socket
import urllib.request
import urllib.error
import sys

# Configuration
RELAY_HOST = 'localhost'
RELAY_PORT = 5000

# SSL context for self-signed certificates (Barco uses self-signed by default)
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


class BarcoRelayHandler:
    """TCP socket handler for the relay server."""

    def __init__(self, client_socket, client_address):
        """Initialize handler with connected socket."""
        self.client_socket = client_socket
        self.client_address = client_address

    def handle(self):
        """Handle incoming connection from Savant."""
        try:
            # Keep connection open to handle multiple commands from Savant
            while True:
                # Read JSON command from Savant (ends with \r\n from profile postfix)
                buffer = b''
                while True:
                    try:
                        data = self.client_socket.recv(1024)
                        if not data:
                            # Connection closed by client
                            return
                        buffer += data

                        # Check for end of command (newline)
                        if b'\n' in buffer:
                            break
                    except socket.timeout:
                        # Timeout waiting for data, client may have disconnected
                        return

                # Decode and parse JSON
                json_str = buffer.decode('utf-8').strip()

                if not json_str:
                    self._send_response({'result': 'error', 'message': 'Empty request'})
                    continue

                try:
                    request_data = json.loads(json_str)
                    action = request_data.get('action')

                    print(f'[{self.client_address[0]}] ACTION: {action}', file=sys.stderr)

                    # Route based on action
                    if action == 'set_power':
                        response = self._handle_set_power(request_data)
                    elif action == 'get_power':
                        response = self._handle_get_power(request_data)
                    elif action == 'set_brightness':
                        response = self._handle_set_brightness(request_data)
                    elif action == 'get_brightness':
                        response = self._handle_get_brightness(request_data)
                    elif action == 'set_preset':
                        response = self._handle_set_preset(request_data)
                    else:
                        response = {'result': 'error', 'message': f'Unknown action: {action}'}

                    print(f'[{self.client_address[0]}] RESPONSE: {response}', file=sys.stderr)
                    self._send_response(response)

                except json.JSONDecodeError as e:
                    self._send_response({'result': 'error', 'message': f'Invalid JSON: {str(e)}'})
                    print(f'[{self.client_address[0]}] JSON decode error: {str(e)}', file=sys.stderr)
                except Exception as e:
                    self._send_response({'result': 'error', 'message': str(e)})
                    print(f'[{self.client_address[0]}] Error: {str(e)}', file=sys.stderr)

        except Exception as e:
            print(f'[{self.client_address[0]}] Connection error: {str(e)}', file=sys.stderr)
        finally:
            self.client_socket.close()

    def _get_session_cookie(self, api_key, barco_ip):
        """
        Authenticate with Barco and get a session cookie.
        Returns the cookie string on success, or a dict error on failure.
        """
        auth_url = f'https://{barco_ip}/api/v1/auth/key'
        print(f'[{self.client_address[0]}] Authenticating with Barco at {barco_ip}', file=sys.stderr)

        auth_body = json.dumps({
            'type': 'REST',
            'key': api_key
        }).encode('utf-8')

        try:
            req = urllib.request.Request(
                auth_url,
                data=auth_body,
                headers={'Content-Type': 'application/json'}
            )

            response = urllib.request.urlopen(req, context=ssl_context, timeout=10)

            # Extract session cookie from Set-Cookie header
            cookie_header = response.headers.get('Set-Cookie', '')
            if not cookie_header:
                return {'result': 'error', 'message': 'No session cookie received from Barco'}

            # Extract SID from cookie (format: "SID=xxx; Path=/; ...")
            session_cookie = cookie_header.split(';')[0]
            print(f'[{self.client_address[0]}] Got session cookie', file=sys.stderr)
            return session_cookie

        except urllib.error.HTTPError as e:
            return {'result': 'error', 'message': f'Authentication failed: {e.code} {e.reason}'}
        except Exception as e:
            return {'result': 'error', 'message': f'Authentication error: {str(e)}'}

    def _handle_set_power(self, request_data):
        """
        Set power state (on, standby, or idle).

        Expected request: {"api_key": "...", "barco_ip": "...", "action": "set_power", "power_state": "on|standby|idle"}
        Returns: {"result": "accepted"} or error
        """
        api_key = request_data.get('api_key')
        barco_ip = request_data.get('barco_ip')
        power_state = request_data.get('power_state', '').lower()

        if not api_key or not barco_ip:
            return {'result': 'error', 'message': 'Missing api_key or barco_ip'}

        if power_state not in ['on', 'standby', 'idle']:
            return {'result': 'error', 'message': f'Invalid power_state: {power_state}'}

        # Get fresh session cookie
        session_cookie = self._get_session_cookie(api_key, barco_ip)
        if isinstance(session_cookie, dict) and 'error' in session_cookie:
            return session_cookie

        return self._relay_to_barco(
            f'https://{barco_ip}/api/v1/wall/power',
            {'power': power_state},
            session_cookie
        )

    def _handle_get_power(self, request_data):
        """
        Get current power state.

        Expected request: {"api_key": "...", "barco_ip": "...", "action": "get_power"}
        Returns: {"power": "on|standby|idle"}
        """
        api_key = request_data.get('api_key')
        barco_ip = request_data.get('barco_ip')

        if not api_key or not barco_ip:
            return {'result': 'error', 'message': 'Missing api_key or barco_ip'}

        # Get fresh session cookie
        session_cookie = self._get_session_cookie(api_key, barco_ip)
        if isinstance(session_cookie, dict) and 'error' in session_cookie:
            return session_cookie

        return self._relay_to_barco(
            f'https://{barco_ip}/api/v1/wall/power',
            None,
            session_cookie,
            method='GET'
        )

    def _handle_set_brightness(self, request_data):
        """
        Set brightness level.

        Expected request: {"api_key": "...", "barco_ip": "...", "action": "set_brightness", "brightness": 0-100}
        Returns: {"result": "accepted"} or error
        """
        api_key = request_data.get('api_key')
        barco_ip = request_data.get('barco_ip')
        brightness = request_data.get('brightness')

        if not api_key or not barco_ip:
            return {'result': 'error', 'message': 'Missing api_key or barco_ip'}

        if brightness is None:
            return {'result': 'error', 'message': 'Missing brightness'}

        try:
            brightness_int = int(brightness)
            if not (0 <= brightness_int <= 100):
                return {'result': 'error', 'message': 'Brightness must be 0-100'}
        except (ValueError, TypeError):
            return {'result': 'error', 'message': 'Brightness must be an integer'}

        # Get fresh session cookie
        session_cookie = self._get_session_cookie(api_key, barco_ip)
        if isinstance(session_cookie, dict) and 'error' in session_cookie:
            return session_cookie

        return self._relay_to_barco(
            f'https://{barco_ip}/api/v1/wall/brightness',
            {'brightness': brightness_int},
            session_cookie
        )

    def _handle_get_brightness(self, request_data):
        """
        Get current brightness level.

        Expected request: {"api_key": "...", "barco_ip": "...", "action": "get_brightness"}
        Returns: {"brightness": 0-100}
        """
        api_key = request_data.get('api_key')
        barco_ip = request_data.get('barco_ip')

        if not api_key or not barco_ip:
            return {'result': 'error', 'message': 'Missing api_key or barco_ip'}

        # Get fresh session cookie
        session_cookie = self._get_session_cookie(api_key, barco_ip)
        if isinstance(session_cookie, dict) and 'error' in session_cookie:
            return session_cookie

        return self._relay_to_barco(
            f'https://{barco_ip}/api/v1/wall/brightness',
            None,
            session_cookie,
            method='GET'
        )

    def _handle_set_preset(self, request_data):
        """
        Set preset/profile.

        Expected request: {"api_key": "...", "barco_ip": "...", "action": "set_preset", "preset_name": "..."}
        Returns: {"result": "accepted"} or error
        """
        api_key = request_data.get('api_key')
        barco_ip = request_data.get('barco_ip')
        preset_name = request_data.get('preset_name')

        if not api_key or not barco_ip:
            return {'result': 'error', 'message': 'Missing api_key or barco_ip'}

        if not preset_name:
            return {'result': 'error', 'message': 'Missing preset_name'}

        # Get fresh session cookie
        session_cookie = self._get_session_cookie(api_key, barco_ip)
        if isinstance(session_cookie, dict) and 'error' in session_cookie:
            return session_cookie

        return self._relay_to_barco(
            f'https://{barco_ip}/api/v1/wall/preset',
            {'name': preset_name},
            session_cookie
        )

    def _relay_to_barco(self, url, body_data, session_cookie, method='POST'):
        """
        Relay request to Barco REST API.

        Args:
            url: The Barco API endpoint URL
            body_data: Dictionary to send as JSON body (None for GET requests)
            session_cookie: Session cookie string (e.g., "SID=...")
            method: HTTP method (GET or POST)

        Returns:
            Response dictionary from Barco API
        """
        try:
            headers = {
                'Cookie': session_cookie,
                'Content-Type': 'application/json'
            }

            if method == 'GET':
                req = urllib.request.Request(url, headers=headers, method='GET')
            else:
                body = json.dumps(body_data).encode('utf-8')
                req = urllib.request.Request(url, data=body, headers=headers, method='POST')

            response = urllib.request.urlopen(req, context=ssl_context, timeout=10)
            response_data = json.loads(response.read().decode('utf-8'))

            return response_data

        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            try:
                error_data = json.loads(error_body)
            except:
                error_data = {'message': error_body}

            return {
                'result': 'error',
                'http_code': e.code,
                'message': f'Barco API error: {e.reason}',
                'details': error_data
            }
        except Exception as e:
            return {'result': 'error', 'message': f'Relay error: {str(e)}'}

    def _send_response(self, data):
        """Send response back to Savant."""
        response_text = json.dumps(data)

        # Append \r\n to match Savant profile expectations
        response_bytes = (response_text + '\r\n').encode('utf-8')
        print(f'[{self.client_address[0]}] Sending response: {repr(response_text)}', file=sys.stderr)
        print(f'[{self.client_address[0]}] Response bytes: {repr(response_bytes)}', file=sys.stderr)
        try:
            self.client_socket.sendall(response_bytes)
        except Exception as e:
            print(f'[{self.client_address[0]}] Error sending response: {str(e)}', file=sys.stderr)


def run_relay_server():
    """Start the relay server listening for TCP connections."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((RELAY_HOST, RELAY_PORT))
    server_socket.listen(5)

    print(f'Barco Relay Server starting on {RELAY_HOST}:{RELAY_PORT}')
    print(f'Relay server is stateless - each request must include api_key and barco_ip')
    print(f'Press Ctrl+C to stop the server')
    print()

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            handler = BarcoRelayHandler(client_socket, client_address)
            # Handle each connection in a separate thread (using daemon threads)
            import threading
            thread = threading.Thread(target=handler.handle)
            thread.daemon = True
            thread.start()
    except KeyboardInterrupt:
        print('\nShutting down relay server...')
    finally:
        server_socket.close()


if __name__ == '__main__':
    run_relay_server()
