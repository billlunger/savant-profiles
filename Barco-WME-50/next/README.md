# Barco WME-50 profile v2.00, direct REST (no relay)

`barco_wme-50_rest_direct.xml` talks to the Video Wall Manager Edge directly over HTTPS. Newer VwM firmware has a REST API "No key" mode, so there's no auth call, no session cookie and no relay server on the Savant Host.

```
Savant profile  --HTTPS :443 (self-signed, https-insecure)-->  Barco VwM /api/v1
```

## Setup

1. In VwM, go to **Menu → System settings → Security**, enable the API and choose **No key**.
2. In Blueprint, add the component and set its IP address to the VwM Edge.
3. Set the preset-name state variables (`HDMI`, `DisplayPort`, `Profile3`–`Profile7`) to the exact preset names in VwM. They're case-sensitive, and an unknown name returns HTTP 500.
4. If v0.29 was installed, remove `relay_server.py` and its launch agent from the host (see `../current/RELAY_SETUP.md`, section 5).

## Changes from v0.29

| | v0.29 | v2.00 |
| --- | --- | --- |
| Transport | TCP to relay on localhost:5000 | HTTPS straight to the wall on port 443 |
| Auth | Relay logs in with API key per command | None ("No key" mode) |
| State vars `Barco_IP`, `API_Key` | Required | Removed (Blueprint IP is used) |
| Power feedback | Broken (read `power_state`) | Reads `$.power`, polled every 30 s, and set on success |
| Brightness feedback | Wrote to undeclared `Screen_Luminance` | `Screen_Luminance` declared, polled every 30 s |
| Selected input | Set to `"accepted"` | Set to the input/profile name on success |
| New | | `SetBrightness` with a 0–100 `Level` argument; `Last_Error` shows Barco's message when an input preset fails |
| Removed | `Authenticate`, `SelectedInputUpdate` status message | |
| Schema | Fails the Savant XSD | Passes |

Action names are unchanged, so existing Blueprint wiring carries over. The model name is `WME-50 REST Direct`, so it can be installed beside v0.29 while you test.

## Verified (2026-10-30, wall at VwM 4.7.0.3)

- With no auth, every GET works, and POST brightness returns `202 {"result":"accepted"}`. Content-Type is optional.
- An unknown preset name returns `500` with `error.message`.
- Request bodies built from the XML are valid JSON. `GetPowerState`, `GetBrightness`, `SetBrightness` (50) and `SetBrightnessMed` were replayed against the wall, and the response paths resolve.
- Power and preset changes were **not** sent from here, so the wall's state wasn't changed.

## Still to verify in Savant

Savant's native HTTPS request format (`command_string` with `http_request_type` plus `isHttpBody` parameters) has never been captured on this device. The 2025 debug log only recorded network monitors. On first load, check these in RPM Terminal or a packet capture:

1. Commands arrive as `POST /api/v1/wall/power` with the JSON body.
2. Responses parse, and `Power_State` and `Screen_Luminance` update within 30 s.
3. The input buttons select the right presets.

This wall's presets are `Default`, `AppleTV`, `Kaleidescape`, `Kaleidescape2` and `Roku`.
