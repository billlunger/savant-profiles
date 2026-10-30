## Scope

Converting a Savant Profile for Barco Video Wall from the deprecated TEXT API to the new REST API. There is an existing working profile in the examples folder that uses the deprecated TEXT API and needs to be converted to use the new REST API. A helper relay server will run on the Savant Host to take commands from Savant and relay them to the Barco Video Wall Manager.

**Why the relay server is needed**: Savant does not support dynamic headers, but the Barco REST API requires a session cookie that expires every 30 minutes to be passed with all control endpoints. The relay server acts as an intermediary that manages cookie lifecycle and handles authentication, allowing Savant to use the REST API without managing dynamic headers.

## Architecture

```
Savant (running on Host)
    ↓ JSON commands to localhost:5000
Relay Server (relay_server.py on localhost:5000)
    ↓ HTTPS requests with proper cookies/headers
Barco Video Wall Manager (REST API at /api/v1)
```

## Important Files

- **examples/barco_WME-50.xml** - Original working Savant Profile using deprecated TEXT API (reference)
- **barco_WME-50_REST_API.xml** - New Savant Profile (v0.1) using REST API via relay server
- **relay_server.py** - Relay server that runs on localhost:5000 to handle authentication and relay commands
- **PROFILE_VALIDATION.md** - Comprehensive validation checklist and testing recommendations for the profile
- **examples/Barco_VwM_RESTAPI_Python_Example.py** - Reference implementation showing REST API usage patterns
- **apiDocumentation/** - Contains the REST API documentation
- **savantProfileDocumentation/** - Contains Savant Profile schema and styling information

## Implementation Progress

### ✅ Completed

1. **New Savant Profile (v0.1)** - barco_WME-50_REST_API.xml
   - **Version corrected**: rpm_xml_version changed to "0.1" (was incorrectly set to 1.18)
   - **Parameter structure fixed**: All parameters now in separate `<parameter_list>` elements (not inline)
   - Control interface changed from port 23500 (TEXT API) to port 5000 (relay server)
   - Added state variables: API_Key, Session_Cookie
   - Converted all TEXT API commands to JSON format for relay server
   - Implemented Authenticate action to obtain and store session cookie
   - All control actions now send session_cookie (not api_key) per REST API requirements
   - Supports all original functionality:
     - Power On/Off (PowerOn, PowerOff actions)
     - Brightness control with get/set (GetBrightness, SetBrightness actions)
     - Input selection (SelectInputHDMI, SelectInputDisplayPort actions)
     - Preset/Profile selection (SelectProfile3-7 actions)
   - Response parsing uses JSON path extraction syntax
   - **Validation**: See PROFILE_VALIDATION.md for comprehensive schema compliance checklist

2. **Relay Server (relay_server.py)**
   - Built with Python standard library only (no external dependencies)
   - Runs on localhost:5000 listening for JSON commands from Savant
   - Handles SSL/TLS connections with Barco's self-signed certificates
   - Implements the following actions:
     - `authenticate` - Receives api_key, gets session cookie from Barco
     - `set_power` - Control power state (on/standby)
     - `get_power` - Query current power state
     - `set_brightness` - Set brightness level (0-100)
     - `get_brightness` - Query current brightness
     - `set_preset` - Select preset/profile by name
   - Proper error handling and logging
   - Timeout protection (10-second timeouts on all requests)

### 📋 Next Steps / Not Yet Done

- Test the relay server against actual Barco VwM hardware
- Verify Savant profile XML against racepoint_component_profile.xsd documentation
- Create deployment and testing documentation
- Version bump to 1.0 after successful testing

## Configuration

### Relay Server Setup

1. Edit `relay_server.py` and update the BARCO_IP variable:
   ```python
   BARCO_IP = '172.29.1.1'  # Change to your Barco WME IP
   ```

2. Run the relay server:
   ```bash
   python3 relay_server.py
   ```

3. Expected output:
   ```
   Barco Relay Server starting on localhost:5000
   Relay server will forward requests to Barco VwM at 172.29.1.1
   Press Ctrl+C to stop the server
   ```

### Savant Profile Setup

1. Import `barco_WME-50_REST_API.xml` into Savant
2. Configure state variables:
   - **Barco_IP**: Set to your Barco Video Wall Manager IP address (default: 172.29.1.1)
   - **API_Key**: Set to your Barco Video Wall Manager API key (from VwM UI Security page)
   - **Session_Cookie**: Will be auto-populated by Authenticate action
3. Run ConfigureRelay action first to initialize the relay server with Barco IP
4. Ensure the relay server is running on localhost:5000 before controlling the wall

**Initial Configuration Sequence:**
1. Set Barco_IP state variable to your Barco device IP
2. Call ConfigureRelay action to pass IP to relay server
3. Call Authenticate action to get session cookie
4. Use control actions (PowerOn, SetBrightness, etc.)

## Technical Details

### Command Format

All commands from Savant to relay server are JSON POST requests to localhost:5000:

**Authenticate request:**
```json
{
  "api_key": "your_api_key_here",
  "action": "authenticate"
}
```

**Configure relay server request:**
```json
{
  "action": "configure",
  "barco_ip": "172.29.1.1"
}
```

**Control request example (set power):**
```json
{
  "session_cookie": "SID=...",
  "action": "set_power",
  "power_state": "on"
}
```

### Configuration and Session Cookie Lifecycle

**Configuration Phase (first time setup):**
1. Savant receives Barco_IP in state variable (or user enters it)
2. Savant calls ConfigureRelay action with barco_ip parameter
3. Relay server updates internal configuration with Barco IP address
4. Relay server confirms: `{"result": "accepted", "message": "Relay configured for Barco at X.X.X.X"}`

**Authentication Phase (before first control command):**
1. Savant calls Authenticate action with api_key parameter
2. Relay server receives api_key, calls `/api/v1/auth/key` on Barco (using configured IP)
3. Barco returns Set-Cookie header with SID (30-minute expiration)
4. Relay server extracts and returns session_cookie to Savant
5. Savant stores in Session_Cookie state variable
6. Relay server confirms: `{"result": "accepted", "session_cookie": "SID=..."}`

**Control Phase (all subsequent commands):**
1. All control actions include Session_Cookie from state variable
2. Relay server relays requests to Barco using configured IP and session cookie
3. Commands expire after 30 minutes (Barco cookie expires), requiring re-authentication

## Must Do (Verification Checklist)

- [ ] Always verify any Savant profile against the documentation in savantProfileDocumentation/
- [ ] Verify endpoints against REST API Documentation before updating
- [ ] When making updates to Savant Profile, always increment the version
- [ ] Test relay server with actual Barco VwM hardware
- [ ] Validate XML against racepoint_component_profile.xsd
- [ ] Ask questions when uncertain - do not assume
