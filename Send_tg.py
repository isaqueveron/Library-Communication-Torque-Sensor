"""
Telegram format:
♦ STX
♦ Command byte
♦ Receiver (RX) address
♦ Transmitter (TX) address
♦ Number of parameter bytes
♦ Parameters (optional)
♦ Checksum (byte)
♦ Weighted checksum (byte) 
"""

from config import *

def calc_checksums(tg: tuple[int]) -> tuple[int, int]:
        """Generates checksums for the telegram.
        
        Args:
            tg (list[int]): The telegram data to calculate checksums from.

        Returns:
            tuple[int, int]: The calculated checksum and weighted checksum.
        """
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

#COMANDS--------------------------------------
class Commands:
    def Hello(PARAMETERS: list[int]=[]) -> None:
        """
        Sensors can be configured to send this message after power up.
        This only makes sense in point to point applications because there is no protection against collisions with
        the RS485.
        The main purpose if this message is to help you to debug your side of the system. 
            
        Args:
            PARAMETERS (): parameters: Last error (in case of a restart)

        Returns:
            Nothing.
        """

        global STX, SCMD_Hello
        rx      =   0x00 #receiver
        tx      =   0x01 #transmiter
        command = SCMD_Hello
        par = (len(PARAMETERS))
        for i in PARAMETERS:
            par.append(i)
        
        # create the telegram to send
        telegram =[STX,STX,command,rx,tx]  #(stx,stx,command,rx,tx)
        telegram.append(par) # + (nro_par,parameters)
        CHECKSUM_WCHECKSUM = calc_checksums(telegram[2:]) # calls function to calculate the check sums excluding stx
        telegram = tuple(telegram)
        telegram = bytearray(telegram+CHECKSUM_WCHECKSUM) #transform the tuple of ints in a byte array for sending
        #print(telegram)
        SerialPort.write(telegram) #send the telegram

    def ReadRaw(PARAMETERS: list[int]=[]) -> None:
        """
        Sensors send the latest calibrated and uncalibrated measurement values. Used for calibrating the sensor
        or measuring in normal mode.
        With sensors or interfaces using one channel only both channels have the same value.
        Sensors with a digital input the output value of that channel is 0x8000 (low input) or 0x7FFF (high input).
        The output value with 100% load depends on the used sensor type. Please refer the Document of
        calibration or contact your distributor for information. 
            
        Args:
            PARAMETERS (None):

        Returns:
            Nothing.
        """

        global STX, SCMD_ReadRaw
        rx      =   0x01 #receiver
        tx      =   0xff #transmiter
        command=SCMD_ReadRaw
        par = (len(PARAMETERS))
        for i in PARAMETERS:
            par.append(i)
        
        # create the telegram to send
        telegram =[STX,STX,command,rx,tx]  #(stx,stx,command,rx,tx)
        telegram.append(par) # + (nro_par,parameters)
        CHECKSUM_WCHECKSUM = calc_checksums(telegram[2:]) # calls function to calculate the check sums excluding stx
        telegram = tuple(telegram)
        telegram = bytearray(telegram+CHECKSUM_WCHECKSUM) #transform the tuple of ints in a byte array for sending
        #print(telegram)
        SerialPort.write(telegram) #send the telegram

    def ReadStatus(PARAMETERS: list[int]=[]) -> None:
        """
        Send a detailed status report. It includes some internal information about the healthiness of the sensor.
        The number of parameters can change with various devices.   
            
        Args:
            PARAMETERS (None):

        Returns:
            Nothing.
        """

        global STX, SCMD_ReadStatus
        rx      =   0x01 #receiver
        tx      =   0xff #transmiter
        command=SCMD_ReadStatus
        par = (len(PARAMETERS))
        for i in PARAMETERS:
            par.append(i)
        
        # create the telegram to send
        telegram =[STX,STX,command,rx,tx]  #(stx,stx,command,rx,tx)
        telegram.append(par) # + (nro_par,parameters)
        CHECKSUM_WCHECKSUM = calc_checksums(telegram[2:]) # calls function to calculate the check sums excluding stx
        telegram = tuple(telegram)
        telegram = bytearray(telegram+CHECKSUM_WCHECKSUM) #transform the tuple of ints in a byte array for sending
        #print(telegram)
        SerialPort.write(telegram) #send the telegram

    def ReadStatusShort(PARAMETERS: list[int]=[]) -> None:
        """
        Send a short version of the status report. 
            
        Args:
            PARAMETERS (None):

        Returns:
            Nothing.
        """

        global STX, SCMD_ReadStatusShort
        rx      =   0x01 #receiver
        tx      =   0xff #transmiter
        #rx      =   0x00 #receiver
        #tx      =   0x00 #transmiter
        command=SCMD_ReadStatusShort
        par = (len(PARAMETERS))
        for i in PARAMETERS:
            par.append(i)
        
        # create the telegram to send
        telegram =[STX,STX,command,rx,tx]  #(stx,stx,command,rx,tx)
        telegram.append(par) # + (nro_par,parameters)
        CHECKSUM_WCHECKSUM = calc_checksums(telegram[2:]) # calls function to calculate the check sums excluding stx
        telegram = tuple(telegram)
        telegram = bytearray(telegram+CHECKSUM_WCHECKSUM) #transform the tuple of ints in a byte array for sending
        #print(telegram)
        SerialPort.write(telegram) #send the telegram

    def ReadConfig(PARAMETERS: list[int]=[]) -> None:
        """
        Reads a configuration block. There are several blocks containing different data.
            
        Args:
            PARAMETERS (None):

        Returns:
            Nothing.
        """

        global STX, SCMD_ReadConfig
        rx      =   0x01 #receiver
        tx      =   0xff #transmiter
        command=SCMD_ReadConfig
        par = (len(PARAMETERS))
        for i in PARAMETERS:
            par.append(i)
        
        # create the telegram to send
        telegram =[STX,STX,command,rx,tx]  #(stx,stx,command,rx,tx)
        telegram.append(par) # + (nro_par,parameters)
        CHECKSUM_WCHECKSUM = calc_checksums(telegram[2:]) # calls function to calculate the check sums excluding stx
        telegram = tuple(telegram)
        telegram = bytearray(telegram+CHECKSUM_WCHECKSUM) #transform the tuple of ints in a byte array for sending
        #print(telegram)
        SerialPort.write(telegram) #send the telegram

    def WriteConfig(PARAMETERS: list[int]=[]) -> None: #parameter: Block number + 32 bytes
        """
        Writes a configuration block. Blocks 0,1,128,129 can only be written once in the production of the sensor
            
        Args:
            PARAMETERS (parameters[n]): Block number + 32 bytes

        Returns:
            Nothing.
        """

        global STX, SCMD_WriteConfig
        rx      =   0x01 #receiver
        tx      =   0xff #transmiter
        command=SCMD_WriteConfig
        par = (len(PARAMETERS))
        for i in PARAMETERS:
            par.append(i)
        
        # create the telegram to send
        telegram =[STX,STX,command,rx,tx]  #(stx,stx,command,rx,tx)
        telegram.append(par) # + (nro_par,parameters)
        CHECKSUM_WCHECKSUM = calc_checksums(telegram[2:]) # calls function to calculate the check sums excluding stx
        telegram = tuple(telegram)
        telegram = bytearray(telegram+CHECKSUM_WCHECKSUM) #transform the tuple of ints in a byte array for sending
        #print(telegram)
        SerialPort.write(telegram) #send the telegram

    def WriteFullStroke(PARAMETERS: list[int]=[]) -> None: #parameter: on/off
        """
        Sets the sensor into the check mode where it sends a 100% signal.
        Note: There must not be any torque applied to the sensor, it would add false information to the 100%
        signal. 
            
        Args:
            PARAMETERS (on/off): parameter: on/off
        Returns:
            Nothing.
        """

        global STX, SCMD_WriteFullStroke 
        rx      =   0x01 #receiver
        tx      =   0xff #transmiter
        command=SCMD_WriteFullStroke 
        par = (len(PARAMETERS))
        for i in PARAMETERS:
            par.append(i)
        
        # create the telegram to send
        telegram =[STX,STX,command,rx,tx]  #(stx,stx,command,rx,tx)
        telegram.append(par) # + (nro_par,parameters)
        CHECKSUM_WCHECKSUM = calc_checksums(telegram[2:]) # calls function to calculate the check sums excluding stx
        telegram = tuple(telegram)
        telegram = bytearray(telegram+CHECKSUM_WCHECKSUM) #transform the tuple of ints in a byte array for sending
        #print(telegram)
        SerialPort.write(telegram) #send the telegram

    def RestartDevice(PARAMETERS: list[int]=[]) -> None:
        """
        Resets the device. It responses with a ‘hello’ even if it is permitted in configuration block or not
            
        Args:
            PARAMETERS (None):
        Returns:
            Nothing.
        """

        global STX, SCMD_RestartDevice 
        rx      =   0x01 #receiver
        tx      =   0xff #transmiter
        command=SCMD_RestartDevice 
        par = (len(PARAMETERS))
        for i in PARAMETERS:
            par.append(i)
        
        # create the telegram to send
        telegram =[STX,STX,command,rx,tx]  #(stx,stx,command,rx,tx)
        telegram.append(par) # + (nro_par,parameters)
        CHECKSUM_WCHECKSUM = calc_checksums(telegram[2:]) # calls function to calculate the check sums excluding stx
        telegram = tuple(telegram)
        telegram = bytearray(telegram+CHECKSUM_WCHECKSUM) #transform the tuple of ints in a byte array for sending
        #print(telegram)
        SerialPort.write(telegram) #send the telegram

while True:
    print('________________________')
    print('choose a command:       |')
    print('(1) -> Hello            |')
    print('(2) -> ReadRaw          |')
    print('(3) -> ReadStatus       |')
    print('(4) -> ReadStatusShort  |')
    print('(5) -> ReadConfig       |')
    print('(6) -> WriteConfig      |')
    print('(7) -> WriteFullStroke  |')
    print('(8) -> RestartDevice    |')
    print('________________________')
    selection = input('write command: ')
    if selection == '1':
        Commands.Hello()
    elif selection == '2':
        Commands.ReadRaw()
    elif selection == '3':
        Commands.ReadStatus()
    elif selection == '4':
        Commands.ReadStatusShort()
    elif selection == '5':
        Commands.ReadConfig()
    elif selection == '6':
        Commands.WriteConfig()
    elif selection == '7':
      Commands.WriteFullStroke()
    elif selection == '8':
       Commands.RestartDevice()
    else:
        print('!invalid command!')  
        print('________________________')
    time.sleep(1.5)  