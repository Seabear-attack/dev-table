# Plots every spectrum in a user-selected folder. Works for the Yokogawa spectrometer.
import matplotlib.pyplot as plt
from utils.spectrometerdata import OSAData, readFromFiles
from pathlib import Path
import numpy as np
from scipy.signal import lfilter

if __name__ == "__main__":
    directorypath = Path(
        r'/home/mike/Documents/Data/1-23-24 SHG vs. rep rate')
    raw_data = readFromFiles(directorypath, skip_header=1, pattern='spectrum*.csv')
    labels = (r'27.91 $\mu$m', r'29.08 $\mu$m', r'30.49 $\mu$m')
              
    powers_mW = [1, 1, 1]

    n = 15  # the larger n is, the smoother curve will be
    b = [1.0 / n] * n
    a = 1
    #processed_data = [np.array([dat[:,0], lfilter(b, a, dat[:,1])]) for dat in raw_data]
    for dat in raw_data:
        dat[:,1] = lfilter(b,a,dat[:,1]) - np.median(dat[:,1])

    data = [OSAData(dat[:,:2], ('nm', 'mW'), labels[i], powers_mW[i], frep_MHz=60.5) for i, dat in enumerate(raw_data)]

    fig, axs = plt.subplots()

    for datum in data:
        datum.y_axis_units = 'mW'
        axs.plot(datum._x_axis_data, datum.y_axis_data, label=datum.label)
    axs.set_xlabel('Wavelength (nm)')
    axs.set_ylabel(f'Spectral Power (arb.)')
    axs.legend()

    plt.show()
    plt.tight_layout()
    '''
    frep_frac = [1,1, 1/2, 1/5, 1/15, 1/20, 0]
    is_background = (False, False, False, False, True)   
    powers_mW = [1,191, 33, 15.37, 13.9]

    data = [OSAData(dat, ('nm', 'dBm/nm'), labels[i], powers_mW[i], frep_MHz=frep_frac[i] * 60.56, is_background=is_background[i]) for i, dat in enumerate(raw_data)]
    data = data[:-1]

    for datum in data[1,0:1]:
        datum.y_axis_units = 'dBm/nm'
        axs[1,0].plot(datum.x_axis_data, datum.y_axis_data, label=datum.label)
    axs[1,0].set_xlabel('Wavelength (nm)')
    axs[1,0].set_ylabel(f'Spectral Power ({data[0].y_axis_units})')
    # axs[1,0, 1].set_title('NDHNLF Spectrum')
    axs[1,0].legend()
    
    for datum in data[1,0:1]:
        datum.y_axis_units = 'mW/nm'
        axs[1,1].plot(datum.x_axis_data, datum.y_axis_data, label=datum.label)
    axs[1,1].set_xlabel('Wavelength (nm)')
    axs[1,1].set_ylabel(f'Spectral Power ({data[1,0].y_axis_units})')
    '''