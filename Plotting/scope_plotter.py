# Plots every scope lineout in user-selected folder. Works for Tektronix scopes
from pathlib import Path
import matplotlib.pyplot as plt
from plottools.spectrometerdata import readFromFiles
import numpy as np

if __name__ == "__main__":
    save_fig = False
    directorypath = Path(r'/home/mike/Documents/Boulder_PhD/Data/9-3-2025/optimized')
    data, names = readFromFiles(directorypath,skip_header=12)
    labels = ['Single Shot Interferogram']
    pad_factor = 6 
    sample_interval = data[0][1,0] - data[0][0,0]

    # Create a figure and axis object using matplotlib
    fig, ax = plt.subplots()
    fig2, ax2 = plt.subplots()

    for i, datum in enumerate(data):
        ax.plot(datum[:,0], datum[:,1],  label=labels[i], alpha=.7)
        fftsize = len(datum[:,1]) * 2 ** pad_factor
        fft = np.abs(np.fft.fftshift(np.fft.fft(datum[:,1], n = fftsize)))**2
        freqs = np.fft.fftshift(np.fft.fftfreq(fftsize,d=sample_interval))
        ax2.plot(freqs, fft, label='Single Shot Spectrum', color='tab:orange',alpha=.8)
    # Add axis labels and a legend
    ax.set_xlabel('Time [s]')
    ax.set_ylabel('Voltage [V]')
    ax.grid()
    ax.legend()

    ax2.set_xlim(-1e5, 50e6)
    ax2.set_ylim(1e5, 1e9)
    ax2.grid()
    ax2.legend()
    ax2.set_yscale('log')
    ax2.set_xlabel("Fourier Frequency (Hz)")
    ax2.set_ylabel("Spectral Power (arb.)")
    # Display the plot
    np.fft.fft(data)
    fig.savefig(directorypath/'interferogram.svg')
    fig2.savefig(directorypath/'spectrum.svg')
    plt.show()
