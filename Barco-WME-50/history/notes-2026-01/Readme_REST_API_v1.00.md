# Setup Guide: Running `relay_server.py` in the Background (macOS)

This guide explains how to set up your Python script to run automatically at login as a background service.

## 1. Move the Script to a Safe Location

macOS security (TCC) often blocks background processes from accessing the **Desktop**, **Documents**, or **Downloads** folders.

If your relay_server.py is on the desktop do the following, otherwise ensure the file is in the home directory

1. Open **Terminal**.
2. Move your script to your User Home folder:

```bash
mv ~/Desktop/relay_server.py ~/relay_server.py

```

## 2. Create the Service Configuration

Create a "Launch Agent" file. This tells macOS how and when to run your script.

1. In Terminal, run:

```bash
nano ~/Library/LaunchAgents/com.user.relayserver.plist

```

2. Paste the following block exactly as shown:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.relayserver</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/YOUR_USERNAME/relay_server.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardErrorPath</key>
    <string>/tmp/relay_error.log</string>
    <key>StandardOutPath</key>
    <string>/tmp/relay_output.log</string>
</dict>
</plist>

```

**Note:** Replace `YOUR_USERNAME` with your actual macOS shortname (type `whoami` in Terminal if unsure). 3. Press `Ctrl + O`, then `Enter` to save. Press `Ctrl + X` to exit.

## 3. Activate the Background Service

Run this command to register and start the script:

```bash
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.user.relayserver.plist

```

## 4. Verify Success

To ensure the script is running correctly, run:

```bash
launchctl list | grep relayserver

```

- **Success:** You see a number (the PID) in the first column.
- **Error:** You see a `-` in the first column. Check the logs by running: `cat /tmp/relay_error.log`.

---

## 5. Useful Management Commands

| Action                   | Command                                                                            |
| ------------------------ | ---------------------------------------------------------------------------------- |
| **Check Resource Usage** | `top -pid $(pgrep -f relay_server.py)`                                             |
| **Watch Live Logs**      | `tail -f /tmp/relay_output.log`                                                    |
| **Stop the Service**     | `launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.user.relayserver.plist` |
| **Restart Service**      | Stop it (command above), then Run the "Activate" command from Step 3.              |

---

### Why this method?

- **Auto-Restart:** If the script crashes, macOS will automatically restart it.
- **Persistence:** It starts automatically when you log in.
- **Independence:** You can close your Terminal window and the script will keep running.
