from glob import glob
import re
import numpy as np
import os
from pathlib import Path


class FrogData:
    def __init__(self, delays, wavelengths, trace, delays_recon=None, wavelengths_recon=None, trace_recon=None,
                 label=None, pulse_time=None, pulse_intensity=None, t_FWHM=None, wl_FWHM=None, frog_error=None):
        self.delays = delays
        self.wavelengths = wavelengths
        self.trace = trace
        self.delays_recon = delays_recon
        self.wavelengths_recon = wavelengths_recon
        self.trace_recon = trace_recon
        self.label = label
        self.pulse_time = pulse_time
        self.pulse_intensity = pulse_intensity
        self.frog_error = frog_error
        self.wl_FWHM = wl_FWHM
        self.t_FWHM = t_FWHM

    def autocorrelation(self):
        # Replace this function with your actual autocorrelation calculation
        return np.sum(self.trace, axis=0)


def read_frog(filepath):
    # Replace this function with your actual FROG trace data generation
    input_file = np.genfromtxt(filepath, usecols=(0))
    num_bins = int(input_file[0])
    wavelengths = input_file[2:2 + num_bins]
    delays = input_file[2 + num_bins:2 + 2 * num_bins]
    trace = input_file[2 + 2 * num_bins:]
    trace = np.flipud(np.reshape(trace, (num_bins, num_bins)))
    return delays, wavelengths, trace


def read_pulse(filepath):
    # Replace this function with your actual FROG trace data generation
    input_file = np.genfromtxt(filepath)
    time = input_file[:, 0]
    intensity = input_file[:, 1]
    return time, intensity


def read_frog_directory(directorypath, pattern=None):
    filepaths = directorypath.glob("**/a.dat")
    dirpaths = [filepath.parent for filepath in filepaths]
    frog_list = []
    for dirpath in dirpaths:
        if pattern is not None:
            label = re.search(pattern, dirpath.name)
            if label is not None:
                label = label[0]
                pulse_time, pulse_intensity = read_pulse(dirpath / 'Ek.dat')
                delays_recon, wavelengths_recon, trace_recon = read_frog(dirpath / 'arecon.dat')
                delays, wavelengths, trace = read_frog(dirpath / 'a.dat')
                t_FWHM, wl_FWHM, frog_error = read_recon_parameters(dirpath / 'frog.dat')
                frog_list.append(
                    FrogData(delays, wavelengths, trace, delays_recon=delays_recon, wavelengths_recon=wavelengths_recon,
                            trace_recon=trace_recon, label=label, pulse_time=pulse_time, pulse_intensity=pulse_intensity,
                            t_FWHM=t_FWHM, wl_FWHM=wl_FWHM, frog_error=frog_error))
        else:
            label = dirpath.stem
            pulse_time, pulse_intensity = read_pulse(dirpath / 'Ek.dat')
            delays_recon, wavelengths_recon, trace_recon = read_frog(dirpath / 'arecon.dat')
            delays, wavelengths, trace = read_frog(dirpath / 'a.dat')
            t_FWHM, wl_FWHM, frog_error = read_recon_parameters(dirpath / 'frog.dat')
            frog_list.append(
                FrogData(delays, wavelengths, trace, delays_recon=delays_recon, wavelengths_recon=wavelengths_recon,
                        trace_recon=trace_recon, label=label, pulse_time=pulse_time, pulse_intensity=pulse_intensity,
                        t_FWHM=t_FWHM, wl_FWHM=wl_FWHM, frog_error=frog_error))
    return frog_list


def read_recon_parameters(filepath):
    with open(filepath) as input_file:
        lines = input_file.readlines()
    t_FWHM = float(re.search(r'\d+\.\d+', lines[-7])[0])
    wl_FWHM = float(re.search(r'\d+\.\d+', lines[-6])[0])
    frog_error = float(re.search(r'\d+\.\d+', lines[-10])[0])
    return t_FWHM, wl_FWHM, frog_error
