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
    x_um = np.linspace(0, 1500, 50)
    dx = x_um[1] - x_um[0]
    stddev = 324
    middle = 500
    power = np.power(norm.cdf(x_um, loc=middle, scale=stddev),1) 

    # Do the fit
    popt, _ = curve_fit(knifeedge, x_um, power, ((max(x_um)-min(x_um))/2, np.median(power),
                                                 max(power), min(power)))
    
    # Plot the fit against the raw data
    f, axs = plt.subplots(2, 1, figsize=(6, 6), sharex=True)
    axs[0].scatter(x_um, power, label='Data')
    axs[0].plot(x_um, knifeedge(x_um, *popt), color='r', label=r'Fit: $\frac{1}{e^2}$ radius = ' f'{popt[0]: .0f} $\mu$m')
    axs[0].set_ylabel(r'Cumulative Power (W)')
    axs[0].legend()
    axs[0].set_title('Fit of Raw Knife Edge Data')
    
    # calculate and the spatial profile against the derivative of the fit (i.e. the pdf)
    
    dp_dx = FinDiff(0, dx, 1)
    axs[1].scatter(x_um, dp_dx(power), marker='o', label='Spatial Profile')
    axs[1].plot(x_um, norm.pdf(x_um, loc=popt[1], scale=popt[0] / 2), 'r-', label=r'Fit: $\frac{1}{e^2}$ radius = ' f'{popt[0]: .0f} $\mu$m')
    axs[1].legend()
    axs[1].set_title('Fit vs. Calculated Spatial Profile')
    axs[1].set_xlabel(r'Position($\mu$m)')
    axs[1].set_ylabel('Spatial Power (arb.)')
    plt.tight_layout()
    plt.show()
