# Debug Server Setup Guide

This debug server captures exactly what your Savant profile is sending over HTTPS, helping diagnose protocol issues.

## Quick Start

### 1. Start the Server

```bash
cd ~/... Developer/WME-50
python3 debug_server.py
```

The server will:
- Create a self-signed certificate (first run only)
- Listen on port 8443 (port 443 requires root)
- Display your local IP address and listening port
- Show every request with full details

### 2. Update Your Profile

In your `barco_WME-50_REST.xml`, change the DeviceIP state variable to match your local IP:

```xml
<state_variable name="DeviceIP" user_editable="yes" state_center_type="string" owning_logical_component="HD_monitor">YOUR.LOCAL.IP.HERE</state_variable>
```

If the server is running on port 8443 (non-root), you may need to:
- Update the port in your profile control_interfaces, OR
- Include the port in DeviceIP: `YOUR.LOCAL.IP.HERE:8443`

### 3. Test from Savant

Trigger your profile actions (PowerOn, Authenticate, etc.) from RPM Terminal.

The debug server will display:
- **Exact timestamp** of request
- **Method** (GET/POST)
- **Full headers** (with sensitive data masked)
- **Request body** (with JSON parsing if present)
- **Raw bytes** (showing exact \r\n, spaces, etc.)
- **What response was sent**

## What to Look For

### Successful Request Flow

```
[TIMESTAMP] POST Request Received
REQUEST LINE:
  POST /api/v1/auth/key HTTP/1.1
HEADERS:
  Host: 127.0.0.1:8443
  Content-Type: application/json
  Content-Length: 40
BODY (40 bytes):
  {"type":"REST","key":"MyAPIKey1234"}
→ Sending AUTH response (session created)
```

### Common Issues to Spot

**Issue: Missing Content-Length or wrong value**
```
HEADERS:
  Content-Length: 35        ← TOO SMALL
BODY (40 bytes):
  {"type":"REST","key":"MyAPIKey1234"}  ← ACTUALLY 40
```
→ Server waits for more data, times out

**Issue: Missing blank line between headers and body**
```
Raw: 'POST /api/v1/auth/key HTTP/1.1\r\nContent-Type: application/json\r\nContent-Length: 40\r\n{"type":"REST","key":"MyAPIKey1234"}'
     ↑ Should have \r\n\r\n before the {
```
→ Server can't parse the request properly

**Issue: Wrong line endings**
```
Raw: 'POST /api/v1/auth/key HTTP/1.1\nContent-Type: application/json\n'
     ↑ Using \n instead of \r\n
```
→ Some servers reject or misbehave

**Issue: Connection closes before response**
- You see the request logged, but no response line appears
- The debug server shows the request, but then nothing
→ Connection is closing too quickly

## Comparing Requests

Once you capture a request from your profile:

1. **Copy the raw bytes** from the server output
2. **Test manually** with curl or Postman using those exact bytes
3. **See if it works manually** (to confirm it's not the command itself)
4. **Compare** what was different

### Manual Test with curl

If your debug server shows this worked:
```
POST /api/v1/auth/key HTTP/1.1
Host: 127.0.0.1:8443
Content-Type: application/json
Content-Length: 40

{"type":"REST","key":"MyAPIKey1234"}
```

Test it manually:
```bash
curl -k -X POST https://127.0.0.1:8443/api/v1/auth/key \
  -H "Content-Type: application/json" \
  -d '{"type":"REST","key":"MyAPIKey1234"}'
```

## Troubleshooting the Server

### Port Already in Use

If you see "Address already in use":
```bash
# Find what's using the port
lsof -i :8443

# Kill it if needed
kill -9 <PID>
```

### Certificate Issues

If your profile can't connect due to certificate issues:

The debug server uses a self-signed certificate. Depending on how your profile handles HTTPS:

**Option 1:** Update profile to accept self-signed (if possible):
```xml
<ip port="8443" protocol="https" response_time_length_ms="1500" verify_ssl="false"/>
```

**Option 2:** If that's not available, you'll need to tell your system to trust it:
```bash
# Copy certificate to system trust
sudo cp debug_cert.pem /usr/local/share/ca-certificates/
sudo update-ca-certificates
```

### Debug Server Won't Start

If you get permission errors:
```bash
# Run with sudo for port 443
sudo python3 debug_server.py

# Or use port 8443 without sudo (default)
python3 debug_server.py
```

## Next Steps

Once the server is running:

1. Run a test action from your Savant profile
2. Watch the debug server output
3. **Note the exact format of what's being sent**
4. Compare with what you paste manually into RPM Terminal
5. Share the output with me to diagnose the issue

## Stopping the Server

Press `Ctrl+C` in the terminal running the server.

---

## Example Session

```
🚀 DEBUG SERVER STARTED
================================================================================

Listening on: https://0.0.0.0:8443
Local IP (for profile): 192.168.1.100
Localhost: https://127.0.0.1:8443

================================================================================
POST Request Received
================================================================================

REQUEST LINE:
  POST /api/v1/auth/key HTTP/1.1
HEADERS:
  Host: 127.0.0.1:8443
  Content-Type: application/json
  Content-Length: 40

BODY (40 bytes):
  {"type":"REST","key":"YOUR_BARCO_API_KEY"}

PARSED JSON:
  {
    "type": "REST",
    "key": "YOUR_BARCO_API_KEY"
  }

→ Sending AUTH response (session created)

Response sent: {"expiresIn": 1800, "kind": "auth#token", "scope": "API"}
```

This output shows a successful authentication request!
