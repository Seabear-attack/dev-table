import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
from numpy.fft import rfft, rfftfreq, irfft
from copy import deepcopy

igm_filepath = Path('/home/mike/Documents/Boulder_PhD/Data/2-6-2026/blue_igm.csv')

igm_df = pd.read_csv(igm_filepath, header=11)
igm_time_axis = igm_df["Second"]
igm_time = igm_df['Value']
npts = len(igm_time_axis)

# Time filter
# igm_time[(igm_time_axis < -.00012) | (igm_time_axis > .00007)] = 0

plt.figure()
plt.title('Time Domain IGM')
plt.plot(igm_time_axis, igm_time)
plt.xlabel('Time (s)')
igm_freq = rfft(igm_time)
igm_freq_axis = rfftfreq(npts, (igm_time_axis[1] - igm_time_axis[0]))

plt.figure()
plt.title('Freq Domain IGM')
plt.xlabel('RF Frequency (Hz)')
plt.plot(igm_freq_axis, igm_freq)
plt.xlim(0, 1.5e7)

igm_freq_no_2h = deepcopy(igm_freq) 
igm_freq_no_2h[(igm_freq_axis>3e6) & (igm_freq_axis < 5e6)]=0

plt.figure()
plt.title('Freq Domain IGM (Filtered)')
plt.xlabel('RF Frequency (Hz)')
plt.plot(igm_freq_axis, igm_freq_no_2h)
plt.xlim(0, 1.5e7)

igm_time_no_2h = irfft(igm_freq_no_2h, npts)
plt.figure()
plt.title('Time Domain IGM (Filtered)')
plt.xlabel('Time (s)')
plt.plot(igm_time_axis, igm_time_no_2h)

plt.show()

