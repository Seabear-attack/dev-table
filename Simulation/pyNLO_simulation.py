# Runs with python ver. 2.7

import numpy as np
import matplotlib.pyplot as plt
import pynlo
from pathlib import Path
from Plotting.utils.spectrometerdata import OSAData, readFromFiles


def dB(num):
    return 10 * np.log10(np.abs(num) ** 2)


# Fundamental constants
c_nm_per_ps = 299792.458

# Comparison Spectrum
directorypath = Path(
    r'C:\Users\wahlm\Documents\School\Research\Allison\Tunable Pump\Pulse Optimization and Spectrum Generation\10-20-23 ADHNLF Spectra\Slow axis')
raw_data = readFromFiles(directorypath)
labels = ('7cm LD-ADHNLF 4A',
          '7cm LD-ADHNLF 3.3A'
          )
powers_mW = [200,
             178]
adhnlf_data = [OSAData(dat, ('nm', 'dBm/nm'), labels[i], powers_mW[i], frep_MHz=60.5) for i, dat in enumerate(raw_data)]


directorypath = Path(
    r'C:\Users\wahlm\Documents\School\Research\Allison\Tunable Pump\Data for Papers\Tunable seed\Spectrum vs. pulse pattern\4cm NDHNLF + 42cm PM1550')
raw_data = readFromFiles(directorypath)

labels = (r'4cm NDHNLF 4A',
          r'$f_{rep}/10$',
          r'$f_{rep}/100$',
          'background')
frep_frac = [1, 1 / 10, 1 / 100, 0]
is_background = (False, False, False, True)
powers_mW = [191, 33, 15.37, 13.9]

ndhnlf_data = [OSAData(dat, ('nm', 'dBm/nm'), labels[i], powers_mW[i], frep_MHz=frep_frac[i] * 60.56,
                is_background=is_background[i]) for i, dat in enumerate(raw_data)]
ndhnlf_data = ndhnlf_data[:-1]

comparison_spectrum = ndhnlf_data[0]

# Pulse characteristics
pulse_dir = Path(
    r'C:\Users\wahlm\Documents\School\Research\Allison\Tunable Pump\Data for Papers\Tunable seed\FROGs vs. pulse pattern\Low rep rate\frep')
label = r'$f_{rep}'
pulse_at_file_in = np.genfromtxt(pulse_dir / 'Ek.dat')
pulse_al_file_in = np.genfromtxt(pulse_dir / 'Speck.dat')
pulse_time_ps = .001 * pulse_at_file_in[:, 0]
pulse_amp = pulse_at_file_in[:, 3] + 1j * pulse_at_file_in[:, 4]
pulse_wavelength_nm = pulse_al_file_in[:, 0]
pulseWL = (max(pulse_wavelength_nm) + min(pulse_wavelength_nm)) / 2  # pulse central wavelength (nm)
rep_rate_MHz = 60.56  # MHz
power_mW = 291
EPP_J = power_mW / rep_rate_MHz * 1e-9

# Simulation constants
Window = 2.0  # simulation window (ps)
Steps = 100  # simulation steps
# Points = 2 ** 13  # simulation points
pad_factor = 2
Raman = True  # Enable Raman effect?
Steep = True  # Enable self steepening?

# Plot options
wavelength_axis = True  # True: wavelength axis, False: frequency axis

font = {'size': 10}
plt.rc('font', **font)

# Fiber 1 (OFS PM ND-HNLF)
axis = 'slow'
Length = 40  # length in mm
Alpha = 0.8 * 10 ** (-5)  # attenuation coefficient (dB/cm)
Gamma = 10.5  # Gamma (1/(W km))
fibWL = 1550  # Center WL of fiber (nm)

if axis == 'slow':
    D = -2.6  # (ps/(nm*km))
    D_slope = .026  # (ps/(nm^2*km))
elif axis == 'fast':
    D = -.8
    D_slope = .024
if D == 0:
    beta2 = -7.5  # (ps^2/km)
    beta3 = 0.00  # (ps^3/km)
else:
    beta2 = -D * fibWL ** 2 / (2 * np.pi * c_nm_per_ps)
    beta3 = fibWL ** 3 / (2 * np.pi ** 2 * c_nm_per_ps ** 2) * (fibWL / 2 * D_slope + D)
