# Development notes: v2 direct profile (VwM 4.7 and newer)

How the direct-to-wall profile in `../VwM-4.7-and-newer/` was built and debugged (Oct 2026). Dealers don't need this; see that folder's README for setup.

`barco_wme-50_rest_direct.xml` controls the Video Wall Manager Edge directly. Newer VwM firmware has a REST API "No key" mode, so there's no auth call, no session cookie and no relay server on the Savant Host.

```
Savant profile  --TLS socket :443, raw HTTP/1.1-->  Barco VwM /api/v1
```

## Why raw HTTP over TLS instead of Savant's `https` protocol

v2.00–v2.02 used `protocol="https-insecure"`. GETs worked, but every POST restarted the control software. The crash report (`avc`, SavantOS 11.0.6 beta 1, 2026-10-30) shows:

```
NSInvalidArgumentException: -[NSTaggedPointerString objectForKeyedSubscript:]
  -[httpsIPCommunicator checkAccessToken:]
  -[httpsIPCommunicator curlResponse:]
```

Savant's HTTPS layer runs `checkAccessToken:` on every reply. When the status isn't 200, it gets a short string and treats it as a dictionary. This happens even with `response_required="no"`. Barco answers every set (power, preset, brightness) with `202 Accepted`, as documented in the Barco REST API guide R5916038/12. So no control command can use Savant's `https` on this OS version. **This is a Savant bug worth reporting.** v2.02 (HTTPS) is kept in `profiles/` in case a fixed SavantOS makes it usable again.

v2.03 uses `protocol="tcp-tls"` and writes the HTTP requests itself:

- Line breaks are `&#13;&#10;` (real CR LF). v0.09 (Nov 2025) wrote literal `\r\n`, which Savant sends as text.
- A `Host` header is required (Barco returns 400 without it). Requests use HTTP/1.1 keep-alive.
- `Content-Length` is fixed per request, so variable values are padded with JSON whitespace:
  - brightness: the value is right-justified to 3 characters, e.g. `{"brightness": 50}` (18 bytes)
  - preset: the action builds `PresetQuoted` = `"` + name + `"`, then sends it right-justified to 42 characters, e.g. `{"name":      "AppleTV"}` (51 bytes). The spaces sit outside the string; Barco does **not** trim spaces inside preset names. Names can be up to 40 characters.
- Replies come back on the same socket. Messages end at `}`. Status messages skip the headers up to `{` and read `power` or `brightness`. `202` replies don't match any status message and are ignored.
- Messages end at `}` **or** `,"kind"`. The second end condition cuts the brightness reply to `...{"brightness":50`. The brightness parser is a copy of the working power parser (skip to `{`, constant, value), with the number read as the last field (`terminator_type="end_of_data"`, the form used in other network profiles). In v2.03–v2.04, the `,`-terminated read never updated `Screen_Luminance`. Power replies contain no `,"kind"`, so their parsing is unchanged.
- The same value is also written to `Screen_Luminance_Text` (a string). If the text copy updates but `Screen_Luminance` doesn't, Savant matched the message but failed the integer conversion.
- Polling is one `PollStatus` action: GET power, wait 1.5 s, then GET brightness. In v2.03 both GETs had their own schedule and went out together. Both replies then arrived in one read, Savant parsed only the first (power), and brightness never updated.

## Tested in Savant (SavantOS 11.0.6 beta 1, 2026-10-30)

- v2.03: the TLS connection to the wall works, and the GETs go out byte-correct and get `200` replies. `Power_State` follows changes made on the wall itself. `Screen_Luminance` didn't.
- v2.04 (staggered polling): `Screen_Luminance` still didn't update, so the cause was the parse, not the timing. v2.05 added the `,"kind"` end condition; v2.06 rewrote the brightness parser to mirror power (see above).
- **v2.06: reported all working.** `Screen_Luminance` now follows brightness changes made on the wall, alongside `Power_State`.

## Setup

1. In VwM, go to **Menu → System settings → Security**, enable the API and choose **No key**.
2. In Blueprint, add the component and set its IP address to the VwM Edge.
3. Set the preset-name state variables (`HDMI`, `DisplayPort`, `Profile3`–`Profile7`) to the exact VwM preset names (case-sensitive). This wall's presets are `Default`, `AppleTV`, `Kaleidescape`, `Kaleidescape2` and `Roku`.
4. If v0.29 was installed, remove `relay_server.py` and its launch agent from the host (see `../VwM-4.6-and-older/RELAY_SETUP.md`, section 5).

## Changes from v0.29

| | v0.29 | v2.06 |
| --- | --- | --- |
| Transport | TCP to relay on localhost:5000 | TLS straight to the wall on port 443 |
| Auth | Relay logs in with API key per command | None ("No key" mode) |
| State vars `Barco_IP`, `API_Key` | Required | Removed (Blueprint IP is used) |
| Power feedback | Broken (read `power_state`) | Set when sent, then polled every 30 s |
| Brightness feedback | Wrote to undeclared `Screen_Luminance` | Declared, set when sent, polled every 30 s |
| Selected input | Set to `"accepted"` | Set to the input/profile name when sent (not polled) |
| New | | `SetBrightness` with a 0–100 `Level` argument |
| Schema | Fails the Savant XSD | Passes |

Action names are unchanged, so existing Blueprint wiring carries over.

## Verified (2026-10-30, wall at VwM 4.7.0.3)

- Requests were built from the XML the way Savant does it: char refs decoded, `update_state_variable` applied, parameters padded. Every `Content-Length` matches its body.
- These were sent over a raw TLS socket to the wall:
  - `GetPowerState` returned 200, parsed as `on`.
  - `GetBrightness` returned 200, parsed as `50`.
  - `SetBrightness(50)` and `SetBrightnessMed` returned 202.
  - The padded preset request, re-selecting the already-active `Kaleidescape`, returned 202.
- Power and other preset changes were not sent from here.

## Troubleshooting

v2.06 depends on these Savant behaviors, all working on SavantOS 11.0.6 beta 1:

1. `tcp-tls` accepts the wall's self-signed certificate.
2. `parameter_total_width` / `parameter_justify="right"` / `parameter_fill=" "` pad values, and `update_state_variable` (set, then append) runs before the command is sent.
3. The power and brightness status messages match. Each has two variants, in case Savant does or doesn't consume the `{` terminator.
4. Savant reconnects after Barco closes an idle keep-alive connection.

After a SavantOS update, if a command stops working, the RPM log of the sent bytes (or a packet capture) shows which of these changed. `Screen_Luminance_Text` is a diagnostic string copy of the brightness value. It's harmless to keep, but you can remove it and its two `update` lines.
