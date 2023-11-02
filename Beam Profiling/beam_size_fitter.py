import numpy as np
from scipy.optimize import curve_fit, Bounds
import matplotlib.pyplot as plt 

def gaussian_beamsize_um(z_mm, z0_mm, w0_um, wavelength_nm = 1550):
    zR_um = np.pi *  w0_um ** 2 / (wavelength_nm / 1000)
    return w0_um * np.sqrt(1 + (1000 * (z_mm - z0_mm) / zR_um) ** 2)


z_positions_data_cm = np.array([10.6,
15.7,
51.3,
74])

radius_data_um = np.array([1085,
1097.5,
1166.5,
1213])

z_positions_data_mm = 10 * z_positions_data_cm


popt, pcov = curve_fit(gaussian_beamsize_um, xdata=z_positions_data_mm, ydata=radius_data_um, p0=(0, 1000), bounds=([-np.inf, 0], np.inf))

print(f'Waist location: {popt[0]} mm')
print(f'Waist size: {popt[1]} um')

z_array_mm = np.linspace(- 2 * max(z_positions_data_mm), 2 * max(z_positions_data_mm), 1000)

plt.plot(z_array_mm, gaussian_beamsize_um(z_array_mm, popt[0], popt[1]), color='r', label=fr'$w_0$ = {popt[1]: .2f} $\mu$m' f'\n $z_0$ = {popt[0]: .2f} mm')
plt.scatter(z_positions_data_mm, radius_data_um)
plt.xlabel('z (mm)')
plt.ylabel(r'w ($\mu$m)')
plt.legend()
plt.tight_layout()
plt.show()