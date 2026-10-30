# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Savant Component Profile Development Project** for the Barco WME-50 video wall display and associated Claude AI skills for profile creation. The project enables developers to create XML-based device drivers (component profiles) that allow the Savant RacePoint OS home automation system to control IP-connected A/V equipment.

### Key Components
- **Device Profiles**: Complete XML profiles for WME-50 (TEXT API and REST API variants)
- **Claude Skills**: Three complementary AI skills (MCP packages) in `claude-skill/` for:
  - `savant-profiles` - General profile creation guidance
  - `savant-ip-control` - IP protocol and network communication expertise
  - `savant-profile-validator` - XML validation and error diagnosis
- **Validation Tools**: Python-based XML validator with schema compliance checking

## Essential Commands

### Validation (Primary Development Task)

```bash
# Validate a profile against schema
python3 claude-skill/savant-profile-validator/scripts/validate_profile.py <profile.xml>

# Validate with specific schema
python3 claude-skill/savant-profile-validator/scripts/validate_profile.py <profile.xml> \
  --schema claude-skill/savant-profile-validator/assets/racepoint_component_profile.xsd

# Strict validation with verbose output
python3 claude-skill/savant-profile-validator/scripts/validate_profile.py <profile.xml> \
  --schema <schema.xsd> --strict --verbose
```

**Exit codes**: 0 (valid), 1 (syntax error), 2 (schema error), 3 (resource error), 4 (structural error)

### Testing/Checking Single Profile

```bash
# Quick validation of WME-50 TEXT variant
python3 claude-skill/savant-profile-validator/scripts/validate_profile.py barco_WME-50.xml

# Check REST API variant
python3 claude-skill/savant-profile-validator/scripts/validate_profile.py barco_WME-50_REST.xml
```

### Skill Package Management

```bash
# Extract skill package (if needed)
tar -xzf claude-skill/savant-profiles.tar.gz
tar -xzf claude-skill/savant-ip-control.tar.gz
tar -xzf claude-skill/savant-profile-validator.tar.gz
```

## Architecture & Structure

### Directory Organization

```
WME-50/
├── Barco_WME-50_REST.md              # REST API documentation
├── barco_WME-50.xml                  # Complete profile (TEXT API)
├── barco_WME-50_REST.xml             # Complete profile (REST API)
│
└── claude-skill/                     # AI Skills Package
    ├── INDEX.md                      # Complete index and quick reference
    ├── SAVANT_SKILLS_README.md       # Quick start guide
    ├── SKILLS_COMPLETE_GUIDE.md      # Detailed learning path
    │
    ├── savant-profiles/              # Skill 1: General guidance
    │   ├── SKILL.md                  # Main documentation
    │   ├── references/
    │   │   ├── profile-template.md   # XML templates for all device types
    │   │   └── device-classes.md     # Device classification guide
    │   ├── assets/
    │   │   ├── racepoint_component_profile.xsd    # Main schema
    │   │   ├── commonConfig.xsd                    # Resource definitions
    │   │   └── Component_Profile_Developers_Guide.md
    │   └── savant-profiles.tar.gz
    │
    ├── savant-ip-control/            # Skill 2: IP protocols
    │   ├── SKILL.md                  # IP protocols and patterns
    │   ├── references/
    │   │   └── checksums-ip.md       # 20+ checksum algorithms
    │   └── savant-ip-control.tar.gz
    │
    └── savant-profile-validator/     # Skill 3: Validation tools
        ├── SKILL.md                  # Validation guide
        ├── scripts/
        │   └── validate_profile.py   # Python 3 XML validator
        ├── assets/
        │   ├── racepoint_component_profile.xsd
        │   └── commonConfig.xsd
        └── savant-profile-validator.tar.gz
```

### Technology Stack

**Format & Schemas**
- XML (component profiles)
- XSD (schema validation) - `racepoint_component_profile.xsd` and `commonConfig.xsd`

**Validation & Testing**
- Python 3 with lxml library (`pip install lxml`)
- Schema-based validation via XSD

**Protocols Supported**
- TCP/IP (persistent and non-persistent connections)
- UDP, HTTP/HTTPS, Telnet, SSH
- RS-232 (serial), IR (infrared)

### Key Design Concepts

