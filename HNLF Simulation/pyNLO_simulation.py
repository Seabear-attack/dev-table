import numpy as np
import matplotlib.pyplot as plt
import pynlo
from pathlib import Path
from plottools.spectrometerdata import OSAData, readFromFiles
from scipy.constants import speed_of_light as C_MKS
from scipy.signal import peak_widths, find_peaks
from scipy.ndimage import zoom
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

directorypath = Path('~/Documents/Boulder_PhD/Data/11-19-24 Compressor FROG')
raw_data = pd.read_csv(directorypath / 'spectrum.CSV', skiprows=38, header = None).to_numpy()
# raw_data, _ = readFromFiles(directorypath, '*', skip_header=38)
labels = ('5 W')
powers_mW = [2.5e3]
rep_rate_MHz = 100
osa_spectrum = OSAData(raw_data, ('nm', 'dBm/nm'), labels[0], powers_mW[0], frep_MHz=rep_rate_MHz) 

comparison_spectrum = osa_spectrum

########### Define pulse characteristics ###############

directorypath = Path('~/Documents/Boulder_PhD/Data/11-20-24 Compressor FROG')

colnames = ['time [s]', 'ampl_t [au]', 'phase_t [rad]', 'freq [Hz]', 'ampl_f [au]', 'phase_f [rad]']
recon = pd.read_csv(directorypath / 'function_data.txt', names=colnames, header = None, sep = ' ', skiprows=1)

pulse_time_ps = 1e12 * recon['time [s]']
pulse_freq_THz = 1e-12 * recon['freq [Hz]']
phase_sign = 1 # Phase sign is arbitrary for SHG FROG
pulse_amp_f = recon['ampl_f [au]'] * np.exp (phase_sign * 1j * recon['phase_f [rad]'])

pulseWL_nm = 1556 # pulse central wavelength (nm)
power_mW = 2.5e3 
epp_J = power_mW / rep_rate_MHz * 1e-9
label = 'After HNLF+PM1550'

# Manually pad frequency axes to accommodate supercontinuua

pad_factor = 6
pulse_amp_f = expand_freq_axis(pulse_amp_f, pad_factor)

############## Simulation variables ##############3

Window = 2.0  # simulation window (ps)
Steps = 100  # simulation steps
Raman = True  # Enable Raman effect?
Steep = True  # Enable self steepening?


############ Fiber definitions ###############

# Fiber 1 (OFS PM ND-HNLF)
axis = 'fast'
Length = 70  # length in mm
Alpha = 0.8 * 10 ** (-5)  # attenuation coefficient (dB/cm)
Gamma = 10.5  # Gamma (1/(W km))
fibWL = 1550  # Center WL of fiber (nm)

if axis == 'slow':
    D = -2.6  # (ps/(nm*km))
    D_slope = .026  # (ps/(nm^2*km))
elif axis == 'fast':
    D = -.8
    D_slope = .024
else:
    D = 0
    D_slope = 0
if D == 0:
    beta2 = -7.5  # (ps^2/km)
    beta3 = 0.00  # (ps^3/km)
else:
    beta2 = -D * fibWL ** 2 / (2 * np.pi * C_NM_PS)
    beta3 = fibWL ** 3 / (2 * np.pi ** 2 * C_NM_PS ** 2) * (fibWL / 2 * D_slope + D)
beta4 = 0.00  # (ps^4/km)
alpha = np.log((10 ** (Alpha * 0.1))) * 100  # convert from dB/cm to 1/m
fiber_ofs_ndhnlf = pynlo.media.fibers.fiber.FiberInstance()  # create the fiber!
fiber_ofs_ndhnlf.generate_fiber(Length * 1e-3, center_wl_nm=fibWL, betas=(beta2, beta3, beta4),
                      gamma_W_m=Gamma * 1e-3, gvd_units='ps^n/km', gain=-alpha)

# Fiber 2 (PM1550)
Length = 50  # length in mm
Alpha = 1 * 10 ** (-5)  # attenuation coefficient (dB/cm)
Gamma = 1  # Gamma (1/(W km)) *****guess******
fibWL = 1550  # Center WL of fiber (nm)
D = 18  # (ps/(nm*km))
D_slope = .06  # (ps/(nm^2*km))
if D == 0:
    beta2 = -7.5  # (ps^2/km)
    beta3 = 0.00  # (ps^3/km)
else:
    beta2 = -D * fibWL ** 2 / (2 * np.pi * C_NM_PS)
    beta3 = fibWL ** 3 / (2 * np.pi ** 2 * C_NM_PS ** 2) * (fibWL / 2 * D_slope + D)
