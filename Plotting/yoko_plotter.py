from plottools.spectrometerdata import OSAData, readFromFiles
import matplotlib.pyplot as plt
from pathlib import Path

directorypath = Path(r"/home/mike/Documents/Boulder_PhD/Data/9-3-2025/optimized")
raw_data, names = readFromFiles(directorypath, pattern='*.CSV', skip_header=39)
print(names)
print(raw_data)
labels = ['Leo', 'Mikey']

fig, axs = plt.subplots(1,1)

# for datum in data:
for i, datum in enumerate(raw_data):
    # datum.y_axis_units = 'dBm/nm'
    axs.plot(datum[:,0], datum[:,1], label=labels[i], alpha=.5)
    # axs.plot(datum.x_axis_data, datum.y_axis_data)

axs.set_xlabel('Wavelength (nm)')
axs.set_ylabel(f'Spectral Power (dBm/nm)')
axs.set_ylim(-90,-50)
axs.legend()
axs.grid()

plt.tight_layout()
plt.savefig(directorypath/"plot.svg")
plt.show()