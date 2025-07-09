from pathlib import Path
from plottools.spectrometerdata import readFromFiles
import numpy as np
import re
import matplotlib.pyplot as plt
from pandas import to_datetime
from datetime import datetime, timedelta

# Config
data_directory = Path(r"Z:\Research Projects\UVDCS\Data\6-11-2025\mikey_uv_time_series")
interval = timedelta(minutes=1)
start_time = to_datetime("14:48")
regex = r'Spectrum_(\d+)\.csv'
divide_by = 20

# Read files
data, labels = readFromFiles(data_directory, skip_header=1)
data = np.array(data)

data = data[::divide_by]
labels = labels[::divide_by]

timestamp_list= []

for filename in labels:
    match = re.search(regex, str(filename.name))
    if match:
        number = int(match.group(1))
        timestamp = start_time + (number - 1) * interval
        timestamp_list.append(timestamp)
        
# Set up plot
f, ax = plt.subplots(1,1)

for i, spectrum in enumerate(data):
    # print(spectrum)
    ax.plot(spectrum[:,0], spectrum[:,1], label=timestamp_list[i])

ax.set_ylabel(f"Spectral Power (lin arb.)")
ax.set_xlabel("Wavelength (nm)")
# ax.set_ylim(-70,-25)
ax.grid()
ax.legend()
plt.show()