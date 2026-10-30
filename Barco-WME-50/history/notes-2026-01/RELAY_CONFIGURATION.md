# Relay Server Configuration - Barco IP Management

## Overview

The relay server now supports runtime configuration of the Barco Video Wall Manager IP address. This allows Savant to dynamically tell the relay server which Barco device to communicate with, rather than requiring the IP address to be hard-coded in the relay server code.

## Architecture

```
Savant Profile
    ↓
Barco_IP state variable (user editable)
    ↓
ConfigureRelay action
    ↓
Relay Server (localhost:5000)
    ↓
Barco WME REST API (configurable IP)
```

## State Variables

### Barco_IP
- **Type**: String
- **User Editable**: Yes
- **Default Value**: 172.29.1.1
- **Description**: The IP address of the Barco Video Wall Manager device
- **Used by**: ConfigureRelay action to tell relay server which Barco to communicate with

### API_Key
- **Type**: String
- **User Editable**: Yes
- **Description**: The API key for Barco authentication
- **Used by**: Authenticate action

### Session_Cookie
- **Type**: String
- **User Editable**: No (auto-populated)
- **Description**: The session cookie returned by Barco after authentication
- **Auto-set by**: Authenticate action

## Actions

### ConfigureRelay (New Action)

**Purpose**: Tell the relay server which Barco device IP address to use

**Request Format**:
```json
{
  "action": "configure",
  "barco_ip": "172.29.1.1"
}
```

**Response Format**:
```json
{
  "result": "accepted",
  "message": "Relay server configured for Barco at 172.29.1.1"
}
```

**When to Call**:
- Once at startup/initialization
- Whenever you change the Barco device
- If you need to switch between multiple Barco devices

**Relay Server Behavior**:
- Updates internal `_barco_config` dictionary
- Logs configuration change to stderr: `[CONFIG] Barco IP configured to: 172.29.1.1`
- Affects all subsequent API calls to `/api/v1/*` endpoints

## Relay Server Implementation Details

### Global Configuration State

```python
_barco_config = {
    'ip': '172.29.1.1',
    'api_url': 'https://172.29.1.1/api/v1'
}
```

### Configuration Method

```python
def _handle_configure(self, request_data):
    """Configure the relay server with Barco IP address"""
    global _barco_config

    barco_ip = request_data.get('barco_ip')
    _barco_config['ip'] = barco_ip
    _barco_config['api_url'] = f'https://{barco_ip}/api/v1'

    return {
        'result': 'accepted',
        'message': f'Relay server configured for Barco at {barco_ip}'
    }
```

### Using Configured IP in API Calls

All methods now reference `_barco_config["api_url"]` instead of the hard-coded `BARCO_API_URL`:

- `_handle_authenticate()`: Uses configured URL for `/auth/key`
- `_handle_set_power()`: Uses configured URL for `/wall/power`
- `_handle_get_power()`: Uses configured URL for `/wall/power`
- `_handle_set_brightness()`: Uses configured URL for `/wall/brightness`
- `_handle_get_brightness()`: Uses configured URL for `/wall/brightness`
- `_handle_set_preset()`: Uses configured URL for `/wall/preset`

## Initialization Sequence

**On Relay Server Startup**:
1. Relay server starts on localhost:5000
2. Loads default Barco IP from `BARCO_IP = '172.29.1.1'`
3. Prints startup message with default IP and note about runtime configuration

**On Savant Startup**:
1. Load profile `barco_WME-50_REST_API.xml`
2. User enters (or accepts default) Barco_IP in state variable
3. Call ConfigureRelay action to pass IP to relay server
4. Relay server updates configuration
5. Call Authenticate action to get session cookie
6. Call control actions as needed

## Multi-Device Support

This design enables supporting multiple Barco devices:

1. Create separate Savant profiles for each Barco device (or reuse same profile)
2. Each profile has its own Barco_IP state variable
3. Before sending commands, call ConfigureRelay on the appropriate relay server instance
4. Or run multiple relay server instances on different ports (5000, 5001, etc.) with separate profiles

Example with two devices:
```
Relay Server 1 (localhost:5000) → Barco A (192.168.1.100)
Relay Server 2 (localhost:5001) → Barco B (192.168.1.101)

Savant Profile A → ConfigureRelay → Relay Server 1 (port 5000)
Savant Profile B → ConfigureRelay → Relay Server 2 (port 5001)
```

## Backward Compatibility

- Default value of Barco_IP is 172.29.1.1 (same as original hard-coded value)
- Relay server works with or without ConfigureRelay being called
- If ConfigureRelay is never called, relay server uses default IP
- Existing deployments don't need to change (will use default IP)

## Error Handling

### Missing barco_ip in ConfigureRelay

```json
{
  "result": "error",
  "message": "Missing barco_ip"
}
```

### Invalid IP Format

Currently, the relay server does basic validation. Invalid IPs will fail when attempting to connect to that address, returning:

```json
{
  "result": "error",
  "http_code": 0,
  "message": "Relay error: [error from urllib]"
}
```

Future enhancement: Add IP validation before accepting configuration.

## Testing ConfigureRelay

### Manual Test with curl

```bash
# Configure relay server for a Barco at 192.168.1.50
curl -X POST http://localhost:5000/ \
  -H "Content-Type: application/json" \
  -d '{"action": "configure", "barco_ip": "192.168.1.50"}'

# Response
{"result": "accepted", "message": "Relay server configured for Barco at 192.168.1.50"}
```

### Relay Server Log Output

Watch stderr for configuration messages:

```
[CONFIG] Barco IP configured to: 192.168.1.50
```

## Files Modified

1. **barco_WME-50_REST_API.xml**
   - Added Barco_IP state variable
   - Added ConfigureRelay action

2. **relay_server.py**
   - Added global `_barco_config` dictionary
   - Added `_handle_configure()` method
   - Changed all hardcoded references from `BARCO_API_URL` to `_barco_config["api_url"]`
   - Updated startup message to note runtime configuration capability

3. **claude.md**
   - Updated setup instructions to include ConfigureRelay step
   - Added Initial Configuration Sequence
   - Documented Configuration and Session Cookie Lifecycle phases

4. **PROFILE_VALIDATION.md**
   - Added Barco_IP to state variables checklist
   - Added ConfigureRelay to actions checklist
   - Updated integration testing steps
   - Added runtime IP change testing

## Security Considerations

- IP address is stored in user-editable state variable (not secret)
- No authentication required for ConfigureRelay action (could be added if needed)
- ConfigureRelay doesn't validate IP format (future enhancement)
- Relay server doesn't log IP addresses in responses (logging only in stderr)

## Future Enhancements

1. Add IP address validation before accepting configuration
2. Add logging to file for audit trail
3. Support for multiple Barco devices in single relay instance
4. Add metrics/monitoring endpoint
5. Configuration persistence (save to file)
6. Rate limiting on ConfigureRelay calls
