---
name: savant-ip-control
description: Specialized skill for creating Savant component profiles with IP network communication. Use this skill specifically when creating profiles for devices controlled via TCP/IP, UDP, HTTP/HTTPS, Telnet, or SSH protocols. Focuses on IP-specific configuration including connection handling, command formatting, protocol variants, authentication, and bidirectional communication patterns for matrix switches, A/V receivers, displays, and other IP-controlled equipment.
---

# Savant IP Control Profiles

This skill provides specialized guidance for creating Savant component profiles that communicate over IP networks.

## When to Use This Skill

Use this skill when creating profiles for devices that:
- Communicate via network sockets (TCP/UDP)
- Use HTTP/HTTPS REST APIs
- Support Telnet or SSH protocols
- Require authentication over network connections
- Have complex IP command structures with custom framing

## IP Control Interface Configuration

### Basic IP Element Structure

```xml
<control_interfaces preferred="ip">
    <ip protocol="tcp" port="23">
        <send_prefix type="hex">02</send_prefix>
        <send_postfix type="hex">03</send_postfix>
    </ip>
</control_interfaces>
```

### Protocol Types

**TCP (Transmission Control Protocol)**
- Reliable, connection-oriented
- Use for: Most IP-controlled A/V equipment, matrix switches, displays
- Maintains persistent connection
```xml
<ip protocol="tcp" port="23">
```

**Non-Persistent TCP**
- Opens connection, sends command, closes connection
- Use for: Devices that don't maintain persistent connections
```xml
<ip protocol="non-persistentTCP" port="9999">
```

**UDP (User Datagram Protocol)**
- Connectionless, no reliability guarantee
- Use for: Status broadcasts, lightweight commands
```xml
<ip protocol="udp" port="48630">
```

**HTTP/HTTPS**
- Web-based REST APIs
- Supports GET and POST requests
```xml
<ip protocol="http" port="80">
    <!-- or -->
<ip protocol="https" port="443">
    <!-- for HTTPS with cert validation bypass: -->
<ip protocol="https-insecure" port="443">
```

**HTTP with cURL**
- Enhanced HTTP support with full cURL features
```xml
<ip protocol="http-curl" port="80">
```

**Telnet**
- Text-based protocol with negotiation
```xml
<ip protocol="telnet" port="23">
```

**SSH**
- Encrypted communication
- Requires authentication
```xml
<ip protocol="ssh" port="22">
```

### Send Prefix and Postfix

Frame commands with consistent start/end markers:

```xml
<ip protocol="tcp" port="9999">
    <send_prefix type="hex">02</send_prefix>
    <send_postfix type="hex">03 0D 0A</send_postfix>
</ip>
```

**Common patterns:**
- STX/ETX: `<send_prefix type="hex">02</send_prefix>` and `<send_postfix type="hex">03</send_postfix>`
- Carriage return + line feed: `<send_postfix type="character">\r\n</send_postfix>`
- Line feed only: `<send_postfix type="character">\n</send_postfix>`
- Custom delimiters: `<send_postfix type="character">!</send_postfix>`

**Type attribute:**
- `hex`: Raw bytes (e.g., `02 03` = bytes 0x02, 0x03)
- `character`: ASCII text (e.g., `\r\n` = carriage return + line feed)

### Receive Prefix and Postfix

Define expected framing for incoming messages:

```xml
<ip protocol="tcp" port="9999">
    <receive_prefix type="hex">02</receive_prefix>
    <receive_postfix type="hex">03</receive_postfix>
</ip>
```

System automatically strips these frames before status message parsing.

## IP Command Structures

### Basic Commands

```xml
<action name="PowerOn">
    <command>
        <command_string type="character">POWER ON</command_string>
        <delay>100</delay>
    </command>
</action>
```

### Commands with Parameters

**Using action_argument:**
```xml
<action name="RouteInputToOutput">
    <action_argument name="input" type="integer" min="1" max="16"/>
    <action_argument name="output" type="integer" min="1" max="16"/>
    <command>
        <command_string type="character">ROUTE </command_string>
        <parameter_list>
            <standard_parameter>
                <action_argument>input</action_argument>
            </standard_parameter>
            <constant type="character"> TO </constant>
            <standard_parameter>
                <action_argument>output</action_argument>
            </standard_parameter>
        </parameter_list>
        <delay>50</delay>
    </command>
</action>
```

This sends: `ROUTE 3 TO 5` (routes input 3 to output 5)

**Formatting parameters:**
```xml
<standard_parameter>
    <action_argument>volume</action_argument>
    <format>%02d</format>  <!-- Zero-padded 2-digit decimal -->
</standard_parameter>
```

