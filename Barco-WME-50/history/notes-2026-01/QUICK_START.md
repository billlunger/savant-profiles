# Barco WME-50 REST API - Quick Start Guide

**Get up and running in 10 minutes**

---

## Step 1: Get Your API Key (2 minutes)

1. Open browser → https://[your-barco-ip]
2. Log in to Barco VwM
3. Go to **Settings → Security → API Keys**
4. Copy the API key (example: `YOUR_BARCO_API_KEY`)
5. Keep this safe - you'll need it

---

## Step 2: Start the Relay Server (1 minute)

```bash
# On your Savant host, navigate to this directory
cd /path/to/Barco\ WME\ SCLI

# Run this command
python3 relay_server.py
```

**Expected output:**
```
Barco Relay Server starting on localhost:5000
Default Barco IP: 172.29.1.1
Press Ctrl+C to stop the server
```

**Keep this terminal open!** The relay server must be running while you use Savant.

---

## Step 3: Import Savant Profile (2 minutes)

1. Open Savant Designer
2. **File → Import Profile**
3. Select `barco_WME-50_REST_API.xml`
4. Click Import

Done! Profile is now available in Savant.

---

## Step 4: Configure State Variables (3 minutes)

1. In Savant, right-click the Barco device
2. Edit device properties/settings
3. Find the state variables section
4. Edit these values:
   - **Barco_IP** = Your Barco IP (e.g., `192.168.1.100` or `172.29.1.1`)
   - **API_Key** = Your API key from Step 1 (e.g., `YOUR_BARCO_API_KEY`)
5. Save settings

---

## Step 5: Test It! (2 minutes)

1. In Savant, trigger the **Authenticate** action
   - Relay server should log: `ACTION: authenticate` and return `session_cookie`
   - Savant should show success
2. Check that **Session_Cookie** state variable is now filled (not blank)
3. Try **PowerOn** action
   - Your Barco display should turn on
4. Try **SetBrightness**
   - Set **Screen_Luminance** to 75, then trigger action
   - Display brightness should change

**Success!** You're ready to control the display.

---

## Available Control Actions

Copy-paste friendly action names:

| What You Want | Action Name | Parameter |
|---|---|---|
| Turn on | PowerOn | (none) |
| Turn off | PowerOff | (none) |
| Check power | GetPowerState | (none) |
| Set brightness | SetBrightness | Set Screen_Luminance first (0-100) |
| Get brightness | GetBrightness | (none) |
| Switch to Profile 3 | SelectProfile3 | (none) |
| Switch to Profile 4 | SelectProfile4 | (none) |
| Switch to Profile 5 | SelectProfile5 | (none) |
| Switch to Profile 6 | SelectProfile6 | (none) |
| Switch to Profile 7 | SelectProfile7 | (none) |
| Switch to HDMI | SelectInputHDMI | (none) |
| Switch to DisplayPort | SelectInputDisplayPort | (none) |
| Re-authenticate | Authenticate | (none) |

---

## State Variables Reference

| Variable | Purpose | Example |
|---|---|---|
| Barco_IP | Your Barco device IP | 172.29.1.1 |
| API_Key | API key from Barco VwM | YOUR_BARCO_API_KEY |
| Session_Cookie | (Auto-populated by Authenticate) | SID=abc123... |
| Power_State | Current power (on/standby) | standby |
| Screen_Luminance | Brightness 0-100 | 75 |
| SelectedInput | Current input/profile | Profile3 |
| HDMI | HDMI input name | HDMI |
| DisplayPort | DisplayPort input name | DisplayPort |
| Profile3-7 | Profile names (customize if needed) | Profile3 |

---

## Common Tasks

### Task: Turn Display On and Set to 80% Brightness
1. Trigger **PowerOn**
2. Set **Screen_Luminance** to 80
3. Trigger **SetBrightness**

