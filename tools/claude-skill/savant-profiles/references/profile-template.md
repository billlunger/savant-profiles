# Complete Component Profile Template

This template shows the complete structure of a Savant component profile with all major elements.

## Basic Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<component 
    manufacturer="ManufacturerName"
    model="ModelNumber"
    device_class="DeviceClassName"
    minimum_component_engine_version="8.5"
    rpm_xml_version="2.0.0"
    rpm_xml_version_date="2025-01-15">
    
    <!-- Optional notes about the profile -->
    <notes>
        <note>Profile created: 2025-01-15</note>
        <note>IP control protocol version 2.1</note>
    </notes>

    <!-- Device properties (optional) -->
    <component_properties>
        <property name="property_name">property_value</property>
    </component_properties>

    <!-- Control interface (choose one primary: ip, rs232, or ir) -->
    <control_interfaces preferred="ip">
        <ip protocol="tcp" port="23">
            <send_prefix type="character">!</send_prefix>
            <send_postfix type="character">\r\n</send_postfix>
        </ip>
    </control_interfaces>

    <!-- Physical connectors -->
    <media_interfaces>
        <input name="HDMI 1" audio_media="hdmi_multichannel" video_media="hdmi">
            <resource>AV_MONITOR_SINK</resource>
        </input>
        <output name="Audio Out" audio_media="rca_stereo">
            <resource>AV_AUDIO_SOURCE</resource>
        </output>
        <data name="Network" data_media="rj45_ethernet">
            <combined_media control_port="ip"/>
        </data>
    </media_interfaces>

    <!-- Logical component (device functional block) -->
    <logical_component name="main">
        
        <!-- Implementation (device state) -->
        <implementation name="HDMI1">
            <input>HDMI 1</input>
            <action_to_select>SelectHDMI1</action_to_select>
        </implementation>

        <!-- Universal actions (power) -->
        <universal_component_actions>
            <action name="PowerOn">
                <command>
                    <command_string type="character">PWR1</command_string>
                    <delay>100</delay>
                </command>
            </action>
            <action name="PowerOff">
                <command>
                    <command_string type="character">PWR0</command_string>
                    <delay>100</delay>
                </command>
            </action>
        </universal_component_actions>

        <!-- Resource actions (device-specific functionality) -->
        <resource_component_actions>
            <action name="SelectHDMI1" resource="AV_MONITOR_SINK">
                <command>
                    <command_string type="character">INP1</command_string>
                    <delay>100</delay>
                </command>
            </action>
        </resource_component_actions>

        <!-- Status messages (for bidirectional devices) -->
        <status_messages>
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
        </status_messages>

        <!-- State variables -->
        <state_variable_list>
            <state_variable name="power_state" initial_value="UNKNOWN"/>
        </state_variable_list>

    </logical_component>

</component>
```

## Template Variations by Device Type

### Source Device (DVD Player)

```xml
<component device_class="AudioVideoSource">
    <media_interfaces>
        <output name="HDMI" audio_media="hdmi_multichannel" video_media="hdmi">
            <resource>AV_DVD_SOURCE</resource>
        </output>
    </media_interfaces>
    
    <logical_component name="main">
        <implementation name="active">
            <output>HDMI</output>
        </implementation>
        
        <resource_component_actions>
            <action name="Play" resource="AV_DVD_SOURCE">
                <command>
                    <command_string type="character">PLAY</command_string>
                </command>
            </action>
            <action name="Stop" resource="AV_DVD_SOURCE">
                <command>
                    <command_string type="character">STOP</command_string>
                </command>
            </action>
        </resource_component_actions>
    </logical_component>
</component>
```

### Switching Device (A/V Receiver)

```xml
<component device_class="AudioVideoReceiver">
    <media_interfaces>
        <input name="DVD" audio_media="hdmi_multichannel" video_media="hdmi">
            <resource>AV_DVD_SOURCE</resource>
        </input>
        <input name="Cable" audio_media="hdmi_multichannel" video_media="hdmi">
            <resource>AV_SATELLITETV_SOURCE</resource>
        </input>
        <output name="Monitor" video_media="hdmi">
            <resource>AV_VIDEOSWITCH_FUNCTION</resource>
        </output>
        <output name="Speakers" audio_media="speaker_wire_5.1">
            <resource>AV_AUDIOSWITCH_FUNCTION</resource>
            <resource>AV_VOLUMECONTROL_FUNCTION</resource>
            <resource>AV_SURROUNDSOUNDPROCESSOR_FUNCTION</resource>
            <resource>AV_AMPLIFIER_FUNCTION</resource>
        </output>
    </media_interfaces>
    
    <logical_component name="main_zone">
        <!-- One implementation per input -->
        <implementation name="DVD">
            <input>DVD</input>
            <output>Monitor</output>
            <output>Speakers</output>
            <action_to_select>SelectDVD</action_to_select>
        </implementation>
        
        <implementation name="Cable">
            <input>Cable</input>
            <output>Monitor</output>
            <output>Speakers</output>
            <action_to_select>SelectCable</action_to_select>
        </implementation>
    </logical_component>
</component>
```

### Matrix Switch

```xml
<component device_class="AudioVideoSwitch">
    <media_interfaces>
        <!-- Multiple inputs -->
        <input name="Input 1" video_media="hdmi"/>
        <input name="Input 2" video_media="hdmi"/>
        <input name="Input 3" video_media="hdmi"/>
        <input name="Input 4" video_media="hdmi"/>
        
        <!-- Multiple outputs -->
        <output name="Output 1" video_media="hdmi">
            <resource>AV_VIDEOSWITCH_FUNCTION</resource>
        </output>
        <output name="Output 2" video_media="hdmi">
            <resource>AV_VIDEOSWITCH_FUNCTION</resource>
        </output>
        <output name="Output 3" video_media="hdmi">
            <resource>AV_VIDEOSWITCH_FUNCTION</resource>
        </output>
        <output name="Output 4" video_media="hdmi">
            <resource>AV_VIDEOSWITCH_FUNCTION</resource>
        </output>
    </media_interfaces>
    
    <!-- One logical component per output -->
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
        <!-- ... more implementations -->
    </logical_component>
    
    <logical_component name="output_2">
        <!-- Similar structure for output 2 -->
    </logical_component>
</component>
```

## Required Attributes Reference

### Component Element
- `manufacturer` (required): Manufacturer name
- `model` (required): Model number/name
- `device_class` (required): Device classification
- `minimum_component_engine_version` (required): Minimum RacePoint version (typically "8.5")
- `rpm_xml_version` (optional but recommended): Profile version
- `rpm_xml_version_date` (optional but recommended): Profile date

### Control Interfaces
- `preferred` (required): Primary control method ("ip", "rs232", "ir")

### IP Element
- `protocol` (required): "tcp", "udp", "http", "https", "telnet"
- `port` (required): Port number

### RS232 Element
- `baud_rate` (required): 9600, 19200, 38400, 57600, 115200
- `data_length` (required): 7 or 8
- `parity_bit` (required): "none", "even", "odd"
- `stop_bit` (required): 1 or 2
- `flow_control` (required): "none", "hardware"

### Media Interface Elements
- `name` (required): Connector name as labeled on device
- `audio_media`, `video_media`, `data_media` (at least one required): Connector type

### Logical Component
- `name` (required): Logical component identifier

### Implementation
- `name` (required): Implementation identifier

### Action
- `name` (required): Action identifier
- `resource` (required for resource_component_actions): Associated resource
