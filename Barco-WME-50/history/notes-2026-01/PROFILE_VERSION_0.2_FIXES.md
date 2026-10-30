# Profile Version 0.2 - Critical Fixes

## Issues Fixed

### 1. HTTP Body Parameter Injection Syntax (CRITICAL)
**Problem**: Previous versions tried to split command_string across multiple XML elements, which caused HTTP 400 errors because Savant was sending fragments as separate requests.

**Solution**: Completely rewrote parameter injection to use Savant's `isHttpBody="true"` attribute:
- Single `<command_string>` per action with placeholder empty strings `""`
- Parameters marked with `isHttpBody="true"` fill those placeholders
- Single complete HTTP POST body is sent

**Before:**
```xml
<command_string type="character">{"session_cookie":"</command_string>
<parameter_list>
    <parameter parameter_data_type="character" state_variable="Session_Cookie" />
</parameter_list>
<command_string type="character">","action":"set_power"}</command_string>
```

**After:**
```xml
<command_string type="character">{"session_cookie":"","action":"set_power","power_state":"on"}</command_string>
<parameter_list>
    <parameter parameter_data_type="character" state_variable="Session_Cookie" isHttpBody="true" />
</parameter_list>
```

### 2. Authentication Sequence (CRITICAL)
**Problem**: Control commands were being sent without authentication, which fails because the relay server requires a session cookie.

**Solution**: Moved `Authenticate` action to the FIRST position in universal_component_actions. Now the proper sequence is:
1. Call ConfigureRelay (to tell relay server which Barco IP)
2. Call Authenticate (to get session cookie from relay)
3. Call any control actions (PowerOn, SetBrightness, etc.)

### 3. HTTP Request Type Specification
Added `http_request_type="POST"` attribute to all command elements to explicitly tell Savant to use POST method.

## Actions Reorganized

All actions moved to `<universal_component_actions>` (not custom_component_actions):
1. Authenticate - Gets session cookie (must be called first)
2. ConfigureRelay - Sets relay server's Barco IP
3. PowerOn - Control action
4. PowerOff - Control action
5. SelectProfile3-7 - Control actions
6. SelectInputHDMI/DisplayPort - Control actions
7. SetBrightness/GetBrightness - Control actions
8. GetPowerState - Status action

## Parameter Syntax Changes

All parameters now use `isHttpBody="true"` format:

```xml
<parameter parameter_data_type="character" state_variable="StateVarName" isHttpBody="true" />
```

This tells Savant to:
1. Get the value from StateVarName
2. Inject it into the next empty string placeholder `""` in the command_string
3. Include it in the HTTP body (not headers or URL)

## Version Increment

- **Old**: rpm_xml_version="0.1"
- **New**: rpm_xml_version="0.2"

Updated notes to indicate "Fixed HTTP body parameter injection syntax"

## Expected Behavior

With v0.2, when you call ConfigureRelay:
- Savant sends: `{"action":"configure","barco_ip":"172.29.1.1"}` as HTTP POST body
- Relay server receives properly-formed JSON
- No more HTTP 400 parsing errors

When you call PowerOn after Authenticate:
- Savant sends: `{"session_cookie":"SID=xxx","action":"set_power","power_state":"on"}` as HTTP POST body
- Relay server receives properly-formed JSON
- Successfully relays to Barco

## Testing Sequence

1. Start relay server: `python3 relay_server.py`
2. Import profile into Savant
3. Set Barco_IP state variable (or use default 172.29.1.1)
4. Set API_Key state variable
5. Call **Authenticate** first (this is critical!)
6. Wait for session_cookie to be populated
7. Then call PowerOn or other control actions

## Schema Compliance

The new parameter syntax is fully compliant with racepoint_component_profile.xsd:
- Uses `parameter_t` complexType correctly
- `isHttpBody="true"` is an optional boolean attribute
- Parameters are in `<parameter_list>` elements
- State variables referenced via `state_variable` attribute
- All required attributes present (`parameter_data_type`)

## Files Modified

- **barco_WME-50_REST_API.xml** - Complete profile rewrite with proper HTTP body parameter injection

## Known Limitations

None at this time - all syntax now matches Savant profile specifications for HTTP-based device control.
