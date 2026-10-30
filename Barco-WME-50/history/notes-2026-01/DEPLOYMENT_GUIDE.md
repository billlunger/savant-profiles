# Barco WME-50 REST API - Deployment Guide

## Quick Start (5 Minutes)

### Step 1: Get Your Barco API Key
1. Open Barco VwM web interface in browser (https://[barco-ip])
2. Navigate to **Settings → Security → API Keys**
3. Copy the API key (e.g., `YOUR_BARCO_API_KEY`)
4. Note: API key does not expire and is used only for initial authentication

### Step 2: Start the Relay Server
```bash
# Navigate to the directory with relay_server.py
cd /path/to/Barco\ WME\ SCLI

# Start the relay server
python3 relay_server.py
```

**Expected output:**
```
Barco Relay Server starting on localhost:5000
Default Barco IP: 172.29.1.1
Note: Barco IP can be configured at runtime via ConfigureRelay action
Press Ctrl+C to stop the server
```

### Step 3: Configure Savant Profile
1. In Savant, import `barco_WME-50_REST_API.xml` (version 0.13)
2. Set these state variables:
   - **Barco_IP**: Your Barco device IP (e.g., `172.29.1.1`)
   - **API_Key**: The API key from Step 1 (e.g., `YOUR_BARCO_API_KEY`)
   - Leave **Session_Cookie** blank (auto-populated by Authenticate)

### Step 4: Authenticate
1. In Savant, trigger the **Authenticate** action
2. Barco VwM will respond with a session cookie
3. Savant automatically stores it in Session_Cookie state variable
4. You're ready to control the display!

### Step 5: Control the Display
- **PowerOn** / **PowerOff** - Control power state
- **SetBrightness** - Set brightness (0-100), then trigger action
- **SelectProfile3-7** - Switch to preset profiles
- **SelectInputHDMI** / **SelectInputDisplayPort** - Switch inputs
- **GetBrightness** / **GetPowerState** - Query current state

---

## Detailed Configuration

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ Savant Control System (Windows/Mac/Linux)                   │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ barco_WME-50_REST_API.xml (Profile v0.13)               │ │
│ │ State Variables:                                         │ │
│ │  - Barco_IP: 172.29.1.1                                 │ │
│ │  - API_Key: YOUR_BARCO_API_KEY                             │ │
│ │  - Session_Cookie: (auto-populated)                     │ │
│ │  - Power_State, Screen_Luminance, SelectedInput, etc.   │ │
│ └─────────────────────────────────────────────────────────┘ │
│         │ JSON commands over TCP to localhost:5000            │
│         ▼                                                     │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Relay Server (relay_server.py)                          │ │
│ │ Listen: localhost:5000 (TCP)                            │ │
│ │ Functions:                                               │ │
│ │  - Parse JSON commands from Savant                      │ │
│ │  - Manage session cookies (30-min lifetime)             │ │
│ │  - Relay to Barco HTTPS API                             │ │
│ │  - Return JSON responses to Savant                      │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
         │ HTTPS to 172.29.1.1/api/v1
         ▼
┌─────────────────────────────────────────────────────────────┐
│ Barco Video Wall Manager (REST API)                         │
│ - /api/v1/auth/key (authentication)                        │
│ - /api/v1/wall/power (power control)                       │
│ - /api/v1/wall/brightness (brightness control)             │
│ - /api/v1/wall/preset (profile/input selection)            │
└─────────────────────────────────────────────────────────────┘
```

### Prerequisites

**Software:**
- Python 3.6+ (uses only standard library: socket, json, ssl, threading)
- Savant (any recent version supporting REST/TCP profiles)

**Hardware:**
- Barco WME-50 or compatible Barco Video Wall Manager
- Network connectivity between Savant host and Barco device
- Both systems on same network or routable network

**Network:**
- Barco IP accessible from Savant host (test: `ping 172.29.1.1`)
- Port 5000 available on Savant host (test: `netstat -an | grep 5000`)
- HTTPS connectivity from Savant to Barco (usually port 443)

### Configuration Details

#### Relay Server Configuration

**File:** `relay_server.py` (lines 23-39)

```python
# Configuration
RELAY_HOST = 'localhost'  # Change to 0.0.0.0 for remote access
RELAY_PORT = 5000

# Default Barco IP - can be changed via Authenticate action
BARCO_IP = '172.29.1.1'  # Update to your Barco device IP

# SSL context for self-signed certificates (Barco uses self-signed by default)
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE
```

**To change the Barco IP:**
1. Option A: Edit line 28 in relay_server.py and restart
2. Option B: Update `Barco_IP` state variable in Savant - relay server accepts it in Authenticate action

#### Savant Profile Configuration

**File:** `barco_WME-50_REST_API.xml`

**State Variables (lines 43-57):**
```xml
<state_variable name="Barco_IP" ... >172.29.1.1</state_variable>
<state_variable name="API_Key" ... ></state_variable>
<state_variable name="Session_Cookie" ... ></state_variable>
<state_variable name="Power_State" ... >standby</state_variable>
<state_variable name="SelectedInput" ... />
<state_variable name="Screen_Luminance" ... >50</state_variable>
```

**User Editable Variables:**
- `Barco_IP` - Set to your Barco VwM IP
- `API_Key` - Set to your API key from VwM Security page
- `Screen_Luminance` - Default brightness (0-100)
- `HDMI` / `DisplayPort` / `Profile3-7` - Customize names if needed

**Control Interface (lines 19-24):**
```xml
<ip port="5000" response_time_length_ms="6000" protocol="tcp">
    <send_postfix type="hex">0D0A</send_postfix>
    <receive_end_condition test_condition="data" type="hex">0D0A</receive_end_condition>
</ip>
```

This specifies:
- TCP port 5000 (where relay server listens)
- 6-second timeout for responses
- Commands are appended with `\r\n` (0D0A hex)
- Responses must contain `\r\n` to be recognized as complete

---

## Installation Steps

### Step 1: Obtain Files

You should have:
- `relay_server.py` - The relay server application
- `barco_WME-50_REST_API.xml` - The Savant profile

Place both in a directory accessible to Savant host. Example locations:
- Linux/Mac: `/opt/barco/` or `~/Documents/Barco/`
- Windows: `C:\Barco\` or `C:\Users\[username]\Documents\Barco\`

### Step 2: Prepare Barco Device

1. Access Barco VwM web interface: `https://[barco-ip]`
2. Log in with admin credentials
3. Navigate to **Settings → Security → API Keys**
4. Generate or copy existing API key
5. **Keep the API key secret** - treat it like a password

### Step 3: Update Relay Server (Optional)

If your Barco device is at a different IP than 172.29.1.1:

**Option A: Edit relay_server.py**
```python
# Line 28 - Change default IP
BARCO_IP = 'YOUR_ACTUAL_BARCO_IP'
```

**Option B: Configure via Savant state variable**
- Set `Barco_IP` in Savant profile to your IP
- Relay server will use it when Authenticate action is called

### Step 4: Test Relay Server Connectivity

Before importing profile, verify relay server can reach Barco:

```bash
# Start relay server
python3 relay_server.py

# In another terminal, test connectivity
telnet localhost 5000
# Should connect without error; press Ctrl+C to exit

# Test Barco connectivity (from relay server host)
curl -k https://172.29.1.1/api/v1/auth/key \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"type":"REST","key":"YOUR_API_KEY"}'
# Should return a Set-Cookie header
```

### Step 5: Import Savant Profile

1. In Savant Designer, go to **File → Import Profile**
2. Select `barco_WME-50_REST_API.xml`
3. Verify import shows no errors
4. Profile version should show as **0.13**

### Step 6: Configure State Variables

1. Select the Barco device in Savant
2. Open Properties or Device Settings
3. Set user-editable state variables:
   - **Barco_IP**: Your actual Barco IP (e.g., `192.168.1.100`)
   - **API_Key**: Your API key from Barco VwM (e.g., `YOUR_BARCO_API_KEY`)
   - **Screen_Luminance**: Default brightness (0-100), default 50
4. Leave **Session_Cookie** blank (will be auto-populated)

### Step 7: Start Relay Server

```bash
# Navigate to relay server directory
cd /path/to/relay_server.py

# Start the relay server (keep this running while Savant controls display)
python3 relay_server.py
```

Expected output:
```
Barco Relay Server starting on localhost:5000
Default Barco IP: 172.29.1.1
Note: Barco IP can be configured at runtime via ConfigureRelay action
Press Ctrl+C to stop the server
```

**Keep this terminal open and the relay server running while using Savant control.**

### Step 8: Authenticate from Savant

1. In Savant, trigger the **Authenticate** action
2. Relay server logs should show:
   ```
   [127.0.0.1] ACTION: authenticate
   [127.0.0.1] RESPONSE: {'result': 'accepted', 'session_cookie': 'SID=...'}
   ```
3. Check that **Session_Cookie** state variable is now populated
4. If it's still blank, check Savant logs for errors

### Step 9: Test Control Actions

Try these actions in order:
1. **GetPowerState** - Should return current power state
2. **PowerOn** - Turn display on
3. **SetBrightness** (set Screen_Luminance to 75 first) - Change brightness
4. **SelectProfile3** - Switch to Profile3
5. **PowerOff** - Turn display to standby

---

## Operation and Maintenance

### Starting the Relay Server

**For development/testing:**
```bash
python3 relay_server.py
```

**For production (background process):**

Linux/Mac (using nohup):
```bash
nohup python3 relay_server.py > /var/log/barco-relay.log 2>&1 &
# Or with screen/tmux for easy monitoring
screen -d -m -S barco python3 relay_server.py
```

Windows (using Task Scheduler):
1. Create a batch file:
   ```batch
   @echo off
   cd C:\Path\To\Barco
   python3 relay_server.py
   ```
2. Create Task Scheduler task to run at startup
3. Set "Run whether user is logged in or not"

### Monitoring the Relay Server

The relay server logs all activity to stderr (usually the terminal window):

```
[CLIENT_IP] ACTION: action_name
[CLIENT_IP] RESPONSE: response_data
[CLIENT_IP] Error: error_message
```

Example healthy log output:
```
[127.0.0.1] ACTION: authenticate
[127.0.0.1] RESPONSE: {'result': 'accepted', 'session_cookie': 'SID=abc123...'}
[127.0.0.1] ACTION: set_power
[127.0.0.1] RESPONSE: {'result': 'accepted'}
[127.0.0.1] ACTION: get_brightness
[127.0.0.1] RESPONSE: {'brightness': 75}
```

### Restarting the Relay Server

If the relay server crashes or becomes unresponsive:
1. Note any error messages in the terminal
2. Stop the server: Press Ctrl+C or kill the process
3. Restart: `python3 relay_server.py`
4. Re-authenticate from Savant if needed (Session_Cookie will be invalid after restart)

### Session Cookie Lifecycle

- **Valid**: First obtained, valid for 30 minutes
- **Expiring Soon**: If commands start failing with 401/403 errors, cookie is expired
- **Expired**: Re-run Authenticate action to get a new cookie
- **Server Restart**: All cookies become invalid, must re-authenticate

---

## Troubleshooting

### Problem: "Connection refused" when Savant tries to control

**Causes:**
1. Relay server not running
2. Wrong port configured in profile
3. Firewall blocking port 5000

**Solutions:**
1. Check relay server is running: `python3 relay_server.py`
2. Verify port 5000 in profile matches relay server RELAY_PORT
3. Check firewall: `netstat -an | grep 5000` (should show LISTEN)

### Problem: "Bad request syntax" or JSON decode errors

**Causes:**
1. Profile generating invalid JSON (shouldn't happen with v0.13)
2. Relay server receiving corrupted data
3. Network issue between Savant and relay server

**Solutions:**
1. Verify profile is v0.13 or later
2. Check relay server logs for exact error
3. Test network: `ping` relay server host from Savant
4. Check for other apps on port 5000: `netstat -an | grep 5000`

### Problem: Session_Cookie not being populated after Authenticate

**Causes:**
1. Barco API key is invalid
2. Barco device not reachable from relay server
3. Profile's JSON path extraction is incorrect
4. Relay server crashed during authentication

**Solutions:**
1. Verify API_Key state variable matches Barco VwM
2. Test connectivity: `curl -k https://[barco-ip]/api/v1/auth/key -X POST ...`
3. Check relay server logs for auth errors
4. Check Savant logs for response parsing errors
5. Re-run Authenticate action

### Problem: Control actions fail with "Missing session_cookie"

**Causes:**
1. Session_Cookie state variable is blank
2. Session cookie has expired (> 30 minutes)
3. Relay server restarted and cookies invalidated

**Solutions:**
1. Run Authenticate action to get session cookie
2. Re-authenticate after 30 minutes
3. Check Session_Cookie state variable is not blank

### Problem: Barco doesn't respond to control commands

**Causes:**
1. Session cookie is invalid/expired
2. Barco VwM is offline or unreachable
3. Command syntax is incorrect
4. Barco device doesn't support the command

**Solutions:**
1. Try re-authenticating
2. Verify Barco IP is correct: `ping [barco-ip]`
3. Check relay server logs for exact error from Barco
4. Verify Barco VwM REST API documentation for endpoint support

### Problem: Relay server crashes or becomes unresponsive

**Causes:**
1. Unexpected error in relay server code
2. Memory leak or resource exhaustion
3. Network timeout on Barco connection

**Solutions:**
1. Check relay server error output
2. Restart relay server
3. Check Barco connectivity
4. Monitor system resources (CPU, memory, open connections)
5. Review FIX_SUMMARY.md for known issues

---

## Performance and Limits

### Expected Performance
- **Authentication**: 1-2 seconds
- **Power Control**: 1-3 seconds
- **Brightness Control**: 1-3 seconds
- **Profile/Input Selection**: 1-5 seconds
- **Status Query**: 1-2 seconds

### Limits
- **Concurrent Connections**: Limited by system resources, typically 50+
- **Commands per Minute**: No strict limit, test with your hardware
- **Session Timeout**: 30 minutes (set by Barco VwM)
- **Request Timeout**: 10 seconds (set in relay_server.py)
- **Response Timeout**: 6 seconds (set in profile)

### Optimization Tips
1. Use persistent connections - don't recreate connection for each command
2. Cache session cookie - avoid re-authenticating unnecessarily
3. Batch brightness changes - don't send every slider movement
4. Add delays between commands if Barco shows slowness

---

## Version History

### v0.13 (Current)
- **Status**: Stable, ready for production
- **Changes**: Fixed JSON path extraction for state variable updates
- **Profile**: barco_WME-50_REST_API.xml (v0.13)
- **Relay Server**: relay_server.py (persistent connections, threading)
- **Test Status**: Comprehensive testing checklist in TESTING_CHECKLIST.md

### v0.12
- Fixed missing closing quotes in JSON commands
- Profile version updated

### v0.11
- Initial release of persistent connection relay server
- Replaced HTTP server with raw TCP socket server

---

## Support and Resources

### Files in This Package
- `relay_server.py` - Main relay server application
- `barco_WME-50_REST_API.xml` - Savant profile (v0.13)
- `DEPLOYMENT_GUIDE.md` - This file
- `TESTING_CHECKLIST.md` - Comprehensive testing guide
- `FIX_SUMMARY.md` - Technical details on major fixes
- `CLAUDE.md` - Project scope and architecture documentation
- `apiDocumentation/` - Barco REST API reference

### Getting Help
1. **Check the logs** - Relay server logs are very detailed
2. **Review FIX_SUMMARY.md** - Documents the architecture and fixes
3. **Review TESTING_CHECKLIST.md** - Test each phase systematically
4. **Check Barco VwM logs** - Access at https://[barco-ip]/log
5. **Verify network connectivity** - Use ping, curl, telnet to test

### Common Configuration Files
- Relay Server: `relay_server.py` (lines 23-39 for configuration)
- Savant Profile: `barco_WME-50_REST_API.xml` (lines 43-57 for state variables)
- Control Interface: `barco_WME-50_REST_API.xml` (lines 19-24 for TCP settings)

---

## License and Attribution

This Barco WME-50 REST API profile and relay server were developed as a modern replacement for the deprecated TEXT API profile. The relay server uses only Python standard library components for maximum compatibility.

Barco and WME-50 are registered trademarks of Barco.