**Services vs Resources**
- **Services**: End-user experiences (e.g., "Watch DVD", "Listen to Radio")
- **Resources**: Device capabilities providing the service (SOURCE, FUNCTION, SINK types)
  - `_SOURCE`: Content provider (e.g., `AV_DVD_SOURCE`)
  - `_FUNCTION`: Processing/switching capability (e.g., `AV_VIDEOSWITCH_FUNCTION`)
  - `_SINK`: Output to user (e.g., `AV_MONITOR_SINK`)

**Profile Components**
- **Logical Components**: Independent functional units (one per zone/output)
- **Implementations**: Device states (one per input selection)
- **Actions**: Control commands (PowerOn, VolumeUp, RouteInput, etc.)
- **Status Messages**: Parsing rules for device feedback

**IP Control Pattern** (for WME-50 and similar)
- Protocol: TCP or HTTP
- Command framing: Hex prefix/postfix (e.g., `0D0A` for `\r\n`)
- Checksums: Some devices require CRC, MD5, or other algorithms
- State tracking: Status messages parsed to update device state

## Important References & Validation

### Schema Files
- `claude-skill/savant-profiles/assets/racepoint_component_profile.xsd` - Primary schema defining valid profile structure
- `claude-skill/savant-profile-validator/assets/commonConfig.xsd` - Resource definitions and valid resource strings

### Example Profiles
- `barco_WME-50.xml` - Complete example with TEXT API control (port 23500)
- `barco_WME-50_REST.xml` - Same device with REST API variant
- Reference: `Barco_WME-50_REST.md` for API documentation

### Validator Checks
The Python validator checks:
1. XML well-formedness
2. Schema compliance
3. Required attributes (manufacturer, model, device_class, minimum_component_engine_version)
4. Resource string validity (e.g., `AV_DVD_SOURCE`, `AV_MONITOR_SINK`)
5. Control interface configuration (preferred method must be defined)
6. Logical component structure (connectors must be defined)
7. Implementation references (all connectors must exist)

### Common Resource Strings
Valid resources include:
- Sources: `AV_DVD_SOURCE`, `AV_TV_SOURCE`, `AV_STREAMINGDIGITALVIDEO_SOURCE`, `AV_GAME_SOURCE`, etc.
- Functions: `AV_VIDEOSWITCH_FUNCTION`, `AV_AUDIOSWITCH_FUNCTION`, `AV_AMPLIFIER_FUNCTION`, `AV_VIDEOPROCESSOR_FUNCTION`, etc.
- Sinks: `AV_MONITOR_SINK`, `AV_STEREOSPEAKERS_SINK`, `AV_SURROUNDSOUNDSPEAKERS_SINK`
- Environmental: `ENV_LIGHTINGCONTROLLER_SOURCE`, `ENV_HVACCONTROLLER_SOURCE`, etc.

## Claude Skills Integration

The three skills are designed to be automatically triggered by Claude based on query context:

1. **savant-profiles**: Triggers for general profile questions, device structure, services/resources, any device type
2. **savant-ip-control**: Triggers for IP protocols, TCP/UDP/HTTP, network devices, matrix switches, checksums
3. **savant-profile-validator**: Triggers for validation, errors, troubleshooting, testing

Users interact naturally by asking questions, and skills provide structured guidance with templates and examples.

## Development Workflow

### Creating a New Profile
1. Gather device specs: IP address/port, control commands from manual
2. Use **savant-profiles** skill for structure guidance
3. Use **savant-ip-control** skill for IP protocol details (if applicable)
4. Reference templates in `savant-profiles/references/profile-template.md`
5. Validate with: `python3 claude-skill/savant-profile-validator/scripts/validate_profile.py`
6. Fix errors reported and re-validate

### Modifying Existing Profile
1. Edit XML directly or ask Claude for guidance
2. Run validation after changes
3. Test with actual device if possible (Wireshark recommended for network capture)

## Notes for Future Development

- **No traditional build system** - This is documentation and skill-based, not a compiled project
- **Validation is primary**: Always validate XML against schema before testing
- **Schema is source of truth**: XSD files define all valid elements, attributes, and values
- **IP control is common**: Most modern devices use TCP/IP, so `savant-ip-control` skill is frequently needed
- **Real-world example**: WME-50 profiles demonstrate TEXT and REST variants of same device
- **Error handling**: Validator provides specific error messages with line numbers for debugging
