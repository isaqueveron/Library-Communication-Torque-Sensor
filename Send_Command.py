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


def Send_Byte(data):
    if data > 255 or data < 0 or type(data)!=int:
        print("INVALID DATA")
    else:
        to_send=(data).to_bytes(1,'big')
        SerialPort.write(to_send)


while True:
    try:
        inicialbyte=int(input('>'))
        Send_Byte(inicialbyte)#.encode())

    except:
        print("INVALID DATA")
        END=input('end program? y/n >')
        if END == "y":
            exit()
    else: pass  
    
    inicialbyte=None
    
