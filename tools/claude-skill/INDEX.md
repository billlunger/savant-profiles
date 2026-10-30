# Savant Component Profile Skills - Complete Index

## 📋 Quick Access

- **Start Here**: [SAVANT_SKILLS_README.md](SAVANT_SKILLS_README.md)
- **Complete Guide**: [SKILLS_COMPLETE_GUIDE.md](SKILLS_COMPLETE_GUIDE.md)
- **Visual Structure**: [SKILL_STRUCTURE.txt](SKILL_STRUCTURE.txt)

---

## 📦 SKILL 1: savant-profiles (Main Comprehensive Skill)

### Core Files
- `savant-profiles/SKILL.md` - Main skill with complete workflow

### References (Progressive Disclosure)
- `savant-profiles/references/profile-template.md` - Complete XML templates for all device types
- `savant-profiles/references/device-classes.md` - All device classes with decision tree

### Assets
- `savant-profiles/assets/racepoint_component_profile.xsd` - Main XML schema
- `savant-profiles/assets/commonConfig.xsd` - Resource definitions schema
- `savant-profiles/assets/Component_Profile_Developers_Guide.md` - Original guide

### Archive
- `savant-profiles.tar.gz` - Compressed skill (35KB)

**Purpose**: Complete guide for creating any Savant component profile  
**Triggers**: General profile questions, device structure, services/resources  
**Best For**: Understanding concepts, any device type, overall structure

---

## 📦 SKILL 2: savant-ip-control (IP Communication Specialist)

### Core Files
- `savant-ip-control/SKILL.md` - IP protocols and patterns guide

### References
- `savant-ip-control/references/checksums-ip.md` - Complete checksum reference (20+ algorithms with examples)

### Archive
- `savant-ip-control.tar.gz` - Compressed skill (7KB)

**Purpose**: Deep dive into IP network communication  
**Triggers**: IP, TCP, UDP, HTTP, network, matrix switch, checksums  
**Best For**: IP-controlled devices, custom protocols, matrix switches, A/V receivers

---

## 📦 SKILL 3: savant-profile-validator (Validation & Troubleshooting)

### Core Files
- `savant-profile-validator/SKILL.md` - Validation guide and error catalog

### Scripts
- `savant-profile-validator/scripts/validate_profile.py` - Python XML validator
  - Validates XML syntax
  - Checks schema compliance
  - Verifies resources
  - Reports structural issues

### Assets
- `savant-profile-validator/assets/racepoint_component_profile.xsd` - Schema for validation
- `savant-profile-validator/assets/commonConfig.xsd` - Resource schema

### Archive
- `savant-profile-validator.tar.gz` - Compressed skill (25KB)

**Purpose**: Validate XML and diagnose errors  
**Triggers**: Validate, check, error, troubleshoot, test  
**Best For**: Catching errors early, fixing issues, testing profiles

---

## 📚 Documentation Files

### Overview & Getting Started
- **SAVANT_SKILLS_README.md** (6KB)
  - Quick start guide
  - Skill descriptions
  - Common device types
  - Best practices

### Detailed Guide
- **SKILLS_COMPLETE_GUIDE.md** (8KB)
  - Complete package documentation
  - Usage examples
  - Learning path
  - Tips for best results

### Visual Reference
- **SKILL_STRUCTURE.txt** (6KB)
  - Visual skill structure
  - Usage patterns
  - File tree
  - Quick reference

### This File
- **INDEX.md** - Complete file index

---

## 🎯 How to Use

### Option 1: Use Skills in Claude
Simply ask Claude questions about Savant profiles. The skills will automatically trigger based on your question.

**Examples:**
- "Create a profile for an IP-controlled matrix switch"
- "What are services and resources?"
- "Validate this profile XML"

### Option 2: Browse Documentation
Read the skill files directly to learn:
1. Start with SAVANT_SKILLS_README.md
2. Browse SKILL.md files for each skill
3. Reference the specific guides in references/ directories

### Option 3: Use Validation Script Standalone
```bash
# Extract validator
tar -xzf savant-profile-validator.tar.gz

# Run validation
python savant-profile-validator/scripts/validate_profile.py my_profile.xml
```

---

## 📁 Directory Structure

```
/mnt/user-data/outputs/
├── Documentation (Read First)
│   ├── INDEX.md (this file)
│   ├── SAVANT_SKILLS_README.md (start here)
│   ├── SKILLS_COMPLETE_GUIDE.md (detailed)
│   └── SKILL_STRUCTURE.txt (visual)
│
├── Skill 1: Comprehensive
│   ├── savant-profiles/
│   │   ├── SKILL.md
│   │   ├── references/
│   │   │   ├── profile-template.md
│   │   │   └── device-classes.md
│   │   ├── assets/
│   │   │   ├── *.xsd (schemas)
│   │   │   └── Component_Profile_Developers_Guide.md
│   │   └── scripts/ (empty, placeholder)
│   └── savant-profiles.tar.gz
│
├── Skill 2: IP Specialist
│   ├── savant-ip-control/
│   │   ├── SKILL.md
│   │   ├── references/
│   │   │   └── checksums-ip.md
│   │   ├── assets/ (empty, placeholder)
│   │   └── scripts/ (empty, placeholder)
│   └── savant-ip-control.tar.gz
│
└── Skill 3: Validator
    ├── savant-profile-validator/
    │   ├── SKILL.md
    │   ├── scripts/
    │   │   └── validate_profile.py
    │   ├── assets/
    │   │   ├── commonConfig.xsd
    │   │   └── racepoint_component_profile.xsd
    │   └── references/ (empty, placeholder)
    └── savant-profile-validator.tar.gz
```

