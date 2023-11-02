# Plots every scope lineout in user-selected folder. Works for Tektronix scopes
from utils.plotting_utils import directory_to_dataframes, get_scope_data, normalize_by_maximum
import matplotlib.pyplot as plt
from utils.spectrometerdata import RFSAData, readFromFiles
import numpy as np
from pathlib import Path

if __name__ == "__main__":
    save_fig = True
    filename = 'polarization_scope_traces.eps'
    savepath = Path(r'C:\Users\wahlm\Documents\School\Research\Allison\Papers\tunable-pump-seed')


    # Pyplot options
    fig, ax = plt.subplots(1, 2, figsize=(12, 8))
    title_text_size = 16
    axes_text_size = 14
    legend_text_size = 12

    # Begin plot of post-EDFA pulses
    directorypath = Path(r'C:\Users\wahlm\Documents\School\Research\Allison\Tunable Pump\Polarization Control\9-19-23 '
                         r'Pre, Post EDFA Pulses\post-EDFA\Tektronix Scope')
    plot_order = [0, 6, 2, 4, 3, 5, 1]
    offset = 1.2
    dfs = directory_to_dataframes(directorypath)
    labels = ('Background',
              r'$f_{rep}/4$ vertical',
              r'$f_{rep} vertical',
              r'f_{rep}/2 vertical',
              r'f_{rep}/2 horizontal',
              r'f_{rep}/4 horizontal',
              r'f_{rep} horizontal'
              )
    data = get_scope_data(dfs, labels)
    normalize_by_maximum(data, 'voltage_V')

    for i, tup in enumerate(sorted(data.items(), key=lambda x: plot_order[labels.index(x[0])])[3:]):
        ax[1].plot(tup[1]['time_s'], tup[1]['voltage_V'] - i * offset, label=tup[0])
    # Add axis labels and a legend
    ax[1].set_xlabel('Time (s)', fontsize=axes_text_size)
    ax[1].set_ylabel('Voltage (arb.)', fontsize=axes_text_size)
    # ax[1].legend(fontsize=legend_text_size)
    ax[1].set_title(f'Post-EDFA Pulses', fontsize=title_text_size)

    # Begin plot of pre-EDFA pulses
    directorypath = Path(r'C:\Users\wahlm\Documents\School\Research\Allison\Tunable Pump\Polarization Control\9-19-23 '
                         r'Pre, Post EDFA Pulses\pre-EDFA\Tektronix Scope')
    dfs = directory_to_dataframes(directorypath)
    labels = ('Background',
              r'$f_{rep}$ horizontal',
              r'$f_{rep}/2$ horizontal',
              r'$f_{rep}/4$ horizontal',
              r'$f_{rep}$ vertical',
              r'$f_{rep}/2$ vertical',
              r'$f_{rep}/4$ vertical'
              )
    plot_order = [0, 1, 3, 5, 2, 4, 6]

    data = get_scope_data(dfs, labels)
    normalize_by_maximum(data, 'voltage_V')

    for i, tup in enumerate(sorted(data.items(), key=lambda x: plot_order[labels.index(x[0])])[3:]):
        ax[0].plot(tup[1]['time_s'], tup[1]['voltage_V'] - i * offset, label=tup[0])
    # Add axis labels and a legend
    ax[0].set_xlabel('Time (s)', fontsize=axes_text_size)
    ax[0].set_ylabel('Voltage (arb.)', fontsize=axes_text_size)
    ax[0].legend(fontsize=legend_text_size)
    ax[0].set_title(f'Pre-EDFA Pulses', fontsize=title_text_size)
    # fig.canvas.manager.window.showMaximized()  # toggle fullscreen mode
    plt.tight_layout()
    if save_fig:
        fig.savefig(savepath / filename, dpi=300)

    plt.show()
