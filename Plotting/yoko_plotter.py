from plottools_allisonlab.spectrometerdata import OSAData, readFromFiles
import matplotlib.pyplot as plt
from pathlib import Path

directorypath = Path(r"C:/Users/Splinter/OneDrive - UCB-O365/Data/1-3-25 Waveplate-HNLF angle/HNLF spectra")
raw_data, names = readFromFiles(directorypath, pattern='*.CSV', skip_header=39)
print(raw_data)
labels = [name.name for name in names]

powers_mW = [1 for i in names]

data = [OSAData(dat, ('nm', 'dBm/nm'), labels[i], powers_mW[i]) for i, dat in enumerate(raw_data)]

fig, axs = plt.subplots(1,1)

for datum in data:
    datum.y_axis_units = 'dBm/nm'
    axs.plot(datum.x_axis_data, datum.y_axis_data, label=datum.label)
    # axs.plot(datum.x_axis_data, datum.y_axis_data)

axs.set_xlabel('Wavelength (nm)')
axs.set_ylabel(f'Spectral Power ({data[0].y_axis_units})')
axs.legend()
axs.grid()

plt.tight_layout()
plt.show()