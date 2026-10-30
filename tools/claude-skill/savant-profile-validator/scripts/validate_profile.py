#!/usr/bin/env python3
"""
Savant Component Profile Validator

Validates XML component profiles against the RacePoint schema.
"""

import sys
import argparse
from pathlib import Path
from lxml import etree

class ProfileValidator:
    def __init__(self, schema_path=None):
        self.errors = []
        self.warnings = []
        self.schema = None
        
        if schema_path:
            self.load_schema(schema_path)
    
    def load_schema(self, schema_path):
        """Load XSD schema for validation."""
        try:
            schema_doc = etree.parse(schema_path)
            self.schema = etree.XMLSchema(schema_doc)
            return True
        except Exception as e:
            self.errors.append(f"Failed to load schema: {e}")
            return False
    
    def validate_xml_wellformed(self, xml_path):
        """Check if XML is well-formed."""
        try:
            tree = etree.parse(xml_path)
            return True, tree
        except etree.XMLSyntaxError as e:
            self.errors.append(f"XML Syntax Error: {e}")
            return False, None
        except Exception as e:
            self.errors.append(f"Error reading file: {e}")
            return False, None
    
    def validate_against_schema(self, tree):
        """Validate XML against schema."""
        if not self.schema:
            self.warnings.append("No schema loaded - skipping schema validation")
            return True
        
        try:
            self.schema.assertValid(tree)
            return True
        except etree.DocumentInvalid as e:
            self.errors.append(f"Schema Validation Error: {e}")
            return False
    
    def check_required_attributes(self, tree):
        """Check for required attributes on component element."""
        root = tree.getroot()
        
        if root.tag != 'component':
            self.errors.append(f"Root element must be 'component', found '{root.tag}'")
            return False
        
        required_attrs = ['manufacturer', 'model', 'device_class', 'minimum_component_engine_version']
        missing = [attr for attr in required_attrs if attr not in root.attrib]
        
        if missing:
            self.errors.append(f"Missing required attributes: {', '.join(missing)}")
            return False
        
        return True
    
    def check_resource_strings(self, tree):
        """Verify all resource strings are valid."""
        # Valid resources from commonConfig.xsd
        valid_resources = {
            'AV_DVD_SOURCE', 'AV_ENHANCEDDVD_SOURCE', 'AV_TV_SOURCE',
            'AV_SATELLITETV_SOURCE', 'AV_STREAMINGDIGITALVIDEO_SOURCE',
            'AV_DIGITALVIDEO_SOURCE', 'AV_DIGITALIMAGE_SOURCE',
            'AV_AUDIO_SOURCE', 'AV_VIDEO_SOURCE', 'AV_AMRADIO_SOURCE',
            'AV_FMRADIO_SOURCE', 'AV_MULTIBANDRADIO_SOURCE',
            'AV_SATELLITERADIO_SOURCE', 'AV_CD_SOURCE', 'AV_SACD_SOURCE',
            'AV_DIGITALAUDIO_SOURCE', 'AV_GAME_SOURCE',
            'AV_SURROUNDSOUNDPROCESSOR_FUNCTION', 'AV_STEREOPROCESSOR_FUNCTION',
            'AV_PEQ_FUNCTION', 'AV_AUDIODAC_FUNCTION', 'AV_VIDEODAC_FUNCTION',
            'AV_VIDEOPROCESSOR_FUNCTION', 'AV_AMPLIFIER_FUNCTION',
            'AV_VIDEOSWITCH_FUNCTION', 'AV_AUDIOSWITCH_FUNCTION',
            'AV_VOLUMECONTROL_FUNCTION', 'AV_STEREOSPEAKERS_SINK',
            'AV_SURROUNDSOUNDSPEAKERS_SINK', 'AV_MONITOR_SINK',
            'ENV_LIGHTINGCONTROLLER_SOURCE', 'ENV_FANCONTROLLER_SOURCE',
            'ENV_HVACCONTROLLER_SOURCE', 'ENV_SHADECONTROLLER_SOURCE',
            'AV_VCR_SOURCE', 'AV_IPOD_SOURCE', 'AV_IPODCONTROL_FUNCTION',
            'AV_APPLEREMOTEMEDIASERVER_SOURCE', 'AV_CCTV_SOURCE',
            # Add more as needed
        }
        
        resources = tree.xpath('//resource')
        invalid = []
        
        for resource in resources:
            resource_text = resource.text.strip() if resource.text else ''
            if resource_text and resource_text not in valid_resources:
                invalid.append(resource_text)
        
        if invalid:
            self.warnings.append(f"Potentially invalid resources: {', '.join(set(invalid))}")
        
        return True
    
    def check_control_interface(self, tree):
        """Check control interface configuration."""
        control_interfaces = tree.xpath('//control_interfaces')
        
        if not control_interfaces:
            self.errors.append("Missing control_interfaces element")
            return False
        
        ci = control_interfaces[0]
        if 'preferred' not in ci.attrib:
            self.errors.append("control_interfaces missing 'preferred' attribute")
            return False
        
        preferred = ci.attrib['preferred']
        valid_preferred = ['ip', 'rs232', 'ir', 'serial_pwm', 'trigger', 'contact_sensor']
        
        if preferred not in valid_preferred:
            self.errors.append(f"Invalid preferred control: '{preferred}'")
            return False
        
        # Check if preferred control method is defined
        if not tree.xpath(f'//control_interfaces/{preferred}'):
            self.errors.append(f"Preferred control '{preferred}' not defined")
            return False
        
        return True
    
    def check_implementations(self, tree):
        """Check logical component implementations."""
        logical_components = tree.xpath('//logical_component')
        
        if not logical_components:
            self.warnings.append("No logical components defined")
            return True
        
        # Get all connector names
        inputs = {inp.get('name') for inp in tree.xpath('//media_interfaces/input')}
        outputs = {out.get('name') for out in tree.xpath('//media_interfaces/output')}
        data = {d.get('name') for d in tree.xpath('//media_interfaces/data')}
        
        all_connectors = inputs | outputs | data
        
        for lc in logical_components:
            lc_name = lc.get('name', 'unnamed')
            implementations = lc.xpath('implementation')
            
            if not implementations:
                self.warnings.append(f"Logical component '{lc_name}' has no implementations")
            
            for impl in implementations:
                impl_name = impl.get('name', 'unnamed')
                
                # Check connectors referenced
                for connector_type in ['input', 'output', 'data']:
                    connectors = impl.xpath(connector_type)
                    for conn in connectors:
                        conn_name = conn.text.strip() if conn.text else ''
                        if conn_name and conn_name not in all_connectors:
                            self.errors.append(
                                f"Implementation '{impl_name}' references {connector_type} "
                                f"'{conn_name}' which doesn't exist"
                            )
                
                # Check action_to_select
                action_to_select = impl.xpath('action_to_select')
                if not action_to_select:
                    self.warnings.append(
                        f"Implementation '{impl_name}' has no action_to_select"
                    )
        
        return True
    
    def validate(self, xml_path, strict=False):
        """Run all validations."""
        print(f"Validating: {xml_path}")
        print("-" * 60)
        
        # Check well-formedness
        is_wellformed, tree = self.validate_xml_wellformed(xml_path)
        if not is_wellformed:
            return False
        
        print("✓ XML is well-formed")
        
        # Check against schema
        if self.schema:
            if self.validate_against_schema(tree):
                print("✓ Valid against schema")
            else:
                return False
        
        # Additional checks
        self.check_required_attributes(tree)
        self.check_resource_strings(tree)
        self.check_control_interface(tree)
        self.check_implementations(tree)
        
        # Report results
        if self.errors:
            print("\n❌ ERRORS:")
            for error in self.errors:
                print(f"  - {error}")
            return False
        
        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        if not self.warnings:
            print("\n✓ No warnings")
        
        print("\n✅ Validation passed!")
        return True


def main():
    parser = argparse.ArgumentParser(description='Validate Savant component profile')
    parser.add_argument('profile', help='Path to component profile XML')
    parser.add_argument('--schema', help='Path to XSD schema file')
    parser.add_argument('--strict', action='store_true', help='Enable strict checking')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Try to find schema if not provided
    schema_path = args.schema
    if not schema_path:
        common_paths = [
            Path('racepoint_component_profile.xsd'),
            Path('../racepoint_component_profile.xsd'),
            Path('/mnt/user-data/uploads/racepoint_component_profile.xsd'),
        ]
        for path in common_paths:
            if path.exists():
                schema_path = str(path)
                break
    
    validator = ProfileValidator(schema_path)
    
    try:
        success = validator.validate(args.profile, strict=args.strict)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
