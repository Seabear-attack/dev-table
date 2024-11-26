import numpy as np
import matplotlib.pyplot as plt
import pynlo
from pathlib import Path
from plottools.spectrometerdata import OSAData, readFromFiles
from scipy.constants import speed_of_light as C_MKS
from scipy.signal import peak_widths, find_peaks
import pandas as pd

######## Functions and Constants ##############

def dB(num):
    return 10 * np.log10(np.abs(num) ** 2)

def expand_freq_axis(aw, factor_log2):
    num_new_pts = len(aw)*(2**factor_log2 - 1)
    pts_before = int(np.floor(num_new_pts * 0.5))
    pts_after  = num_new_pts - pts_before
    return np.hstack( (np.zeros(pts_before,), 
                            aw, 
                            np.zeros(pts_after,)) )  

# Fundamental constants
C_NM_PS = C_MKS * 1e-3


##### Read in a spectrum for comparison #################

directorypath = Path('/home/mike/Documents/Boulder_PhD/Data/11-25-24 Partially Compressed HNLF Pulse')
raw_data = pd.read_csv(directorypath / 'spectrum.CSV', skiprows=44, header = None).to_numpy()
labels = ('5.5 W, 7cm PM 1550 + 4 cm ND-HNLF')
powers_mW = [2.5e3]
rep_rate_MHz = 100
osa_spectrum = OSAData(raw_data, ('nm', 'dBm'), labels, powers_mW[0], frep_MHz=rep_rate_MHz) 

plt.plot(osa_spectrum.x_axis_data, osa_spectrum.y_axis_data, label = osa_spectrum.label)
plt.xlabel('Wavelength (nm)')
plt.ylabel('PSD (dBm/nm)')
plt.legend()
plt.grid()
plt.savefig(directorypath / 'spectrum.png', dpi=300)
plt.show()

##### Take Fourier Transform and find peak width ##########
osa_spectrum.y_axis_units = 'mW'
osa_spectrum.x_axis_units = 'THz'
# freq_THz = osa_spectrum.x_axis_data
# data = osa_spectrum.y_axis_data
pad_factor = 6

# freq_THz_padded = np.linspace(freq_TH)
# osa_spectrum.set_x_window(0, 1500, 'THz', .5)

# plt.plot(osa_spectrum.x_axis_data, osa_spectrum.y_axis_data, label = osa_spectrum.label)
# plt.xlabel('Freq (THz)')
# plt.ylabel('PSD (dBm/nm)')
# plt.show()
# inp_pow_t = np.pow(np.abs(np.fft.fft(np.sqrt(osa_spectrum.y_axis_data))),2)
inp_pow_t = np.pow(np.abs(np.fft.fftshift(np.fft.fft(np.sqrt(osa_spectrum.y_axis_data), n=len(osa_spectrum.y_axis_data) * 2 **pad_factor))),2)

# Create time axis
df_THz = osa_spectrum.x_axis_data[1] - osa_spectrum.x_axis_data[0]
time_axis_ps = np.fft.fftshift(np.fft.fftfreq(len(inp_pow_t), df_THz))
dt_ps = time_axis_ps[1] - time_axis_ps[0]

peak, _ = find_peaks(inp_pow_t, np.max(inp_pow_t))
inp_fwhm_samples, _, _, _ = peak_widths(inp_pow_t, peak, rel_height=.5)
inp_fwhm_fs = 1e3 * dt_ps * inp_fwhm_samples[0]

plt.plot(time_axis_ps, inp_pow_t, label=f'FWHM: {inp_fwhm_fs: .1f} fs')
# plt.plot(time_axis_ps, inp_pow_t )
plt.xlabel('Time (ps)')
plt.ylabel('Intensity (a.u.)')
plt.xlim(-1, 1)
plt.legend()
plt.grid()
# plt.plot(time_axis_ps, inp_pow_t)
# plt.plot(inp_pow_t)
plt.savefig(directorypath /'spectrum_transform_limit.png', dpi=300)
plt.show()