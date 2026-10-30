# IP Protocol Checksums

Complete guide to checksum types used in IP-controlled devices.

## Checksum Parameter Structure

```xml
<checksum_parameter 
    type="hex"
    constant_length="1"
    checksum_type="standard"
    checksum_offset_A="0"
    checksum_offset_B="0"
    calculate_checksum_based_on_data="before_checksum"/>
```

## Common Checksum Types

### standard
Simple sum with offsets: `offsetA - offsetB + sum(bytes)`

**Example:**
```xml
<checksum_parameter 
    type="hex" 
    constant_length="1" 
    checksum_type="standard" 
    checksum_offset_A="0" 
    checksum_offset_B="0"/>
```

For command `02 05 01 00`:
- Sum = 0x02 + 0x05 + 0x01 + 0x00 = 0x08
- Checksum = 0 - 0 + 0x08 = 0x08
- Result: `02 05 01 00 08`

### ones_complement
One's complement: `offsetA + ~(offsetB + sum(bytes))`

**Example:**
```xml
<checksum_parameter 
    type="hex" 
    constant_length="1" 
    checksum_type="ones_complement" 
    checksum_offset_A="0" 
    checksum_offset_B="0"/>
```

### twos_complement
Two's complement: `offsetA + ~(offsetB + 1 + sum(bytes))`

### bitwise_xor
XOR all bytes together:

**Example:**
```xml
<checksum_parameter 
    type="hex" 
    constant_length="1" 
    checksum_type="bitwise_xor" 
    checksum_offset_A="0" 
    checksum_offset_B="0"/>
```

For command `02 05 01 00`:
- XOR = 0x02 ^ 0x05 ^ 0x01 ^ 0x00 = 0x06
- Result: `02 05 01 00 06`

### bitwise_or
OR all bytes together:

### crc_16_modbus
Standard Modbus CRC-16 (little endian):

**Example:**
```xml
<checksum_parameter 
    type="hex" 
    constant_length="2" 
    checksum_type="crc_16_modbus" 
    checksum_offset_A="0" 
    checksum_offset_B="0"/>
```

Used in Modbus RTU over TCP/IP.

### crc_16_modbus_big_endian
Modbus CRC-16 in big endian format.

### crc_16_ibm_little_endian / crc_16_ibm_big_endian
IBM CRC-16 polynomial in specified endianness.

## Calculate Checksum Based On Data

Determines which bytes are included in checksum calculation:

### before_checksum (default)
Include all bytes that come before the checksum position:

```xml
<command>
    <command_string type="hex">02 05</command_string>
    <parameter_list>
        <standard_parameter>
            <action_argument>value</action_argument>
        </standard_parameter>
        <checksum_parameter 
            type="hex" 
            constant_length="1" 
            checksum_type="standard" 
            checksum_offset_A="0" 
            checksum_offset_B="0"
            calculate_checksum_based_on_data="before_checksum"/>
    </parameter_list>
</command>
```

If value=10 (0x0A):
- Bytes before checksum: `02 05 0A`
- Checksum calculated on: `02 05 0A`
- Result: `02 05 0A [checksum]`

### after_checksum
Include bytes that come after the checksum position:

```xml
<command>
    <command_string type="hex">02 05</command_string>
    <parameter_list>
        <checksum_parameter 
            type="hex" 
            constant_length="1" 
            checksum_type="standard" 
            checksum_offset_A="0" 
            checksum_offset_B="0"
            calculate_checksum_based_on_data="after_checksum"/>
        <standard_parameter>
            <action_argument>value</action_argument>
        </standard_parameter>
    </parameter_list>
</command>
```

If value=10 (0x0A):
- Bytes after checksum: `0A`
- Checksum calculated on: `02 05 0A` (header + data after)
- Result: `02 05 [checksum] 0A`

## Source Data Type

Specifies input format for checksum calculation:

```xml
<checksum_parameter 
    type="hex" 
    constant_length="2"
    checksum_type="crc_16_modbus"
    source_data_type="hex"/>
```

- `hex`: Calculate on raw byte values
- `character`: Calculate on ASCII character codes

## Practical Examples

### Example 1: Simple Sum Checksum
Protocol: Header + Command + Data + Checksum (sum of all bytes)

```xml
<action name="SetVolume">
    <action_argument name="volume" type="integer" min="0" max="100"/>
    <command>
        <command_string type="hex">02 05</command_string>
        <parameter_list>
            <standard_parameter>
                <action_argument>volume</action_argument>
                <format>%02X</format>
            </standard_parameter>
            <checksum_parameter 
                type="hex" 
                constant_length="1" 
                checksum_type="standard" 
                checksum_offset_A="0" 
                checksum_offset_B="0"/>
        </parameter_list>
    </command>
</action>
```

For volume=50 (0x32):
- Command: `02 05 32`
- Sum: 0x02 + 0x05 + 0x32 = 0x39
- Full command: `02 05 32 39`

### Example 2: XOR Checksum with Offset
Protocol: STX + Length + Command + Data + XOR(all except STX) + ETX

```xml
<action name="PowerOn">
    <command>
        <command_string type="hex">02 04 01</command_string>
        <parameter_list>
            <checksum_parameter 
                type="hex" 
                constant_length="1" 
                checksum_type="bitwise_xor" 
                checksum_offset_A="0" 
                checksum_offset_B="2"/>  <!-- Skip first 2 bytes -->
            <constant type="hex">03</constant>
        </parameter_list>
    </command>
</action>
```

Command breakdown:
- 02 = STX (not included in checksum due to offset)
- 04 = Length
- 01 = Command
- XOR of 04 ^ 01 = 0x05
- 03 = ETX
- Full command: `02 04 01 05 03`

### Example 3: Modbus CRC
Protocol: Address + Function + Data + CRC16

```xml
<action name="WriteRegister">
    <action_argument name="value" type="integer" min="0" max="65535"/>
    <command>
        <command_string type="hex">01 06 00 00</command_string>
        <parameter_list>
            <standard_parameter>
                <action_argument>value</action_argument>
                <format>%04X</format>  <!-- 2 bytes -->
            </standard_parameter>
            <checksum_parameter 
                type="hex" 
                constant_length="2" 
                checksum_type="crc_16_modbus" 
                checksum_offset_A="0" 
                checksum_offset_B="0"/>
        </parameter_list>
    </command>
</action>
```

### Example 4: Two's Complement
Protocol: Command with two's complement checksum

```xml
<action name="SetInput">
    <action_argument name="input" type="integer" min="1" max="8"/>
    <command>
        <command_string type="hex">AA 01</command_string>
        <parameter_list>
            <standard_parameter>
                <action_argument>input</action_argument>
            </standard_parameter>
            <checksum_parameter 
                type="hex" 
                constant_length="1" 
                checksum_type="twos_complement" 
                checksum_offset_A="0" 
                checksum_offset_B="0"/>
        </parameter_list>
    </command>
</action>
```

## Troubleshooting Checksums

### Device Rejects Commands
1. Capture working command with network sniffer
2. Calculate checksum manually
3. Compare with device documentation
4. Verify offset_A and offset_B values
5. Check source_data_type setting
6. Try different checksum types

### Testing Checksum Calculation
Use the validation tool:

```bash
python scripts/validate_checksum.py "02 05 01 00" --type standard
```

### Common Mistakes
1. Wrong checksum_type
2. Incorrect offset values
3. Including/excluding wrong bytes
4. Wrong endianness (little vs big endian)
5. Wrong constant_length (1 byte vs 2 bytes)
