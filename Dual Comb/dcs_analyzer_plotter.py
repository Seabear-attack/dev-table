import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
from numpy.fft import rfft, rfftfreq, irfft
from copy import deepcopy
import numpy as np

cepstral_filepath = Path('/home/mike/Documents/Boulder_PhD/Data/3-25-2026/cepstral_Rb.csv')
cepstral_df = pd.read_csv(cepstral_filepath)
spectrum = cepstral_df[' Real Spectrum']
freq = cepstral_df['Optical Axis (Hz)']

rb85_1_1_com = 710.96057993e12 
rb87_1_1_com = 710.96069031e12

rb85_1_3_com = 713.284114994e12
rb87_1_3_com = 713.284240050e12

rb85_1_1_lines = rb85_1_1_com + 1e6 * np.array([1770.84, 1770.84-3035.73])
rb85_1_3_lines = rb85_1_3_com + 1e6 *np.array([1770.84, 1770.84-3035.73])

rb87_1_1_lines = rb87_1_1_com + 1e6 *np.array([4271.68, 4271.68-6834.68])
rb87_1_3_lines = rb87_1_3_com + 1e6 *np.array([4271.68, 4271.68-6834.68])

f, (ax1, ax2) = plt.subplots(1,2,sharey=True)
ax1.plot(freq, spectrum)
ax1.vlines(rb85_1_3_lines, 0, 2, colors='k')
ax1.vlines(rb87_1_3_lines, 0, 2, colors='k')
ax1.set_xlim(713.27e12, 713.30e12)
ax1.set_ylim(0,2)
ax1.set_xlabel('Frequency (Hz)')
ax1.set_ylabel('Transmission')

ax2.plot(freq, spectrum)
ax2.vlines(rb85_1_1_lines, 0, 2, colors='k')
ax2.vlines(rb87_1_1_lines, 0, 2, colors='k')
ax2.set_xlim(710.94e12, 710.98e12)
ax2.set_ylim(0,2)
ax2.set_xlabel('Frequency (Hz)')
plt.tight_layout()
plt.show()