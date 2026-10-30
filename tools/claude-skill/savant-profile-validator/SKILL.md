---
name: savant-profile-validator
description: Validation and troubleshooting tool for Savant component profiles. Use this skill when users need to validate XML profiles against the schema, troubleshoot profile errors, check for common mistakes, verify resource assignments, test command structures, or debug status message parsing. Provides automated validation scripts and detailed error diagnosis.
---

# Savant Profile Validator

This skill provides validation tools and troubleshooting guidance for Savant component profiles.

## Quick Start

### Validate a Profile

```bash
python scripts/validate_profile.py path/to/profile.xml
```

This validates:
- XML well-formedness
- Schema compliance (against racepoint_component_profile.xsd)
- Resource string validity
- Common structural errors
- Required attribute presence

### Check Profile Structure

```bash
python scripts/check_structure.py path/to/profile.xml
```

Reports:
- Missing required elements
- Logical component configuration
- Media interface completeness
- Action definitions
- Status message coverage

## Validation Scripts

### validate_profile.py

Primary validation script. Usage:

```bash
python scripts/validate_profile.py profile.xml [--schema path/to/schema.xsd]
```

**Options:**
- `--schema`: Path to racepoint_component_profile.xsd (auto-detects if in standard location)
- `--verbose`: Detailed output with line numbers
- `--strict`: Enable additional strictness checks

**Exit codes:**
- 0: Valid profile
- 1: XML well-formedness error
- 2: Schema validation error
- 3: Resource string error
- 4: Structural error

### check_structure.py

Analyzes profile structure and reports potential issues:

```bash
python scripts/check_structure.py profile.xml
```

Reports on:
- Logical components and implementations
- Media interfaces and resource assignments
- Control interface configuration
- Action completeness
- State variable usage

### test_commands.py

Test command string generation:

```bash
python scripts/test_commands.py profile.xml --action PowerOn
```

Shows:
- Generated command bytes
- With prefix/postfix applied
- Parameter substitution (if applicable)
- Checksum calculation (if applicable)

## Common Errors and Solutions

### XML Well-Formedness Errors

**Error**: "mismatched tag"
```
Error at line 45: mismatched tag: line 42, column 4
```

**Solution**: Every opening tag must have a closing tag:
```xml
<!-- Wrong -->
<input name="HDMI 1">

<!-- Right -->
<input name="HDMI 1"></input>
<!-- or self-closing -->
<input name="HDMI 1"/>
```

**Error**: "attribute value must be quoted"
```
Error: attribute value must be quoted
```

**Solution**: Use double quotes around all attribute values:
```xml
<!-- Wrong -->
<input name=HDMI 1>

<!-- Right -->
<input name="HDMI 1">
```

### Schema Validation Errors

**Error**: "Element 'component': Missing child element"
```
Element 'component': Missing child element(s). Expected is ( control_interfaces ).
```

**Solution**: Add the required child element:
```xml
<component ...>
    <control_interfaces preferred="ip">
        <ip protocol="tcp" port="23"/>
    </control_interfaces>
</component>
```

**Error**: "Invalid attribute value"
```
Element 'component', attribute 'device_class': 'InvalidClass' is not a valid value
```

**Solution**: Use valid device_class from schema. Common values:
- AudioVideoSource
- AudioVideoReceiver
- AudioVideoSwitch
- Television
- Monitor
- EnvironmentalController

Check references/device-classes.md for complete list.

**Error**: "The value 'AV_INVALID_RESOURCE' is not an element of the set"
```
Element 'resource': [facet 'enumeration'] The value 'AV_INVALID_RESOURCE' is not an element
```

**Solution**: Use exact resource string from schema (case-sensitive):
```xml
<!-- Wrong -->
<resource>av_dvd_source</resource>
<resource>AV_DVD_SRC</resource>

<!-- Right -->
<resource>AV_DVD_SOURCE</resource>
```

### Structural Errors

**Error**: Implementation references non-existent connector
```
Implementation 'DVD' references input 'DVD Input' but no such input exists
```

**Solution**: Ensure connector names match exactly:
```xml
<media_interfaces>
    <input name="DVD Input" .../>
</media_interfaces>

<logical_component name="main">
    <implementation name="DVD">
        <input>DVD Input</input>  <!-- Must match exactly -->
    </implementation>
</logical_component>
```

**Error**: Action references non-existent resource
```
Action 'Play' references resource 'AV_DVD_SOURCE' but no connector provides this resource
```

**Solution**: Add resource to appropriate connector:
```xml
<output name="HDMI" video_media="hdmi">
    <resource>AV_DVD_SOURCE</resource>
</o>
```

**Error**: Missing action_to_select
```
Implementation 'Input1' has no action_to_select defined
```

**Solution**: Add action_to_select to implementation:
```xml
<implementation name="Input1">
    <input>Input 1</input>
    <action_to_select>SelectInput1</action_to_select>
</implementation>
```

And define the corresponding action:
```xml
<resource_component_actions>
    <action name="SelectInput1" resource="...">
        <command>...</command>
    </action>
</resource_component_actions>
```

