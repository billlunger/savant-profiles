# Development notes: v0.29 relay profile (VwM 4.6 and older)

Technical detail behind the "Known limitations" in `../VwM-4.6-and-older/README.md`.

Architecture: the Savant profile sends one-line JSON over TCP to `relay_server.py` on `localhost:5000`. For each command the relay does `POST /api/v1/auth/key`, sends the call with the session cookie, then drops the cookie (it keeps no state).

Issues found in v0.29 (Oct 2026):

- `Authenticate` sends `action: authenticate`, which the relay doesn't handle. It also writes to an undeclared `Session_Cookie` state. It's left over from an earlier stateful design.
- `GetPowerState` reads `$.power_state`, but Barco returns `power`, so `Power_State` never updates.
- Brightness actions update `Screen_Luminance`, which isn't declared. Preset and input actions write `"accepted"` into `SelectedInput`.
- The `SelectedInputUpdate` status message expects a `selected_input` field that nothing sends.
- The profile fails the bundled `racepoint_component_profile.xsd`: `http_request_type` sits on `<command>` instead of `<command_string>`, and `parameter_data_type="integer"` isn't valid. Savant loads it anyway.
- The relay turns off TLS verification (Barco uses a self-signed cert), binds to localhost only, and logs every response to stderr.
