# Device Classes

Complete list of valid device_class values for Savant component profiles.

## Audio/Video Devices

### AudioVideoSource
Source devices that output audio/video content.
- DVD/Blu-ray players
- Media servers
- Cable/satellite boxes
- Game consoles
- Streaming devices (Apple TV, Roku, etc.)

**Typical resources:** `AV_DVD_SOURCE`, `AV_SATELLITETV_SOURCE`, `AV_GAME_SOURCE`

### AudioVideoReceiver
A/V receivers with switching, processing, and amplification.
- Home theater receivers
- Pre-amplifier/processors
- Integrated amplifiers with switching

**Typical resources:** 
- `AV_AUDIOSWITCH_FUNCTION`
- `AV_VIDEOSWITCH_FUNCTION`
- `AV_SURROUNDSOUNDPROCESSOR_FUNCTION`
- `AV_VOLUMECONTROL_FUNCTION`
- `AV_AMPLIFIER_FUNCTION`

### AudioVideoSwitch
Devices primarily for switching signals.
- HDMI matrix switches
- Component video switches
- Audio distribution systems

**Typical resources:** `AV_VIDEOSWITCH_FUNCTION`, `AV_AUDIOSWITCH_FUNCTION`

### Television
Displays with built-in tuners.
- Smart TVs
- LED/OLED/Plasma TVs with tuners
- TVs with integrated speakers

**Typical resources:** `AV_MONITOR_SINK`, `AV_STEREOSPEAKERS_SINK`, `AV_TV_SOURCE`

### Monitor
Display-only devices without tuners.
- Computer monitors
- Professional displays
- Projectors

**Typical resources:** `AV_MONITOR_SINK`

### AudioSource
Audio-only source devices.
- CD players
- Turntables with preamps
- FM/AM tuners
- Streaming audio devices

**Typical resources:** `AV_CD_SOURCE`, `AV_FMRADIO_SOURCE`, `AV_DIGITALAUDIO_SOURCE`

### AudioProcessor
Audio processing devices.
- Equalizers
- Digital signal processors
- Room correction systems

**Typical resources:** `AV_PEQ_FUNCTION`, `AV_AUDIOPROCESSOR_FUNCTION`

### AudioAmplifier
Power amplifiers.
- Multi-channel amplifiers
- Mono block amplifiers
- Distribution amplifiers

**Typical resources:** `AV_AMPLIFIER_FUNCTION`

### VideoProcessor
Video processing devices.
- Video scalers
- Video format converters
- Video noise reducers

**Typical resources:** `AV_VIDEOPROCESSOR_FUNCTION`

## Environmental Control

### EnvironmentalController
General environmental control devices.
- HVAC thermostats
- Lighting control systems
- Motorized shade controllers
- Pool/spa controllers

**Typical resources:**
- `ENV_HVACCONTROLLER_SOURCE`
- `ENV_LIGHTINGCONTROLLER_SOURCE`
- `ENV_SHADECONTROLLER_SOURCE`
- `ENV_POOLANDSPACONTROLLER_SOURCE`

### SecurityController
Security and surveillance systems.
- Security panels
- Camera systems
- Access control

**Typical resources:**
- `ENV_SECURITYSYSTEMCONTROLLER_SOURCE`
- `ENV_SECURITYCAMERA_SOURCE`
- `AV_SURVEILLANCECONTROLLER_SOURCE`

## Other Devices

### DataDevice
Devices primarily for data/network functions.
- Network switches
- Media streamers
- Control processors

### GenericDevice
Catch-all for devices that don't fit other categories.
- Custom equipment
- Relay-controlled devices
- Specialty equipment

**Typical resources:** `ENV_GENERALRELAYCONTROLLEDDEVICE_SOURCE`

### Speaker
Passive or powered speakers.
- In-wall/in-ceiling speakers
- Bookshelf speakers
- Powered monitors
- Subwoofers

**Typical resources:** `AV_STEREOSPEAKERS_SINK`, `AV_SURROUNDSOUNDSPEAKERS_SINK`

## Choosing the Right Device Class

### Decision Tree

1. **Does it output video to a display?**
   - Yes, with tuner → Television
   - Yes, without tuner → Monitor

2. **Does it provide audio/video source content?**
   - DVD/Blu-ray → AudioVideoSource
   - Game console → AudioVideoSource
   - Cable/satellite → AudioVideoSource

3. **Does it switch multiple inputs to outputs?**
   - With processing/amplification → AudioVideoReceiver
   - Primarily switching only → AudioVideoSwitch

4. **Is it for environmental control?**
   - HVAC/lighting/shades → EnvironmentalController
   - Security → SecurityController

5. **Audio only?**
   - Source → AudioSource
   - Amplifier → AudioAmplifier
   - Processing → AudioProcessor
   - Output → Speaker

6. **Doesn't fit above?**
   - GenericDevice or DataDevice

## Examples by Category

### Matrix Switch Examples
```xml
<component device_class="AudioVideoSwitch" ...>
```
- 8x8 HDMI matrix
- 16x16 component video matrix
- Audio distribution system

### A/V Receiver Examples
```xml
<component device_class="AudioVideoReceiver" ...>
```
- Denon AVR-X4800H
- Marantz SR7015
- Anthem MRX 1140

### Display Examples
```xml
<component device_class="Television" ...>  <!-- If has tuner -->
<component device_class="Monitor" ...>      <!-- If display only -->
```
- LG OLED TV → Television
- Sony projector → Monitor
- Samsung display → Monitor (if no tuner)

### Source Examples
```xml
<component device_class="AudioVideoSource" ...>
```
- Apple TV
- Roku
- Cable box
- Blu-ray player
- PlayStation 5

### Environmental Examples
```xml
<component device_class="EnvironmentalController" ...>
```
- Lutron lighting
- Nest thermostat
- Somfy shades
- Jandy pool controller

## Impact on Profile Structure

Device class affects:

1. **Expected resources**: What resources make sense for the device
2. **Logical components**: How many are typically needed
3. **Implementations**: Structure and number needed
4. **Services**: Which services the device can participate in

### Example: AudioVideoSwitch
- Multiple logical components (one per output)
- Multiple implementations per logical component (one per input)
- Switch function resources on outputs
- Source resources on inputs

### Example: AudioVideoSource
- Single logical component
- Single implementation (always outputting)
- Source resources on outputs
- Limited action set (Play, Stop, etc.)

### Example: Monitor
- Single logical component
- Multiple implementations (one per input)
- Monitor sink resource on inputs
- Input selection actions

## Validation

The device_class must:
- Be a valid value from schema
- Be spelled exactly (case-sensitive)
- Match the device's primary function
- Support the resources assigned in the profile

Invalid:
```xml
<component device_class="Receiver" ...>      <!-- Use AudioVideoReceiver -->
<component device_class="audio_source" ...>  <!-- Use AudioSource -->
<component device_class="TV" ...>            <!-- Use Television -->
```

Valid:
```xml
<component device_class="AudioVideoReceiver" ...>
<component device_class="AudioSource" ...>
<component device_class="Television" ...>
```
