"""
Telegram format:
♦ STX (double)
♦ Command byte
♦ Receiver (RX) address
♦ Transmitter (TX) address
♦ Number of parameter bytes
♦ Parameters (optional)
♦ Checksum (byte)
♦ Weighted checksum (byte) 
"""
#from ConfigMac import * #this works in my mac
from ConfigLinux import * #this works in my linux

class Tools:
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
    
    def SendTelegram(tg:bytearray) -> None:
        #print('bytearray sent    :',Receive.translate(tg))
        SerialPort.write(bytes(tg))

    def TransforData(RawData): 
        """Does the transformations of the measurementes sent by the sensor to its respectives positive or negative numbers
        
        Args: iterable

        return: data or None if overload
        """
        RawData = list(RawData)        
        i = 0
        while i < len(RawData):
            if RawData[i] >= 0 and RawData[i] <= 32767 : # is > 0
                None
            elif RawData[i] >= 0x7fff and RawData[i] <= 0xffff: # is < 0
                RawData[i]=RawData[i]-65536
            #possivel conversao para n/m 
            if abs(RawData[i]) > 25000:
                return None #overload  
            RawData[i] = (RawData[i]*5000)/25000
            i+=1
        return (RawData)

class Commands:
    #for later
    def __init__(self):
        self.torque=0
        self.velocidade=0
    ###
    def Hello(PARAMETERS: list[int]=[]) -> bytearray:
        """
        Sensors can be configured to send this message after power up.
        This only makes sense in point to point applications because there is no protection against collisions with
        the RS485.
        The main purpose if this message is to help you to debug your side of the system. 
            
        Args:
            PARAMETERS (None)

        Returns:
            the telegram bytearray.
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
        CHECKSUM_WCHECKSUM = Tools.calc_checksums(telegram[2:]) # calls function to calculate the check sums excluding stx
        telegram = tuple(telegram)
        telegram = bytearray(telegram+CHECKSUM_WCHECKSUM) #transform the tuple of ints in a byte array for sending
        return telegram #return the telegram

    def ReadRaw(PARAMETERS: list[int]=[]) -> bytearray:
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
            the telegram bytearray.
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
        CHECKSUM_WCHECKSUM = Tools.calc_checksums(telegram[2:]) # calls function to calculate the check sums excluding stx
        telegram = tuple(telegram)
        telegram = bytearray(telegram+CHECKSUM_WCHECKSUM) #transform the tuple of ints in a byte array for sending
        return telegram #return the telegram

    def ReadStatus(PARAMETERS: list[int]=[]) -> bytearray:
        """
        Send a detailed status report. It includes some internal information about the healthiness of the sensor.
        The number of parameters can change with various devices.   
            
        Args:
            PARAMETERS (None):

        Returns:
            the telegram bytearray.
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
        CHECKSUM_WCHECKSUM = Tools.calc_checksums(telegram[2:]) # calls function to calculate the check sums excluding stx
        telegram = tuple(telegram)
        telegram = bytearray(telegram+CHECKSUM_WCHECKSUM) #transform the tuple of ints in a byte array for sending
        return telegram #return the telegram

    def ReadStatusShort(PARAMETERS: list[int]=[]) -> bytearray:
        """
        Send a short version of the status report. 
            
        Args:
            PARAMETERS (None):

        Returns:
            the telegram bytearray.
        """

        global STX, SCMD_ReadStatusShort
        rx      =   0x01 #receiver
        tx      =   0xff #transmiter
        command=SCMD_ReadStatusShort
        par = (len(PARAMETERS))
        for i in PARAMETERS:
            par.append(i)
        
        # create the telegram to send
        telegram =[STX,STX,command,rx,tx]  #(stx,stx,command,rx,tx)
        telegram.append(par) # + (nro_par,parameters)
        CHECKSUM_WCHECKSUM = Tools.calc_checksums(telegram[2:]) # calls function to calculate the check sums excluding stx
        telegram = tuple(telegram)
        telegram = bytearray(telegram+CHECKSUM_WCHECKSUM) #transform the tuple of ints in a byte array for sending
        return telegram #return the telegram

    def ReadConfig(PARAMETERS: list[int]=[]) -> bytearray: #parameter: Block number
        """
        Reads a configuration block. There are several blocks containing different data.
            
        Args:
            PARAMETERS (Block number): Block number

        Returns:
            the telegram bytearray.
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
        CHECKSUM_WCHECKSUM = Tools.calc_checksums(telegram[2:]) # calls function to calculate the check sums excluding stx
        telegram = tuple(telegram)
        telegram = bytearray(telegram+CHECKSUM_WCHECKSUM) #transform the tuple of ints in a byte array for sending
        return telegram #return the telegram

    def WriteConfig(PARAMETERS: list[int]=[]) -> bytearray: #parameter: Block number + 32 bytes
        """
        Writes a configuration block. Blocks 0,1,128,129 can only be written once in the production of the sensor
            
        Args:
            PARAMETERS (parameters[n]): Block number + 32 bytes

        Returns:
            the telegram bytearray.
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
        CHECKSUM_WCHECKSUM = Tools.calc_checksums(telegram[2:]) # calls function to calculate the check sums excluding stx
        telegram = tuple(telegram)
        telegram = bytearray(telegram+CHECKSUM_WCHECKSUM) #transform the tuple of ints in a byte array for sending
        return telegram #return the telegram

    def WriteFullStroke(PARAMETERS: list[int]=[]) -> bytearray: #parameter: on/off
        """
        Sets the sensor into the check mode where it sends a 100% signal.
        Note: There must not be any torque applied to the sensor, it would add false information to the 100%
        signal. 
            
        Args:
            PARAMETERS (on/off): parameter: on/off
        Returns:
            the telegram bytearray.
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
        CHECKSUM_WCHECKSUM = Tools.calc_checksums(telegram[2:]) # calls function to calculate the check sums excluding stx
        telegram = tuple(telegram)
        telegram = bytearray(telegram+CHECKSUM_WCHECKSUM) #transform the tuple of ints in a byte array for sending
        return telegram #return the telegram

    def RestartDevice(PARAMETERS: list[int]=[]) -> bytearray:
        """
        Resets the device. It responses with a ‘hello’ even if it is permitted in configuration block or not
            
        Args:
            PARAMETERS (None):
        Returns:
            the telegram bytearray.
        """

        global STX, SCMD_RestartDevice 
        rx      =   0x01 #receiver
        tx      =   0xFF #transmiter
        command=SCMD_RestartDevice 
        par = (len(PARAMETERS))
        for i in PARAMETERS:
            par.append(i)
        
        # create the telegram to send
        telegram =[STX,STX,command,rx,tx]  #(stx,stx,command,rx,tx)
        telegram.append(par) # + (nro_par,parameters)
        CHECKSUM_WCHECKSUM = Tools.calc_checksums(telegram[2:]) # calls function to calculate the check sums excluding stx
        telegram = tuple(telegram)
        telegram = bytearray(telegram+CHECKSUM_WCHECKSUM) #transform the tuple of ints in a byte array for sending
        return telegram #return the telegram

class Receive:
    def translate(byte_array)->tuple:
        """transforma o bytearray recebido em uma tupla de int

        Args: 
            bytearray recebido
        """
        lista = []
        char = ''
        for byte in byte_array:
            try: char = (byte.decode())
            except:  
                char = (byte)
            lista.append(char)
        return (lista)
    
    def clean_tg(tg):
        if tg[-2:]==b'\r\n':
            tg = tg[:-2]
        if tg[1]==2:
            tg = tg[2:]
        else:            
            tg = tg[1:]
        return (tg)

    def check_checksums(tg: bytearray) -> bool|tuple:
        """check the equality of received checksums and calulated checksums
        
        Args:
            the tuple with the received values of the bytearray
            
        Returns:
            bool, tuple of calculated checksum and wgchecksum"""
        tg=Receive.clean_tg(tg)
        #print(tg)
        #print(Tools.calc_checksums(Receive.translate(tg[:-2])),tuple(Receive.translate(tg[-2:])))
        if Tools.calc_checksums(Receive.translate(tg[:-2]))==tuple(Receive.translate(tg[-2:])):
            return True
        else: return False
   
    def read_from()->bytes|None:
        data = SerialPort.readline()
        if data != b'': #if nothing is being told do not listen
            #print('bytearray received:',Receive.translate(data)) #print the data
            return data
        else: return None

    def ToHex(parameters): # func to trasnfor data to hex values
        i=0
        while i < len(parameters):
            parameters[i] = hex(parameters[i])
            i+=1
        return parameters

    def GetRaw(command_para:tuple)-> tuple: 
        """
        Outputs -> (MesurementChannel_0, MesurementChannel_1, CalibratedValCha_0, CalibratedValCha_1, FullstrokeFlag)
        """
        if command_para == None: return None
        command = command_para[0]
        if command== 65:
            command_para=list(command_para)
            parameters = Receive.ToHex(command_para[1:])
            MesurementChannel_0 = int((parameters[0])+(parameters[1])[2:],16)
            MesurementChannel_1 = int((parameters[2])+(parameters[3])[2:],16)
            CalibratedValCha_0  = int((parameters[4])+(parameters[5])[2:],16)
            CalibratedValCha_1  = int((parameters[6])+(parameters[7])[2:],16)
            FullstrokeFlag      = int((parameters[8]),16)
            return MesurementChannel_0,MesurementChannel_1,CalibratedValCha_0,CalibratedValCha_1,FullstrokeFlag
        else: return None

    def ReceiveMeasuring(code_received):
        global isReceiving
        code_translated = Receive.translate(Receive.clean_tg(code_received))
        if Receive.check_checksums(code_received): # if check sums check
            command = code_translated[0]
            #print("Command           :",command)
            #print("RX                :",code_translated[1])
            #print("TX                :",code_translated[2])
            #print("NBR OF PARAMETERS :",code_translated[3])
            if code_translated[3]==0: # if no parameters, do not print
                #print("CHECK SUMS        :",code_translated[4:])
                parameters_received=[0]
            else: 
                parameters_received=code_translated[4:-2] #here is the important information !!
                #print("PARAMS            :",parameters_received)
                #print("CKSUMS            :",code_translated[-2:])
            
            isReceiving = False
            return [command]+parameters_received
        else: pass #print('BAD CHECK SUMS')
        return None
    
    def ReceiveTg(code_received):
        global isReceiving
        code_translated = Receive.translate(Receive.clean_tg(code_received))
        print(code_translated)
        if Receive.check_checksums(code_received): # if check sums check
            command = code_translated[0]
            print("Command           :",command)
            print("RX                :",code_translated[1])
            print("TX                :",code_translated[2])
            print("NBR OF PARAMETERS :",code_translated[3])
            if code_translated[3]==0: # if no parameters, do not print
                print("CHECK SUMS        :",code_translated[4:])
                parameters_received=[0]
            else: 
                parameters_received=code_translated[4:-2] #here is the important information !!
                print("PARAMS            :",parameters_received)
                print("CKSUMS            :",code_translated[-2:])
            
            isReceiving = False
            return [command]+parameters_received
        else:print('BAD CHECK SUMS')
        return None

   
