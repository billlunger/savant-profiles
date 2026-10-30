# Barco WME-50 video wall: Savant profiles

Savant component profiles for Barco video walls controlled through the **Video Wall Manager Edge (WME-50)**.

## Which profile do I use?

Pick by the **Video Wall Manager firmware** version on the VwM Edge:

| VwM firmware | Folder | How it connects | Feedback |
| --- | --- | --- | --- |
| **4.7 and newer** (recommended) | [VwM-4.7-and-newer](VwM-4.7-and-newer/) | Savant talks to the wall directly | Power and brightness |
| **4.6 and older** | [VwM-4.6-and-older](VwM-4.6-and-older/) | Through a small relay program on the Savant Host | Limited |

Firmware 4.7 added a REST API mode with no login ("No key"), which lets Savant control the wall directly. On older firmware, every command needs a login that Savant can't do by itself, so a relay on the host handles it.

If the wall is on 4.6 or older, updating it to 4.7 or newer and using the direct profile is the simpler, more reliable setup.

**Finding the firmware version:** it's shown in Video Wall Manager. If the REST API is already set to "No key", you can also open `https://<VwM IP>/api/v1/version` in a browser.

Each folder's README covers the wall settings, Savant setup, state variables and troubleshooting.

## Other folders (for developers)

| Folder | Contents |
| --- | --- |
| `history/` | Earlier profile versions, development notes, and test tools |
| `reference/` | The original TEXT-API profile; Savant and Barco reference docs are kept locally and not published |
