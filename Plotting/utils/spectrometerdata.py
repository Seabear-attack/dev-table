import os
import re
from natsort import natsorted
import numpy as np

c_nm_ps = 299792.458


class RFSAData:
    def __init__(self, data, axis_units, data_label, frep_MHz=60.5):
        self._x_axis_units = axis_units[0]
        self._y_axis_units = axis_units[1]
        self.x_axis_data = data[:, 0]
        self.y_axis_data = data[:, 1]
        self.label = data_label
        self._frep_MHz = frep_MHz
        if self._y_axis_units == 'dBm':
            self.total_power_mW = sum(np.power(10, self.y_axis_data / 10))
        else:
            self.total_power_mW = sum(self.y_axis_data)

        self._pulse_energy_nJ = self.total_power_mW / self._frep_MHz

    @property
    def x_axis_units(self):
        return self._x_axis_units

    @x_axis_units.setter
    def x_axis_units(self, units):
        self._x_axis_units = units

    @property
    def y_axis_units(self):
        return self._y_axis_units

    @y_axis_units.setter
    def y_axis_units(self, units):
        if self._y_axis_units[:2] == 'dB':
            self.y_axis_data = np.power(10, self.y_axis_data / 10)
        self._y_axis_units = units
        self.__normalize()

    def __normalize(self):
        integral = sum(self.y_axis_data)
        delta_lambda = self.x_axis_data[1] - self.x_axis_data[0]

        if self._y_axis_units == 'mW':
            self.y_axis_data = self.y_axis_data * self.total_power_mW / integral

        elif self._y_axis_units == 'mW/nm':
            self.y_axis_data = self.y_axis_data * self.total_power_mW / integral / delta_lambda

        elif self._y_axis_units == 'dBm':
            self.y_axis_data = 10 * np.log10(self.y_axis_data * self.total_power_mW / integral)

        elif self._y_axis_units == 'dBm/nm':
            self.y_axis_data = 10 * np.log10(self.y_axis_data * self.total_power_mW / integral / delta_lambda)

        elif self._y_axis_units == 'nJ':
            self.y_axis_data = self.y_axis_data * self._pulse_energy_nJ / integral

        elif self._y_axis_units == 'dBnJ':
            self.y_axis_data = 10 * np.log10(self.y_axis_data * self._pulse_energy_nJ / integral)

        elif self._y_axis_units == 'nJ/nm':
            self.y_axis_data = self.y_axis_data * self._pulse_energy_nJ / integral / delta_lambda

        elif self._y_axis_units == 'dBnJ/nm':
            self.y_axis_data = 10 * np.log10(self.y_axis_data * self._pulse_energy_nJ / integral / delta_lambda)


