#!/usr/bin/env python3
# Specify that the script should be run using Python 3

import warnings
# Import the warnings module to issue warning messages

import serial
# Import the serial module for serial communication

from pathlib import Path
# Import Path from pathlib for handling file paths

from enum import IntEnum
# Import IntEnum for creating enumerated constants

from configBlocks import Config
# Import the Config class from the lorenztelegram.configBlocks module

# Custom exception for unsupported commands
class UnsupportedCommand(Exception):
    pass

# Custom exception for communication errors
class CommunicationError(Exception):
    pass

# Enum for error codes related to the Lorenz sensors
class Error(IntEnum):
    OK = 0
    GENERIC = 1
    WATCHDOG = 2
    ROTOR_GENERIC = 3
    ROTOR_WRONG_SPEED = 4
    ROTOR_TOO_SLOW = 5
    ROTOR_TOO_FAST = 6
    ROTOR_NOT_COMPATIBLE = 7
    ROTOR_GOT_RESET = 8
    ROTOR_NOT_FOUND = 9
    ROTOR_UNSTABLE = 10
    ROTOR_TIMEOUT = 11
    ROTOR_GOT_NACK = 12
    ROTOR_BAD_CMD_ECHO = 13
    ROTOR_BAD_EE_WRITE = 14
    ROTOR_BAD_COMUNICAITON = 15
    
    ROTOR_CONFIG = 31
    
    CONFIG_BLOCK = 20
    STATOR_CONFIG = 21
    
    STATOR_HARDWARE_CONFIG = 26
    STATOR_OPERATION_CONFIG = 27
    
    FACTORY_CALIBRATE = 32
    USER_CALIBRATE = 33
    FACTORY_CALIBRATE_CONTENTS = 34
    USER_CALIBRATE_CONTENTS = 35

    BAD_PARM_SIZE = 40
    BAD_CMD = 41
    BAD_CHECKSUM = 42
    BAD_PARM = 43
    BAD_ADDR = 44
    CANT_OVERWRITE = 45

    STACK_OVERFLOW = 60
    ANGLE_OVERFLOW = 61

# Enum for communication commands for Lorenz sensors
class Command(IntEnum):
    STX = 0x02,  # Start of text
    SCMD_ACK = 0x06,  # Acknowledgment command
    SCMD_NACK = 0x15,  # Negative acknowledgment command
    SCMD_Hello = 0x40,  # Hello command
    SCMD_ReadRaw = 0x41,  # Command to read raw data
    SCMD_ReadStatus = 0x42,  # Command to read full status
    SCMD_ReadStatusShort = 0x43,  # Command to read short status
    SCMD_ReadConfig = 0x44,  # Command to read configuration
    SCMD_WriteCalibrationControl = 0x45,  # Command to write calibration control
    SCMD_WriteConfig = 0x46,  # Command to write configuration
    SCMD_RestartDevice = 0x49,  # Command to restart the device
    SCMD_SetAngleToZero = 0x4B,  # Command to set angle to zero
    SCMD_GotoSpecialMode = 0x5A  # Command to switch to special mode

# Dictionary mapping commands to their expected parameter counts for RX and TX
cmd_parameter_counts = {
    'RX': {
        Command.SCMD_ACK: 0,
        Command.SCMD_NACK: 1,
        Command.SCMD_Hello: 1,
        Command.SCMD_ReadRaw: 9,
        Command.SCMD_ReadStatus: 14,
        Command.SCMD_ReadStatusShort: 1,
        Command.SCMD_ReadConfig: 33,
        Command.SCMD_WriteConfig: Command.SCMD_ACK,
        Command.SCMD_WriteCalibrationControl: Command.SCMD_ACK,
        Command.SCMD_RestartDevice: Command.SCMD_Hello,
        Command.SCMD_SetAngleToZero: Command.SCMD_ACK,
        Command.SCMD_GotoSpecialMode: Command.SCMD_ACK
    },
    'TX': {
        # Transmission expected parameter counts can be added here
    }
}

