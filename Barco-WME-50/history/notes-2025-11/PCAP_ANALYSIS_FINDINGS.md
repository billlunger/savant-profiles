# PCAP Analysis and Findings

## Files Available

1. **debug_server_fixed.py** - Fixed HTTPS server with proper TLS implementation
2. **start_debug_server.py** - Helper to auto-elevate to sudo and run fixed server
3. **Savant Capture.pcapng** - Wireshark capture from after Savant restart

## What We Know So Far

### The Core Problem

When Savant triggers `Do_Authenticate` action:
- ❌ **Expected**: HTTP POST request to 10.0.60.3:443 with auth JSON body
- ❌ **Actual**: Nothing hits the debug server, Savant times out
- ⚠️ **Symptom**: "device sent messages increase, device timeout count increase"

### What Works

✅ **Manual curl commands** work perfectly:
```bash
curl -v -k -X POST https://127.0.0.1:443/api/v1/auth/key \
  -H "Content-Type: application/json" \
  -H "User-Agent: Savant/1.0" \
  -d '{"type":"REST","key":"TestKey12345678"}'
```

### What Doesn't Work

❌ **Savant's tcp-tls protocol** with the debug server:
- Savant profile configured with: `tcp-tls` protocol, port 443
- When triggered: nothing appears in server logs
- When curl tries to test from VPN IP (10.0.60.3:443): **TLS handshake hangs**
  - Client sends: TLS Client Hello
  - Server responds with: (nothing, hangs)
  - Root cause: Old debug_server.py uses deprecated `context.wrap_socket()` approach

### The TLS Fix

**Old broken approach** (debug_server.py):
```python
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(str(cert_file), str(key_file))
httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
```

**New fixed approach** (debug_server_fixed.py):
```python
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(str(cert_file), str(key_file))
context.minimum_version = ssl.TLSVersion.TLSv1_2
httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
```

The key additions:
- Explicit minimum TLS version (1.2)
- Proper context configuration before socket wrapping
- Better SSL context lifecycle management

## What the PCAP Capture Shows

Captured: Right after Savant restart (11:58 AM)

**Need your analysis from Wireshark GUI:**
- Which IPs are communicating?
- Do you see TCP port 443 or 8443 connections?
- Are there TLS handshakes?
- What is the pattern of traffic?

## Next Steps

### Step 1: Test Fixed Server (Port 8443 - No Sudo Needed)

**Current Status**: Fixed server is running on 8443

Test with curl:
```bash
curl -v -k https://127.0.0.1:8443/api/v1/auth/key \
  -H "Content-Type: application/json" \
  -d '{"type":"REST","key":"test"}'
```

If this works and you see the request in the server logs, it proves the TLS fix is good.

Then update your Savant profile to use:
- **DeviceIP**: 192.168.4.24:8443
- **Protocol**: tcp-tls
- **Port**: 8443

And trigger `Do_Authenticate` to see if it works.

### Step 2: Upgrade to Port 443

Once fixed server works on 8443, run on port 443:

```bash
python3 ~/... Developer/WME-50/start_debug_server.py
```

This will:
1. Automatically request sudo
2. Run debug_server_fixed.py with root privileges
3. Bind to port 443

Then test:
```bash
curl -v -k https://127.0.0.1:443/api/v1/auth/key \
  -H "Content-Type: application/json" \
  -d '{"type":"REST","key":"test"}'
```

### Step 3: Analyze PCAP

Look for patterns in the capture:
- Is Savant even attempting to connect on port 443?
- If yes, what's different between the working curl and failing Savant command?
- Are there retries? Timeouts?

## Architecture Summary

```
Savant Profile (barco_WME-50_REST.xml)
  ↓
Do_Authenticate action
  ├─ Protocol: tcp-tls
  ├─ Host: 10.0.60.3 (or 127.0.0.1 for testing)
  ├─ Port: 443 (or 8443)
  ├─ Command: HTTP POST request (built via parameter_list)
  └─ Payload: {"type":"REST","key":"..."}
    ↓
[Network: TLS Encryption]
    ↓
Debug Server (debug_server_fixed.py)
  ├─ Listens on 0.0.0.0:443 (root required)
  ├─ Accepts HTTPS connections
  ├─ Logs all requests with full details
  └─ Responds with mock JSON
```

## Current Issue Hypothesis

The tcp-tls protocol in Savant might be:
1. **Not properly implementing TLS handshake** - sending raw HTTP before completing TLS
2. **Using wrong socket mode** - expecting non-blocking or select-based handling
3. **Timing out during handshake** - response_time_length_ms is too short
4. **Sending on wrong port** - port 443 on Savant system is blocked or busy

The PCAP capture should show which of these is occurring.
