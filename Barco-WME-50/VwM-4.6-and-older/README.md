# Barco WME-50: Video Wall Manager 4.6 and older

Savant profile: `barco_wme-50_rest.xml`. In Blueprint it appears as manufacturer **Barco**, model **WME-50 REST**.

On this firmware, the Barco API needs a login and a session cookie that expires every 30 minutes, which Savant can't handle on its own. A small helper, `relay_server.py`, runs on the Savant Host. Savant sends it commands, and it logs in to the wall and passes them on.

- **Controls:** power, input/preset selection and brightness.
- **Better option:** if the wall can be updated to VwM **4.7 or newer**, use `../VwM-4.7-and-newer/` instead. It needs no relay and has working feedback.

## Requirements

- Video Wall Manager (VwM Edge) with the REST API available
- A **macOS** Savant Host with `/usr/bin/python3`, which can reach the VwM Edge on TCP port 443
- One VwM preset for each source the wall will show

## 1. Set up the wall

1. In Video Wall Manager, go to **Menu → System settings → Security**.
2. Turn the REST API **on**.
3. Select **security key**, and copy the key. This profile requires a key; it won't work with "No key".
4. Create a preset for each source, and note the exact names, which are case-sensitive.

## 2. Install the relay on the Savant Host

Follow [RELAY_SETUP.md](RELAY_SETUP.md). It copies `relay_server.py` to the host's home folder and installs it as a launch agent, so it starts at login and restarts if it stops. The relay listens only on `localhost:5000`.

The launch agent in that guide uses the path `/Users/rpm/relay_server.py`. If the host's user isn't `rpm`, change the path to match.

## 3. Set up Savant

1. Add `barco_wme-50_rest.xml` to Blueprint as a component profile, and add the component to the configuration.
2. Connect the wall's **HDMI** and **DisplayPort** inputs in Blueprint like any display.
3. Set the state variables below.

| Variable | Set it to | Default |
| --- | --- | --- |
| `Barco_IP` | IP address of the VwM Edge | `172.29.1.1` |
| `API_Key` | The security key from step 1 | (blank) |
| `HDMI` | VwM preset to recall when Savant selects HDMI | `HDMI` |
| `DisplayPort` | VwM preset to recall when Savant selects DisplayPort | `DisplayPort` |
| `Profile3` – `Profile7` | Up to five more VwM presets, used by `SelectProfile3`–`7` | `Profile3` … |
| `Screen_Luminance_High` / `Med` / `Low` | Brightness (0–100) for the three brightness buttons | 100 / 50 / 25 |

### Actions

`PowerOn`, `PowerOff`, `SelectInputHDMI`, `SelectInputDisplayPort`, `SelectProfile3`–`SelectProfile7`, `SetBrightnessHigh`/`Med`/`Low`, `GetBrightness`, `GetPowerState`. (`Authenticate` is left over from an earlier design and isn't needed.)

## Known limitations

- **Feedback doesn't work:** power and brightness feedback don't update in Savant, and `SelectedInput` shows `accepted` instead of the input name. Commands still work.
- **Helper process:** the relay is an extra process on the host. If it isn't running, every command fails.

The 4.7-and-newer profile fixes all of these.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| Nothing responds | Is the relay running? See "Verify Success" in RELAY_SETUP.md. Check `/tmp/relay_error.log`. |
| Relay log shows `Authentication failed: 401` | `API_Key` doesn't match the key in VwM. |
| Relay log shows `Missing api_key or barco_ip` | `Barco_IP` or `API_Key` is blank in Blueprint. |
| An input or profile doesn't change | The preset name doesn't exactly match VwM (case, spaces). |