# Class representing a communication telegram
class Telegram:
    def __init__(self, command: Command=None, addr_from: int=0xFF, addr_to: int=0x01, parameters: list[int] = []) -> None:
        # Initialize a Telegram object with command, source and destination addresses, and parameters
        self.command = command  # The command of the telegram
        self.addr_to = addr_to  # Address to send the telegram to
        self.addr_from = addr_from  # Address sending the telegram

        # If parameters are in bytes, convert them to a list
        if type(parameters) in [bytes, bytearray]:
            parameters = list(parameters)
        self.parameters = parameters  # Store the parameters

        self.parameter_cnt = len(parameters)  # Count of parameters
        self.checksum = 0  # Initialize checksum
        self.wchecksum = 0  # Initialize weighted checksum

        self.stuffed = False  # Flag for indicating if the telegram is stuffed
        self.valid = False  # Flag for indicating if the telegram is valid
        if command is not None:
            self.checksum, self.wchecksum = self.calc_checksums()  # Calculate checksums if command is set
    
    def from_bytes(self, bytes_obj: bytes):
        """Construct a Telegram object from a bytes object

        Args:
            bytes_obj (bytes): The serialized telegram
        """
        # If the first byte indicates a stuffed telegram
        if bytes_obj[1] == Command.STX:
            bytes_obj = bytes_obj[2:]  # Remove extra STX for stuffed telegram
            self.stuffed = True  # Mark as stuffed
        else:
            bytes_obj = bytes_obj[1:]  # Remove the STX byte
        
        # Populate the Telegram fields from bytes
        self.command = Command(bytes_obj[0])  # Set the command
        self.addr_to = bytes_obj[1]  # Set the destination address
        self.addr_from = bytes_obj[2]  # Set the source address
        self.parameter_cnt = bytes_obj[3]  # Set the parameter count
        
        # If there are parameters, extract them
        if self.parameter_cnt > 0:
            self.parameters = []
            for b in bytes_obj[4:-2]:  # Extract parameters except for the last two checksum bytes
                self.parameters.append(b)
        
        # Calculate checksums and validate the telegram
        self.checksum, self.wchecksum = self.calc_checksums()
        self.valid = self.checksum == bytes_obj[-2] and self.wchecksum == bytes_obj[-1]

    def calc_checksums(self):
        """Generates checksums of telegram
           
           checksum: 1-byte sum of all the bytes in the message excluding STX and checksums
           wchecksum: 1-byte sum of all the checksums, with 1 added on overflows

        Returns:
            tuple[int, int]: The checksum and weighted checksum
        """
        # Prepare the list for checksum calculation
        tg = [self.command, self.addr_to, self.addr_from, self.parameter_cnt] + self.parameters
        
        checksum = 0  # Initialize checksum
        wchecksum = 0  # Initialize weighted checksum
        for itm in tg:  # Iterate through telegram items
            checksum += itm  # Add current item to checksum
            checksum = checksum & 0xFF  # Ensure checksum fits in one byte
            
            wchecksum += checksum  # Add to weighted checksum
            if wchecksum > 0xFF:  # Handle overflow
                wchecksum += 1
            wchecksum = wchecksum & 0xFF  # Ensure wchecksum fits in one byte
        
        return checksum, wchecksum  # Return calculated checksums

    def stuff(self, payload: list[int]) -> list[int]:
        out = []  # List to hold stuffed payload
        for itm in payload:  # Iterate through the payload
            out.append(itm)  # Add current item to the output
            if itm == Command.STX:  # If the item is STX, duplicate it
                out.append(itm)
        return out  # Return the stuffed payload

    def serialize(self) -> bytes:
        """Serialize the Telegram to a bytes string for sending

        Returns:
            bytes: bytes string to send to sensor
        """
        # Prepare the telegram data for serialization
        tg = [self.command, self.addr_to, self.addr_from, self.parameter_cnt] + self.parameters
        tg += list(self.calc_checksums())  # Append checksums

        tg = self.stuff(tg)  # Stuff the telegram if necessary

        return bytes([Command.STX] + tg)  # Return the serialized bytes including STX