beta4 = 0.00  # (ps^4/km)
alpha = np.log((10 ** (Alpha * 0.1))) * 100  # convert from dB/cm to 1/m
fiber1 = pynlo.media.fibers.fiber.FiberInstance()  # create the fiber!
fiber1.generate_fiber(Length * 1e-3, center_wl_nm=fibWL, betas=(beta2, beta3, beta4),
                      gamma_W_m=Gamma * 1e-3, gvd_units='ps^n/km', gain=-alpha)

# Fiber 2 (PM1550)
# Length = 1000  # length in mm
# Alpha = 1 * 10 ** (-5)  # attenuation coefficient (dB/cm)
# Gamma = 1  # Gamma (1/(W km)) *****guess******
# fibWL = 1550  # Center WL of fiber (nm)
# D = 18  # (ps/(nm*km))
# D_slope = .06  # (ps/(nm^2*km))
# if D == 0:
#     beta2 = -7.5  # (ps^2/km)
#     beta3 = 0.00  # (ps^3/km)
# else:
#     beta2 = -D * fibWL ** 2 / (2 * np.pi * c_nm_per_ps)
#     beta3 = fibWL ** 3 / (2 * np.pi ** 2 * c_nm_per_ps ** 2) * (fibWL / 2 * D_slope + D)
# beta4 = 0.00  # (ps^4/km)
# alpha = np.log((10 ** (Alpha * 0.1))) * 100  # convert from dB/cm to 1/m
# fiber2 = pynlo.media.fibers.fiber.FiberInstance()  # create the fiber!
# fiber2.generate_fiber(Length * 1e-3, center_wl_nm=fibWL, betas=(beta2, beta3, beta4),
#                       gamma_W_m=Gamma * 1e-3, gvd_units='ps^n/km', gain=-alpha)


######## This is where the PyNLO magic happens! ############################
pulse = pynlo.light.PulseBase.Pulse()
pulse.set_NPTS(len(pulse_time_ps))
pulse.set_center_wavelength_nm(1565)
pulse.set_time_window_ps(max(pulse_time_ps) - min(pulse_time_ps))
pulse.set_AT(pulse_amp)
pulse.set_frep_MHz(rep_rate_MHz)
pulse.set_epp(EPP_J)  # set the pulse energy
pulse.expand_time_window(pad_factor, "even")
dict = pulse.get_pulse_dict()
# Propagation
evol = pynlo.interactions.FourWaveMixing.SSFM.SSFM(local_error=0.001, USE_SIMPLE_RAMAN=True,
                                                   disable_Raman=np.logical_not(Raman),
                                                   disable_self_steepening=np.logical_not(Steep))

y, AW, AT, pulse_out = evol.propagate(pulse_in=pulse, fiber=fiber1, n_steps=Steps)

########## That's it! Physic done. Just boring plots from here! ################


F_THz = pulse.W_mks / (2 * np.pi) * 1e-12  # convert to THz

F_plus_THz = F_THz[F_THz > 0]
spectra_by_distance = np.power(np.abs(np.transpose(AW)[:, (F_THz > 0)]), 2)
spectra_by_distance = [OSAData(np.transpose(np.array([F_plus_THz, spectrum])), ('THz', 'mW'), label, power_mW) for
                       spectrum in spectra_by_distance]
pulses_by_distance = np.power(np.abs(np.transpose(AT)), 2)

pulses_by_distance_dB = dB(pulses_by_distance)

y = y * 1e3  # convert distance to mm

# set up plots for the results:
fig = plt.figure(figsize=(10, 10))
ax0 = plt.subplot2grid((4, 3), (0, 0))
ax1 = plt.subplot2grid((4, 3), (0, 1))
ax2 = plt.subplot2grid((4, 3), (1, 0), sharex=ax0)

ax3 = plt.subplot2grid((4, 3), (1, 1), sharex=ax1)
ax4 = plt.subplot2grid((4, 3), (2, 0), rowspan=2, sharex=ax0)
ax5 = plt.subplot2grid((4, 3), (2, 1), rowspan=2, sharex=ax1)

ax6 = plt.subplot2grid((4, 3), (0, 2), rowspan=2)
ax7 = plt.subplot2grid((4, 3), (2, 2), rowspan=2)