---

## 🔑 Key Concepts Quick Reference

### Services
End-user experiences (Watch DVD, Listen to Radio)

### Resources
Device capabilities:
- `_SOURCE`: Provides content (e.g., `AV_DVD_SOURCE`)
- `_FUNCTION`: Processes/switches (e.g., `AV_VIDEOSWITCH_FUNCTION`)
- `_SINK`: Outputs to user (e.g., `AV_MONITOR_SINK`)

### Logical Components
Independent functional blocks (one per zone/output)

### Implementations
Device states (one per input selection)

### Actions
Control commands (PowerOn, VolumeUp, RouteInput, etc.)

### Status Messages
Parsing rules for device feedback

---

## ✅ What's Validated

The validator checks:
- ✓ XML well-formedness
- ✓ Schema compliance
- ✓ Required attributes
- ✓ Resource string validity
- ✓ Control interface configuration
- ✓ Logical component structure
- ✓ Implementation references
- ✓ Action definitions

---

## 📊 File Sizes

| File | Size | Purpose |
|------|------|---------|
| savant-profiles.tar.gz | 35KB | Main skill compressed |
| savant-ip-control.tar.gz | 7KB | IP skill compressed |
| savant-profile-validator.tar.gz | 25KB | Validator compressed |
| SAVANT_SKILLS_README.md | 6KB | Overview |
| SKILLS_COMPLETE_GUIDE.md | 8KB | Detailed guide |
| SKILL_STRUCTURE.txt | 6KB | Visual structure |

**Total Package: ~90KB**

---

## 🚀 Getting Started Checklist

- [ ] Read SAVANT_SKILLS_README.md (5 min)
- [ ] Ask Claude a test question about profiles
- [ ] Browse one SKILL.md file (10 min)
- [ ] Extract and test validator script
- [ ] Create your first profile with Claude's help

---

## 💡 Pro Tips

1. **Let skills auto-trigger**: Just ask natural questions
2. **Mention "IP control"**: Gets IP specialist skill
3. **Request validation often**: Catch errors early
4. **Use templates**: Copy and modify from references
5. **Test incrementally**: Add features one at a time

---

## 📞 Usage Examples

### Creating New Profile
```
You: "Create an IP profile for an 8x8 HDMI matrix switch using TCP 
      on port 5000. Route commands are 'X1Y1' format."

Claude: [Uses savant-ip-control]
→ Guides through complete profile creation
→ Sets up IP configuration
→ Creates logical components
→ Adds routing actions
```

### Understanding Concepts
```
You: "Explain how services and resources work in Savant profiles"

Claude: [Uses savant-profiles]
→ Explains service requirements
→ Shows resource chain examples
→ Demonstrates with DVD service
```

### Fixing Errors
```
You: "Validate this profile and fix any errors" [uploads XML]

Claude: [Uses savant-profile-validator]
→ Runs validation
→ Reports specific errors with line numbers
→ Provides fixes for each issue
```

---

## 🎓 Learning Resources

### Included in Package
- Complete developer guide (assets/)
- XML schemas with all valid values (assets/)
- Template library (references/)
- Checksum algorithms (references/)
- Device class guide (references/)
- Error catalog (validator SKILL.md)

### External Tools Mentioned
- Oxygen XML Editor (recommended, schema-aware)
- Wireshark (for protocol analysis)
- Python 3 + lxml (for validator script)

---

## ✨ What Makes This Special

1. **Tailored to Your Needs**
   - IP control focus
   - Matrix switches
   - Complex protocols
   - Validation built-in

2. **Progressive Disclosure**
   - Essentials in SKILL.md
   - Details in references/
   - Schemas in assets/
   - Only loads what's needed

3. **Comprehensive Coverage**
   - 20+ checksum types
   - All IP protocols
   - Complete templates
   - Error solutions

4. **Validation-First**
   - Python validator
   - Common errors documented
   - Testing procedures
   - Troubleshooting guide

---

## 📝 Notes

- Skills automatically trigger based on keywords in your questions
- Multiple skills can work together on complex questions
- Validator requires Python 3 with lxml library: `pip install lxml`
- All XML examples are copy-paste ready
- Schemas included for reference and validation

---

## 🎯 Next Actions

1. **Read**: Start with SAVANT_SKILLS_README.md
2. **Ask**: Try a question with Claude
3. **Validate**: Test the validator script
4. **Create**: Build your first profile

The skills are ready to use immediately - just start asking questions!

---

*Skills created: November 2025*  
*Based on: RacePoint Component Profile Schema & Developer Guide v1.0.0*  
*Optimized for: IP-controlled matrix switches, A/V receivers, displays*
