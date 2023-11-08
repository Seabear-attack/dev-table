import numpy as np
from findiff import FinDiff
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from scipy.stats import norm 


'''
Define the functional model of the knife edge measurement. Here we assume that the transverse profile is gaussian, so the knife edge should follow the integral of a gaussian (i.e. the cumulative distribution/cdf). Note that the 1/e^2 distance is equivalent to twice the standard deviation.
'''
def knifeedge(x_um, intensity_e_sq_radius, center, max_power, offset):
    return max_power * norm.cdf(x_um, loc=center, scale=intensity_e_sq_radius / 2) + offset


if __name__ == "__main__":
    x_um_data = np.array([17000,
        16900,
        16800,
        16700,
        16600,
        16500,
        16400,
        16300,
        16200,
        16100,
        16000,
        15900,
        15800,
        15700,
        15600,
        15500,
        15400,
        15300,
        15200,
        15100,
        15000,
        14900,
        14800,
        14700,
        14600,
        14500,
        14400,
        14300,
        14200,
        14100,
        14000,
        13900,
        13800,
        13700,
        13600,
        13500,
        13400,
        13300,
        13200,
        13100,
        13000,
        12900])
    x_um_interp = np.linspace(min(x_um_data), max(x_um_data), 1000)
    dx_data = x_um_data[1] - x_um_data[0]
    dx_interp = x_um_interp[1]-x_um_interp[0]
    stddev = 324
    middle = 500
    power = [1.9,
1.9,
1.9,
1.9,
1.9,
1.9,
1.85,
1.84,
1.84,
1.84,
1.84,
1.83,
1.82,
1.82,
1.81,
1.8,
1.78,
1.77,
1.75,
1.73,
1.72,
1.71,
1.68,
1.64,
1.6,
1.56,
1.5,
1.42,
1.34,
1.25,
1.14,
1.04,
0.95,
0.85,
0.73,
0.62,
0.53,
0.46,
0.39,
0.33,
0.28,
0.22]
    power = np.array(power)
    x_um_data = x_um_data[7:]
    power = power[7:]
    # Do the fit
    radius_guess = (max(x_um_data)-min(x_um_data))/2
    center_guess = x_um_data[power==np.median(power)][0]
    max_pow_guess = max(power)
    offset_guess = min(power)
    popt, _ = curve_fit(knifeedge, x_um_data, power, (radius_guess, center_guess, max_pow_guess, offset_guess))
    # , bounds=(((max(x_um)-min(x_um))/2, np.median(power)/1.5, max(power)/1.5, min(power)/1.5),
                                                                                #   ((max(x_um)-min(x_um))/2, np.median(power)*1.5, max(power)*1.5, min(power)*1.5))
    print(popt)
    # Plot the fit against the raw data
    f, axs = plt.subplots(2, 1, figsize=(6, 6), sharex=True)
    axs[0].scatter(x_um_data, power, label='Data')
    axs[0].plot(x_um_interp, knifeedge(x_um_interp, *popt), color='r', label=r'Fit: $\frac{1}{e^2}$ radius = ' f'{popt[0]: .0f} $\mu$m')
    axs[0].set_ylabel(r'Cumulative Power (W)')
    axs[0].legend()
    axs[0].set_title('Fit of Raw Knife Edge Data')
    
    # calculate and the spatial profile against the derivative of the fit (i.e. the pdf)
    
    dp_dx_data = FinDiff(0, dx_data, 1)
    dp_dx_interp = FinDiff(0,dx_interp, 1)
    axs[1].scatter(x_um_data, dp_dx_data(power), marker='o', label='Spatial Profile')
    axs[1].plot(x_um_interp, dp_dx_interp(knifeedge(x_um_interp, *popt)), 'r-', label=r'Fit: $\frac{1}{e^2}$ radius = ' f'{popt[0]: .0f} $\mu$m')
    axs[1].legend()
    axs[1].set_title('Fit vs. Calculated Spatial Profile')
    axs[1].set_xlabel(r'Position($\mu$m)')
    axs[1].set_ylabel('Spatial Power (arb.)')
    plt.tight_layout()
    plt.show()
