# Barco WME-50 REST API Profile - Testing Checklist

## Overview
This document provides a comprehensive testing checklist for the Barco WME-50 REST API profile (v0.13) and relay server. The tests verify proper communication between Savant, the relay server, and the Barco Video Wall Manager.

---

## Phase 1: Pre-Testing Setup

### 1.1 Environment Verification
- [ ] Barco Video Wall Manager is powered on and accessible at configured IP (e.g., 172.29.1.1)
- [ ] Barco VwM is reachable via HTTPS from the Savant host
- [ ] API key is obtained from Barco VwM UI (Security → API Keys)
- [ ] Savant Host has Python 3 installed
- [ ] Port 5000 is available on Savant host (not in use by other services)

### 1.2 File Preparation
- [ ] `relay_server.py` is in the working directory
- [ ] `barco_WME-50_REST_API.xml` profile file is available for import
- [ ] Review relay_server.py configuration:
  - [ ] `RELAY_HOST` is set to 'localhost'
  - [ ] `RELAY_PORT` is set to 5000
  - [ ] `BARCO_IP` variable matches your Barco device IP (default: 172.29.1.1)

### 1.3 Profile Configuration
- [ ] Import `barco_WME-50_REST_API.xml` (v0.13) into Savant
- [ ] Configure state variables:
  - [ ] **Barco_IP**: Set to your Barco device IP (e.g., 172.29.1.1)
  - [ ] **API_Key**: Set to your Barco API key (from VwM Security page)
  - [ ] **Session_Cookie**: Leave blank (will be auto-populated by Authenticate)
  - [ ] **Screen_Luminance**: Optional, default 50 is fine

---

## Phase 2: Server Startup and Connection Tests

### 2.1 Relay Server Startup
1. Open terminal/command prompt on Savant host
2. Navigate to the directory containing `relay_server.py`
3. Start the relay server:
   ```bash
   python3 relay_server.py
   ```
4. Verify output shows:
   ```
   Barco Relay Server starting on localhost:5000
   Default Barco IP: 172.29.1.1
   Note: Barco IP can be configured at runtime via ConfigureRelay action
   Press Ctrl+C to stop the server
   ```

### 2.2 Connection Verification
- [ ] Relay server is running without errors
- [ ] No port binding errors (if port 5000 is in use, change `RELAY_PORT` in relay_server.py)
- [ ] Savant can reach localhost:5000 (verify network connectivity if needed)

---

## Phase 3: Authentication Flow Testing

### 3.1 Authenticate Action Test
**Objective**: Verify that Savant can authenticate with the relay server and receive a session cookie.

1. In Savant, trigger the **Authenticate** action
2. Observe relay server logs (stderr):
   - [ ] Should see: `[127.0.0.1] ACTION: authenticate`
   - [ ] Should see: `[127.0.0.1] RESPONSE: {'result': 'accepted', 'session_cookie': 'SID=...'}`
   - [ ] No JSON decode errors or "Bad request syntax" messages

3. Verify Savant updates:
   - [ ] Savant receives a successful response (no error dialogs)
   - [ ] **Session_Cookie** state variable is populated with `SID=...` value
   - [ ] Check Savant's state variable display or logs to confirm the cookie value

**Expected Relay Server Log Output:**
```
[127.0.0.1] ACTION: authenticate
[127.0.0.1] RESPONSE: {'result': 'accepted', 'session_cookie': 'SID=xxx...xxx'}
```

**Troubleshooting**:
- If no cookie: Check API_Key state variable is correct
- If "Bad request syntax": Verify relay server is listening on port 5000
- If "Connection refused": Verify relay server is running with `python3 relay_server.py`
- If Savant doesn't update Session_Cookie: The XML path extraction in Authenticate action may need review

---

## Phase 4: Power Control Testing

### 4.1 PowerOn Action Test
**Objective**: Verify relay server can set Barco to power on state.

1. In Savant, trigger the **PowerOn** action
2. Observe relay server logs:
   - [ ] Should see: `[127.0.0.1] ACTION: set_power`
   - [ ] Should see: `[127.0.0.1] RESPONSE: {'result': 'accepted'}`

3. Verify Barco:
   - [ ] Barco display turns on (or stays on if already on)
   - [ ] No errors in Barco VwM UI logs

**Expected Relay Server Log Output:**
```
[127.0.0.1] ACTION: set_power
[127.0.0.1] RESPONSE: {'result': 'accepted'}
```

### 4.2 PowerOff Action Test
**Objective**: Verify relay server can set Barco to standby state.

1. In Savant, trigger the **PowerOff** action
2. Observe relay server logs:
   - [ ] Should see: `[127.0.0.1] ACTION: set_power`
   - [ ] Response shows power_state as 'standby'

