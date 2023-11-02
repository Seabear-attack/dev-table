# open one csv file
import pandas as pd
import easygui as eg
import numpy as np
import matplotlib.pyplot as plt
import os
from utils.plotting_utils import openDirectory, directory_to_dataframes, get_spectrometer_data

if __name__ == "__main__":
    dfs = directory_to_dataframes(r'C:\Users\wahlm\Documents\School\Research\Allison\Tunable Pump\Polarization '
                                  r'Control\9-8-23 Spectra by Input Power\Varying pulse energy\Output 1', skiprows=44)

    labels = ('1.054 mW',
              '1.676 mW',
              '1.966 mW',
              '2.65 mW')
    data = get_spectrometer_data(dfs, data_labels=labels)

    # curve_labels = ['4x 1.15A', '4x 1.2A', '4x 1.25A', '4x 1.175A', '4x 1.2A', '4x 1.225A', '4x 1.25A']
    # curve_labels = ['a', 'b', 'c','d','e','f','g']
    curve_labels = range(14)
    # curve_labels = ['4x1A', '3x1 + 1x1.1A', '2x1 + 2x1.1A', '1x1 + 3x1.1A', '4x1.1A']
    curve_powers_mW = np.array([49, 56, 64, 72, 80, 87, 95, 102, 110, 117, 124, 132, 139, 146])
    # curve_powers_nJ = [4, 4, 4, 4, 4, 4]
    frep = 60.5  # MHz
    frep_eff = frep * np.array(range(14)) / 19
    curve_powers_nJ = curve_powers_mW / frep_eff
    while directory is not None:
        title, pulse_energy_nj = eg.multenterbox(fields=["Title", "Pulse energy (nJ)"])
        pulse_energy_nj = float(pulse_energy_nj)
        # loop through all files in the directory

        dfs = []
        for filename in filenames:
            # check if file ends with .csv or .txt
            if filename.endswith('.csv') or filename.endswith('.txt') or filename.endswith('.CSV'):
                df = pd.read_csv(os.path.join(directory, filename), skiprows=4)
                dfs.append(df)
            if filename.endswith('.xls') or filename.endswith('.xlsx'):
                df = pd.read_excel(os.path.join(directory, filename), sheet_name=1)
                dfs.append(df)

        # Create a figure and axis object using matplotlib
        fig, ax = plt.subplots(figsize=(20, 8))

        spectra = []
        top = 0
        for i in range(len(dfs)):
            if i > 0:
                df_new = dfs[i].iloc[:, :2]  # select first two column
                df_new_numeric = df_new.applymap(
                    lambda x: pd.to_numeric(x, errors='coerce')).dropna()  # select only numerical rows
                WaveLength = np.array(df_new_numeric.iloc[:, 0].values, dtype='float64')
                SpectrumIntensity = np.array(df_new_numeric.iloc[:, 1].values, dtype='float64')

                if SpectrumIntensity[int(len(SpectrumIntensity) / 2)] < 0:
                    SpectrumIntensity = np.power(10, SpectrumIntensity / 10)
                # Normalize, assume even sample spacing
                delta_lambda = WaveLength[1] - WaveLength[0]
                integral = np.sum(SpectrumIntensity)
                # SpectrumIntensity = SpectrumIntensity / integral * curve_powers_mW[i] / delta_lambda
                # SpectrumIntensity = SpectrumIntensity / integral * pulse_energy_nj / delta_lambda
                SpectrumIntensity = SpectrumIntensity / integral * curve_powers_nJ[i] / delta_lambda
                if max(SpectrumIntensity) > top:
                    top = max(SpectrumIntensity)

                spectra.append(np.array([WaveLength, SpectrumIntensity]))
                ax.plot(WaveLength, SpectrumIntensity, label=curve_labels[i])
        # Add axis labels and a legend
        ax.set_xlabel('wavelength (nm)')
        ax.set_ylabel('Spectral Energy per Pulse (nJ/nm)')
        ax.legend()
        ax.set_title(title)
        plt.semilogy()
        plt.ylim(top * 10 ** (-4), top)
        # Display the plot
        plt.show(block=False)
        plt.tight_layout()
        # response = eg.multenterbox(fields = ['Plot # (0 indexed)',
        #                            'Lower bound [nm]',
        #                            'Upper bound [nm]',
        #                            'Total power [mW]'])
        # while response is not None:
        #     spectrum = spectra[int(response[0])]
        #     lower = int(response[1])
        #     upper = int(response[2])
        #     power = int(response[3])
        #     integrate_power(spectrum, lower, upper, power)
        #     response = eg.multenterbox(fields=['Plot # (0 indexed)',
        #                                        'Lower bound [nm]',
        #                                        'Upper bound [nm]',
        #                                        'Total power [mW]'])
        directory, filenames = openDirectory(os.path.split(home_path))
