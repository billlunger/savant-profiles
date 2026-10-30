# HTTP Parsing Fix - Single-Line JSON Commands

## Problem

The relay server was receiving malformed HTTP requests with errors like:
```
[127.0.0.1] code 400, message Bad request syntax ('",')
[127.0.0.1] ""," 400 -
```

This occurred because the profile was formatting JSON commands across multiple lines with newlines between command_string segments.

## Root Cause

**Original (problematic) format:**
```xml
<command_string type="character">{
  "session_cookie": "</command_string>
<parameter_list>
    <parameter parameter_data_type="character" state_variable="Session_Cookie" />
</parameter_list>
<command_string type="character">",
  "action": "set_power",
  "power_state": "on"
}</command_string>
```

When Savant concatenated these segments, it created:
```
{
  "session_cookie": "[value]",
  "action": "set_power",
  "power_state": "on"
}
```

The embedded **newlines and spaces** in the JSON broke the HTTP parser because:
1. HTTP expects POST body to be properly formatted
2. The line breaks between segments caused parsing confusion
3. The HTTP handler interpreted the multiline JSON incorrectly

## Solution

**New (correct) format:**
```xml
<command_string type="character">{"session_cookie":"</command_string>
<parameter_list>
    <parameter parameter_data_type="character" state_variable="Session_Cookie" />
</parameter_list>
<command_string type="character">","action":"set_power","power_state":"on"}</command_string>
```

This produces:
```json
{"session_cookie":"[value]","action":"set_power","power_state":"on"}
```

**Key improvements:**
- All JSON is on **single lines** with no embedded newlines
- Compact JSON format (no spaces or formatting)
- HTTP parser receives clean, properly-formatted JSON body
- Parameter injection happens cleanly between opening and closing quotes

## Changes Made

All actions in the profile were updated to use single-line JSON:

### Universal Component Actions
- ✅ PowerOn
- ✅ PowerOff

### Custom Component Actions
- ✅ ConfigureRelay
- ✅ Authenticate
- ✅ SelectProfile3-7 (5 actions)
- ✅ SelectInputHDMI
- ✅ SelectInputDisplayPort
- ✅ SetBrightness
- ✅ GetBrightness
- ✅ GetPowerState

**Total: 13 actions corrected**

## Examples of Corrected Commands

### ConfigureRelay
Before: Multi-line JSON with formatting
After: `{"action":"configure","barco_ip":"[IP]"}`

### Authenticate
Before: Multi-line JSON with formatting
After: `{"api_key":"[KEY]","action":"authenticate"}`

### SetBrightness
Before: Multi-line JSON with formatting and "brightness": value syntax
After: `{"session_cookie":"[COOKIE]","action":"set_brightness","brightness":[VALUE]}`

Note: SetBrightness has no quotes around the brightness value since it's a number.

## Validation

The corrected profile will now:
1. Generate valid HTTP POST requests
2. Send properly-formatted JSON to relay server
3. Avoid HTTP 400 "Bad request syntax" errors
4. Properly parse responses from relay server

## Best Practices for Savant Profiles

When injecting parameters into JSON command bodies:

1. **Use single-line JSON** - No embedded newlines in the final JSON
2. **Compact formatting** - No spaces around colons or commas
3. **Split at parameter injection points** - Only break command_string where parameters go
4. **Keep JSON structure intact** - All braces, brackets, and quotes must be valid

Example template:
```xml
<command_string type="character">{"key":"</command_string>
<parameter_list>
    <parameter parameter_data_type="character" state_variable="MyVar" />
</parameter_list>
<command_string type="character">","action":"my_action"}</command_string>
```

This produces: `{"key":"[MyVar_value]","action":"my_action"}`

## Files Updated

- **barco_WME-50_REST_API.xml** - All 13 actions updated to single-line JSON format

## Testing

The relay server should now:
- Accept ConfigureRelay action without HTTP errors
- Accept Authenticate action and return session cookie
- Accept all control actions (PowerOn, SetBrightness, etc.)
- Return proper JSON responses

If HTTP 400 errors persist, check:
1. All JSON is on single lines (no embedded \n characters)
2. All quotes and braces are properly balanced
3. Parameter values don't contain special characters (they're escaped properly)