3. Verify Barco:
   - [ ] Barco display goes to standby (LED changes color, screen goes dark)
   - [ ] No errors in logs

### 4.3 GetPowerState Action Test
**Objective**: Verify relay server can query current power state.

1. In Savant, trigger the **GetPowerState** action
2. Observe relay server logs:
   - [ ] Should see: `[127.0.0.1] ACTION: get_power`
   - [ ] Should see response containing current power state

3. Verify Savant:
   - [ ] Power_State state variable is updated with current state ("on" or "standby")

---

## Phase 5: Brightness Control Testing

### 5.1 SetBrightness Action Test
**Objective**: Verify brightness can be controlled via relay server.

1. Set **Screen_Luminance** state variable to 75
2. In Savant, trigger the **SetBrightness** action
3. Observe relay server logs:
   - [ ] Should see: `[127.0.0.1] ACTION: set_brightness`
   - [ ] Should see brightness value in response

4. Verify Barco:
   - [ ] Brightness changes to 75% (display visibly brighter or dimmer)
   - [ ] Barco VwM confirms new brightness level

### 5.2 GetBrightness Action Test
**Objective**: Verify brightness state can be queried.

1. In Savant, trigger the **GetBrightness** action
2. Observe relay server logs:
   - [ ] Should see: `[127.0.0.1] ACTION: get_brightness`
   - [ ] Response includes brightness value

3. Verify Savant:
   - [ ] Screen_Luminance state variable reflects current brightness

---

## Phase 6: Preset/Profile Selection Testing

### 6.1 SelectProfile3 through SelectProfile7 Tests
**Objective**: Verify preset/profile selection works for profiles 3-7.

For each profile (SelectProfile3, SelectProfile4, SelectProfile5, SelectProfile6, SelectProfile7):
1. In Savant, trigger the action (e.g., **SelectProfile3**)
2. Observe relay server logs:
   - [ ] Should see: `[127.0.0.1] ACTION: set_preset`
   - [ ] Should see preset name in command

3. Verify Barco:
   - [ ] Barco switches to the corresponding profile
   - [ ] Input/resolution/layout changes to match profile

### 6.2 Input Selection Tests
**Objective**: Verify HDMI and DisplayPort input selection works.

#### SelectInputHDMI Test
1. In Savant, trigger the **SelectInputHDMI** action
2. Observe relay server logs:
   - [ ] Should see: `[127.0.0.1] ACTION: set_preset` with preset_name "HDMI"

3. Verify Barco:
   - [ ] Display switches to HDMI input
   - [ ] SelectedInput state variable updates

#### SelectInputDisplayPort Test
1. In Savant, trigger the **SelectInputDisplayPort** action
2. Observe relay server logs:
   - [ ] Should see: `[127.0.0.1] ACTION: set_preset` with preset_name "DisplayPort"

3. Verify Barco:
   - [ ] Display switches to DisplayPort input
   - [ ] SelectedInput state variable updates

---

## Phase 7: Persistent Connection Testing

### 7.1 Multiple Sequential Commands Test
**Objective**: Verify that the relay server maintains persistent connections and handles multiple commands on the same connection.

1. Trigger the following sequence rapidly (within 1 second of each other):
   - [ ] Authenticate
   - [ ] PowerOn
   - [ ] SetBrightness (to 80)
   - [ ] SelectProfile4

2. Observe relay server logs:
   - [ ] All four actions appear in sequence
   - [ ] No "Connection closed" messages between commands
   - [ ] All responses show success

3. Expected behavior:
   - [ ] All commands execute without errors
   - [ ] No need to re-authenticate between commands
   - [ ] Session cookie remains valid throughout sequence

**Expected Relay Server Log Output:**
```
[127.0.0.1] ACTION: authenticate
[127.0.0.1] RESPONSE: {'result': 'accepted', 'session_cookie': 'SID=...'}
[127.0.0.1] ACTION: set_power
[127.0.0.1] RESPONSE: {'result': 'accepted'}
[127.0.0.1] ACTION: set_brightness
[127.0.0.1] RESPONSE: {'result': 'accepted'}
[127.0.0.1] ACTION: set_preset
[127.0.0.1] RESPONSE: {'result': 'accepted'}
```

---

## Phase 8: Error Handling and Edge Cases

### 8.1 Session Timeout Test
**Objective**: Verify behavior when session cookie expires (after 30 minutes).

1. Authenticate and get a session cookie (at time T=0)
2. Wait 30+ minutes
3. Trigger a control action (e.g., PowerOn)
4. Expected behavior:
   - [ ] First attempt may fail with "Invalid session" error
   - [ ] Re-authenticate to get a new session cookie
   - [ ] Control action succeeds with new cookie

