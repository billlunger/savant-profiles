---
name: savant-profiles
description: Comprehensive guide for creating and editing Savant component profiles (XML-based device drivers for RacePoint OS). Use this skill when users need to create component profiles for third-party equipment integration, understand profile structure, work with services and resources, define media interfaces, create logical components, or develop any type of Savant device profile including A/V receivers, matrix switches, displays, source devices, or environmental controls.
---

# Savant Component Profiles

This skill provides comprehensive guidance for creating Savant component profiles - XML documents that enable RacePoint OS to integrate and control third-party equipment.

## What Are Component Profiles?

Component profiles are device-specific "drivers" that contain:
- **Description information**: Device capabilities, inputs/outputs, connectors
- **Control information**: Commands to communicate with devices (IR, RS232, IP)
- **Service/Resource mappings**: Defines what services the device supports
- **Status parsing**: Rules for interpreting device feedback

Profiles are plain-text XML documents that act as modular databases, allowing the system to control any device by issuing standardized service requests (like "Play" or "VolumeUp") without knowing device-specific commands.

## Core Workflow

### 1. Gather Device Information
Before starting, collect:
- Manufacturer name and model number
- Complete list of physical connectors (HDMI, RCA, RS232, network port, etc.)
- Control protocol documentation (IP commands, RS232 codes, or IR codes)
- Device capabilities (what it can do: play DVD, switch inputs, control volume, etc.)
- Status/feedback message formats (if bidirectional)

### 2. Choose the Right Profile Type
Determine device class based on primary function:
- `AudioVideoSource` - DVD players, media servers, cable boxes
- `AudioVideoReceiver` - A/V receivers, processors
- `AudioVideoSwitch` - Matrix switches, HDMI switchers
- `Television` - Displays with tuners
- `Monitor` - Display-only devices
- `EnvironmentalController` - HVAC, lighting, shades
- See references/device-classes.md for complete list

### 3. Create Basic Profile Structure
Start with the root `component` element containing required attributes and child elements. See references/profile-template.md for complete template.

### 4. Define Media Interfaces
List all physical connectors with their resource contributions:
- Inputs receive signals/data
- Outputs provide signals/data to other devices
- Data connectors enable bidirectional communication
- Assign appropriate resources to each connector

For complex devices, also define:
- **Logical IOs**: Groupings of connectors (e.g., HDMI video + analog audio)
- **Modular Chassis**: Interchangeable card slots

### 5. Create Logical Components
Define independent functional blocks:
- One logical component per audio/video zone
- Each logical component contains implementations (device states)
- Implementations specify active inputs/outputs for each state

### 6. Define Control Interfaces
Configure communication method:
- **IP**: Specify protocol, port, send_prefix/postfix
- **RS232**: Specify baud rate, data bits, parity, flow control
- **IR**: Use racepointmedia format for IR codes

### 7. Add Actions
Define control commands in three categories:
- **Universal actions**: PowerOn, PowerOff (common to all devices)
- **Resource actions**: Service-specific (Play, Stop, VolumeUp, ChannelUp)
- **Custom actions**: Device-specific commands

### 8. Configure Status Messages
For bidirectional devices, define parsing rules:
- Match incoming data patterns using `constant` and `data` elements
- Extract variable data and update status variables
- Handle checksums and validation

### 9. Validate and Test
- Validate XML against schema (see savant-profile-validator skill)
- Test all control commands
- Verify status message parsing
- Check resource assignments enable proper services

## Key Concepts

### Services and Resources

**Services** are end-user experiences (e.g., "Watch DVD", "Listen to Radio"). Each service requires specific **resources** in the audio/video path.

**Resource types:**
- `_SOURCE`: Beginning of resource chain (e.g., `AV_DVD_SOURCE`)
- `_FUNCTION`: Middle of chain (e.g., `AV_VOLUMECONTROL_FUNCTION`)
- `_SINK`: End of chain (e.g., `AV_MONITOR_SINK`)

**Example**: DVD Service requires:
- Audio path: DVD source → audio switch → surround processor → volume control → amplifier → speakers
- Video path: DVD source → video switch → video processor → monitor

Assign resources to device connectors to declare capabilities. RacePoint Blueprint uses these to determine available services in a configuration.

### Command Structure

**Basic command:**
```xml
<command>
    <command_string type="hex">02 05 01 00 08</command_string>
    <delay>100</delay>
</command>
```

**Command with parameters:**
```xml
<command>
    <command_string type="hex">02 05 01 00</command_string>
    <parameter_list>
        <standard_parameter>
            <action_argument>volume</action_argument>
        </standard_parameter>
    </parameter_list>
    <delay>100</delay>
</command>
```

**Type attribute:**
- `hex`: Raw bytes (e.g., `02 05` = bytes 0x02, 0x05)
- `character`: ASCII string (e.g., `PWR1` = chars P, W, R, 1)

### Status Message Parsing

Parse incoming device feedback using pattern matching:
```xml
<status_message name="Power">
    <constant type="character">PWR</constant>
    <data length="1" name="power_state">
        <data_string_match>
            <match string="1" updates_to="ON"/>
            <match string="0" updates_to="OFF"/>
        </data_string_match>
    </data>
    <update status="power_state" always_notify="true"/>
</status_message>
```

## When to Read Additional References

This SKILL.md provides core workflow and concepts. Read these references when needed:

- **references/profile-template.md**: Complete XML structure template for starting new profiles
- **references/device-classes.md**: All device class types and when to use each
- **references/resources-complete.md**: Complete resource catalog with usage guidelines
- **references/connector-types.md**: All audio/video/data media types for connectors
- **references/ip-protocols.md**: IP-specific configuration (protocols, authentication, HTTP)
- **references/actions-advanced.md**: Advanced action constructs (arguments, conditionals, state variables)
- **references/status-advanced.md**: Advanced status parsing (bitmasks, checksums, dynamic variables)
- **references/checksum-types.md**: All supported checksum algorithms

For IP-specific profiles, consider using the companion **savant-ip-control** skill which focuses on IP communication.

For validation and troubleshooting, use the **savant-profile-validator** skill.

## Critical XML Rules

1. **Well-formed XML**: All tags must close, attributes must be quoted
2. **Schema compliance**: Profile must validate against racepoint_component_profile.xsd
3. **Resource strings**: Must use exact capitalized strings from schema (e.g., `AV_DVD_SOURCE`)
4. **Encoding**: Always UTF-8
5. **First line**: XML declaration `<?xml version="1.0" encoding="UTF-8"?>`
6. **Root element**: `<component>` with all required attributes

## Quick Start Example

For a simple IP-controlled display:

1. Create component element with manufacturer, model, device_class="Monitor"
2. Add media_interfaces with video inputs (assign `AV_MONITOR_SINK` resource)
3. Add control_interfaces/ip with port and protocol
4. Create one logical_component with one implementation listing active inputs
5. Add universal_component_actions (PowerOn, PowerOff)
6. Add resource_component_actions for the monitor (SelectInput, etc.)
7. If bidirectional, add status_messages to parse power state and input

See references/profile-template.md for complete structure.

## Best Practices

1. **Start simple**: Get basic power and control working before adding complex features
2. **One change at a time**: Test after each modification
3. **Use Oxygen XML Editor**: Syntax awareness and schema validation prevent errors
4. **Copy similar profiles**: Find existing profile for similar device as starting point
5. **Document thoroughly**: Use notes element for version history and quirks
6. **Test all implementations**: Verify each input/source combination works
7. **Validate early, validate often**: Use schema validation to catch errors immediately
