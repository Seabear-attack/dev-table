from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.constants import elementary_charge as q

# Define file paths
datadir = Path(
    '/home/mike/Shares/Shredder/Research Projects/UVDCS/Data/6-15-2026/Noise Scaling RFSA')
datafile = datadir / 'NoiseScaling.ods'
spectradir = datadir / 'Spectra'

# RFSA Config
rbw = 300e3

# Integration center/range
rf_center_freq = 25e6
bandwidth = 20e6

# Detector values
trans_gain_dc = 10e3
trans_gain_50 = 5e3
output_imp = 50
photon_mult = 10 * 156/42


def load_file(head):
    filename = spectradir / head
    filename = filename.with_suffix('.csv')
    return pd.read_csv(filename, skiprows=34, nrows=785-34, names=['Frequency (Hz)', 'RF Power (dBm)'])


def integrate_noise(df):
    rf_mask = (df['Frequency (Hz)'] < rf_center_freq + bandwidth /
               2) & (df['Frequency (Hz)'] > rf_center_freq - bandwidth / 2)
    noise_band_log = df['RF Power (dBm)'][rf_mask]
    noise_band_lin = 10**(noise_band_log/10) / 1000  # Watts
    noise_psd_mean = np.mean(noise_band_lin)/rbw # W/Hz
    return noise_psd_mean


def linear(x, m, b):
    return m * x + b


# Construct dataframe
data = pd.read_excel(datafile)
background_data = data.tail(2)
data = data.iloc[:-2]


# Load files and integrate noise
data['RF Spectrum'] = data['RFSA File Name'].apply(load_file)
data['PSD (W/Hz)'] = data['RF Spectrum'].apply(integrate_noise)
data['DC Voltage (V)'] = data['DC Voltage (mV)'] * 1e-3
data['DC Photocurrent (A)'] = data['DC Voltage (V)'] / trans_gain_dc 
data['Current PSD (A^2/Hz)'] = data['PSD (W/Hz)'] * output_imp / trans_gain_50**2

fig, ax = plt.subplots()
colors = plt.cm.turbo(np.linspace(0, 1, len(data)))
ax.set_prop_cycle(color=colors)

for i, row in data.iterrows():
    spectrum = row['RF Spectrum'] - 10 * np.log10(rbw)
    plt.plot(spectrum['Frequency (Hz)'], spectrum['RF Power (dBm)'])

plt.vlines([rf_center_freq - bandwidth/2, rf_center_freq +
           bandwidth/2], [-140, -140], [-100, -100], 'k')
plt.xlabel('Frequency (Hz)')
plt.ylabel('RF PSD (dBm/Hz)')
plt.show()

xaxis = 'DC Photocurrent (A)'
yaxis = 'Current PSD (A^2/Hz)'

x = data[xaxis].to_numpy() 
y = data[yaxis].to_numpy() 

# Linear fit
popt, _ = curve_fit(linear, x, y)


# Plot fit
x_fit = np.linspace(0, x.max(), 1000)
y_fit = linear(x_fit, *popt)

excess_noise = popt[0]  / 2 / q / photon_mult
# k = excess_noise / (2-1/photon_mult)
print(f'Excess noise: {excess_noise}')

plt.scatter(x, y, label='Data')
plt.loglog(x_fit, y_fit, 'r', label=f'Linear Fit')
plt.xlabel(xaxis)
plt.ylabel(yaxis)
plt.grid()
plt.legend()
plt.savefig('noise_scaling.png', bbox_inches='tight')
plt.show()