### Command Structure Errors

**Error**: Invalid hex string
```
Invalid hex in command_string: 'GG' is not a valid hex byte
```

**Solution**: Hex strings must contain only 0-9, A-F:
```xml
<!-- Wrong -->
<command_string type="hex">02 GG 04</command_string>

<!-- Right -->
<command_string type="hex">02 0A 04</command_string>
```

**Error**: Missing required parameter
```
Action 'SetVolume' has action_argument 'volume' but command doesn't use it
```

**Solution**: Use action_argument in command:
```xml
<action name="SetVolume">
    <action_argument name="volume" type="integer" min="0" max="100"/>
    <command>
        <command_string type="character">VOL </command_string>
        <parameter_list>
            <standard_parameter>
                <action_argument>volume</action_argument>
            </standard_parameter>
        </parameter_list>
    </command>
</action>
```

### Status Message Errors

**Error**: Status message never matches
```
Warning: Status message 'PowerStatus' may never match - check constant values
```

**Solution**: Verify constant values match actual device responses:
```xml
<!-- If device sends "PWR:ON", not "PWR1" -->
<status_message name="Power">
    <constant type="character">PWR:</constant>  <!-- Add colon -->
    <data length="2" name="state">
        <data_string_match>
            <match string="ON" updates_to="ON"/>     <!-- Use "ON" not "1" -->
            <match string="OFF" updates_to="OFF"/>
        </data_string_match>
    </data>
</status_message>
```

**Error**: Update references non-existent state variable
```
Update references status 'power_state' but no such state variable exists
```

**Solution**: Declare state variable:
```xml
<state_variable_list>
    <state_variable name="power_state" initial_value="UNKNOWN"/>
</state_variable_list>
```

## Validation Checklist

Use this checklist before finalizing a profile:

### Basic Structure
- [ ] XML declaration present: `<?xml version="1.0" encoding="UTF-8"?>`
- [ ] Root element is `<component>`
- [ ] Required attributes: manufacturer, model, device_class, minimum_component_engine_version
- [ ] Profile validates against schema with no errors

### Control Interface
- [ ] control_interfaces element present
- [ ] Preferred control method specified
- [ ] Protocol-specific attributes correct (port for IP, baud_rate for RS232, etc.)
- [ ] send_prefix/postfix match device documentation
- [ ] receive_prefix/postfix defined for bidirectional devices

### Media Interfaces
- [ ] All physical connectors listed
- [ ] Connector names match device silkscreen/documentation
- [ ] Media types correct (audio_media, video_media, data_media)
- [ ] Resources assigned appropriately
- [ ] Data connector has combined_media for control port

### Logical Components
- [ ] One logical component per zone/output
- [ ] All implementations defined
- [ ] Each implementation lists correct active connectors
- [ ] action_to_select references valid action
- [ ] Implementation names are descriptive

### Actions
- [ ] PowerOn and PowerOff in universal_component_actions
- [ ] All resource actions have correct resource attribute
- [ ] action_arguments defined where needed
- [ ] Command strings match device protocol
- [ ] Delays appropriate (typically 50-100ms)
- [ ] All action_to_select actions exist

### Status Messages (if bidirectional)
- [ ] Status messages cover all important device states
- [ ] Constant patterns match actual device responses
- [ ] Data extraction correct (length, delimiters)
- [ ] Updates reference valid state variables
- [ ] State variables declared with initial values

### Testing
- [ ] All commands tested with actual device
- [ ] Status parsing verified with real feedback
- [ ] All routing combinations work (for switches)
- [ ] Edge cases handled (max/min values, rapid commands)

## Troubleshooting Workflow

### 1. Validate XML Syntax
```bash
python scripts/validate_profile.py profile.xml
```
Fix any XML errors first.

### 2. Check Schema Compliance
```bash
python scripts/validate_profile.py profile.xml --strict
```
Fix schema validation errors.

### 3. Analyze Structure
```bash
python scripts/check_structure.py profile.xml
```
Address structural warnings.

### 4. Test Commands
```bash
python scripts/test_commands.py profile.xml --action PowerOn
```
Verify command generation.

### 5. Live Testing
- Deploy profile to test system
- Test each action with device
- Monitor device responses
- Verify status updates

## Advanced Validation

### Checksum Validation

Verify checksum calculation:

```bash
python scripts/validate_checksum.py "02 05 01 00" --type standard --offset_a 0 --offset_b 0
```

### Protocol Simulation

Simulate device communication:

```bash
python scripts/simulate_protocol.py profile.xml --port 9999
```

Listens on specified port and reports what commands would be sent.

### Resource Path Analysis

Verify service requirements met:

```bash
python scripts/analyze_resources.py profile.xml
```

Reports which services the device can participate in based on resources.

## References

- **references/validation-examples.md**: Example validation scenarios with solutions
- **references/error-catalog.md**: Complete catalog of validation errors
- **references/testing-procedures.md**: Comprehensive testing procedures

For profile creation, use **savant-profiles** or **savant-ip-control** skills.
