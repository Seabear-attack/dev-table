import matplotlib.pyplot as plt
import numpy as np
from scipy.constants import Planck as h
from scipy.constants import elementary_charge as e
from scipy.constants import speed_of_light as c

# Technical parameters
nep = .21e-12 # W/rt(Hz)
gamma = 1 # Comb power ratio
eta = .8 # Detector quantum efficiency 
optical_bandwidth = 50e12 # Spectral width (Hz)
fr = 100e6 # Comb rep rate (Hz)
optical_resolution = fr # Resolution can nominally be greater than fr
center_wavelength = 400e-9 # Optical center wavelength (m)
b = 2 # 1 for balanced, 2 for unbalanced
average_time = 1 # Averaging time (s)
responsivity = 12 # Responsivity (A/W)
n_bits = 16
rin = 0


powers = np.logspace(-9, -4, 1000)

center_freq = c / center_wavelength
eta = responsivity / e * h * center_freq
print(eta)
d = 3**.5 * 2**n_bits
c_gamma = (1+gamma)/(2 * gamma)
c_gamma_2 = (1+gamma**2)/(2 * gamma)
epsilon = optical_resolution / fr
M = optical_bandwidth / optical_resolution

a_nep = nep**2 / gamma
a_shot = 4 * c_gamma / eta * h * center_freq
a_rin = 2 * c_gamma_2 * b * rin
a_range = 8 * d**(-2) * fr**(-1)

sigma_h =  M * epsilon**0.5 / 0.8 * average_time**0.5 * (a_nep / powers**2 + a_shot / powers +a_rin + a_range)**.5
sigma_nep = M * epsilon**0.5 / 0.8 * average_time**0.5 * (a_nep / powers**2) **.5
sigma_shot = M * epsilon**0.5 / 0.8 * average_time**0.5 * (a_shot/ powers) **.5
sigma_rin = M * epsilon**0.5 / 0.8 * average_time**0.5 * (a_rin) **.5
sigma_range = M * epsilon**0.5 / 0.8 * average_time**0.5 * (a_range) **.5

plt.plot(powers, 1/sigma_h, label='Total SNR')
plt.plot(powers, 1/sigma_nep, label='Detector noise')
plt.plot(powers, 1/sigma_shot, label='Shot noise')
plt.hlines(1/sigma_range, min(powers), max(powers), label='Digitization noise', colors='tab:red')
plt.loglog()
plt.xlabel('Source Power (W)')
plt.ylabel(r'SNR, $1/\sigma_H$ (Hz$^{1/2}$)')
plt.legend()
plt.title('Thorlabs APD130A2, 400 nm')

plt.show()