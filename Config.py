import time
import serial
import serial.tools.list_ports

ports = list(serial.tools.list_ports.comports())
print(ports[0][0])

port = ports[0][0]
#baudrate = 115200
baudrate = 230400
SerialPort = serial.Serial(port, baudrate, timeout=30)

STX =                           0x02
SCMD_ACK =                      0x06
SCMD_NACK =                     0x15
SCMD_Hello =                    0x40
SCMD_ReadRaw =                  0x41
SCMD_ReadStatus =               0x42
SCMD_ReadStatusShort =          0x43
SCMD_ReadConfig =               0x44
SCMD_WriteFullStroke =          0x45
SCMD_WriteConfig =              0x46
SCMD_RestartDevice  =           0x4B
SCMD_GotoSpecialMode =          0x5a