### 8.2 Invalid Session Cookie Test
**Objective**: Verify error handling when session cookie is invalid/expired.

1. Manually set Session_Cookie state variable to an invalid value: `SID=invalid_token_xxx`
2. Trigger a control action (e.g., PowerOn)
3. Observe relay server logs:
   - [ ] Should see error response from Barco API
   - [ ] Error is clearly logged

4. Expected behavior:
   - [ ] Savant receives error response
   - [ ] No crash or undefined behavior

### 8.3 Connection Reset Test
**Objective**: Verify relay server handles unexpected connection closures gracefully.

1. Start relay server
2. Open a connection from Savant
3. While relay server is handling a command, manually kill the relay server process
4. Restart relay server
5. Trigger another action from Savant
6. Expected behavior:
   - [ ] New connection is established successfully
   - [ ] Action executes without issues

---

## Phase 9: Stress and Performance Testing

### 9.1 Concurrent Connections Test (if Savant supports it)
**Objective**: Verify relay server handles multiple concurrent connections.

1. Configure multiple Savant instances or profiles to connect to relay server
2. Trigger actions simultaneously from different connections
3. Observe relay server logs:
   - [ ] All connections are handled
   - [ ] No cross-connection interference (responses go to correct client)
   - [ ] Threading works correctly

4. Expected behavior:
   - [ ] All actions execute successfully
   - [ ] No deadlocks or race conditions

### 9.2 Rapid Command Sequence Test
**Objective**: Verify relay server handles rapid successive commands.

1. Trigger 10+ actions in rapid succession (< 100ms between each)
2. Observe relay server logs:
   - [ ] All actions logged and executed
   - [ ] No commands are dropped

3. Expected behavior:
   - [ ] All commands execute
   - [ ] Responses are accurate and in order

---

## Phase 10: Complete End-to-End Workflow

### 10.1 Full Control Workflow Test
**Objective**: Verify complete workflow from initial configuration to full control.

**Workflow:**
1. Start relay server: `python3 relay_server.py`
2. Import profile into Savant: v0.13
3. Configure state variables:
   - Barco_IP: 172.29.1.1
   - API_Key: [your actual API key]
4. Trigger Authenticate action
   - Verify Session_Cookie is populated
5. Trigger PowerOn action
   - Verify Barco powers on
6. Set Screen_Luminance to 75 and trigger SetBrightness
   - Verify brightness changes
7. Trigger SelectProfile5
   - Verify Barco switches profile
8. Trigger PowerOff action
   - Verify Barco goes to standby
9. Trigger GetPowerState action
   - Verify Power_State reflects standby status

**Expected Result**: All steps complete successfully with no errors.

---

## Phase 11: Documentation and Version Verification

### 11.1 Profile Version Check
- [ ] barco_WME-50_REST_API.xml shows `rpm_xml_version="0.13"`
- [ ] Version notes describe JSON path extraction fix

### 11.2 Relay Server Version Check
- [ ] relay_server.py header comment describes persistent connection handling
- [ ] Code includes threading for concurrent connections
- [ ] Socket timeout handling is present

---

## Test Results Summary

| Test Phase | Status | Notes |
|-----------|--------|-------|
| Phase 1: Setup | PASS/FAIL | |
| Phase 2: Server Startup | PASS/FAIL | |
| Phase 3: Authentication | PASS/FAIL | |
| Phase 4: Power Control | PASS/FAIL | |
| Phase 5: Brightness Control | PASS/FAIL | |
| Phase 6: Preset/Input Selection | PASS/FAIL | |
| Phase 7: Persistent Connections | PASS/FAIL | |
| Phase 8: Error Handling | PASS/FAIL | |
| Phase 9: Stress Testing | PASS/FAIL | |
| Phase 10: End-to-End | PASS/FAIL | |
| Phase 11: Documentation | PASS/FAIL | |

---

## Known Limitations and Future Improvements

1. **Session Cookie Refresh**: Currently, session cookies expire after 30 minutes. Future enhancement could auto-refresh before expiration.

2. **Connection Multiplexing**: The relay server uses simple sequential processing. Could optimize for higher concurrency if needed.

3. **Logging**: Currently uses stderr for logging. Future enhancement could add file logging with rotation.

4. **Configuration Persistence**: Barco IP is currently configured via state variable but relay server holds config in memory. Could be persisted to file.

5. **Status Message Support**: Profile includes placeholder for status_messages but relay server doesn't support push notifications. This is a future enhancement if Barco VwM supports webhooks.

---

## Contact and Support

For issues or questions:
1. Check relay_server.py logs for detailed error messages
2. Verify Barco VwM is accessible and API key is valid
3. Ensure Savant profile version is 0.13 or later
4. Review the FIX_SUMMARY.md for architectural details
