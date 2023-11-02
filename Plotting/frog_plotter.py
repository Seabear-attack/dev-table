import matplotlib.pyplot as plt
from utils import frogdata
from pathlib import Path
import re

if __name__ == "__main__":
    # Sample time delay and wavelength arrays
    frog_path = Path(r'C:\Users\wahlm\Documents\School\Research\Allison\Tunable Pump\Data for Papers\Tunable seed\FROGs vs. pulse pattern\Low rep rate')
    pattern = r'.*'
    cmap = 'rainbow'
    save_files = False
    frogs = frogdata.read_frog_directory(frog_path, pattern=pattern)
    frogs = sorted(frogs, key=lambda frog: len(re.findall(r'1', frog.label)))
    for i, frog in enumerate(frogs):
        # # Plot the FROG trace
        if i % 3 == 0:
            f = plt.figure(figsize=(10, 20))
        ax1 = f.add_subplot(3, 3, (3 * i) % 9 + 1)
        map = ax1.imshow(frog.trace, aspect='auto', extent=[min(frog.delays), max(frog.delays), min(frog.wavelengths),
                                                      max(frog.wavelengths)], cmap=cmap)
        ax1.set_ylim([760, 810])
        ax1.set_xlim([-1000, 750])
        plt.xlabel('Time Delay [fs]')
        plt.ylabel('Wavelength [nm]')
        plt.title(f'Measured, {frog.label}')
        plt.colorbar(map)

        # Plot the autocorrelation
        # ax2 = f.add_subplot(3, 3, (3 * i + 1) % 9 + 1, sharex=ax1)
        # ax2.plot(frog.delays, frog.autocorrelation())
        # plt.xlabel('Time Delay [fs]')
        # plt.ylabel('Intensity')
        # plt.title('Autocorrelation')

        # Plot the reconstructed trace

        ax2 = f.add_subplot(3, 3, (3 * i + 1) % 9 + 1, sharex=ax1)
        ax2.imshow(frog.trace_recon, aspect='auto', extent=[min(frog.delays), max(frog.delays), min(frog.wavelengths),
                                                      max(frog.wavelengths)], cmap=cmap)

        ax2.set_ylim([760, 810])
        ax2.set_xlim([-750, 750])
        plt.xlabel('Time Delay [fs]')
        plt.ylabel('Wavelength [nm]')
        plt.title(f'Reconstructed Trace, Error = {frog.frog_error: .3f}')


        # Plot the pulse
        ax3 = f.add_subplot(3, 3, (3 * i + 2) % 9 + 1, sharex=ax2)
        ax3.plot(frog.pulse_time, frog.pulse_intensity, label=f'FWHM: {frog.t_FWHM: 1.1f} fs')
        plt.xlabel('Time Delay [fs]')
        plt.ylabel('Intensity')
        plt.title('Reconstructed Pulse')
        plt.legend()
        f.canvas.manager.window.showMaximized() #toggle fullscreen mode
        plt.tight_layout()
        if save_files:
            plt.savefig(frog_path / frog.label, dpi=500)
        plt.show(block=False)
    plt.show()