beta4 = 0.00  # (ps^4/km)
alpha = np.log((10 ** (Alpha * 0.1))) * 100  # convert from dB/cm to 1/m
fiber_pm1550 = pynlo.media.fibers.fiber.FiberInstance()  # create the fiber!
fiber_pm1550.generate_fiber(Length * 1e-3, center_wl_nm=fibWL, betas=(beta2, beta3, beta4),
                      gamma_W_m=Gamma * 1e-3, gvd_units='ps^n/km', gain=-alpha)


######## This is where the PyNLO magic happens! ############################

pulse_in = pynlo.light.PulseBase.Pulse()
pulse_in.set_NPTS(len(pulse_amp_f))
# pulse_in.set_NPTS(len(pulse_amp_t))
pulse_in.set_center_wavelength_nm(pulseWL_nm)
pulse_in.set_time_window_ps(max(pulse_time_ps) - min(pulse_time_ps))
# pulse_in.set_AT(pulse_amp_t)
pulse_in.set_AW(pulse_amp_f)
pulse_in.set_frep_MHz(rep_rate_MHz)
pulse_in.set_epp(epp_J)  # set the pulse energy
# pulse_in.expand_time_window(pad_factor, "even")
dict = pulse_in.get_pulse_dict()
# Propagation
evol = pynlo.interactions.FourWaveMixing.SSFM.SSFM(local_error=0.001, USE_SIMPLE_RAMAN=True,
                                                   disable_Raman=np.logical_not(Raman),
                                                   disable_self_steepening=np.logical_not(Steep))

y, aw, at, pulse_inter = evol.propagate(pulse_in=pulse_in, fiber=fiber_pm1550, n_steps=Steps)

y2, aw2, at2, pulse_out = evol.propagate(pulse_in=pulse_inter, fiber=fiber_ofs_ndhnlf, n_steps=Steps)

# Add the sections together
y = np.append(y, y2[1:] + y[-1], axis=0)
aw = np.append(aw, aw2[:, 1:], axis=1)
at = np.append(at, at2[:, 1:], axis=1)


############# Calculations for relavant plots ##################

F_THz = pulse_in.W_mks / (2 * np.pi) * 1e-12  # convert to THz

F_plus_THz = F_THz[F_THz > 0] # Take only positive frequencies
spectra_by_distance = np.power(np.abs(np.transpose(aw)[:, (F_THz > 0)]), 2) # Convert from amplitude to power
spectra_by_distance = [OSAData(np.transpose(np.array([F_plus_THz, spectrum])), ('THz', 'mW'), label, power_mW, rep_rate_MHz) for
                       spectrum in spectra_by_distance] # Create an easily manipulatable spectrum object

pulses_by_distance = np.power(np.abs(np.transpose(at)), 2)
pulses_by_distance_dB = dB(pulses_by_distance)

y = y * 1e3  # convert distance to mm

# Caculate FWHM for the input pulse
inp_pow_t = pulses_by_distance[0]
peak, _ = find_peaks(inp_pow_t, np.max(inp_pow_t))
inp_fwhm_samples, _, _, _ = peak_widths(inp_pow_t, peak, rel_height=.5)
inp_fwhm_fs = 1e3 * pulse_out.dT_ps * inp_fwhm_samples[0]

# Caculate transform limit and FWHM for the output pulse

# TODO not sure how to enforce flat phase. Enforcing flat phase on the 
# spectrum still creates complex numbers in time. Here, I'm just taking the 
# magnitude again
tl_pow_t = np.pow(np.abs(np.fft.ifftshift(np.fft.ifft(np.abs(pulse_out.AW)))),2)
tl_fwhm_samples, _, _, _ = peak_widths(tl_pow_t, [int(tl_pow_t.size/2)], rel_height=.5)
tl_fwhm_fs = 1e3 * pulse_out.dT_ps * tl_fwhm_samples[0]

########### Generate plots ####################
wavelength_axis = True  # True: wavelength axis, False: frequency axis

font = {'size': 10}
plt.rc('font', **font)

fig = plt.figure(figsize=(20, 10))
dims = (4,3)
lin_spec_ax = plt.subplot2grid(dims, (0, 0))
lin_puls_ax = plt.subplot2grid(dims, (0, 1))
log_spec_ax = plt.subplot2grid(dims, (1, 0), sharex=lin_spec_ax)

log_puls_ax = plt.subplot2grid(dims, (1, 1), sharex=lin_puls_ax)
prop_spec_ax = plt.subplot2grid(dims, (2, 0), rowspan=2, sharex=lin_spec_ax)
prop_puls_ax = plt.subplot2grid(dims, (2, 1), rowspan=2, sharex=lin_puls_ax)

lin_spec_comp_ax = plt.subplot2grid(dims, (0, 2), rowspan=2)
log_spec_comp_ax = plt.subplot2grid(dims, (2, 2), rowspan=1)

lin_tl_ax = plt.subplot2grid(dims, (3,2))

# Plot details

wl_ll = 1300
wl_ul = 1800

