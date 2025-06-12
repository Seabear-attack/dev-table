from json import load
from pathlib import Path
from plottools.spectrometerdata import readFromFiles
import numpy as np
import re
import matplotlib.pyplot as plt

# Configure data directory 
data_directory_1 = Path(r"Z:/Research Projects/UVDCS\Data/6-6-2025/14h-16m_spectrum_time_series")
data_directory_2 = Path(r"Z:/Research Projects/UVDCS\Data/6-6-2025/15h-25m_spectrum_time_series")


# Load config
config_file = data_directory_1 / "configs.json"
with open(config_file,'r') as file:
    configs = load(file)

# Load data
data, labels = readFromFiles(data_directory_1, skip_header=0)
data = np.array(data)

data2, labels2 = readFromFiles(data_directory_2, skip_header=0)
data2 = np.array(data)

data = np.append(data, data2, axis=0)
labels += labels2

# Take subset of data
divide_by = 10
data = data[::divide_by]
labels = labels[::divide_by]

# Parse filenames to extract timestamps
regex = r'(\d+)h-(\d+)m-(\d+)s\.csv'
timestamp_list = []
for filename in labels:
    match = re.search(regex, str(filename))
    if match:
        hours, minutes, seconds = map(int, match.groups())
        timestamp_list.append(f"{hours}:{minutes}:{seconds}")

# Set up plot
f, ax = plt.subplots(1,1)

for i, spectrum in enumerate(data):
    ax.plot(spectrum[0], spectrum[1], label=timestamp_list[i])

ax.set_ylabel(f"Spectral Power (log arb.)")
ax.set_xlabel("Wavelength (nm)")
ax.set_ylim(-70,-25)
ax.grid()
ax.legend()
plt.show()