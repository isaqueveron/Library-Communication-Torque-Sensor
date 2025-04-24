from LCTSfunctions import *

class RunReading:
    def __init__(self,MesurementChannel_0=0,MesurementChannel_1=0,CalibratedValCha_0=0,CalibratedValCha_1=0):
        self.data = []
        self.MesurementChannel_0 = 0
        self.MesurementChannel_1 = 0
        self.CalibratedValCha_0  = 0
        self.CalibratedValCha_1  = 0
        self.FullstrokeFlag      = 0

    def RunReading(self)->list:

        Tools.SendTelegram(Commands.ReadRaw()) 
        isReceiving = True
        while isReceiving: #loop for receiving
            try:code_received=Receive.read_from()
            except: code_received = None
            if code_received != None:
                try:data = Tools.TransforData(Receive.GetRaw(Receive.ReceiveMeasuring(code_received)))
                except:data = None
                if data != None: 
                    self.data = data
                    self.MesurementChannel_0 = data[0]
                    self.MesurementChannel_1 = data[1]
                    self.CalibratedValCha_0  = data[2] #TORQUE
                    self.CalibratedValCha_1  = data[3] #RPM
                    self.FullstrokeFlag      = data[4]
                else: pass
            else:
                break 

SensorTorque = RunReading() 
while True: 
    SensorTorque.RunReading()
    print(SensorTorque.CalibratedValCha_0)
