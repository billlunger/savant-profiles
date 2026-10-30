# Barco WME-50 REST API Profile Validation Tests

## Version Information
- Profile Version: 0.1 (Testing Phase)
- Profile File: `barco_WME-50_REST_API.xml`
- rpm_xml_version: 0.1
- Schema: racepoint_component_profile.xsd

## Validation Checklist

### ✅ Structure Compliance

- [x] XML declaration present
- [x] Component root element with required attributes:
  - [x] manufacturer="Barco"
  - [x] model="WME-50"
  - [x] device_class="HD_monitor"
  - [x] minimum_component_engine_version="0.0"
  - [x] rpm_xml_version="0.1" (corrected from 1.18)
  - [x] unique_identifier="none"
- [x] Notes section describing the profile
- [x] Notes include version indicator "Version 0.1 - Testing phase"

### ✅ Control Interfaces

- [x] control_interfaces element with preferred="ip"
- [x] ip element with port="5000"
- [x] protocol="tcp"
- [x] send_postfix (0D0A - CRLF)
- [x] receive_end_condition (0D0A - CRLF)

### ✅ Media Interfaces

- [x] HDMI input with video_media type="hdmi"
- [x] DisplayPort input with video_media type="display_port"
- [x] LAN data interface with ethernet and control port

### ✅ State Variables

- [x] Barco_IP (string, user_editable) - IP address of Barco Video Wall Manager
- [x] API_Key (string, user_editable) - for storing Barco API key
- [x] Session_Cookie (string) - for storing authentication cookie
- [x] Power_State (string) - current power state
- [x] SelectedInput (string) - current input selection
- [x] Screen_Luminance (integer, 0-100) - brightness level
- [x] HDMI (string) - HDMI input name
- [x] DisplayPort (string) - DisplayPort input name
- [x] Profile3-7 (strings) - preset profile names
- [x] All state variables have state_center_binding
- [x] All state variables have owning_logical_component="HD_monitor"
- [x] Configuration-related variables (Barco_IP, API_Key) marked as user_editable

### ✅ Parameter Structure (Corrected)

- [x] Parameters are in separate `<parameter_list>` elements (NOT inline in command_string)
- [x] Parameters reference state variables via `state_variable` attribute
- [x] All parameters have `parameter_data_type` attribute set to "character" or appropriate type
- [x] Examples verified:
  - PowerOn action: session_cookie parameter separate
  - Authenticate action: api_key parameter separate
  - SelectProfile3 action: two parameters (session_cookie, Profile3)
  - SetBrightness action: two parameters (session_cookie, Screen_Luminance)

### ✅ Command Strings

- [x] Command strings use type="character" for JSON
- [x] Multiple command_string elements can appear in sequence (for parameter injection)
- [x] Each parameter_list is between command_string elements
- [x] JSON structure is properly split around parameters

#### Example: PowerOn Action
```xml
<command_string type="character">{"session_cookie": "</command_string>
<parameter_list>
    <parameter parameter_data_type="character" state_variable="Session_Cookie" />
</parameter_list>
<command_string type="character">",
  "action": "set_power",
  "power_state": "on"
}</command_string>
```

### ✅ Actions Implemented

#### Universal Component Actions
- [x] PowerOn - Sends set_power with "on" state
- [x] PowerOff - Sends set_power with "standby" state

#### Custom Component Actions
- [x] ConfigureRelay - Configures relay server with Barco IP address
  - Sends barco_ip from Barco_IP state variable
  - Confirms configuration with relay server
  - Must be called once at startup before Authenticate
- [x] Authenticate - Gets session cookie from relay server
  - Sends api_key
  - Extracts session_cookie from response via JSON path `$.session_cookie`
  - Stores in Session_Cookie state variable
- [x] SelectProfile3 - Sets preset
- [x] SelectProfile4 - Sets preset
- [x] SelectProfile5 - Sets preset
- [x] SelectProfile6 - Sets preset
- [x] SelectProfile7 - Sets preset
- [x] SelectInputHDMI - Sets preset to HDMI value
- [x] SelectInputDisplayPort - Sets preset to DisplayPort value
- [x] SetBrightness - Sets brightness level (0-100)
- [x] GetBrightness - Gets current brightness
- [x] GetPowerState - Gets current power state

### ✅ Response Parsing

- [x] Responses use format="json"
- [x] JSON path extraction syntax `$.field_name`
- [x] Examples:
  - Authenticate: `$.session_cookie`
  - Brightness: `$.brightness`
  - Power: `$.power_state`
  - Profile selection: `$.result`

### ✅ Delays and Timing

- [x] Authenticate action: 500ms delay
- [x] Control actions: 1000ms delay (1 second)
- [x] All actions have response_required="yes"

### ✅ Logical Component

- [x] logical_component_name="HD_monitor"
- [x] Implementation section with input mappings:
  - HDMI → SelectInputHDMI
  - DisplayPort → SelectInputDisplayPort
- [x] Status messages for SelectedInputUpdate

## Testing Recommendations

### Pre-Deployment Testing
1. [ ] Validate XML against racepoint_component_profile.xsd using an XML validator
2. [ ] Test Authenticate action to verify session cookie retrieval
3. [ ] Test PowerOn/PowerOff commands
4. [ ] Test brightness get/set operations
5. [ ] Test input selection (HDMI/DisplayPort)
6. [ ] Test profile/preset selection
7. [ ] Verify session cookie expiration handling (30 minutes)
8. [ ] Test error responses from relay server
9. [ ] Verify parameter substitution in all actions
10. [ ] Test on actual Barco VwM hardware

### Integration Testing
1. [ ] Import profile into Savant
2. [ ] Configure Barco_IP state variable (or use default 172.29.1.1)
3. [ ] Configure API_Key state variable
4. [ ] Call ConfigureRelay action first (to set relay server's Barco IP)
5. [ ] Call Authenticate action to obtain session cookie
6. [ ] Run through all control operations
7. [ ] Verify state updates in Savant
8. [ ] Check relay server logs for configuration and authentication messages
9. [ ] Test changing Barco_IP at runtime and recalling ConfigureRelay

## Known Limitations (v0.1)

- Profile is in testing phase - not for production use
- Requires relay server running on localhost:5000
- Session cookie must be obtained via Authenticate action before control commands
- All responses assumed to be JSON format
- Limited error handling in response parsing

## Next Steps for v1.0

- [ ] Complete testing on hardware
- [ ] Add more detailed error handling
- [ ] Implement session cookie refresh logic
- [ ] Add get_status actions for all controllable parameters
- [ ] Consider command queuing for rapid successive commands
- [ ] Update version to 1.0
- [ ] Update rpm_xml_version to 1.0

## Files Related to This Profile

- **barco_WME-50_REST_API.xml** - This profile (v0.1)
- **relay_server.py** - Relay server that runs on localhost:5000
- **examples/barco_WME-50.xml** - Original TEXT API profile (reference)
- **examples/Barco_VwM_RESTAPI_Python_Example.py** - Reference implementation
- **savantProfileDocumentation/racepoint_component_profile.xsd** - XML schema
- **apiDocumentation/** - Barco REST API docs