Common format specifiers:
- `%d` - Integer
- `%02d` - Zero-padded 2-digit integer
- `%03d` - Zero-padded 3-digit integer
- `%X` - Uppercase hexadecimal
- `%02X` - Zero-padded 2-digit hex

### Hex vs Character Command Strings

**Character type** - Human-readable ASCII:
```xml
<command_string type="character">PWR ON</command_string>
```
Sends bytes: 0x50 0x57 0x52 0x20 0x4F 0x4E (ASCII codes for P, W, R, space, O, N)

**Hex type** - Raw binary:
```xml
<command_string type="hex">02 05 01 00 08</command_string>
```
Sends bytes: 0x02, 0x05, 0x01, 0x00, 0x08

**Mixed approach** - Combine in parameter_list:
```xml
<command>
    <command_string type="hex">02 05</command_string>
    <parameter_list>
        <constant type="hex">01</constant>
        <standard_parameter>
            <action_argument>zone</action_argument>
        </standard_parameter>
        <checksum_parameter type="hex" constant_length="1" 
                          checksum_type="standard" 
                          checksum_offset_A="0" 
                          checksum_offset_B="0"/>
    </parameter_list>
</command>
```

## HTTP/HTTPS Specific Configuration

### GET Requests

```xml
<action name="PowerOn">
    <command>
        <command_string type="character" http_request_type="GET">/api/power/on</command_string>
    </command>
</action>
```

Full URL becomes: `http://device-ip/api/power/on`

### POST Requests

```xml
<action name="SetVolume">
    <action_argument name="volume" type="integer" min="0" max="100"/>
    <command>
        <command_string type="character" http_request_type="POST">/api/volume</command_string>
        <parameter_list>
            <constant type="character">{"level":</constant>
            <standard_parameter>
                <action_argument>volume</action_argument>
            </standard_parameter>
            <constant type="character">}</constant>
        </parameter_list>
    </command>
</action>
```

Sends POST to `/api/volume` with body: `{"level":50}`

### HTTP Headers

Add custom headers using device_control_interfaces:

```xml
<device_control_interfaces>
    <device_control_interface>
        <http_request>
            <header name="Content-Type">application/json</header>
            <header name="Authorization">Bearer TOKEN_HERE</header>
        </http_request>
    </device_control_interface>
</device_control_interfaces>
```

### Authentication

**Basic Authentication:**
```xml
<ip protocol="http" port="80" authentication="basic">
    <credential type="username"/>
    <credential type="password"/>
</ip>
```

**OAuth2:**
```xml
<ip protocol="https" port="443" authentication="OAuth2">
    <credential type="client_id"/>
    <credential type="client_secret"/>
</ip>
```

## Checksums for IP Protocols

Many IP protocols require checksums for message integrity:

```xml
<command>
    <command_string type="hex">02 05 01</command_string>
    <parameter_list>
        <standard_parameter>
            <action_argument>value</action_argument>
        </standard_parameter>
        <checksum_parameter 
            type="hex" 
            constant_length="1" 
            checksum_type="standard" 
            checksum_offset_A="0" 
            checksum_offset_B="0"/>
    </parameter_list>
</command>
```

**Common checksum types:**
- `standard` - Simple sum with offsets
- `ones_complement` - One's complement of sum
- `twos_complement` - Two's complement of sum
- `bitwise_xor` - XOR of all bytes
- `crc_16_modbus` - Modbus CRC-16

See references/checksums-ip.md for complete checksum guide.

## Status Message Parsing for IP

Parse bidirectional feedback from IP devices:

### Basic Pattern Matching

```xml
<status_messages>
    <status_message name="PowerStatus">
        <constant type="character">PWR</constant>
        <data length="1" name="state">
            <data_string_match>
                <match string="1" updates_to="ON"/>
                <match string="0" updates_to="OFF"/>
            </data_string_match>
        </data>
        <update status="power_state" always_notify="true"/>
    </status_message>
</status_messages>
```

### Variable Length Data

```xml
<status_message name="InputName">
    <constant type="character">INPUT_NAME:</constant>
    <data delimiter="\r\n" name="input_name">
        <update status="current_input_name" always_notify="true"/>
    </data>
</status_message>
```

### Hex Protocol with Binary Data

```xml
<status_message name="VolumeLevel">
    <constant type="hex">02 06</constant>
    <data length="1" type="hex" name="volume">
        <data_byte_range_match>
            <range from="00" to="64" updates_to_format="VOLUME_%d"/>
        </data_byte_range_match>
    </data>
    <update status="volume_level"/>
</status_message>
```

### JSON Response Parsing

For HTTP REST APIs returning JSON:

```xml
<status_message name="DeviceStatus">
    <root_object name="response">
        <data name="power" json_key="power">
            <data_string_match>
                <match string="on" updates_to="ON"/>
                <match string="off" updates_to="OFF"/>
            </data_string_match>
        </data>
        <data name="input" json_key="selectedInput">
            <update status="current_input"/>
        </data>
    </root_object>
</status_message>
```

