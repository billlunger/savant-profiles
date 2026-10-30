# Savant Component Profile Skills

This package contains three specialized skills for creating and validating Savant component profiles (RacePoint OS device drivers).

## Skills Included

### 1. savant-profiles
**Main comprehensive skill** for creating Savant component profiles.

**Use for:**
- Understanding component profile structure
- Learning services and resources concepts
- General profile creation guidance
- Any device type (A/V, environmental, etc.)

**When to trigger:** Any query about creating or understanding Savant component profiles.

### 2. savant-ip-control
**Specialized IP communication skill** for network-controlled devices.

**Use for:**
- TCP/IP, UDP, HTTP/HTTPS protocols
- Matrix switches and A/V receivers with IP control
- Network displays and processors
- Custom IP command structures
- Checksums and authentication

**When to trigger:** Specifically when working with IP/network-controlled devices or IP protocol questions.

### 3. savant-profile-validator
**Validation and troubleshooting skill** with Python scripts.

**Use for:**
- XML schema validation
- Structure checking
- Error diagnosis
- Testing command generation
- Troubleshooting profile issues

**When to trigger:** When validating profiles, debugging errors, or need to test profile components.

## Quick Start

### Creating a New IP-Controlled Profile

1. **Gather information:** Device manual with IP commands, port number, connector list
2. **Use savant-ip-control skill:** "Create a component profile for [Device] with IP control"
3. **Build the profile:** Follow the skill's guidance for structure and commands
4. **Validate:** Use savant-profile-validator to check the XML

### Example Workflow

```
You: "I need to create a profile for an 8x8 HDMI matrix switch that uses TCP 
     on port 5000. Commands are like 'ROUTE 1 3' to route input 1 to output 3."

Claude: [Uses savant-ip-control skill to guide you through creating the profile]

You: "Validate this profile"

Claude: [Uses savant-profile-validator skill to check the XML and report issues]
```

## Files Included

### savant-profiles/
- `SKILL.md` - Main comprehensive guide
- `references/profile-template.md` - Complete XML templates
- `assets/` - XSD schemas and developer guide

### savant-ip-control/
- `SKILL.md` - IP-specific guide with protocols, checksums, examples
- `references/checksums-ip.md` - Complete checksum reference

### savant-profile-validator/
- `SKILL.md` - Validation guide and error catalog
- `scripts/validate_profile.py` - XML validation script
- `assets/` - XSD schemas for validation

## Key Concepts

### Component Profiles
XML documents that enable Savant RacePoint OS to control third-party devices. Contains:
- Device description (connectors, capabilities)
- Control commands (IP, RS232, IR)
- Status parsing rules
- Service/resource mappings

### Services and Resources
- **Services**: End-user experiences (Watch DVD, Listen to Radio)
- **Resources**: Device capabilities assigned to connectors
- System uses resources to determine which services are available

### IP Control
Most modern A/V equipment uses IP network control:
- TCP for persistent connections
- HTTP/HTTPS for REST APIs
- Custom binary or text protocols
- Often requires checksums for message integrity

## Common Device Types

### Matrix Switches
- Multiple inputs and outputs
- One logical component per output
- Routing actions with arguments
- Resources: `AV_VIDEOSWITCH_FUNCTION` or `AV_AUDIOSWITCH_FUNCTION`

### A/V Receivers
- Multiple inputs, multiple outputs (zones)
- One logical component per zone
- One implementation per input selection
- Resources: switching, processing, amplification

### Displays
- Video inputs with monitor sink resource
- Simple implementations
- Power and input selection actions
- Resources: `AV_MONITOR_SINK`

## Validation Workflow

1. **XML Well-formedness**: Check basic XML syntax
2. **Schema Validation**: Verify against XSD schema
3. **Structure Check**: Ensure logical components and implementations are correct
4. **Resource Validation**: Verify resource strings are valid
5. **Testing**: Deploy and test with actual device

## Troubleshooting

### Common Issues

**"Element 'component': Missing child element"**
- Add the required child element (usually control_interfaces or media_interfaces)

**"Invalid resource string"**
- Resource names are case-sensitive, use exact strings from schema
- Common: `AV_DVD_SOURCE`, `AV_MONITOR_SINK`, `AV_VIDEOSWITCH_FUNCTION`

**"Implementation references non-existent connector"**
- Connector names in implementations must exactly match media_interfaces

**Device not responding to commands**
- Verify IP protocol, port, and framing (prefix/postfix)
- Check command string format (hex vs character)
- Test with network packet capture tool

## Examples in Assets

The `assets/` directories contain:
- XSD schema files for reference
- Complete developer guide
- Use these to understand valid values and structures

## Best Practices

1. **Start simple**: Basic power control first, then add features
2. **Test incrementally**: Validate after each section
3. **Use Oxygen XML Editor**: Schema-aware editing prevents errors
4. **Document everything**: Use notes element for version info and quirks
5. **Capture traffic**: Use Wireshark to verify actual device communication
6. **Reference existing profiles**: Find similar devices to use as templates

## Support

For questions about:
- **Profile structure**: Use savant-profiles skill
- **IP protocols**: Use savant-ip-control skill  
- **Validation errors**: Use savant-profile-validator skill
- **All three**: Claude can use multiple skills as needed

## Version

Skills created: November 2025
Based on: RacePoint Component Profile Schema and Developer Guide v1.0.0
