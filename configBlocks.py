#!/usr/bin/env python3

from typing import Any  # Importing Any type for flexible type hinting
from dataclasses import dataclass  # Importing dataclass decorator for easy class definitions

# Custom exception for handling invalid block IDs
class BadBlockID(Exception):
    pass

# Base class for configuration blocks
class ConfigBlock:
    _PARAMETERS = {}  # Dictionary to hold parameter definitions for each block
    READONLY = False   # Flag indicating if the block is read-only
    _ID: int = None    # Block ID, to be set in subclasses
    BLOCK: int = None  # Block number, to be set in subclasses
    changed: bool = False  # Flag to track if the block has been modified

    # Checksums for data integrity
    checksum: int = 0  # Checksum for the payload
    wchecksum: int = 0  # Weighted checksum for additional integrity checking

    def __init__(self) -> None:
        # Define the structure for parameters, their offsets, and sizes
        self._PARAMETERS['checksum'] = {'offset': 28, 'size': 2}  # Checksum parameter
        self._PARAMETERS['wchecksum'] = {'offset': 30, 'size': 2}  # Weighted checksum parameter
        self._PARAMETERS['_ID'] = {'offset': 0, 'size': 1}  # ID parameter

    def calc_checksums(self, payload: list[int]) -> tuple[bytes, bytes]:
        """Generates checksums for the telegram.
        
        Args:
            payload (list[int]): The payload data to calculate checksums from.

        Returns:
            tuple[int, int]: The calculated checksum and weighted checksum.
        """
        checksum = 0  # Initialize checksum
        wchecksum = 0  # Initialize weighted checksum
        for itm in payload:  # Iterate over each byte in the payload
            checksum += itm  # Add the current byte to the checksum
            checksum &= 0xFFFF  # Limit checksum to 2 bytes

            wchecksum += checksum  # Add current checksum to weighted checksum
            wchecksum &= 0xFFFF  # Limit weighted checksum to 2 bytes
        
        # Convert checksums to 2-byte representations
        return checksum.to_bytes(2), wchecksum.to_bytes(2)

    def from_payload(self, payload: list[int]) -> None:
        """Initializes the block from a given payload.
        
        Args:
            payload (list[int]): The input data to populate the block.
        """
        block_num = payload[0]  # Get the first byte as block number
        if block_num != self.BLOCK:  # Check if the block number matches expected
            raise BadBlockID(f'Expected block: {self.BLOCK}, got block {block_num}')
        payload = payload[1:]  # Exclude the block number from payload
        
        for attr in self._PARAMETERS:  # Iterate over each defined parameter
            if attr in ['checksum', 'wchecksum']:  # Skip checksum fields
                continue  

            value = 0  # Initialize the value for the current attribute
            idx = self._PARAMETERS[attr]['offset']  # Get the offset for the attribute
            for _ in range(self._PARAMETERS[attr]['size']):  # Loop for the size of the attribute
                value = value << 8  # Shift left to make room for the next byte
                value += payload[idx]  # Add the byte from payload to the value
                idx += 1  # Move to the next byte in payload

            # Check for lookup table (LUT) conversion
            if 'LUT' in self._PARAMETERS[attr]:  # If there is a LUT defined
                if value in self._PARAMETERS[attr]['LUT']:  # Check if value is in LUT
                    value = self._PARAMETERS[attr]['LUT'][value]  # Convert value using LUT
            
            setattr(self, attr, value)  # Set the attribute with the calculated value

    def gen_payload(self) -> list[int]:
        """Generates a payload from the block's attributes.
        
        Returns:
            list[int]: The generated payload data.
        """
        payload = [0 for _ in range(27)]  # Initialize payload with zeros (27 bytes)
        payload[0] = self._ID  # Set the block ID at the beginning of the payload

        for attr in self._PARAMETERS:  # Iterate over each defined parameter
            if attr in ['checksum', 'wchecksum']:  # Skip checksum fields
                continue  

            value = getattr(self, attr)  # Get the current attribute's value
            # Reverse lookup for LUT if it exists
            if 'LUT' in self._PARAMETERS[attr]:  # If there is a LUT defined
                REVERSE_LUT = {v: k for k, v in self._PARAMETERS[attr]['LUT'].items()}  # Create reverse LUT
                if value in REVERSE_LUT:  # Check if value is in reverse LUT
                    value = REVERSE_LUT[value]  # Convert value using reverse LUT
             
            idx = self._PARAMETERS[attr]['offset'] + self._PARAMETERS[attr]['size'] - 1  # Get the index for storing value
            for _ in range(self._PARAMETERS[attr]['size']):  # Loop for the size of the attribute
                payload[idx] = value & 0xFF  # Store the least significant byte in the payload
                value >>= 8  # Shift right to process the next byte
                idx -= 1  # Move to the previous index
            
        return payload  # Return the constructed payload

    def __setattr__(self, name: str, value: Any) -> None:
        """Override for attribute setting to track changes."""
        if name in self._PARAMETERS:  # If the attribute is defined in parameters
            self.changed = True  # Mark block as changed
        super().__setattr__(name, value)  # Set the attribute normally

    def serialize(self) -> bytes:
        """Serializes the block to bytes, including checksums.
        
        Returns:
            bytes: The serialized data with checksums.
        """
        if self.READONLY:  # Check if the block is read-only
            raise AttributeError(f'{self.__class__.__name__} is read only')  # Raise error if it is read-only
        payload = self.gen_payload()  # Generate the payload
            
        checksum, wchecksum = self.calc_checksums(payload)  # Calculate the checksums
        # Return serialized data combining payload and checksums
        return bytes(payload) + checksum + wchecksum  