class OSAData:
    def __init__(self, data, axis_units, data_label, spectrum_power_mW, frep_MHz=60.5, is_background=False):
        self._x_axis_units = axis_units[0]
        self._y_axis_units = axis_units[1]
        self._total_power_mW = spectrum_power_mW
        self.__data_is_log = (self.y_axis_units[:2] == 'dB')
        self._x_axis_data = data[:, 0]
        self._y_axis_data = data[:, 1]
        self.label = data_label
        if not is_background:
            self._frep_MHz = frep_MHz
            self._pulse_energy_nJ = self.total_power_mW / self._frep_MHz
        self.__normalize()

    @property
    def total_power_mW(self):
        return self._total_power_mW

    @total_power_mW.setter
    def total_power_mW(self, power):
        self._total_power_mW = power
        self._pulse_energy_nJ = self.total_power_mW / self._frep_MHz
        self.__normalize()

    @property
    def x_axis_units(self):
        return self._x_axis_units

    @x_axis_units.setter
    def x_axis_units(self, units):
        if (units == 'THz' and self.x_axis_units == 'nm') or (units == 'nm' and self.x_axis_units == 'THz'):
            old_x_data = self.x_axis_data  # e.g. THz
            old_y_data = self.y_axis_data
            new_x_data_lin = np.flip(np.linspace(c_nm_ps / np.min(old_x_data), c_nm_ps / np.max(old_x_data),
                                                 len(old_x_data)))  # nm
            new_x_data_hyp = np.flip(c_nm_ps / old_x_data)  # nm

            y_units = self.y_axis_units
            old_y_data = np.flip(old_y_data)
            new_y_data = np.interp(new_x_data_lin, new_x_data_hyp, old_y_data)
            self.y_axis_units = 'mW'
            self._y_axis_data = new_y_data / np.power(new_x_data_lin, 2)  # 1/lambda^2 Jacobian
            self._x_axis_data = new_x_data_lin  # nm
            self.y_axis_units = y_units

        self._x_axis_units = units

    @property
    def y_axis_units(self):
        return self._y_axis_units

    @y_axis_units.setter
    def y_axis_units(self, units):
        self._y_axis_units = units
        self.__normalize()

    @property
    def x_axis_data(self):
        return self._x_axis_data

    @property
    def y_axis_data(self):
        return self._y_axis_data

    @y_axis_data.setter
    def y_axis_data(self, data):
        if self.__data_is_log:
            self._y_axis_data = np.nan_to_num(data, nan=-np.inf)
        else:
            self._y_axis_data = data
            self._y_axis_data[self._y_axis_data < 0] = 0
        self.__normalize()

    def set_x_window(self, lower_bound, upper_bound, units, resolution):
        if units == self.x_axis_units:
            in_bounds = np.logical_and(self._x_axis_data >= lower_bound, self._x_axis_data <= upper_bound)
            old_x_data = self._x_axis_data[in_bounds]
            old_y_data = self.y_axis_data[in_bounds]

            x_range = np.max(old_x_data) - np.min(old_x_data)
            npts = int(x_range / resolution)
            new_x_data = np.linspace(np.min(old_x_data), np.max(old_x_data), npts)
            new_y_data = np.interp(new_x_data, old_x_data, old_y_data)
            self._x_axis_data = new_x_data
            self._y_axis_data = new_y_data
            self.__normalize()

        elif (units == 'THz' and self.x_axis_units == 'nm') or (units == 'nm' and self.x_axis_units == 'THz'):
            in_bounds = np.logical_and(c_nm_ps / self._x_axis_data >= lower_bound,  c_nm_ps / self._x_axis_data <= upper_bound)
            old_x_data = self._x_axis_data[in_bounds]
            old_y_data = self.y_axis_data[in_bounds]

            new_x_data_hyp = np.flip(c_nm_ps / old_x_data)
            x_range = np.max(new_x_data_hyp) - np.min(new_x_data_hyp)
            npts = int(x_range / resolution)
            new_x_data_lin = np.flip(np.linspace(c_nm_ps / np.min(old_x_data), c_nm_ps / np.max(old_x_data),
                                                 npts))


            y_units = self.y_axis_units
            old_y_data = np.flip(old_y_data)
            new_y_data = np.interp(new_x_data_lin, new_x_data_hyp, old_y_data)
            self.y_axis_units = 'mW'
            self._y_axis_data = new_y_data / np.power(new_x_data_lin, 2)  # Jacobian
            self._x_axis_data = new_x_data_lin
            self.y_axis_units = y_units

        self._x_axis_units = units
    def integral(self, lower_bound=None, upper_bound=None):
        if lower_bound is None:
            lower_bound = min(self._x_axis_data)
        if upper_bound is None:
            upper_bound = max(self._x_axis_data)
        in_bounds = np.where(np.logical_and(lower_bound <= self._x_axis_data, self._x_axis_data <= upper_bound))
        y_data_subsection = self.y_axis_data[in_bounds]
        if self.__data_is_log:
            return sum(np.power(10, y_data_subsection / 10))
        else:
            return sum(y_data_subsection)

    def __normalize(self):
        integral = self.integral()
        delta_x = (self._x_axis_data[-1] - self._x_axis_data[0]) / (len(self._x_axis_data) - 1)
        if self.__data_is_log:
            linear_y_data = np.power(10, self._y_axis_data / 10)

        else:
            linear_y_data = self.y_axis_data

        if self._y_axis_units == 'mW':
            self.__data_is_log = False
            self._y_axis_data = linear_y_data * self.total_power_mW / integral

        elif self._y_axis_units == 'mW/nm':
            self.__data_is_log = False
            self._y_axis_data = linear_y_data * self.total_power_mW / integral / delta_x

        elif self._y_axis_units == 'dBm':
            self.__data_is_log = True
            self._y_axis_data = 10 * np.log10(linear_y_data * self.total_power_mW / integral)

        elif self._y_axis_units == 'dBm/nm':
            self.__data_is_log = True
            self._y_axis_data = 10 * np.log10(linear_y_data * self.total_power_mW / integral / delta_x)

        elif self._y_axis_units == 'nJ':
            self.__data_is_log = False
            self._y_axis_data = linear_y_data * self._pulse_energy_nJ / integral

        elif self._y_axis_units == 'dBnJ':
            self.__data_is_log = True
            self._y_axis_data = 10 * np.log10(linear_y_data * self._pulse_energy_nJ / integral)

        elif self._y_axis_units == 'nJ/nm':
            self.__data_is_log = False
            self._y_axis_data = linear_y_data * self._pulse_energy_nJ / integral / delta_x

        elif self._y_axis_units == 'dBnJ/nm':
            self.__data_is_log = True
            self._y_axis_data = 10 * np.log10(linear_y_data * self._pulse_energy_nJ / integral / delta_x)


def readFromFiles(path, pattern='*.csv', skip_header=40):
    data_list = []
    files = path.glob(pattern)
    filepaths = natsorted([file for file in files], key=lambda f: str(f.name))
    for filepath in filepaths:
        data_list.append(np.genfromtxt(filepath, invalid_raise=False, skip_header=skip_header,
                                       delimiter=',', comments='"'))
    return data_list, filepaths
