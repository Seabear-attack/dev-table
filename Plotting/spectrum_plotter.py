# Plots every spectrum in a user-selected folder. Works for the Yokogawa spectrometer.
import matplotlib.pyplot as plt
from utils.spectrometerdata import OSAData, readFromFiles
from pathlib import Path
import numpy as np
from scipy.signal import lfilter
import re

if __name__ == "__main__":
    directorypath = Path(
        r'/home/mike/Documents/Data/2-8-24 OPA Power')
    raw_data, filenames = readFromFiles(directorypath, skip_header=1, pattern=r'[0-9]*.csv')
    labels = []
    for filename in filenames:
        match = re.match(r"\d*_\d*", filename.name)
        labels.append(f'{match[0]} $\mu$m')
    #labels = (r'25.2 $\mu$m', r'25.5 $\mu$m', r'25.8 $\mu$m', r'26.1 $\mu$m', r'26.4 $\mu$m', r'26.75 $\mu$m'
    #          , r'27.1 $\mu$m', r'27.8 $\mu$m', r'27.45 $\mu$m', r'27.91 $\mu$m', r'28.15 $\mu$m', r'28.28 $\mu$m', 
    #          r'28.67 $\mu$m', r'29.08 $\mu$m', r'29.52 $\mu$m', r'29.98 $\mu$m', r'30.49 $\mu$m')
              
              
              
              
    powers_mW = [1 for i in labels]

    n = 3 # the larger n is, the smoother curve will be
    b = [1.0 / n] * n
    a = 1
    #processed_data = [np.array([dat[:,0], lfilter(b, a, dat[:,1])]) for dat in raw_data]
    for i, dat in enumerate(raw_data):
        if np.max(dat[:,1]) < 1000:
            dat[:,1] = np.pow(2, dat[:,1])
        np.nan_to_num(dat, copy=False)
        dat[:,1] = lfilter(b,a,dat[:,1]) 
        dat[:,1] = dat[:,1] - dat[20,1]

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