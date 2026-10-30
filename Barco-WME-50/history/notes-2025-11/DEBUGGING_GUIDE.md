# Savant REST API Profile - Debugging Guide

## Problem Statement

When sending commands via the Savant profile over TCP-TLS:
- ❌ Command sent by Savant → **No response**
- ✅ Same command pasted manually into RPM Terminal → **Response received**

This indicates a **protocol-level issue** with how Savant is framing or sending the HTTP request.

## Solution: Use Local Debug Server

We've created a local HTTPS server that captures every byte sent to it, showing you exactly what's different.

---

## Step 1: Start the Debug Server

```bash
cd ~/... Developer/WME-50
python3 debug_server.py
```

**Expected output:**
```
🚀 DEBUG SERVER STARTED
================================================================================
Listening on: https://0.0.0.0:8443
Local IP (for profile): 192.168.1.XXX
Localhost: https://127.0.0.1:8443
```

Note your local IP address (or use 127.0.0.1 if testing locally).

---

## Step 2: Load Debug Profile

In your Savant development environment:

1. Import `barco_WME-50_DEBUG.xml` profile
2. Update the `DeviceIP` state variable to your local IP or `127.0.0.1`
3. If the server is running on port 8443 (non-root), make sure port 8443 is set in the profile

This profile has three simple test actions:
- **Do_Authenticate** - Tests the auth endpoint
- **PowerOn** - Tests injecting the session cookie
- **PowerOff** - Tests another power command
- **Get_Status** - Tests GET requests

---

## Step 3: Test Individual Actions

### Test 1: Authentication (Start here)

In RPM Terminal, trigger: **Do_Authenticate**

**Watch the debug server output:**
```
================================================================================
[2024-01-15 14:23:45.123] POST Request Received
================================================================================

REQUEST LINE:
  POST /api/v1/auth/key HTTP/1.1
HEADERS:
  Host: 127.0.0.1:8443
  Content-Type: application/json
  User-Agent: Savant/1.0
  Content-Length: 40
BODY (40 bytes):
  {"type":"REST","key":"TestKey12345678"}

PARSED JSON:
  {
    "type": "REST",
    "key": "TestKey12345678"
  }

→ Sending AUTH response (session created)

Response sent: {"expiresIn": 1800, "kind": "auth#token", "scope": "API"}
```

**What to verify:**
- [ ] Request appears in server output
- [ ] Content-Length matches actual body size (count the JSON bytes)
- [ ] Headers are complete and correct
- [ ] Server log shows "Response sent"
- [ ] Did you see this working in RPM Terminal?

### Test 2: If Auth Worked, Test Power

In RPM Terminal, trigger: **PowerOn**

**Watch the debug server output for:**
- [ ] Request appears in server log
- [ ] Cookie header is populated: `Cookie: sid=debug_session_12345`
- [ ] Content-Length is correct (15 for `{"power": "on"}`)
- [ ] Response is sent

---

## Step 4: Compare Working vs Non-Working

If the debug server shows a request but Savant doesn't get a response:

### Method A: Copy from Debug Server

1. In debug server output, find the "RAW REQUEST" section
2. Copy the exact raw bytes (the long `repr()` string)
3. Paste into RPM Terminal
4. Note: Does it work when you paste it manually?

**Example:**
```
Raw: 'POST /api/v1/auth/key HTTP/1.1\r\nHost: 127.0.0.1:8443\r\nContent-Type: application/json\r\nUser-Agent: Savant/1.0\r\nContent-Length: 40\r\n\r\n{"type":"REST","key":"TestKey12345678"}'
```

### Method B: Test with curl

```bash
curl -v -k -X POST https://127.0.0.1:8443/api/v1/auth/key \
  -H "Content-Type: application/json" \
  -H "User-Agent: Savant/1.0" \
  -d '{"type":"REST","key":"TestKey12345678"}'
```

Does curl get a response? (It should if your server is running)

---

## Common Issues & Solutions

### Issue 1: Content-Length Mismatch

**Symptom:** Server shows request but body size doesn't match Content-Length header

```
Content-Length: 35
BODY (40 bytes):
  {"type":"REST","key":"TestKey12345678"}
```

**Why it fails:** Server waits for 5 more bytes (35+5=40), times out before responding

**Solution:** Count the JSON bytes exactly
```python
# Count this:
json = '{"type":"REST","key":"TestKey12345678"}'
len(json)  # = 40 bytes
```

Update your profile's Content-Length to match.

---

### Issue 2: Missing or Extra Blank Line

