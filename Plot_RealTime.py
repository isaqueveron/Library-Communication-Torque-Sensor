"""
EXEMPLO DE ROTINA PARA REALIZAR LEITURAS CONSTANTES DO TORQUIMETRO
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


import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from collections import deque

# --- Configuration ---
MAX_X_VALUES = 500  # Number of x-values to display
UPDATE_INTERVAL_MS = Ts  # tempo entre mensagens max Sample rate: f = 10kHz ou T = 0.001 s

# --- Initialize data structures ---
# Deque to hold the last MAX_X_VALUES y-values
y_data = deque(np.zeros(MAX_X_VALUES), maxlen=MAX_X_VALUES)
# X-values are fixed for a scrolling plot
x_data = np.arange(0, MAX_X_VALUES)
x2_data = np.arange(0, MAX_X_VALUES)

# --- Set up the plot ---
fig, ax = plt.subplots()
line, = ax.plot(x_data, y_data) # Initial plot line

ax.set_ylim(-5, 5)  # Set appropriate y-axis limits
ax.set_xlim(0, MAX_X_VALUES - 1) # Set appropriate x-axis limits
ax.set_title("Real-Time Plot (Last 100 Values)")
ax.set_xlabel("Index")
ax.set_ylabel("Value")

# --- Animation function ---
def animate(i):
    """
    This function is called repeatedly by FuncAnimation to update the plot.
    """
    # Generate a new random data point (replace with your actual data source)
    new_value = SensorTorque.ReadRaw()[2]

    # Add the new value to the deque, automatically dropping the oldest
    y_data.append(new_value)

    # Update the line data
    line.set_ydata(y_data)

    return line, # Return the artist(s) that were modified (important for blitting)

# --- Create the animation ---
ani = animation.FuncAnimation(
    fig,
    animate,
    frames=None,  # Set to None for continuous animation
    interval=UPDATE_INTERVAL_MS,
    blit=True,     # Optimize rendering by only redrawing changed elements
    cache_frame_data=False # Often good to set to False for real-time to avoid memory issues
)

plt.show()

