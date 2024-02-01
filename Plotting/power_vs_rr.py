import numpy as np
from utils.spectrometerdata import readFromFiles
import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv('/home/mike/Documents/Data/1-23-24 SHG vs. rep rate/1-23-24 SHG Power vs. Rep. rate - Sheet1.csv')
lam= [700, 730, 795]
for x, label in enumerate(data['Polling period (um)'].dropna().drop_duplicates()): 
    plot_data = data[data['Polling period (um)'] == label]
    plt.scatter([float(i) for i in plot_data['Rep rate (n * frep)']], [float(i) for i in plot_data['SH power (mW)']],
                label=f'{label} $\mu$m : $\lambda$={lam[x]} nm')
    plt.ylabel('Power (mW)')
    plt.xlabel('Repetition Rate (x 60.56 MHz)')
    plt.legend()

plt.show()