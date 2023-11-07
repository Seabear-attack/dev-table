import numpy as np
from scipy.special import erf
from findiff import FinDiff
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
# from scipy.integrate import quad
from scipy.stats import norm 

def knifeedge(x_um, intensity_e_sq_radius, center, max_power, offset):
    return max_power / 2 * (1 + erf((x_um - center) / (intensity_e_sq_radius / np.sqrt(2)))) + offset
if __name__ == "__main__":
    x_um = np.linspace(-10000, 10000, 100)
    stddev = 324
    middle = 500
    power = norm.cdf(x_um, loc=middle, scale=stddev) 

    popt, _ = curve_fit(knifeedge, x_um, power, ((max(x_um)-min(x_um))/2, np.mean(x_um),
                                                 max(power), min(power)))

    plt.scatter(x_um, power, alpha=.5)
    plt.plot(x_um, knifeedge(x_um, *popt), color='r', label=r'$\frac{1}{e^2}$ radius: ' f'{popt[0]: .0f} $\mu$m')
    #plt.scatter(x_um, power, alpha=.5)
    plt.xlabel(r'Position ($\mu$m)')
    plt.ylabel(r'Cumulative Power (W)')
    plt.legend()
    plt.show(block=False)
    plt.figure()
    plt.plot(x_um, norm.pdf(x_um, loc=middle, scale=stddev) / max(norm.pdf(x_um, loc=middle, scale=stddev)))
    plt.scatter(400, np.exp(-2))
    plt.show()
