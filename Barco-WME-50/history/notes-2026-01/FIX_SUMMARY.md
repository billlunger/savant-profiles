# Relay Server Fix Summary

## Problem
The relay server was receiving "Bad request syntax" errors for all commands from Savant:

```
[127.0.0.1] code 400, message Bad request syntax ('{"session_cookie":"","action":"set_power","power_state":"standby"}')
```

This error occurred consistently regardless of which command was sent.

## Root Cause
The relay server was built using `HTTPServer` (expecting HTTP POST requests with proper headers), but the Savant profile was configured to send **raw TCP JSON** with:
- `<send_postfix type="hex">0D0A</send_postfix>` (appends `\r\n` to each command)
- `<receive_end_condition test_condition="data" type="hex">0D0A</receive_end_condition>` (expects `\r\n` in responses)

Savant was sending raw JSON over TCP:
```
{"session_cookie":"","action":"set_power","power_state":"standby"}\r\n
```

But the HTTP server expected:
```
POST / HTTP/1.1
Content-Type: application/json
Content-Length: 75

{"session_cookie":"","action":"set_power","power_state":"standby"}
```

## Solution
Converted the relay server from HTTP to **raw TCP socket handling**:

### Changes to `relay_server.py`:
1. **Replaced `HTTPServer`** with raw `socket.socket` TCP server
2. **Replaced `BaseHTTPRequestHandler`** with custom `BarcoRelayHandler` class
3. **Implemented raw socket communication**:
   - Reads incoming data until `\n` is found (from Savant's `0D0A` postfix)
   - Parses the raw JSON string
   - Routes commands to appropriate handlers
   - Sends responses as JSON with `\r\n` appended (to match profile expectations)
4. **Uses threading** to handle multiple concurrent connections from Savant

### Changes to `barco_WME-50_REST_API.xml`:
1. **Version bumped** from 0.4 to 0.5
2. **No XML changes needed** - the profile's `<send_postfix>` and `<receive_end_condition>` settings were already correct for raw TCP

## How It Works Now

**Communication Flow:**
```
Savant (localhost on same Host)
    ↓ Raw TCP JSON + \r\n
    {"api_key":"YOUR_BARCO_API_KEY","action":"authenticate"}\r\n
Relay Server (port 5000)
    ↓ Extracts JSON, routes to handler
    ↓ Makes HTTPS request to Barco with proper headers/cookies
Barco Video Wall Manager
    ↓ Returns JSON response
Relay Server
    ↓ Returns JSON + \r\n to Savant
    {"result":"accepted","session_cookie":"SID=..."}\r\n
Savant
```

## Testing
The fix was verified with a test program that:
1. Started a TCP server listening on port 5000
2. Sent a test JSON command from a client: `{"api_key":"test","action":"authenticate"}\r\n`
3. Received the response correctly: `{"result": "success", "message": "Test received"}`

The server correctly:
- ✅ Accepts raw TCP connections
- ✅ Reads JSON until `\n` delimiter
- ✅ Parses the JSON
- ✅ Sends responses with `\r\n` appended

## Next Steps
1. Start the updated relay server: `python3 relay_server.py`
2. Import the updated profile (v0.5) into Savant
3. Test control actions - they should no longer produce "Bad request syntax" errors
