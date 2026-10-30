# Parameter Concatenation Fix - Version 0.4

## Critical Discovery

The correct mechanism for parameter injection in Savant profiles is **parameter concatenation**, NOT placeholder replacement with `isHttpBody="true"`.

Parameters in a `<parameter_list>` are **concatenated in sequence** with the `<command_string>` to form the complete command body. Each parameter can be:
- A state variable reference (via `state_variable` attribute)
- A literal string value (as parameter element text)

## The Correct Pattern

```xml
<command_string type="character">{"session_cookie":"</command_string>
<parameter_list>
    <parameter parameter_data_type="character" state_variable="Session_Cookie" />
    <parameter parameter_data_type="character">","action":"set_power","power_state":"on"}</parameter>
</parameter_list>
```

This produces: `{"session_cookie":"[Session_Cookie_value]","action":"set_power","power_state":"on"}`

## Key Principles

1. **command_string opens the structure** - Sets up the JSON opening with quoted key
2. **First parameter is the state variable** - Gets injected where the string ends
3. **Remaining parameters are literals** - Close the quotes and add the rest of the JSON

## Example: Authenticate Action (v0.4)

```xml
<action name="Authenticate">
    <command_interface interface="ip">
        <command response_required="yes" http_request_type="POST">
            <command_string type="character">{"api_key":"</command_string>
            <parameter_list>
                <parameter parameter_data_type="character" state_variable="API_Key" />
                <parameter parameter_data_type="character">","action":"authenticate"}</parameter>
            </parameter_list>
            <!-- response codes... -->
        </command>
    </command_interface>
</action>
```

Result: `{"api_key":"[API_Key_value]","action":"authenticate"}`

## Example: ConfigureRelay Action (v0.4)

```xml
<action name="ConfigureRelay">
    <command_interface interface="ip">
        <command response_required="yes" http_request_type="POST">
            <command_string type="character">{"action":"configure","barco_ip":"</command_string>
            <parameter_list>
                <parameter parameter_data_type="character" state_variable="Barco_IP" />
                <parameter parameter_data_type="character">"}}</parameter>
            </parameter_list>
            <!-- response codes... -->
        </command>
    </command_interface>
</action>
```

Result: `{"action":"configure","barco_ip":"[Barco_IP_value]"}`

## Example: PowerOn Action (v0.4)

```xml
<action name="PowerOn">
    <command_interface interface="ip">
        <command response_required="yes" http_request_type="POST">
            <command_string type="character">{"session_cookie":"</command_string>
            <parameter_list>
                <parameter parameter_data_type="character" state_variable="Session_Cookie" />
                <parameter parameter_data_type="character">","action":"set_power","power_state":"on"}</parameter>
            </parameter_list>
            <!-- response codes... -->
        </command>
    </command_interface>
</action>
```

Result: `{"session_cookie":"[Session_Cookie_value]","action":"set_power","power_state":"on"}`

## Example: SelectProfile3 Action (v0.4 - Multiple Variables)

```xml
<action name="SelectProfile3">
    <command_interface interface="ip">
        <command response_required="yes" http_request_type="POST">
            <command_string type="character">{"session_cookie":"</command_string>
            <parameter_list>
                <parameter parameter_data_type="character" state_variable="Session_Cookie" />
                <parameter parameter_data_type="character">","action":"set_preset","preset_name":"</parameter>
                <parameter parameter_data_type="character" state_variable="Profile3" />
                <parameter parameter_data_type="character">"}}</parameter>
            </parameter_list>
            <!-- response codes... -->
        </command>
    </command_interface>
</action>
```

Result: `{"session_cookie":"[Session_Cookie_value]","action":"set_preset","preset_name":"[Profile3_value]"}`

## Example: SetBrightness Action (v0.4 - Integer Type)

```xml
<action name="SetBrightness">
    <command_interface interface="ip">
        <command response_required="yes" http_request_type="POST">
            <command_string type="character">{"session_cookie":"</command_string>
            <parameter_list>
                <parameter parameter_data_type="character" state_variable="Session_Cookie" />
                <parameter parameter_data_type="character">","action":"set_brightness","brightness":</parameter>
                <parameter parameter_data_type="integer" state_variable="Screen_Luminance" />
                <parameter parameter_data_type="character">}</parameter>
            </parameter_list>
            <!-- response codes... -->
        </command>
    </command_interface>
</action>
```

Result: `{"session_cookie":"[Session_Cookie_value]","action":"set_brightness","brightness":50}` (where 50 is the Screen_Luminance integer value, NOT quoted)

## Parameter Data Types

- **character** - String value, added as-is to JSON
- **integer** - Numeric value, added without quotes
- **Other types** - Use appropriate type for the variable being referenced

## Removal of isHttpBody Attribute

The `isHttpBody="true"` attribute from v0.3 was incorrect and has been removed entirely in v0.4. The mechanism for getting variables into the HTTP body is **parameter concatenation**, not a special attribute.

Parameters automatically become part of the HTTP body when used with `http_request_type="POST"` on the command element.

## All Affected Actions in v0.4

✅ Authenticate - Single session variable
✅ ConfigureRelay - Single barco_ip variable
✅ PowerOn - Single session variable
✅ PowerOff - Single session variable
✅ SelectProfile3-7 - Two variables (session + profile)
✅ SelectInputHDMI - Two variables (session + input name)
✅ SelectInputDisplayPort - Two variables (session + input name)
✅ SetBrightness - Two variables (session + brightness integer)
✅ GetBrightness - Single session variable
✅ GetPowerState - Single session variable

## Expected Behavior with v0.4

When Savant executes any action:
1. Reads the command_string: e.g., `{"session_cookie":"`
2. Reads each parameter in order and concatenates them
3. Sends the complete JSON as a single HTTP POST body
4. Relay server receives properly-formatted JSON, no parsing errors

Example execution flow for PowerOn:
- command_string: `{"session_cookie":"`
- parameter[0] (Session_Cookie): `SID=abc123def456`
- parameter[1] (literal): `","action":"set_power","power_state":"on"}`
- **Sent to relay:** `{"session_cookie":"SID=abc123def456","action":"set_power","power_state":"on"}`

## Version History

- **v0.1**: Initial profile with inline parameters (SCHEMA VIOLATION)
- **v0.2**: Attempted to use isHttpBody="true" with placeholder empty strings (INCORRECT MECHANISM)
- **v0.3**: Incremented version to track changes
- **v0.4**: Corrected to parameter concatenation pattern (CORRECT IMPLEMENTATION)

## Files Modified

- **barco_WME-50_REST_API.xml** - All 10 actions updated to use correct concatenation pattern
- **rpm_xml_version** - Changed to "0.4"
- **Notes** - Updated to reflect parameter concatenation fix
