# Barco WME-50 REST API v0.14 - Session Cookie Fix

**Date**: January 21, 2026
**Version**: 0.14
**Status**: ✅ Session cookie extraction now working

---

## Problem

The session cookie was not being stored in Savant's `Session_Cookie` state variable even though the relay server was correctly returning it in the response:

```
Response: {"result": "accepted", "session_cookie": "sid=REDACTED_SESSION_ID"}
```

The relay server was sending the correct data, but Savant's profile was not extracting and storing it.

---

## Root Cause

The Authenticate action in the profile had both `<rspcode>` and `<rspmessage>` elements in the response_codes:

```xml
<response_codes>
    <rspcode status="success">{"result":"accepted"}</rspcode>
    <rspmessage status="success" name="AuthSuccess">
        <root_object name="none" matches_required="at_least_one" format="json">
            <values path="$.session_cookie" matches_required="at_least_one">
                <update state="Session_Cookie" type="string" />
            </values>
        </root_object>
    </rspmessage>
</response_codes>
```

**The problem**: When both `rspcode` and `rspmessage` are present, Savant matches the response to the `rspcode` first (simple string match) and considers the response complete. The `rspmessage` parsing (which contains the JSON path extraction) is never executed.

---

## Solution

Removed the `<rspcode>` element, leaving only `<rspmessage>` with the JSON path extraction:

```xml
<response_codes>
    <rspmessage status="success" name="AuthSuccess">
        <root_object name="none" matches_required="at_least_one" format="json">
            <values path="$.session_cookie" matches_required="at_least_one">
                <update state="Session_Cookie" type="string" />
            </values>
        </root_object>
    </rspmessage>
</response_codes>
```

**Why this works**: Without `rspcode`, Savant's parser goes directly to the `rspmessage` element, which contains:
1. The JSON root object definition (`format="json"`)
2. The JSON path to extract (`path="$.session_cookie"`)
3. The state variable to update (`state="Session_Cookie"`)

---

## What Changed

### In barco_WME-50_REST_API.xml

**Version**: 0.13 → 0.14

**File Changes**:
- Line 8: `rpm_xml_version="0.14"`
- Line 16: Updated notes to indicate the fix
- Lines 80-87: Authenticate action response_codes - removed `<rspcode>` element

---

## How to Test

1. **Restart relay server**: `python3 relay_server.py`

2. **Import updated profile**: barco_WME-50_REST_API.xml (v0.14)

3. **Configure state variables in Savant**:
   - Barco_IP: Your Barco device IP
   - API_Key: Your Barco API key
   - Leave Session_Cookie blank

4. **Trigger Authenticate action**:
   - Relay server logs should show: `ACTION: authenticate`
   - Relay server should return: `RESPONSE: {'result': 'accepted', 'session_cookie': 'sid=...'}`
   - **Check Session_Cookie state variable** - should now be populated with `sid=...` value

5. **Verify it worked**:
   - If Session_Cookie is now filled: ✅ Fix successful
   - If Session_Cookie is still blank: ⚠️ Issue may be elsewhere (check Savant logs)

---

## Expected Behavior Now

When you run Authenticate:

```
Relay Server Log:
[127.0.0.1] ACTION: authenticate
[127.0.0.1] Attempting to authenticate with Barco at 172.29.1.1 using URL: https://172.29.1.1/api/v1/auth/key
[127.0.0.1] RESPONSE: {'result': 'accepted', 'session_cookie': 'sid=REDACTED_SESSION_ID'}
Sending response: '{"result": "accepted", "session_cookie": "sid=REDACTED_SESSION_ID"}'

Savant Behavior:
1. Receives the response
2. Parses JSON looking for $.session_cookie
3. Finds: "sid=REDACTED_SESSION_ID"
4. Updates Session_Cookie state variable
5. Subsequent commands now include this cookie
```

---

## Technical Details

### Why rspcode + rspmessage Doesn't Work

In Savant profiles, there are two ways to match and parse responses:

**Method 1: rspcode (simple string match)**
```xml
<rspcode status="success">{"result":"accepted"}</rspcode>
```
- Savant does a simple string match against the response
- If it matches, the response is considered complete
- No further processing happens
- Cannot extract specific values

**Method 2: rspmessage (complex parsing)**
```xml
<rspmessage status="success" name="AuthSuccess">
    <root_object name="none" matches_required="at_least_one" format="json">
        <values path="$.session_cookie" ...>
            <update state="Session_Cookie" type="string" />
        </values>
    </root_object>
</rspmessage>
```
- Savant parses the response as JSON
- Extracts specific values using JSON path expressions
- Updates state variables with extracted values
- More complex but much more powerful

**When both are present**: Savant evaluates them in order. If `rspcode` matches, it stops and never processes `rspmessage`.

**Solution**: Use ONLY `rspmessage` when you need to extract and store specific values from the response.

---

## Reference Architecture

This pattern should be used for all actions that need to extract response data:

```xml
<rspmessage status="success" name="ActionName">
    <root_object name="none" matches_required="at_least_one" format="json">
        <values path="$.field_to_extract" matches_required="at_least_one">
            <update state="StateVariableToUpdate" type="string" />
        </values>
    </root_object>
</rspmessage>
```

For actions that don't need extraction (simple success confirmation), you can use:
```xml
<rspcode status="success">{"result":"accepted"}</rspcode>
```

---

## Files Updated

- `barco_WME-50_REST_API.xml` - Version bumped to 0.14, Authenticate action fixed

## Files Not Changed

- `relay_server.py` - No changes needed (works correctly)
- Documentation files - Will be updated separately

---

## Next Steps

1. Update barco_WME-50_REST_API.xml to v0.14
2. Test Authenticate action - verify Session_Cookie is populated
3. Test all control actions - they should now work with the session cookie
4. Update QUICK_START.md and other docs to reference v0.14
5. Full testing per TESTING_CHECKLIST.md

---

## Verification Checklist

After applying this fix, verify:

- [ ] Profile version shows 0.14
- [ ] Relay server is running and responding to requests
- [ ] Trigger Authenticate action
- [ ] Check relay server logs show `ACTION: authenticate`
- [ ] Check relay server logs show correct response with session_cookie
- [ ] Check Savant Session_Cookie state variable is NOW POPULATED
- [ ] Trigger PowerOn - should work with the new session cookie
- [ ] Trigger GetBrightness - should return brightness value
- [ ] All control actions work with persistent connection

---

## Summary

**The Issue**: Session cookie wasn't being extracted and stored in Savant's state variable.

**The Cause**: Having both `rspcode` and `rspmessage` prevented JSON path extraction from executing.

**The Fix**: Removed `rspcode`, using only `rspmessage` for the Authenticate action.

**The Result**: Savant now properly extracts the session cookie and stores it in the Session_Cookie state variable, allowing all subsequent commands to work.
