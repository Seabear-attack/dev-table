# Plots every spectrum in a user-selected folder. Works for the Yokogawa spectrometer.
import matplotlib.pyplot as plt
from utils.spectrometerdata import OSAData, readFromFiles
from pathlib import Path

if __name__ == "__main__":
    directorypath = Path(
        r'C:\Users\wahlm\Documents\School\Research\Allison\Tunable Pump\Pulse Optimization and Spectrum Generation\12-4-23 New NDHNLF Spectra\Current variation\1.35V')
    raw_data = readFromFiles(directorypath)
    labels = ('3 A', '3.25 A', '3.5 A', '3.75 A', '4 A')
              
    powers_mW = [0,183.5,
187.5,
193.5,
204.6,
213.5]

    data = [OSAData(dat, ('nm', 'dBm/nm'), labels[i], powers_mW[i], frep_MHz=60.5) for i, dat in enumerate(raw_data)]

    fig, axs = plt.subplots(2, 2, sharex=True)

    for datum in data:
        datum.y_axis_units = 'dBm/nm'
        axs[0,0].plot(datum._x_axis_data, datum.y_axis_data, label=datum.label)
    axs[0,0].set_xlabel('Wavelength (nm)')
    axs[0,0].set_ylabel(f'Spectral Power ({data[0].y_axis_units})')
    axs[0,0].legend()
    axs[0,0].set_title('1.35 V Offset')

    for datum in data:
        datum.y_axis_units = 'mW/nm'
        axs[1,0].plot(datum._x_axis_data, datum.y_axis_data, label=datum.label)
    axs[1,0].set_xlabel('Wavelength (nm)')
    axs[1,0].set_ylabel(f'Spectral Power ({data[0].y_axis_units})')

    directorypath = Path(r'C:\Users\wahlm\Documents\School\Research\Allison\Tunable Pump\Pulse Optimization and Spectrum Generation\12-4-23 New NDHNLF Spectra\Current variation\-2.3V')
    raw_data = readFromFiles(directorypath)

    labels = ('3 A', '3.25 A', '3.5 A', '3.75 A', '4 A')
    powers_mW = (186.5,
194.5,
206.5,
216.7,
217.6)
    data = [OSAData(dat, ('nm', 'dBm/nm'), labels[i], powers_mW[i], frep_MHz=60.5) for i, dat in enumerate(raw_data)]
    for datum in data:
        datum.y_axis_units = 'dBm/nm'
        axs[0,1].plot(datum._x_axis_data, datum.y_axis_data, label=datum.label)
    axs[0,1].set_xlabel('Wavelength (nm)')
    axs[0,1].set_ylabel(f'Spectral Power ({data[0].y_axis_units})')
    axs[0,1].legend()
    axs[0,1].set_title('-2.3 V Offset')

    for datum in data:
        datum.y_axis_units = 'mW/nm'
        axs[1,1].plot(datum._x_axis_data, datum.y_axis_data, label=datum.label)
    axs[1,1].set_xlabel('Wavelength (nm)')
    axs[1,1].set_ylabel(f'Spectral Power ({data[0].y_axis_units})')

    for ax in axs.flatten():
        ax.set_xlim([1000, 2500])
    axs[0,0].set_ylim([-50, 15])
    axs[0,1].set_ylim([-50, 15])
    axs[1,0].set_ylim([-.05, .5])
    axs[1,1].set_ylim([-.05, .5])
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