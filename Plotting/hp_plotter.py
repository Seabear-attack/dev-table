from pathlib import Path
from plottools.spectrometerdata import readFromFiles, OSAData
import numpy as np
import re
import matplotlib.pyplot as plt

# Config
data_directory = Path(r"Z:\Research Projects\UVDCS\Data\2025\HHG Spectra")
# Read files
data, labels = readFromFiles(data_directory, skip_header=1)

# Fix background issue
for datum in data:
    datum[datum[:,0]<250, 1] = 0

# Add experimental parameters
power_nw = [250, 450]
# labels = ["Leo","Mikey"]
labels = ["Comb 1","Comb 2"]

data = [OSAData(datum, 'mW', labels[i], power_nw[i]*1e-6,100) for i, datum in enumerate(data)]

# Set up plot
f, ax = plt.subplots(1,1, figsize=(4,3))
for datum in data:
    datum.y_axis_units = "mW/nm"
    ax.plot(datum.x_axis_data, datum.y_axis_data * 1e-3, label=datum.label)

ax.set_ylabel(f"Spectral Power (W/nm)")
ax.set_xlabel("Wavelength (nm)")
# ax.set_ylim(-70,-25)
ax.set_xlim(250,400)
ax.grid()
ax.legend()
plt.savefig('hhg_spectra.svg', bbox_inches='tight')
# plt.show()