### Task: Create a "Presentation Mode" Macro
1. Create a new macro in Savant
2. Add these steps:
   - Authenticate
   - PowerOn
   - Set Screen_Luminance to 100
   - Trigger SetBrightness
   - Trigger SelectProfile5
3. Save macro
4. Trigger whenever you want presentation mode

### Task: Create a "Power Down" Macro
1. Create new macro
2. Add steps:
   - Set Screen_Luminance to 0
   - Trigger SetBrightness
   - PowerOff
3. Save and use

---

## Troubleshooting (30 seconds)

**Problem: "Connection refused"**
- ❌ Relay server not running
- ✅ Run `python3 relay_server.py` in terminal

**Problem: "Missing session_cookie"**
- ❌ Authenticate action not run yet
- ✅ Trigger Authenticate action first

**Problem: Session_Cookie is blank after Authenticate**
- ❌ API_Key is wrong or Barco is unreachable
- ✅ Check API_Key in state variables
- ✅ Verify Barco IP is correct
- ✅ Check relay server logs for error message

**Problem: Barco doesn't respond to commands**
- ❌ Session expired (>30 minutes)
- ✅ Re-run Authenticate action
- ❌ Barco is offline
- ✅ Verify you can ping Barco IP: `ping [barco-ip]`

---

## Files You Need

Only 2 files are required:
1. **relay_server.py** - The relay server (must be running)
2. **barco_WME-50_REST_API.xml** - The Savant profile (must be imported)

Everything else is documentation:
- QUICK_START.md ← You're reading this
- DEPLOYMENT_GUIDE.md - Detailed setup guide
- TESTING_CHECKLIST.md - Full testing guide
- FIX_SUMMARY.md - How it works
- IMPLEMENTATION_COMPLETE.md - Status overview

---

## What's Happening Behind the Scenes

```
You in Savant
    ↓ Click "PowerOn"
Savant generates JSON
    ↓ {"session_cookie":"SID=...","action":"set_power","power_state":"on"}
Relay Server on localhost:5000
    ↓ Receives JSON, parses it
    ↓ Makes HTTPS request to Barco
Barco VwM at 172.29.1.1
    ↓ Executes power on
    ↓ Returns {"result":"accepted"}
Relay Server
    ↓ Sends back to Savant: {"result":"accepted"}
Savant
    ↓ Displays success
Your Display Turns On! 🎉
```

---

## Next Steps

1. ✅ Get API key (Step 1 above)
2. ✅ Start relay server (Step 2 above)
3. ✅ Import profile (Step 3 above)
4. ✅ Configure state variables (Step 4 above)
5. ✅ Test authentication (Step 5 above)
6. 📖 Read DEPLOYMENT_GUIDE.md for more details
7. 📋 Use TESTING_CHECKLIST.md to verify everything works
8. 🚀 Start controlling your display!

---

## Important Notes

- **Keep relay server running** - Start `python3 relay_server.py` every time you restart
- **Session expires** - After 30 minutes, run Authenticate again for new session
- **Default Barco IP** - If 172.29.1.1 doesn't match yours, update in state variables
- **Port 5000 must be free** - Check nothing else is using this port on your Savant host

---

## How to Restart If Something Goes Wrong

1. **Stop relay server** - Press Ctrl+C in the terminal running it
2. **Check logs** - Look at the last few lines printed to see any error
3. **Restart relay server** - Run `python3 relay_server.py` again
4. **In Savant, re-authenticate** - Trigger Authenticate action again
5. **Try again** - Resume controlling your display

---

## Questions?

- **Relay server won't start?** Check that Python 3 is installed: `python3 --version`
- **Can't import profile?** Verify barco_WME-50_REST_API.xml file exists
- **Connection refused?** Check relay server is actually running in terminal
- **More detail?** Read DEPLOYMENT_GUIDE.md or TESTING_CHECKLIST.md

---

**You're all set! Enjoy controlling your Barco display! 🎮**
