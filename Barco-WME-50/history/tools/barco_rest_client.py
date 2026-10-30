#!/usr/bin/env python3
import argparse
import json
import ssl
import sys
import urllib.request
import urllib.error

# Disable SSL verification for self-signed certificates (common in AV hardware)
ssl._create_default_https_context = ssl._create_unverified_context

def make_request(url, method='GET', data=None, headers=None):
    if headers is None:
        headers = {}
    
    # Ensure Content-Type is JSON if we are sending data
    if data and 'Content-Type' not in headers:
        headers['Content-Type'] = 'application/json'
        
    encoded_data = None
    if data:
        encoded_data = json.dumps(data).encode('utf-8')
        
    req = urllib.request.Request(url, data=encoded_data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            resp_headers = response.info()
            resp_body = response.read().decode('utf-8')
            return {
                'status': response.getcode(),
                'headers': resp_headers,
                'body': resp_body
            }
    except urllib.error.HTTPError as e:
        # Return error details instead of crashing
        error_body = e.read().decode('utf-8')
        return {
            'status': e.code,
            'body': error_body,
            'error': str(e)
        }
    except Exception as e:
        return {'error': str(e)}

def command_auth(args):
    """Authenticate and return the session cookie."""
    url = f"{args.base_url}/auth/key"
    payload = {
        "type": "REST",
        "key": args.key
    }
    
    result = make_request(url, method='POST', data=payload)
    
    if result.get('status') == 200:
        # Extract Set-Cookie header
        # Headers in urllib are case-insensitive dict-like objects
        cookie_header = result['headers'].get('Set-Cookie')
        if cookie_header:
            # Typically format is "sid=...; Path=/; ..."
            # We just need the first part for the Cookie header
            cookie_val = cookie_header.split(';')[0]
            print(f"AuthCookie={cookie_val}")
        else:
            print("Error: No Set-Cookie header returned", file=sys.stderr)
            print(json.dumps(result), file=sys.stderr)
    else:
        print("Error: Auth failed", file=sys.stderr)
        print(json.dumps(result), file=sys.stderr)

def command_power(args):
    """Set power state."""
    url = f"{args.base_url}/wall/power"
    headers = {'Cookie': args.cookie}
    
    if args.state:
        # Set Power
        payload = {"power": args.state}
        result = make_request(url, method='POST', data=payload, headers=headers)
    else:
        # Get Power
        result = make_request(url, method='GET', headers=headers)
        
    if result.get('status') == 200:
        try:
            body_json = json.loads(result['body'])
            # Assuming GET returns {"power": "on"} or similar
            if 'power' in body_json:
                print(f"Power_State={body_json['power'].upper()}") # Savant usually likes uppercase
            else:
                print(result['body'])
        except:
            print(result['body'])
    else:
        print(f"Error: {result.get('error', 'Unknown')}", file=sys.stderr)

def command_brightness(args):
    """Set or Get brightness."""
    url = f"{args.base_url}/wall/brightness"
    headers = {'Cookie': args.cookie}
    
    if args.level is not None:
        # Set Brightness
        payload = {"brightness": int(args.level)}
        result = make_request(url, method='POST', data=payload, headers=headers)
    else:
        # Get Brightness
        result = make_request(url, method='GET', headers=headers)
        
    if result.get('status') == 200:
        try:
            body_json = json.loads(result['body'])
            if 'brightness' in body_json:
                print(f"Screen_Luminance={body_json['brightness']}")
            else:
                print(result['body'])
        except:
            print(result['body'])
    else:
        print(f"Error: {result.get('error', 'Unknown')}", file=sys.stderr)

def command_preset(args):
    """Activate or Get Presets."""
    headers = {'Cookie': args.cookie}
    
    if args.name:
        # Activate Preset
        url = f"{args.base_url}/wall/preset"
        payload = {"name": args.name}
        result = make_request(url, method='POST', data=payload, headers=headers)
        
        if result.get('status') == 200:
            # If successful, we might want to update a state variable
            print(f"SelectedInput={args.name}")
        else:
             print(f"Error invoking preset: {result.get('error')}", file=sys.stderr)

    else:
        # Get Presets List (Optional, mostly for debug or feedback)
        url = f"{args.base_url}/wall/presets"
        result = make_request(url, method='GET', headers=headers)
        print(result.get('body'))

def main():
    parser = argparse.ArgumentParser(description="Barco REST API Helper")
    parser.add_argument("HOST", help="IP address or hostname of the Barco device")
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Auth Command
    auth_parser = subparsers.add_parser("auth", help="Authenticate and retrieve cookie")
    auth_parser.add_argument("--key", required=True, help="API Key")
    
    # Power Command
    power_parser = subparsers.add_parser("power", help="Power control")
    power_parser.add_argument("--cookie", required=True, help="Auth Cookie")
    power_parser.add_argument("--state", choices=["on", "idle", "standby"], help="Power state to set (leave empty to get)")
    
    # Brightness Command
    bright_parser = subparsers.add_parser("brightness", help="Brightness control")
    bright_parser.add_argument("--cookie", required=True, help="Auth Cookie")
    bright_parser.add_argument("--level", type=int, help="Brightness level (0-100)")
    
    # Preset Command (also used for Inputs if they are treated as presets)
    preset_parser = subparsers.add_parser("preset", help="Preset/Input selection")
    preset_parser.add_argument("--cookie", required=True, help="Auth Cookie")
    preset_parser.add_argument("--name", help="Name of any preset to recall")
    
    args = parser.parse_args()
    
    # Construct Base URL
    # Assuming HTTPS based on documentation
    args.base_url = f"https://{args.HOST}/api/v1"
    
    if args.command == "auth":
        command_auth(args)
    elif args.command == "power":
        command_power(args)
    elif args.command == "brightness":
        command_brightness(args)
    elif args.command == "preset":
        command_preset(args)

if __name__ == "__main__":
    main()
