# Plots every spectrum in a user-selected folder. Works for the Yokogawa spectrometer.
import matplotlib.pyplot as plt
from utils.spectrometerdata import RFSAData, readFromFiles
import numpy as np
from pathlib import Path

if __name__ == "__main__":
    raw_data = readFromFiles(Path(r'C:\Users\wahlm\Documents\School\Research\Allison\Tunable Pump\Polarization '
                             r'Control\9-19-23 Pre, Post EDFA Pulses\Rigol RF Spectrum Analyzer'), skip_header=2)
    labels = ('Background',
              'f_rep vertical',
              'f_rep/2 vertical',
              'f_rep/4 vertical',
              'f_rep horizontal',
              'f_rep/2 horizontal',
              'f_rep/4 horizontal')

    data = [RFSAData(np.array([dat[:, 0], dat[:, 2]]).transpose(), ('Hz', 'dBm'), labels[i], frep_MHz=60.5) for i, dat in enumerate(raw_data)]
    plot_order = [0, 2, 4, 6,1 , 3, 5]
    fig, axs = plt.subplots()

    for i, datum in enumerate(sorted(data, key=lambda data: plot_order[labels.index(data.label)])):
        axs.plot(datum.x_axis_data, datum.y_axis_data - i * 25, label=datum.label)
    axs.set_xlim([0, 2.5e8])
    axs.set_xlabel(f'Frequency ({data[0].x_axis_units})')
    axs.set_ylabel(f'Spectral Power ({data[0].y_axis_units})')
    axs.legend()
    axs.set_title('Varying Input Pulse Pattern, Arbitrary 25 dB Offset')
    fig.canvas.manager.window.showMaximized()  # toggle fullscreen mode
    plt.tight_layout()
    plt.show()
