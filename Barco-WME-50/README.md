# Barco WME-50 Savant Profile

Controls a Barco video wall through the Video Wall Manager Edge (WME-50) REST API from a Savant system.

Savant profiles can't send dynamic HTTP headers. The Barco REST API needs a session cookie that expires every 30 minutes. A small Python relay server runs on the Savant Host and handles the cookie:

```
Savant profile  --TCP JSON + \r\n-->  relay_server.py (localhost:5000)  --HTTPS + cookie-->  Barco VwM /api/v1
```

The relay is stateless. Each command carries `api_key` and `barco_ip`, and the relay authenticates (`POST /api/v1/auth/key`), sends the command and drops the cookie.

## Layout

| Folder | Contents |
| --- | --- |
| `current/` | **v0.29**, the version deployed in the field (Sep 2026): profile, `relay_server.py`, relay setup guide |
| `next/` | **v2.06** (in testing): talks to the wall directly over TLS using the API "No key" mode, so no relay. See [next/README.md](next/README.md) |
| `reference/text-api-profile/` | Original profile v1.18 using the deprecated Barco TEXT (SCLI) API |
| `reference/savant/` | Savant profile XSDs and developer guide (not published, see below) |
| `reference/vendor/` | Barco REST API reference and Python example (not published, see below) |
| `history/profiles/` | Earlier profile versions, named `v<version>_<date>_...` |
| `history/notes-2025-11/`, `history/notes-2026-01/` | Development notes, fix write-ups, PCAP analysis |
| `history/tools/` | Mock Barco server, REST client and debug server used during development |

## Current version (v0.29)

| Savant action | Relay action | Barco endpoint |
| --- | --- | --- |
| `PowerOn` / `PowerOff` | `set_power` (`on` / `idle`) | `POST /wall/power` |
| `GetPowerState` | `get_power` | `GET /wall/power` |
| `SelectInputHDMI`, `SelectInputDisplayPort`, `SelectProfile3`–`7` | `set_preset` | `POST /wall/preset` |
| `SetBrightnessHigh` / `Med` / `Low` | `set_brightness` | `POST /wall/brightness` |
| `GetBrightness` | `get_brightness` | `GET /wall/brightness` |

Inputs and profiles are Barco presets. Their names are user-editable state variables, so the preset names in VwM must match. Install by setting `Barco_IP` and `API_Key` in Blueprint, then running the relay as a launch agent ([current/RELAY_SETUP.md](current/RELAY_SETUP.md)).

### Known issues in v0.29

- `Authenticate` sends `action: authenticate`, which the relay doesn't handle. It also writes to an undeclared `Session_Cookie` state. This leftover from the earlier stateful design should be removed.
- `GetPowerState` reads `$.power_state`, but Barco returns `power`, so `Power_State` never updates.
- Brightness actions update `Screen_Luminance`, which isn't declared. Preset and input actions write `"accepted"` into `SelectedInput` instead of the input name.
- The `SelectedInputUpdate` status message expects a `selected_input` field that nothing sends.
- The profile fails the bundled `racepoint_component_profile.xsd` (`http_request_type` isn't allowed), even though it loads and runs in Savant. The XSD copy is likely older than the Savant release in use.
- The relay turns off TLS verification (Barco uses a self-signed cert), binds to localhost only, and logs every response to stderr.
