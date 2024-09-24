"""
code for reading all the readable data comming from the port
"""

from config import *


def read_from():
    data = SerialPort.readline()
    if data != b'':
            print(data)

while True:
    read_from()