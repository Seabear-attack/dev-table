from plottools.spectrometerdata import OSAData, readFromFiles
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.constants import speed_of_light as c

directorypath = Path(r"/home/mike/Shares/Shredder/Research Projects/UVDCS/Data/4-4-2026/OSA Spectra/")
raw_data, paths = readFromFiles(directorypath, pattern='*.CSV', skip_header=39)
print(raw_data)


labels = [path.name for path in paths]
print(labels)
integrated_power_W = 4.5e-6
osa_data = []

for i, datum in enumerate(raw_data):
    osa_data.append(OSAData(datum, ['nm', 'dBm'],labels[i], integrated_power_W*1e3))

fig, axs = plt.subplots(1,1)

for i, datum in enumerate(raw_data):
    plt.plot(c/(1e-9*datum[:,0])*1e-12, datum[:,1], label=labels[i])


# axs.set_xlabel(f'Wavelength (nm)')
axs.set_xlabel(f'Frequency (THz)')
axs.set_ylabel(f'Spectral Power (dBm/nm)')
plt.xlim(560, 600)
plt.ylim(-100, -30)
plt.tight_layout()
plt.savefig(directorypath/"plot_zoomed.png")
plt.legend()
plt.show()
# for datum in data:
# for i, datum in enumerate(osa_data):
    # datum.y_axis_units = 'dBm/nm'
    # wl_axis=datum.x_axis_data
    # datum.y_axis_units = 'mW/nm'
    # axs.plot(datum.x_axis_data, 1e6 * datum.y_axis_data)
    # wl_PSD=datum.y_axis_data
    # datum.x_axis_units = 'THz'
    # datum.y_axis_units = 'mW/THz'
    # freq_axis=datum.x_axis_data
    # freq_PSD=datum.y_axis_data
    # datum.y_axis_units = 'mW/THz'
    # axs.plot(datum[:,0], datum[:,1], label=labels[i], alpha=.5)
    # axs.plot(datum.x_axis_data, datum.y_axis_data)
    # export_info = pd.DataFrame({'Wavelength (nm)':wl_axis,
                                # 'Wavelength PSD (mW/nm)': wl_PSD,
                                # 'Frequency (THz)': np.flip(freq_axis),
                                # 'Frequency PSD (mW/THz)':np.flip(freq_PSD)})
    # export_info.to_csv(f'comb{i+1}_PSD.csv', index=False)
    # print(export_info)
    # np.savetxt(f'comb{i}.txt', delimiter=',', [wl_axis,wl_PSD, freq_axis, freq_PSD],header = 'Wavelength (nm), Wavelength PSD (mW/nm), Frequency (THz), Frequency PSD (mW/THz)')

# axs.set_xlabel(f'Frequency ({osa_data[0].x_axis_units})')
# axs.set_ylabel(f'Spectral Power ({osa_data[0].y_axis_units})')
# axs.legend()
# axs.grid()
# 
# plt.tight_layout()
# plt.savefig(directorypath/"plot.svg")
# plt.legend()
# plt.show()