# Barco WME-50: Video Wall Manager 4.7 and newer

Savant profile: `barco_wme-50_rest_direct.xml`. In Blueprint it appears as manufacturer **Barco**, model **WME-50 REST Direct**.

Savant controls the wall directly over the network. There's no helper software to install on the Savant Host.

- **Tested:** VwM 4.7.0.3 with SavantOS 11.0.6.
- **Controls:** power, input/preset selection and brightness.
- **Feedback:** power and brightness, refreshed every 30 seconds.

## Requirements

- Video Wall Manager (VwM Edge) running firmware **4.7 or newer**
- A Savant Host that can reach the VwM Edge on **TCP port 443**
- One VwM preset for each source the wall will show

## 1. Set up the wall

1. In Video Wall Manager, go to **Menu → System settings → Security**.
2. Turn the REST API **on**.
3. Select **No key**. This profile doesn't support a security key.
4. Create a preset for each source (for example `AppleTV`, `Kaleidescape`, `Roku`). Note the exact names, which are case-sensitive.

With "No key", any device on the network that knows the VwM's IP address can control the wall. Put the VwM Edge on the control VLAN, or otherwise restrict access to it.

**Check:** open `https://<VwM IP>/api/v1/wall/power` in a browser and accept the certificate warning. You should see something like `{"kind":"groups#wall#state","power":"on"}`.

## 2. Set up Savant

1. Add `barco_wme-50_rest_direct.xml` to Blueprint as a component profile, and add the component to the configuration.
2. Set the component's **IP address** to the VwM Edge.
3. Connect the wall's **HDMI** and **DisplayPort** inputs in Blueprint like any display.
4. Set the state variables below.

### State variables to set

| Variable | Set it to | Default |
| --- | --- | --- |
| `HDMI` | VwM preset to recall when Savant selects the HDMI input | `HDMI` |
| `DisplayPort` | VwM preset to recall when Savant selects the DisplayPort input | `DisplayPort` |
| `Profile3` – `Profile7` | Up to five more VwM presets, used by the `SelectProfile3`–`7` actions | `Profile3` … |
| `Screen_Luminance_High` / `Med` / `Low` | Brightness (0–100) for the three brightness buttons | 100 / 50 / 25 |

Preset names must match VwM **exactly**, including case, and can be up to 40 characters. A name that doesn't match does nothing on the wall.

### Feedback variables

| Variable | Shows |
| --- | --- |
| `Power_State` | `on`, `idle` or `standby` |
| `Screen_Luminance` | Current brightness, 0–100 |
| `SelectedInput` | The last input or profile selected from Savant (not read back from the wall) |

`Screen_Luminance_Text` is the same brightness value as text, kept for troubleshooting. `PresetQuoted` is used internally.

### Actions

| Action | What it does |
| --- | --- |
| `PowerOn` / `PowerOff` | Wall on / idle |
| `SelectInputHDMI` / `SelectInputDisplayPort` | Recalls the preset named in `HDMI` / `DisplayPort` |
| `SelectProfile3` … `SelectProfile7` | Recalls the preset named in `Profile3` … `Profile7` |
| `SetBrightnessHigh` / `Med` / `Low` | Sets brightness to the matching state variable |
| `SetBrightness` | Sets brightness to its `Level` argument (0–100) |
| `GetPowerState` / `GetBrightness` | Reads power or brightness now |
| `PollStatus` | Runs automatically every 30 s to refresh power and brightness |

## Troubleshooting

| Symptom | Check |
| --- | --- |
| Nothing responds | The browser check in step 1. The REST API must be on, with **No key**. The host must reach port 443. |
| Power and brightness work, but an input or profile doesn't change | The preset name in the state variable doesn't exactly match VwM (case, spaces). |
| Brightness feedback lags | Barco applies brightness a few seconds after the command, and feedback refreshes every 30 s. |
| Control software restarts on every command | You're using an HTTPS-based version of this profile. Use this one, which is built to avoid that Savant issue. |

## Upgrading from the 4.6-and-older (relay) profile

1. Update the wall to VwM 4.7 or newer, and set the API to **No key**.
2. Replace the component with this profile. The action names are the same, so existing button programming carries over. Set the IP address and preset names again.
3. Remove the relay from the Savant Host: see `../VwM-4.6-and-older/RELAY_SETUP.md`, "Stop the Service". Then delete `~/relay_server.py` and `~/Library/LaunchAgents/com.user.relayserver.plist`.
