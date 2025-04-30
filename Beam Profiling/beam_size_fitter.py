import numpy as np
import pandas as pd
from pathlib import Path
from scipy.optimize import curve_fit, Bounds
import matplotlib.pyplot as plt 

# Beam radius
def gaussian_beamsize_M2_um(z_mm, z0_mm, w0_um, M2, wavelength_nm = 1550):
    zR_um = np.pi *  w0_um ** 2 / (wavelength_nm / 1000)
    # return w0_um * np.sqrt(1 + (1000 * (z_mm - z0_mm) / zR_um) ** 2)
    return np.sqrt(w0_um**2 + M2**2 *(wavelength_nm/1000/(np.pi*w0_um))**2 * (1e3*(z_mm-z0_mm))**2)

def gaussian_beamsize_um(z_mm, z0_mm, w0_um, wavelength_nm = 1550):
    zR_um = np.pi *  w0_um ** 2 / (wavelength_nm / 1000)
    return w0_um * np.sqrt(1 + (1000 * (z_mm - z0_mm) / zR_um) ** 2)

filepath = Path("/home/mike/Documents/Boulder_PhD/Data/3-21-25 OAP Msquared/M2_scan.csv")
data = pd.read_csv(filepath)
z_positions_data_mm = data['z (mm)']

radius_data_x_um = data['1/e^2 Clip x (um)']/2
radius_data_y_um = data['1/e^2 Clip y (um)']/2

poptx, pcovx = curve_fit(gaussian_beamsize_M2_um, xdata=z_positions_data_mm, ydata=radius_data_x_um, p0=(3, 15,1), bounds=([3, 0, 1], [3.5,np.inf,np.inf]))
popty, pcovy = curve_fit(gaussian_beamsize_M2_um, xdata=z_positions_data_mm, ydata=radius_data_y_um, p0=(3, 15,1), bounds=([3, 0, 1], [3.5, np.inf, np.inf]))

# print(f'Waist location: {popt[0]} mm')
# print(f'Waist size: {popt[1]} um')

z_array_mm = np.linspace(min(z_positions_data_mm), max(z_positions_data_mm), 1000)

plt.plot(z_array_mm, gaussian_beamsize_M2_um(z_array_mm, poptx[0], poptx[1],poptx[2]), color='r', label=fr'X-axis: $w_0$ = {poptx[1]: .2f} $\mu$m' f'\n $z_0$ = {poptx[0]: .2f} mm' f'\n $M^2$ = {poptx[2]: .2f}')
plt.plot(z_array_mm, gaussian_beamsize_M2_um(z_array_mm, popty[0], popty[1],popty[2]), color='b', label=fr'Y-axis: $w_0$ = {popty[1]: .2f} $\mu$m' f'\n $z_0$ = {popty[0]: .2f} mm' f'\n $M^2$ = {popty[2]: .2f}')
plt.scatter(z_positions_data_mm, radius_data_x_um, color='r')
plt.scatter(z_positions_data_mm, radius_data_y_um, color='b')
plt.xlabel('z (mm)')
plt.ylabel(r'w ($\mu$m)')
plt.title("Waist Radius vs. Position")
plt.grid()
plt.legend()
plt.tight_layout()
plt.show()