if wavelength_axis:
    # Normalize spectrum in linear units
    spectrum = spectra_by_distance[-1]
    spectrum.set_x_window(100, 5000, 'nm', .5)
    spectrum.y_axis_units = 'nJ/nm'
    comparison_spectrum.y_axis_units = 'nJ/nm'
    lin_spec_ax.plot(spectrum.x_axis_data, spectrum.y_axis_data, color='r', label='Final')
    lin_puls_ax.plot(pulse_in.T_ps, pulses_by_distance[-1], color='r', label='Final')

    spectrum = spectra_by_distance[0]
    spectrum.set_x_window(100, 5000, 'nm', .5)
    spectrum.y_axis_units = 'nJ/nm'
    lin_spec_comp_ax.plot(spectrum.x_axis_data, spectrum.y_axis_data, color='r', label='FROG spectrum')
    lin_spec_comp_ax.plot(comparison_spectrum.x_axis_data, comparison_spectrum.y_axis_data,
             color='b', label='Experimental Spectrum')
    lin_spec_ax.plot(spectrum.x_axis_data, spectrum.y_axis_data, color='b', label='Initial')
    # Plot phase
    lin_spec_phase_ax = lin_spec_ax.twinx()
    wl_axis = C_NM_PS / pulse_in.F_THz
    phase_axis_init = np.unwrap(np.angle(pulse_in.AW))
    phase_axis_fin = np.unwrap(np.angle(pulse_out.AW))
    phase_axis_init = (phase_axis_init - phase_axis_init[int(len(phase_axis_init)/2)])[wl_axis > 0]
    phase_axis_fin = (phase_axis_fin - phase_axis_fin[int(len(phase_axis_fin)/2)])[wl_axis > 0]
    wl_axis = wl_axis[wl_axis > 0]
    lin_spec_phase_ax.plot(wl_axis, phase_axis_init, label='Initial Phase')
    lin_spec_phase_ax.plot(wl_axis, phase_axis_fin, label='Final Phase')

    lin_puls_ax.plot(pulse_in.T_ps, pulses_by_distance[0], color='b', label=f'Initial: FWHM {inp_fwhm_fs: .1f} fs')

    # Spectrum in log units
    spectrum = spectra_by_distance[-1]
    spectrum.set_x_window(100, 5000, 'nm', .5)
    spectrum.y_axis_units = 'dBnJ/nm'
    comparison_spectrum.y_axis_units = 'dBnJ/nm'
    log_spec_ax.plot(spectrum.x_axis_data, spectrum.y_axis_data, color='r', label='Final')
    log_puls_ax.plot(pulse_in.T_ps, pulses_by_distance_dB[-1], color='r', label='Final')


    spectrum = spectra_by_distance[0]
    spectrum.set_x_window(100, 5000, 'nm', .5)
    spectrum.y_axis_units = 'dBnJ/nm'
    log_spec_comp_ax.plot(spectrum.x_axis_data, spectrum.y_axis_data, color='r', label='FROG spectrum')
    log_spec_comp_ax.plot(comparison_spectrum.x_axis_data, comparison_spectrum.y_axis_data,
             color='b', label='Experimental spectrum')
    log_spec_ax.plot(spectrum.x_axis_data, spectrum.y_axis_data, color='b', label='Initial')
    log_puls_ax.plot(pulse_in.T_ps, pulses_by_distance_dB[0], color='b', label='Initial')

    # Spectrum (log) by propagation distance
    spectrum_image_data = []
    for spectrum in spectra_by_distance:
        spectrum.set_x_window(100, 5000, 'nm', .5)
        spectrum.y_axis_units = 'dBnJ/nm'
        spectrum_image_data.append(spectrum.y_axis_data)

    spectrum_image_data = np.array([spectrum.y_axis_data for spectrum in spectra_by_distance])
    extent_pm1550 = (np.min(spectra_by_distance[0].x_axis_data), np.max(spectra_by_distance[0].x_axis_data), 0, y[Steps])
    extent_hnlf = (np.min(spectra_by_distance[0].x_axis_data), np.max(spectra_by_distance[0].x_axis_data), y[Steps], y[-1])
    prop_spec_ax.imshow(spectrum_image_data[0:Steps], extent=extent_pm1550, vmin=np.max(spectrum_image_data[0]) - 60.0,
               vmax=np.max(spectrum_image_data[0]), aspect='auto', origin='lower')
    prop_spec_ax.imshow(spectrum_image_data[Steps:], extent=extent_hnlf, vmin=np.max(spectrum_image_data[0]) - 60.0,
               vmax=np.max(spectrum_image_data[0]), aspect='auto', origin='lower')
    prop_spec_ax.set_ylim(0, y[-1])

    # Pulse (log) by propagation distance
    extent_pm1550 = (np.min(pulse_in.T_ps), np.max(pulse_in.T_ps), 0, y[Steps])
    extent_hnlf = (np.min(pulse_in.T_ps), np.max(pulse_in.T_ps), y[Steps], y[-1])
    prop_puls_ax.imshow(pulses_by_distance_dB[0:Steps], extent=extent_pm1550, vmin=np.max(pulses_by_distance_dB) - 60.0,
               vmax=np.max(pulses_by_distance_dB), aspect='auto', origin='lower')
    prop_puls_ax.imshow(pulses_by_distance_dB[Steps:], extent=extent_hnlf, vmin=np.max(pulses_by_distance_dB) - 60.0,
               vmax=np.max(pulses_by_distance_dB), aspect='auto', origin='lower')
    prop_puls_ax.set_ylim(0, y[-1])

    # Transform limit of resulting spectrum
    lin_tl_ax.plot(1e3 * pulse_in.T_ps, tl_pow_t, label=f'TL FWHM: {tl_fwhm_fs: .1f} fs')

    lin_spec_ax.set_ylabel('Intensity (nJ/nm)')
    lin_spec_comp_ax.set_ylabel('Intensity (nJ/nm)')

    log_spec_ax.set_ylabel('Intensity (dBnJ/nm)')
    log_spec_comp_ax.set_ylabel('Intensity (dBnJ/nm)')

    prop_spec_ax.set_xlabel('Wavelength (nm)')
    log_spec_comp_ax.set_xlabel('Wavelength (nm)')


    prop_puls_ax.set_xlabel('Time (ps)')

    prop_spec_ax.set_ylabel('Propagation distance (mm)')

    lin_tl_ax.set_xlabel('Time (fs)')
    lin_tl_ax.set_ylabel('Intensity (a.u.)')

    lin_spec_ax.set_xlim(wl_ll, wl_ul)
    lin_spec_comp_ax.set_xlim(1530, 1580)
    log_spec_comp_ax.set_xlim(1530, 1580)
    lin_tl_ax.set_xlim(-200, 200)
    # ax0.set_ylim([0, ax0.get_ylim()[1] / 50])
    # ax7.set_ylim([0, ax0.get_ylim()[1] / 50])

    lin_puls_ax.set_xlim(-2, 2)
    log_spec_ax.set_ylim(-60, 20)
    log_spec_comp_ax.set_ylim(-60, 20)
    lin_spec_phase_ax.set_ylim(-30, 30)

    log_puls_ax.set_ylim(30, 100)

    lin_spec_ax.legend()
    lin_puls_ax.legend()
    log_spec_ax.legend()
    log_puls_ax.legend()
    lin_spec_comp_ax.legend()
    log_spec_comp_ax.legend()
    lin_tl_ax.legend()
    lin_spec_phase_ax.legend(loc='upper left')