# Class to handle communication with the Lorenz sensor via serial port
class LorenzConnector:
    UNSUPPORTED_COMMANDS = [
        # List of unsupported commands can be added here
    ]

    def __init__(self, port: str, timeout=0.01, **kwargs):
        """Create an object with a connection to a serial device

        Args:
            port (str): The serial port to connect to the device
            timeout (float): The timeout in to wait for new bytes from device when reading [s]

            kwargs: Supports all the keyword args that Serial.Serial() supports
        """
        # Default baudrate if not provided
        if not 'baudrate' in kwargs:
            kwargs['baudrate'] = 115200
        
        kwargs['bytesize'] = serial.EIGHTBITS  # Set byte size to 8 bits
        kwargs['stopbits'] = serial.STOPBITS_ONE  # Set stop bits to 1
        kwargs['parity'] = serial.PARITY_NONE  # Set no parity

        # Open the serial port if 'port' is in kwargs
        if 'port' in kwargs:
            port = kwargs['port']
            del kwargs['port']  # Remove port from kwargs

        self.ser = serial.Serial(**kwargs)  # Create a Serial object with provided settings
        self.ser.port = port  # Set the port
        self.ser.timeout = timeout  # Set timeout

        self.mode = "undefined"  # Initialize communication mode

        self.config = Config()  # Initialize configuration object
    
    def __enter__(self):
        self.ser.open()  # Open the serial port when entering the context
        return self  # Return the instance for use
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.ser.write(Command.STX.to_bytes(1, 'big'))  # Send STX to stop SOSM (Stream of Special Mode)
        self.ser.close()  # Close the serial port
    
    def _send_telegram(self, tg: Telegram) -> Telegram | None:
        """Send a Telegram and return the response (if any)

        Args:
            tg (Telegram): The Telegram object to send

        Returns:
            Telegram: Telegram response. None if sent telegram was a broadcast
        """
        # Check if the command is unsupported
        if tg.command in self.UNSUPPORTED_COMMANDS:
            raise UnsupportedCommand(f'{self.__class__.__name__} does not support {tg.command}')

        self.ser.write(tg.serialize())  # Serialize and send the telegram
        if tg.addr_to != 0:  # If it's not a broadcast, wait for a response
            rx_tg = self._recv_telegram(tg)  # Receive the response
            return rx_tg  # Return the received telegram
                
    def _recv_telegram(self, tx_tg: Telegram) -> Telegram:
        """Receive a telegram from a sensor

        Args:
            tx_tg (Telegram): The telegram that was sent to the sensor prior to the response

        Returns:
            Telegram: The telegram from the sensor
        """
        # TODO: Handle when sensors shouldn't respond, like on an RS485 bus
        
        # Determine expected parameter count for the response
        rx_params = cmd_parameter_counts['RX'][tx_tg.command]
        
        # Adjust expected length for specific commands
        if rx_params == Command.SCMD_ACK:
            rx_params = 0
        if rx_params == Command.SCMD_Hello:
            rx_params = 1

        expected_len = rx_params + 7  # Total expected length including header and checksums
        
        resp = None  # Initialize response variable
        # Wait for the Start of Text (STX) byte
        while resp != Command.STX.to_bytes(1, 'big') and resp != b'':
            resp = self.ser.read()  # Read a byte from the serial port
        rx = [resp]  # Start the received telegram list with the STX

        # Continue reading bytes until the expected length is reached
        while resp != b'' and len(rx) < expected_len:
            resp = self.ser.read()  # Read the next byte
            if resp == Command.STX.to_bytes(1, 'big'):  # If another STX is encountered
                resp = self.ser.read()  # Read the next byte
            rx.append(resp)  # Append the byte to the received telegram
            # If we encounter a NACK, expect additional bytes
            if len(rx) == 2 and rx[1] == int.to_bytes(Command.SCMD_NACK):
                expected_len = 8  # Set expected length to 8 bytes if NACK is received

        if resp == b'':
            return None  # Return None if no response is received

        # Convert the received byte objects to integers
        rx = [int.from_bytes(b, "big") for b in rx]
        
        tg = Telegram()  # Create a new Telegram object
        tg.from_bytes(bytes(rx))  # Populate it from the received bytes
        return tg  # Return the populated Telegram object

    def hello(self, addr_to: int=1) -> Telegram | None:
        # Send a hello command to the specified address and return the response
        return self._send_telegram(Telegram(Command.SCMD_Hello, addr_to=addr_to))

    def get_raw(self) -> tuple[tuple[int, int], tuple[int, int]]:
        """Return a single set of raw and calibrated values from channel 0 and 1

        Returns:
            tuple[tuple[int, int], tuple[int, int]]: Returns a tuple of channel 0 and 1. (raw, cal)
        """
        tg = Telegram(Command.SCMD_ReadRaw)  # Create a telegram to read raw data
        
        resp_tg = self._send_telegram(tg)  # Send the telegram and receive the response

        # Extract raw and calibrated values from the response
        raw0 = (resp_tg.parameters[0] << 8) + resp_tg.parameters[1]
        raw1 = (resp_tg.parameters[2] << 8) + resp_tg.parameters[3]

        cal0 = (resp_tg.parameters[4] << 8) + resp_tg.parameters[5]
        cal1 = (resp_tg.parameters[6] << 8) + resp_tg.parameters[7]
        return (raw0, cal0), (raw1, cal1)  # Return both channels

    def get_status_short(self, addr_to: int=1) -> Telegram:
        # Send a command to get the short status of the sensor
        return self._send_telegram(Telegram(Command.SCMD_ReadStatusShort, addr_to=addr_to))
    
    def get_status(self, addr_to: int=1) -> Telegram:
        # Send a command to get the full status of the sensor
        return self._send_telegram(Telegram(Command.SCMD_ReadStatus, addr_to=addr_to))

    def restart_device(self, addr_to: int=1) -> Telegram:
        # Send a command to restart the sensor device
        return self._send_telegram(Telegram(Command.SCMD_RestartDevice, addr_to=addr_to))

    def zero_angle(self, addr_to: int=1) -> Telegram:
        # Send a command to set the angle to zero on the sensor
        return self._send_telegram(Telegram(Command.SCMD_SetAngleToZero, addr_to=addr_to))

    def _dump_all_blocks(self, addr_to: int=1, dump_file_path: Path=None):
        # Method to dump all configuration blocks to a file

        if dump_file_path is None:  # Default path if none provided
            dump_file_path = (Path(__file__).parent) / 'dump.txt'

        with dump_file_path.open('w') as fp:  # Open the dump file for writing
            for block in range(0xFF):  # Iterate through all possible blocks
                tg = Telegram(Command.SCMD_ReadConfig, parameters=[block])  # Create a read config telegram
                
                fp.write(f'BLOCK{block:>3}:\n\tTX:')  # Write block number to the file
                for b in tg.serialize():  # Serialize and write the transmitted telegram
                    fp.write(f'{b:02X} ')
                fp.write('\n\tRX:')  # Prepare to write the received response
                
                rx_tg = self._send_telegram(tg)  # Send the telegram and get the response
                if rx_tg is None:  # If no response received, log the failure
                    fp.write(f'Failed to read: {block}\n')
                    continue

                for b in rx_tg.serialize():  # Serialize and write the received telegram
                    fp.write(f'{b:02X} ')
                fp.write('\n')  # New line after each block

    def read_config(self, addr_to: int=1):
        # Read configuration blocks from the sensor
        for block in self.config:  # Iterate through the configuration blocks
            tg = Telegram(Command.SCMD_ReadConfig, parameters=[block.BLOCK])  # Create a read config telegram
            rx_tg = self._send_telegram(tg)  # Send the telegram and receive the response
            if rx_tg is None:  # Log failure if response is not received
                print(f'Failed to read: {block.__class__.__name__}')
                continue
            
            block.from_payload(rx_tg.parameters)  # Populate the block with received parameters

    def write_config(self, addr_to: int=1):
        # Write configuration blocks back to the sensor
        for block in self.config:  # Iterate through the configuration blocks
            if not block.READONLY:  # Check if the block is not read-only
                payload = block.serialize()  # Serialize the block
                params = block.BLOCK.to_bytes(1, 'big') + payload  # Prepare parameters for writing
                tg = Telegram(Command.SCMD_WriteConfig, addr_to=addr_to, parameters=params)  # Create write config telegram
                self._send_telegram(tg)  # Send the write command

    def start_streaming(self, sample_rate: int, count: int=0, channel: str='A'):
        # Start streaming data from the sensor

        if channel not in ['A', 'B', 'C']:  # Validate the channel
            raise ValueError('Channel can only be A B or C')

        if channel == 'C':
            self.mode = 'SOSM_DUAL'  # Set mode for dual streaming
        else:
            self.mode = 'SOSM_SINGLE'  # Set mode for single streaming

        # Sample rate is the period / 200us
        # 0xFF ~ 19.61 Hz
        sample_rate = int(1/sample_rate // 0.0002)  # Convert sample rate to the appropriate value
        sample_rate = min(0xFF, max(0, sample_rate))  # Clamp to valid range
        params = [3, sample_rate]  # Prepare parameters
        
        count = min(0xFFFF, max(0, count))  # Clamp count to valid range
        params.append(count >> 8)  # High byte of count
        params.append(count & 0xFF)  # Low byte of count
        params.append(ord(channel))  # Channel ASCII code
        
        # Switch to SOSM mode #3
        tg = Telegram(Command.SCMD_GotoSpecialMode, parameters=params)  # Create special mode command
        rx_tg = self._send_telegram(tg)  # Send the command and get the response
        if rx_tg.command != Command.SCMD_ACK:  # Check for acknowledgment
            raise ConnectionError(f'\n\tStart streaming failed with error: {repr(Error(rx_tg.parameters[-1]))}.\n\tIs the sampling rate too high?')
    
    def streaming_recv_poll(self):
        # Poll for received streaming data
        if not 'SOSM' in self.mode:  # Check if currently in streaming mode
            return None
        
        expected_bytes = 5 if self.mode == 'SOSM_DUAL' else 3  # Determine expected byte length

        idx = 0
        val = None
        if self.ser.in_waiting >= expected_bytes:  # Check if enough bytes are available
            resp = self.ser.read(expected_bytes)  # Read the response
            idx = resp[0]  # Index from the response
            val = int.from_bytes(resp[1:3], 'big', signed=True)  # Value from the response
            if expected_bytes == 5:  # If in dual mode, read additional value
                val = [val, int.from_bytes(resp[3:], 'big', signed=True), resp]  # Store both values and the response
        return idx, val  # Return index and value
    
    def stop_streaming(self):
        # Stop the streaming process
        self.ser.write(Command.STX.to_bytes(1, 'big'))  # Send STX to indicate stop
        self.ser.write(Command.STX.to_bytes(1, 'big'))  # Repeat to ensure stop command is received
        self.ser.write(Command.STX.to_bytes(1, 'big'))  # One last time for good measure

        self.mode = 'idle'  # Set mode back to idle


if __name__ == '__main__':
    with LorenzConnector('COM7') as lc:
        lc.read_config()  # Read current configuration
        #lc.dump_all_blocks()  # Optionally dump all blocks
        print('horse')
        #start = time.time()  # Uncomment if using time limit
        ret = lc.start_streaming(20)  # Start streaming with a sample rate of 20

        while True:  # Run indefinitely
            idx, val = lc.streaming_recv_poll()  # Poll for data
            if val is not None:  # Check if any value was received
                print(f'{idx:3d}: {val:6d}')  # Print the index and value
            #time.sleep(0.01)  # Uncomment for delay if needed
        lc.stop_streaming()  # Stop streaming when done
