"""
EXEMPLO DE ROTINA PARA REALIZAR LEITURAS CONSTANTES DO TORQUIMETRO
COM LOW_PASS FILTER
"""

#inicializing serial port
import time
import serial
import serial.tools.list_ports
ports = list(serial.tools.list_ports.comports())
print(ports)
print("connected to: ",ports[0][0])
port = ports[0][0] 
time.sleep(1)
########################

from LCTSfunctions import *

SensorTorque = Torquimeter(Port=port, Baudrate = 230400, Timeout=0.003, Tm_max = 100, Rpm_max=30000) 
Ts = 1 # (milliseconds) tempo entre mensagens max Sample rate: fs = 10kHz ou Ts = 0.001 s


import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from matplotlib.animation import FuncAnimation

# Filter parameters
fs = 1/Ts*10e-3  # Sampling frequency 10khz
cutoff_freq = 0.05*fs  # Cutoff frequency
order = 4  # Filter order

# Design the Butterworth filter
b, a = signal.butter(order, cutoff_freq / (0.5 * fs), btype='low', analog=False)

# Data storage for plotting (sliding window)
max_points = 500
unfiltered_data = []
filtered_data = []
time_points = []
current_time = 0

# Setup plot
fig, ax = plt.subplots()
line_unfiltered, = ax.plot([], [], label='Unfiltered')
line_filtered, = ax.plot([], [], label='Filtered')
ax.set_xlim(0, max_points)
ax.set_ylim(-2, 2) # Initial y-limits, will adjust dynamically
ax.legend()
ax.set_xlabel("Time Point (Relative)")
ax.set_ylabel("Amplitude")
ax.set_title("Real-time Filtered vs. Unfiltered Signal")

def update(frame):
    global current_time

    # new data point
    new_data_point = SensorTorque.ReadRaw()[2]
    
    unfiltered_data.append(new_data_point)
    time_points.append(current_time)

    # Apply filter to the entire current unfiltered_data
    current_filtered_signal = signal.lfilter(b, a, unfiltered_data)
    filtered_data.append(current_filtered_signal[-1]) # Only append the latest filtered value

    # Implement sliding window
    if len(unfiltered_data) > max_points:
        unfiltered_data.pop(0)
        filtered_data.pop(0)
        time_points.pop(0)

    # Update plot data
    line_unfiltered.set_data(range(len(unfiltered_data)), unfiltered_data)
    line_filtered.set_data(range(len(filtered_data)), filtered_data)

    ax.set_ylim(-5,5)
    
    current_time += 1

    return line_unfiltered, line_filtered

ani = FuncAnimation(fig, update, interval=Ts, blit=True) # interval in ms
plt.show()