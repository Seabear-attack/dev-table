# Plots every spectrum in a user-selected folder. Works for the Yokogawa spectrometer.
import matplotlib.pyplot as plt
from utils.spectrometerdata import OSAData, readFromFiles
from pathlib import Path

if __name__ == "__main__":
    directorypath = Path('../../Spectra/1-9-24 OPA spectra')
        
    raw_data = readFromFiles(directorypath, pattern=r'*10W*')
    fig, axs = plt.subplots()
    labels = ['p-pol', 's-pol']
    for i, datum in enumerate(raw_data):
        axs.plot(datum[:,0], datum[:,1], label=labels[i])
    axs.set_xlabel('Wavelength (nm)')
    axs.set_ylabel(f'Spectral Power (arb.)')
    plt.title('3 W pump')
    axs.legend()


    plt.show()
    plt.tight_layout()