if wavelength_axis:
    spectrum = spectra_by_distance[-1]
    spectrum.set_x_window(100, 5000, 'nm', .5)
    spectrum.y_axis_units = 'nJ/nm'
    comparison_spectrum.y_axis_units = 'nJ/nm'
    ax0.plot(spectrum.x_axis_data, spectrum.y_axis_data, color='r', label='Final')
    ax1.plot(pulse.T_ps, pulses_by_distance[-1], color='r', label='Final')
    ax6.plot(spectrum.x_axis_data, spectrum.y_axis_data, color='r', label='Simulation')
    ax6.plot(comparison_spectrum.x_axis_data, comparison_spectrum.y_axis_data,
             color='b', label='Experiment')

    spectrum = spectra_by_distance[0]
    spectrum.set_x_window(100, 5000, 'nm', .5)
    spectrum.y_axis_units = 'nJ/nm'
    ax0.plot(spectrum.x_axis_data, spectrum.y_axis_data, color='b', label='Initial')
    ax1.plot(pulse.T_ps, pulses_by_distance[0], color='b', label='Initial')

    spectrum = spectra_by_distance[-1]
    spectrum.set_x_window(100, 5000, 'nm', .5)
    spectrum.y_axis_units = 'dBnJ/nm'
    comparison_spectrum.y_axis_units = 'dBnJ/nm'
    ax2.plot(spectrum.x_axis_data, spectrum.y_axis_data, color='r', label='Final')
    ax3.plot(pulse.T_ps, pulses_by_distance_dB[-1], color='r', label='Final')
    ax7.plot(spectrum.x_axis_data, spectrum.y_axis_data, color='r', label='Simulation')
    ax7.plot(comparison_spectrum.x_axis_data, comparison_spectrum.y_axis_data,
             color='b', label='Experiment')

    spectrum = spectra_by_distance[0]
    # spectrum.set_resolution(100, 5000, 'nm', .5)
    spectrum.y_axis_units = 'dBnJ/nm'
    ax2.plot(spectrum.x_axis_data, spectrum.y_axis_data, color='b', label='Initial')
    ax3.plot(pulse.T_ps, pulses_by_distance_dB[0], color='b', label='Initial')

    spectrum_image_data = []
    for spectrum in spectra_by_distance:
        spectrum.set_x_window(100, 5000, 'nm', .5)
        spectrum.y_axis_units = 'dBnJ/nm'
        spectrum_image_data.append(spectrum.y_axis_data)

    spectrum_image_data = np.array([spectrum.y_axis_data for spectrum in spectra_by_distance])
    extent = (np.min(spectra_by_distance[0].x_axis_data), np.max(spectra_by_distance[0].x_axis_data), 0, Length)
    ax4.imshow(spectrum_image_data, extent=extent, vmin=np.max(spectrum_image_data[0]) - 60.0,
               vmax=np.max(spectrum_image_data[0]), aspect='auto', origin='lower')

    extent = (np.min(pulse.T_ps), np.max(pulse.T_ps), 0, Length)
    ax5.imshow(pulses_by_distance_dB, extent=extent, vmin=np.max(pulses_by_distance_dB) - 60.0,
               vmax=np.max(pulses_by_distance_dB), aspect='auto', origin='lower')

    ax0.set_ylabel('Intensity (nJ/nm)')
    ax6.set_ylabel('Intensity (nJ/nm)')

    ax2.set_ylabel('Intensity (dBnJ/nm)')
    ax7.set_ylabel('Intensity (dBnJ/nm)')

    ax4.set_xlabel('Wavelength (nm)')
    ax7.set_xlabel('Wavelength (nm)')


    ax5.set_xlabel('Time (ps)')

    ax4.set_ylabel('Propagation distance (mm)')

    ax0.set_xlim(1000, 2500)
    ax6.set_xlim(1000, 2500)
    ax7.set_xlim(1000, 2500)
    ax0.set_ylim([0, ax0.get_ylim()[1] / 50])
    ax7.set_ylim([0, ax0.get_ylim()[1] / 50])

    ax1.set_xlim(-1, 1)
    ax2.set_ylim(-60, 20)
    ax7.set_ylim(-60, 20)

    ax3.set_ylim(30, 100)

    ax0.legend()
    ax1.legend()
    ax2.legend()
    ax3.legend()
    ax6.legend()
    ax7.legend()

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