# Configuration block for stator header
@dataclass
class STATOR_HEADER(ConfigBlock):
    BLOCK: int = 0  # Set the block number
    _ID: int = 0x10  # Set the block ID
    READONLY: bool = True  # Set the block as read-only

    # Attributes specific to stator header
    STATOR_TYPE: int = None  # Type of the stator
    SERIAL: int = None  # Serial number of the stator
    SI_IDX: int = None  # SI index
    ACTIVE_PORT_COUNT: int = None  # Number of active ports

    # Parameter definitions for STATOR_HEADER
    _PARAMETERS = {
        'STATOR_TYPE': {'offset': 1, 'size': 3},  # Parameter for stator type
        'SERIAL': {'offset': 4, 'size': 4},  # Parameter for serial number
        'SI_IDX': {'offset': 8, 'size': 1},  # Parameter for SI index
        'ACTIVE_PORT_COUNT': {'offset': 9, 'size': 1}  # Parameter for active port count
    }

# Configuration block for stator hardware
@dataclass
class STATOR_HARDWARE(ConfigBlock):
    BLOCK: int = 1  # Set the block number
    _ID: int = 0x12  # Set the block ID
    READONLY: bool = True  # Set the block as read-only

    # Attributes specific to stator hardware
    PRODUCTION_TIME: int = None  # Time of production
    STAS: int = None  # STAS value
    OEM: int = None  # OEM value
    PULSES_PR_REV: int = None  # Pulses per revolution

    # Parameter definitions for STATOR_HARDWARE
    _PARAMETERS = {
        'PRODUCTION_TIME': {'offset': 1, 'size': 4},  # Parameter for production time
        'STAS': {'offset': 5, 'size': 5},  # Parameter for STAS
        'OEM': {'offset': 10, 'size': 1},  # Parameter for OEM
        'PULSES_PR_REV': {'offset': 11, 'size': 1, 'LUT': {  # Parameter for pulses per revolution with LUT
            0x00: None,  # No pulses
            0x01: 6,  # 6 pulses
            0x02: 30,  # 30 pulses
            0x03: 60,  # 60 pulses
            0x04: 90,  # 90 pulses
            0x05: 120,  # 120 pulses
            0x06: 180,  # 180 pulses
            0x07: 360,  # 360 pulses
            0x08: 720,  # 720 pulses
            0x09: 1440,  # 1440 pulses
            0x10: 100,  # 100 pulses
            0x11: 200,  # 200 pulses
            0x12: 400,  # 400 pulses
            0x13: 500,  # 500 pulses
            0x14: 1000,  # 1000 pulses
            0xFF: None  # No pulses
        }}
    }

# Configuration block for stator operation
@dataclass
class STATOR_OPERATION(ConfigBlock):
    BLOCK: int = 2  # Set the block number
    _ID: int = 0x13  # Set the block ID
    READONLY: bool = False  # Set the block as read-write

    # Attributes specific to stator operation
    modification_time: int = None  # Time of last modification
    wakeup_flag: int = None  # Wake-up flag status
    bus_address: int = None  # Bus address
    op_flags: int = None  # Operation flags
    baudrate: int = None  # Baud rate for communication
    output_A: int = None  # Output A configuration
    output_B: int = None  # Output B configuration
    lp_filter_A: int = None  # Low pass filter A configuration
    lp_filter_B: int = None  # Low pass filter B configuration

    # Parameter definitions for STATOR_OPERATION
    _PARAMETERS = {
        'modification_time': {'offset': 1, 'size': 4},  # Parameter for modification time
        'wakeup_flag': {'offset': 6, 'size': 1},  # Parameter for wake-up flag
        'bus_address': {'offset': 7, 'size': 1},  # Parameter for bus address
        'op_flags': {'offset': 9, 'size': 1},  # Parameter for operation flags
        'baudrate': {'offset': 10, 'size': 1, 'LUT': {  # Parameter for baud rate with LUT
            0x00: None,  # Device default
            0x09: 115200,  # 115200 baud
            0x10: 230400,  # 230400 baud
            0xFF: None  # Device default
        }},
        'output_A': {'offset': 11, 'size': 1, 'LUT': {  # Parameter for output A with LUT
            0x00: None,  # No output
            0x01: "A",  # Output A
            0x02: "B",  # Output B
            0x03: "SPEED",  # Speed output
            0x04: "ANGLE",  # Angle output
            0x05: "FORCE",  # Force output
            0x06: "POWER",  # Power output
            0xFF: None  # No output
        }},
        'output_B': {'offset': 12, 'size': 1, 'LUT': {  # Parameter for output B with LUT
            0x00: None,  # No output
            0x01: "A",  # Output A
            0x02: "B",  # Output B
            0x03: "SPEED",  # Speed output
            0x04: "ANGLE",  # Angle output
            # (Continue similarly for additional outputs and parameters)
        }}
    }