**Symptom:** Server shows request but response doesn't appear

HTTP requires a blank line (`\r\n\r\n`) between headers and body.

**Wrong:**
```
Content-Length: 40\r\n{"type":"REST"...
                   ↑ Missing blank line
```

**Correct:**
```
Content-Length: 40\r\n\r\n{"type":"REST"...
                    ↑ Has blank line
```

**How to fix in profile:**
- After all headers, add: `\r\n\r\n` before the JSON body
- Or use separate `<command_string>` tags (one for headers, one for body with leading `\r\n`)

---

### Issue 3: Connection Closes Before Response

**Symptom:** Request appears in debug server log, but no "Response sent" line

**Why:** Savant closes the TCP connection before the server can send the response

**Solution:** Check your response_time_length_ms in control_interfaces:
```xml
<ip port="8443" protocol="https" response_time_length_ms="2000"/>
```

Try increasing this value (in milliseconds). Current: 2000ms = 2 seconds

---

### Issue 4: Dynamic Parameters Not Injecting

**Symptom:** SessionCookie not appearing in Cookie header after auth

```
// EXPECTED:
Cookie: sid=debug_session_12345

// ACTUAL:
Cookie: %s
```

**Why:** State variable substitution might not be working

**Debug steps:**
1. Check that `Do_Authenticate` was called first (to populate SessionCookie)
2. Watch if the SessionCookie state variable gets populated in your Savant system
3. Try a simpler test with a static value instead of state variable

---

### Issue 5: HTTPS/TLS Handshake Fails

**Symptom:** No request appears in debug server, connection refused

**Why:** Profile can't establish TLS connection to debug server

**Solutions:**
1. Make sure debug_server.py is running
2. Try with `verify_ssl="false"` in your profile (if supported):
   ```xml
   <ip port="8443" protocol="https" verify_ssl="false"/>
   ```
3. Test manually with curl:
   ```bash
   curl -v -k https://127.0.0.1:8443/api/v1/auth/key
   ```
   If curl works but Savant doesn't, it's a profile configuration issue.

---

## Data Collection Template

When you've run the tests, fill this out and share it:

```
DEBUG SESSION REPORT
====================

LOCAL IP: _______________
Port: _______________

TEST 1: Do_Authenticate
- Request appeared in server? YES / NO
- Content-Length correct? YES / NO / NOT SURE
- Response appears in server log? YES / NO
- Did Savant receive the response? YES / NO
- When you paste the raw bytes manually, does it work? YES / NO

SERVER OUTPUT (paste the full request/response):
[INSERT HERE]

TEST 2: PowerOn (after auth)
- Request appeared in server? YES / NO
- Cookie header populated? YES / NO
- Content-Length correct? YES / NO
- Response appears? YES / NO
- Did Savant receive response? YES / NO

SERVER OUTPUT:
[INSERT HERE]

CURL TEST (if attempted):
Command: curl -v -k ...
Result: [PASTE OUTPUT]

MANUAL TEST (command pasted into RPM Terminal):
Raw command: [PASTE FROM SERVER LOG]
Result in RPM Terminal: [SUCCESS / FAILED / TIMEOUT]
```

---

## Next Steps

Once you've collected this data:

1. **If all debug server tests work**, the issue is in Savant's HTTP handling
   - Problem: Content-Length calculation, parameter injection, or connection management
   - Solution: Adjust profile structure, response timeouts, header formatting

2. **If manual pastes work but Savant fails**, the issue is how Savant builds/sends the request
   - Compare the working command with what Savant sent
   - Identify the difference (missing space, wrong CRLF, etc.)

3. **If both fail**, the Barco device isn't responding
   - Verify the actual Barco device is online and API is enabled
   - Test with the real Barco IP address instead of debug server

---

## Files in This Setup

- **debug_server.py** - The HTTPS debug server (captures all requests)
- **barco_WME-50_DEBUG.xml** - Test profile for local debugging
- **DEBUG_SERVER_SETUP.md** - Detailed server setup instructions
- **DEBUGGING_GUIDE.md** - This file
- **debug_cert.pem** - Self-signed certificate (auto-created on first run)
- **debug_key.pem** - Private key (auto-created on first run)

---

## Still Stuck?

If you've run through all this and still can't identify the issue:

1. Run `debug_server.py`
2. Trigger one simple action (Do_Authenticate)
3. Copy the entire output from the server
4. Share that output + the exact error you see in Savant
5. I can help diagnose from there

The debug server output is the key - it shows exactly what Savant is sending vs. what should be sent.