## Matrix Switch Patterns

Matrix switches are complex IP devices with multiple inputs/outputs:

### Logical Component per Output

```xml
<logical_component name="output_1">
    <implementation name="Input1">
        <input>Input 1</input>
        <output>Output 1</output>
        <action_to_select>RouteInput1ToOutput1</action_to_select>
    </implementation>
    <implementation name="Input2">
        <input>Input 2</input>
        <output>Output 1</output>
        <action_to_select>RouteInput2ToOutput1</action_to_select>
    </implementation>
    <!-- One implementation per possible routing for this output -->
</logical_component>

<logical_component name="output_2">
    <!-- Similar structure for output 2 -->
</logical_component>
```

### Routing Action with Arguments

```xml
<resource_component_actions>
    <action name="RouteInput1ToOutput1" resource="AV_VIDEOSWITCH_FUNCTION">
        <command>
            <command_string type="character">ROUTE 1 1</command_string>
            <delay>50</delay>
        </command>
    </action>
</resource_component_actions>
```

Or with dynamic routing:

```xml
<custom_component_actions>
    <action name="RouteAnyInputToOutput">
        <action_argument name="input" type="integer" min="1" max="8"/>
        <action_argument name="output" type="integer" min="1" max="8"/>
        <command>
            <command_string type="character">ROUTE </command_string>
            <parameter_list>
                <standard_parameter>
                    <action_argument>input</action_argument>
                </standard_parameter>
                <constant type="character"> </constant>
                <standard_parameter>
                    <action_argument>output</action_argument>
                </standard_parameter>
            </parameter_list>
        </command>
    </action>
</custom_component_actions>
```

## Best Practices for IP Profiles

1. **Connection Management**
   - Use TCP for persistent connections
   - Use non-persistent TCP for stateless devices
   - Add appropriate delays between commands

2. **Error Handling**
   - Implement status message parsing to verify commands succeeded
   - Use state variables to track connection state

3. **Testing**
   - Test with actual network traffic capture (Wireshark)
   - Verify send_prefix/postfix match protocol documentation
   - Test all routing combinations for matrix switches

4. **Performance**
   - Minimize delays where possible (but ensure device can keep up)
   - For matrix switches, test rapid switching scenarios
   - Consider command queuing behavior

5. **Security**
   - Use HTTPS where available
   - Implement authentication properly
   - Document required credentials in notes element

## Common IP Protocol Examples

### Example 1: Simple TCP with Delimiters

```xml
<control_interfaces preferred="ip">
    <ip protocol="tcp" port="5000">
        <send_postfix type="character">\r\n</send_postfix>
    </ip>
</control_interfaces>

<action name="PowerOn">
    <command>
        <command_string type="character">POWER ON</command_string>
        <delay>100</delay>
    </command>
</action>
```

### Example 2: Binary Protocol with Checksums

```xml
<control_interfaces preferred="ip">
    <ip protocol="tcp" port="9999">
        <send_prefix type="hex">02</send_prefix>
        <send_postfix type="hex">03</send_postfix>
    </ip>
</control_interfaces>

<action name="SetInput">
    <action_argument name="input" type="integer" min="1" max="8"/>
    <command>
        <command_string type="hex">01 05</command_string>
        <parameter_list>
            <standard_parameter>
                <action_argument>input</action_argument>
                <format>%02X</format>
            </standard_parameter>
            <checksum_parameter 
                type="hex" 
                constant_length="1" 
                checksum_type="bitwise_xor" 
                checksum_offset_A="0" 
                checksum_offset_B="0"/>
        </parameter_list>
        <delay>50</delay>
    </command>
</action>
```

### Example 3: HTTP REST API

```xml
<control_interfaces preferred="ip">
    <ip protocol="http" port="80"/>
</control_interfaces>

<action name="SetInput">
    <action_argument name="input" type="integer" min="1" max="4"/>
    <command>
        <command_string type="character" http_request_type="POST">/api/input/select</command_string>
        <parameter_list>
            <constant type="character">{"input":</constant>
            <standard_parameter>
                <action_argument>input</action_argument>
            </standard_parameter>
            <constant type="character">}</constant>
        </parameter_list>
    </command>
</action>
```

## Additional Resources

For complete IP implementation details:
- **references/checksums-ip.md**: Complete checksum algorithms
- **references/http-advanced.md**: Advanced HTTP features
- **references/matrix-switch-patterns.md**: Complex matrix switch implementations
- **references/ip-troubleshooting.md**: Debugging IP communication

For overall profile structure, see the **savant-profiles** skill.
For validation, use the **savant-profile-validator** skill.
