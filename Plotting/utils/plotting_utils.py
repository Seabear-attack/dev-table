import easygui as eg
import os
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.stats import mode


def openDirectory(dirName):
    directory = eg.diropenbox(default=dirName)
    filenames = os.listdir(directory)
    return directory, filenames


def directory_to_dataframes(directory, filenames=None, usecols=None, skiprows=None):
    if filenames is None:
        directory_path = Path(directory)
        filenames = os.listdir(directory_path)
    file_dfs = []
    for filename in filenames:
        if filename.endswith('.csv') or filename.endswith('.txt') or filename.endswith('.CSV'):
            df = pd.read_csv(directory / filename, header=None, usecols=usecols, skiprows=skiprows)
            file_dfs.append(df)
        elif filename.endswith('.xls') or filename.endswith('.xlsx'):
            df = pd.read_excel(directory / filename, sheet_name=1)
            file_dfs.append(df)
    return file_dfs


def get_scope_data(dfs, data_labels, axes_labels=('time_s', 'voltage_V')):
    data = {}
    for i, df in enumerate(dfs):
        new_df = df.iloc[:, 3:5]
        new_df.columns = axes_labels
        data.update({data_labels[i]: new_df})  # select the data columns
    return data


'''
Deprecated. Currently works for Yokogawa only. Needs updating for other spectrometer 
output file formats.
'''


def get_spectrometer_data(dfs, data_labels, axes_labels=('wavelength_nm', 'power_mW')):
    data = {}
    for i, df in enumerate(dfs):
        new_df = df.iloc[:, :2]
        new_df.applymap(
            lambda x: pd.to_numeric(x, errors='coerce')).dropna()
        new_df.columns = axes_labels
        if new_df['power_mW'][0] < 0:
            new_df['power_mW'] = np.power(10, new_df['power_mW'] / 10)
        data.update({data_labels[i]: new_df})  # select the data columns
    return data


def normalize_by_maximum(data, column):
    for df in data.values():
        try:
            df[column] = df[column] - mode(df[column])
        except:
            df[column] = df[column] - mode(df[column])[0]
        df[column] = df[column] / max(df[column])







def offset(data, column, constant_offset):
    for i, df in enumerate(data.values()):
        df[column] = df[column] + i * constant_offset


'''
Deprecated
'''
def integrate_power(spectrum_intensity, wl_lower_bound,
                    wl_upper_bound, total_pwr):
    # calculate the dispersive wave ratio to the total power
    wavelength = spectrum_intensity[0]
    spectrum_intensity = spectrum_intensity[1]
    section_power = np.sum(spectrum_intensity[((wavelength < wl_upper_bound) & (wavelength > wl_lower_bound))])
    integral_power = np.sum(spectrum_intensity)
    print('Power of the selected section: \t', total_pwr * (section_power / integral_power))
    print('Total power is: \t', total_pwr)
    print('The power ratio between dispersive wave and total power is: \t', section_power / integral_power)
    eg.msgbox(
        msg=f'Power in range {wl_lower_bound}-{wl_upper_bound}nm: \t {total_pwr * (section_power / integral_power):.1f} mW\n'
            f'Total power is: \t {total_pwr:.1f} mW\n'
            f'The power ratio between dispersive wave and total power is: \t {100 * section_power / integral_power:.1f}%')
