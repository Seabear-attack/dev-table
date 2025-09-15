from pathlib import Path
from plottools.spectrometerdata import readFromFiles, OSAData
import numpy as np
import re
import matplotlib.pyplot as plt

# Config
data_directory = Path(r"/home/mike/Documents/Boulder_PhD/Data/7-23-25 Spectra/")
# Read files
data, labels = readFromFiles(data_directory, skip_header=1)

# Fix background issue
for datum in data:
    datum[datum[:,0]<250, 1] = 0

# Add experimental parameters
power_nw = [250, 450]
labels = ["Mikey","Leo"]
data = [OSAData(datum, 'mW', labels[i], power_nw[i]*1e-6,100) for i, datum in enumerate(data)]

# Set up plot
f, ax = plt.subplots(1,1)
for datum in data:
    datum.y_axis_units = "mW/nm"
    ax.plot(datum.x_axis_data, datum.y_axis_data * 1e-3, label=datum.label)

ax.set_ylabel(f"Spectral Power (W/nm)")
ax.set_xlabel("Wavelength (nm)")
# ax.set_ylim(-70,-25)
ax.grid()
ax.legend()
plt.show()