# else:
#     # TODO Update frequency space sim to reflect changes to wavelength side
#     ax0.plot(F_plus_THz, spectra_by_distance[-1], color='r')
#     ax1.plot(pulse.T_ps, pulses_by_distance[-1], color='r')
#
#     ax0.plot(F_plus_THz, spectra_by_distance[0], color='b')
#     ax1.plot(pulse.T_ps, pulses_by_distance[0], color='b')
#
#     ax2.plot(F_plus_THz, zW_dB[-1], color='r')
#     ax3.plot(pulse.T_ps, pulses_by_distance_dB[-1], color='r')
#
#     ax2.plot(F_plus_THz, zW_dB[0], color='b')
#     ax3.plot(pulse.T_ps, pulses_by_distance_dB[0], color='b')
#
#     extent = (np.min(F_plus_THz), np.max(F_plus_THz), 0, Length)
#     ax4.imshow(zW_dB, extent=extent, vmin=np.max(zW_dB) - 60.0,
#                vmax=np.max(zW_dB), aspect='auto', origin='lower')
#
#     extent = (np.min(pulse.T_ps), np.max(pulse.T_ps), 0, Length)
#     ax5.imshow(pulses_by_distance_dB, extent=extent, vmin=np.max(pulses_by_distance_dB) - 60.0,
#                vmax=np.max(pulses_by_distance_dB), aspect='auto', origin='lower')
#
#     ax0.set_ylabel('Intensity (arb.)')
#     ax2.set_ylabel('Intensity (dB)')
#
#     ax4.set_xlabel('Frequency (THz)')
#
#     ax5.set_xlabel('Time (ps)')
#
#     ax4.set_ylabel('Propagation distance (mm)')
#
#     ax4.set_xlim(0, 400)
#
#     ax2.set_ylim(-50, 20)
#     ax1.set_ylim(-40, 60)
#     ax1.set_xlim(-1, 1)

fig.canvas.manager.window.showMaximized()
plt.tight_layout(pad=.1)
# plt.tight_layout()
plt.show()
