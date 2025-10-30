import numpy as np
import matplotlib.pyplot as plt
from lmfit.models import VoigtModel, ConstantModel
from pathlib import Path
import pandas as pd
from scipy.constants import Boltzmann as k
from scipy.constants import speed_of_light as c
from scipy.constants import atomic_mass


datapath = Path(r'/home/mike/Documents/Data/rb_cepstral.csv')
data = pd.read_csv(datapath)
axis = data['Optical Axis (Hz)'].to_numpy()
spectrum = data[' Real Spectrum'].to_numpy()

# Experimental parameters
T = 273 + 30

mass_85 = atomic_mass * 84.911789732
mass_87 = atomic_mass * 86.909180520

# Rb87 D1 Transition
nu0_87D1 = 377.1074635e12
gamma_87D1 = 36.10e6/2
os_87D1 = .3420

# Rb85 D2 Transition
nu0_85D2 = 384.230406373e12
gamma_85D2 = 38.117e6/2
os_85D2 = 0.69577

d_PF4_85D2 = 100.357e6
d_PF3_85D2 = -20.503e6
d_PF2_85D2 = -83.955e6
d_PF1_85D2 = -113.307e6

d_SF3_85D2 = -1.2648885163e9
d_SF2_85D2 = 1.7708439228e9

# Calculate
nu_PF4_SF2_85D2 = nu0_85D2 + d_PF4_85D2 + d_SF2_85D2
nu_PF4_SF3_85D2 = nu0_85D2 + d_PF4_85D2 + d_SF3_85D2

nu_PF3_SF2_85D2 = nu0_85D2 + d_PF3_85D2 + d_SF2_85D2
nu_PF3_SF3_85D2 = nu0_85D2 + d_PF3_85D2 + d_SF3_85D2

nu_PF2_SF2_85D2 = nu0_85D2 + d_PF2_85D2 + d_SF2_85D2
nu_PF2_SF3_85D2 = nu0_85D2 + d_PF2_85D2 + d_SF3_85D2

nu_PF1_SF2_85D2 = nu0_85D2 + d_PF1_85D2 + d_SF2_85D2
nu_PF1_SF3_85D2 = nu0_85D2 + d_PF1_85D2 + d_SF3_85D2


# Rb87 D2 Transition
nu0_87D2 = 384.2304844685e12
gamma_87D2 = 38.11e6
os_87D2 = .6956

d_PF3_87D2 = 193.7408e6
d_PF2_87D2 = -72.9113e6
d_PF1_87D2 = -229.8518e6
d_PF0_87D2 = -302.0738e6

d_SF2_87D2 = -2.56300597908911e9
d_SF1_87D2 = 4.27167663181519e9

# Calculate
nu_PF3_SF1_87D2 = nu0_87D2 + d_PF3_87D2 + d_SF1_87D2
nu_PF3_SF2_87D2 = nu0_87D2 + d_PF3_87D2 + d_SF2_87D2

nu_PF2_SF1_87D2 = nu0_87D2 + d_PF2_87D2 + d_SF1_87D2
nu_PF2_SF2_87D2 = nu0_87D2 + d_PF2_87D2 + d_SF2_87D2

nu_PF1_SF1_87D2 = nu0_87D2 + d_PF1_87D2 + d_SF1_87D2
nu_PF1_SF2_87D2 = nu0_87D2 + d_PF1_87D2 + d_SF2_87D2

nu_PF0_SF1_87D2 = nu0_87D2 + d_PF0_87D2 + d_SF1_87D2
nu_PF0_SF2_87D2 = nu0_87D2 + d_PF0_87D2 + d_SF2_87D2

# Shifts


# D2 lists
D2_gammas = 8*[gamma_85D2] + 8*[gamma_87D2]
D2_os = 8*[os_85D2] + 8*[os_87D2]
D2_centers = [
    nu_PF4_SF2_85D2, nu_PF4_SF3_85D2, nu_PF3_SF2_85D2, nu_PF3_SF3_85D2, nu_PF2_SF2_85D2, 
    nu_PF2_SF3_85D2, nu_PF1_SF2_85D2, nu_PF1_SF3_85D2, nu_PF3_SF1_87D2, nu_PF3_SF2_87D2, 
    nu_PF2_SF1_87D2, nu_PF2_SF2_87D2, nu_PF1_SF1_87D2, nu_PF1_SF2_87D2, nu_PF0_SF1_87D2, nu_PF0_SF2_87D2]

D2_centers = np.array(D2_centers)
D2_sigmas = np.concatenate((D2_centers[:8] * np.sqrt(k * T / (mass_85 * c**2)),  D2_centers[8:] * np.sqrt(k * T / (mass_87 * c**2))))
print(D2_sigmas)

############################## D2 Fits ######################################3

mask = (axis >=384.225e12) & (axis <=384.237e12)
axis = axis[mask]
spectrum = spectrum[mask]
# ---------------------------
# Build composite Voigt model
# ---------------------------
n_lines = len(D2_centers)  # number of Voigt components to fit
model = ConstantModel(prefix='bkg_')  # background offset
params = model.make_params()

params['bkg_c'].set(value=1.1, min=1.05, max=1.15)

for i in range(n_lines):
    prefix = f'v{i}_'
    m = VoigtModel(prefix=prefix)
    model += m
    params.update(m.make_params())

    # Give reasonable starting guesses
    params[f'{prefix}amplitude'].set(value=-D2_os[i], max=0)
    params[f'{prefix}center'].set(value=D2_centers[i],vary=False)
    params[f'{prefix}sigma'].set(value=D2_sigmas[i], vary=False)
    params[f'{prefix}gamma'].set(value=D2_gammas[i], vary=False)

# ---------------------------
# Fit model to data
# ---------------------------
result = model.fit(spectrum, params, x=axis)

# ---------------------------
# Display results
# ---------------------------
print(result.fit_report())

plt.figure(figsize=(8, 5))
plt.plot(axis, spectrum, 'k.', label='data')
plt.plot(axis, result.best_fit, 'r-', label='best fit')

# Plot each individual component
cmap = plt.colormaps['hsv']
colors = cmap(np.linspace(0,1,1 + len(D2_centers)))
for i, x in enumerate(result.eval_components(x=axis).items()):
    name = x[0]
    comp = x[1]
    plt.plot(axis, comp, '--', label=name, color = colors[i])

plt.xlabel('Frequency (THz)')
plt.ylabel('Absorbance')
plt.legend()
plt.tight_layout()
plt.show()
