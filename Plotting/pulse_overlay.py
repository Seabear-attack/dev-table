import matplotlib.pyplot as plt
from utils import frogdata
from pathlib import Path
import re

if __name__ == "__main__":
    # Sample time delay and wavelength arrays
    frog_path = Path(
        r'C:\Users\wahlm\Documents\School\Research\Allison\Tunable Pump\Data for Papers\Tunable seed\FROGs vs. pulse pattern\Low rep rate')
    savepath = frog_path.parent / 'rep_rate_vs_pulse_norm_axis.eps'
    pattern = r'.*'
    cmap = 'rainbow'
    sort = lambda frog: 0 if re.search(r'\d+', frog.label) is None else int(re.search(r'\d+', frog.label)[0])
    label = lambda name: r'$f_{rep}$' if re.search(r'\d+', frog.label) is None else r'$f_{rep}/$' + (re.search(r'\d+', name)[0])
    save_files = False
    frogs = frogdata.read_frog_directory(frog_path, pattern=pattern)
    frogs = sorted(frogs, key=sort)
    f, ax = plt.subplots(figsize=(6, 8))
    for i, frog in enumerate(frogs):
        # Fix the phase signs to all be the same (pulse maximum on the left of the plot)
        if frog.pulse_time[frog.pulse_intensity == max(frog.pulse_intensity)] > frog.pulse_time[
                                                                    int(len(frog.pulse_time) / 2)]:
            frog.pulse_intensity = frog.pulse_intensity[::-1]

        # Have all the maxima overlap one another in time
        frog.pulse_time = frog.pulse_time - (frog.pulse_time[frog.pulse_intensity == max(frog.pulse_intensity)] -
                                             frogs[0].pulse_time[frogs[0].pulse_intensity == max(frogs[0].pulse_intensity)])

        # Plot the pulse
        ax.plot(frog.pulse_time, frog.pulse_intensity, label=f'{label(frog.label)}: FWHM={frog.t_FWHM: .1f} fs')
        plt.xlabel('Time (fs)')
        plt.ylabel('Intensity (arb.)')
        plt.title('Reconstructed Pulses')
        plt.legend()
        plt.xlim([-500, 200])
        f.canvas.manager.window.showMaximized()  # toggle fullscreen mode
        plt.tight_layout()
    if save_files:
        plt.savefig(savepath, dpi=500)
    plt.show()
