import matplotlib.pyplot as plt
import numpy as np
from scipy.constants import Planck as h
from scipy.constants import elementary_charge as e
from scipy.constants import speed_of_light as c

# Experimental parameters
gamma = 1 # Comb power ratio
optical_bandwidth = 50e12 # Spectral width (Hz)
fr = 100e6 # Comb rep rate (Hz)
optical_resolution = fr # Resolution can nominally be greater than fr
center_wavelength = 400e-9 # Optical center wavelength (m)
# center_wavelength = 1565e-9 # Optical center wavelength (m)
average_time = 1 # Averaging time (s)
rin_best = -132 # Relative intensity noise (dBc/Hz)
rin_worst = -117 # Relative intensity noise (dBc/Hz)
# rin = -151 # Relative intensity noise (dBc/Hz)

# Detector parameters
## New Focus 1801 - Si PIN
# responsivity = .16 # 400 nm
# photon_multiplier = 1
# trans_gain = 40e3
# integrated_noise = 5e-3
# bandwidth = 125e6
# pmax = 110e-6
# nep = integrated_noise / trans_gain / responsivity / (bandwidth)**.5
# b = 2
# print(nep)
# name = 'New Focus 1801'

## PDA05CF2 - InGaAs PIN
# responsivity = 1.04
# nep = 1.26e-11
# photon_multiplier = 1
# vmax = 5
# trans_gain = 5e3
# pmax = vmax / trans_gain / responsivity
# b = 2
# name = 'Thorlabs PDA05CF2'

## Thorlabs APD130A2 - Si APD (UV-enhanced)
# nep = 25/12*.21e-12 # Adjusted for responsivity drop W/rt(Hz)
# photon_multiplier = 50 # M-factor for APDs / PMTs
# pmax = 2e-6 # Optical saturation power
# ion_ratio = .05 # guess
# responsivity = 12 # Responsivity @ target wavelength (A/W)
# b = 2 # 1 for balanced, 2 for unbalanced
# name = 'Thorlabs APD130A2'

## Thorlabs PDA8A2 - Si PIN
# nep = .53/.14 * 7.8e-12 # W/rt(Hz)
# photon_multiplier = 1 
# responsivity = .14 # Responsivity (A/W)
# vmax = 1.8
# trans_gain = 50e3
# pmax = vmax / trans_gain / responsivity
# b = 2 # 1 for balanced, 2 for unbalanced
# name = 'Thorlabs PDA8A2'

# Thorlabs PDB410A - Si PIN
# nep = .53/.14 * 7e-12 # W/rt(Hz)
# photon_multiplier = 1 
# pmax=
# responsivity = .14 # Responsivity (A/W)
# b = 1 # 1 for balanced, 2 for unbalanced
# name='Thorlabs PDB410A'

## Thorlabs APD430A2 - Si APD (UV-enhanced), minimum M
nep = 49/22.5 * .15e-12 # W/rt(Hz)
photon_multiplier = 100 
responsivity = 22.5 * photon_multiplier / 100 # Responsivity (A/W)
ion_ratio = .05 # guess
vmax = 2 
trans_gain = 5e3
pmax = vmax / trans_gain / responsivity
b = 2 # 1 for balanced, 2 for unbalanced
name = 'Thorlabs APD430A2'


powers = np.logspace(-7, -2, 1000)

center_freq = c / center_wavelength
eta = responsivity / e * h * center_freq / photon_multiplier
# eta = responsivity / e * h * center_freq 
print(eta)
c_gamma = (1+gamma)/(2 * gamma)
c_gamma_2 = (1+gamma**2)/(2 * gamma)
epsilon = optical_resolution / fr
M = optical_bandwidth / optical_resolution

a_nep = nep**2 / gamma
if photon_multiplier == 1:
    a_shot = 4 * c_gamma / eta * h * center_freq
elif photon_multiplier > 1:
    # Excess noise factor for (ideal) APD
    excess_noise = ion_ratio * photon_multiplier + (1-ion_ratio) * (2- 1/photon_multiplier)
    print(excess_noise)
    a_shot = 4 * c_gamma / eta * h * center_freq * excess_noise 
    
a_rin_worst = 2 * c_gamma_2 * b * 10**(rin_worst/10)
a_rin_best = 2 * c_gamma_2 * b * 10**(rin_best/10)
a_range = (nep/pmax)**2

sigma_nep = M * epsilon**0.5 / 0.8 * average_time**0.5 * (a_nep / powers**2) **.5
sigma_shot = M * epsilon**0.5 / 0.8 * average_time**0.5 * (a_shot/ powers) **.5
sigma_rin_best = M * epsilon**0.5 / 0.8 * average_time**0.5 * (a_rin_best) **.5
sigma_rin_worst = M * epsilon**0.5 / 0.8 * average_time**0.5 * (a_rin_worst) **.5
# sigma_rin = M * epsilon**0.5 / 0.8 * average_time**0.5 * (a_rin) **.5
sigma_range = M * epsilon**0.5 / 0.8 * average_time**0.5 * (a_range) **.5

sigma_h_best =  M * epsilon**0.5 / 0.8 * average_time**0.5 * (a_nep / powers**2 + a_shot / powers +a_rin_best + a_range)**.5
sigma_h_worst =  M * epsilon**0.5 / 0.8 * average_time**0.5 * (a_nep / powers**2 + a_shot / powers +a_rin_worst + a_range)**.5
# sigma_h =  M * epsilon**0.5 / 0.8 * average_time**0.5 * (a_nep / powers**2 + a_shot / powers +a_rin + a_range)**.5

plt.plot(powers, 1/sigma_nep, label='Detector noise')
plt.plot(powers, 1/sigma_shot, label='Shot noise')
plt.hlines(1/sigma_range, min(powers), max(powers), label='Dynamic Range', colors='tab:red')
plt.hlines(1/sigma_rin_best, min(powers), max(powers), label='Excess RIN (Best Case)', colors='tab:purple')
plt.hlines(1/sigma_rin_worst, min(powers), max(powers), label='Excess RIN (Worst Case)', colors='k')
plt.plot(powers, 1/sigma_h_best, label='Total SNR (Best Case)')
plt.plot(powers, 1/sigma_h_worst, label='Total SNR (Worst Case)')
# plt.plot(powers, 1/sigma_h, label='Total SNR')
plt.loglog()
plt.xlabel('Source Power (Single Comb) (W)')
plt.ylabel(r'SNR, $1/\sigma_H$ (Hz$^{1/2}$)')
plt.legend()
plt.grid()
plt.title(f'{name}, {center_wavelength *1e9:.0f} nm')
# plt.ylim(1e-2, 1e3)

plt.show()