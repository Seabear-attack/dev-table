# Plots every scope lineout in user-selected folder. Works for Tektronix scopes
from pathlib import Path
import matplotlib.pyplot as plt
from utils.plotting_utils import directory_to_dataframes, get_scope_data, normalize_by_maximum

if __name__ == "__main__":
    save_fig = False
    filename = 'frep_over_4_scope_trace'
    directorypath = Path(r'C:\Users\wahlm\Documents\School\Research\Allison\Tunable Pump\Polarization Control\9-19-23 '
                         r'Pre, Post EDFA Pulses\post-EDFA\Tektronix Scope')
    dfs = directory_to_dataframes(directorypath)
    labels = ('Background',
              'f_rep/4 vertical',
              'f_rep vertical',
              'f_rep/2 vertical',
              'f_rep/2 horizontal',
              'f_rep horizontal',
              'f_rep/4 horizontal'
              )
    data = get_scope_data(dfs, labels)
    normalize_by_maximum(data, 'voltage_V')
    plot_order = [0, 1, 3, 5, 2, 4, 6]

    # Create a figure and axis object using matplotlib
    fig, ax = plt.subplots(figsize=(12, 8))

    for i, tup in enumerate(sorted(data.items(), key=lambda x: plot_order[labels.index(x[0])])):
        if i > 4:
            ax.plot(tup[1]['time_s'], tup[1]['voltage_V'] - i * 1.1, label=tup[0])
    # Add axis labels and a legend
    ax.set_xlabel('Time [s]')
    ax.set_ylabel('Voltage [V]')
    ax.legend()
    # ax.set_title('Photodiode output')
    ax.set_title('Photodiode Voltage of Polarized Pulses')
    # Display the plot
    if save_fig:
        fig.savefig(directorypath.parent / filename, dpi=300)
    plt.show()
