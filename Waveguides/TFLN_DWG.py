# -*- coding: utf-8 -*-
"""
Created on Fri Aug 28 15:29:15 2026

@author: sw8sk

This script simulates a waveguide that is unpoled entirely. Here, we are trying
to simulate efficient dispersive wave generation.

This script is modeled after an actually more complex script (TFLN_DWG_to_SHG)
so if there is mention of poling anywhere here it is leftover from that.

-Skyler Weight

"""

# %% Imports
import os
import json
from datetime import datetime
import time
from pathlib import Path
import numpy as np
from scipy.constants import pi, c
from matplotlib import pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.widgets import Slider, RadioButtons
import matplotlib as mpl
mpl.rcParams['axes.linewidth'] = 3
plt.close('all')
import pynlo
from pynlo import utility as ut
from scipy.interpolate import UnivariateSpline

# Used later for plotting (Ai-generated)
def thz_to_nm(freq_thz):
    with np.errstate(divide='ignore'):
        return c / (1000 * freq_thz)

def nm_to_thz(wvl_nm):
    with np.errstate(divide='ignore'):
        return c / (1000 * wvl_nm)

#%% Define simulation and file information

# Define a current timestamp to precede the simulation/file name
timestamp = datetime.now().strftime("%Y_%m_%d_%Hhr%Mmin%Ssec")
simulation_name = f"{timestamp}_PyNLO_TFLN_DWG"

# %% Setup Constants / Nonlinearities
"""
What the code is doing:
    
    - Import the mode effective index and area from Tody3D simulations
    - Calculation of beta from the the effective index
    - Input of chi-2 and chi-3 nonlinearities
            - d33 is found from the from the 
              Nonlinear_coeff_Millers_delta_scaling.py script. That script
              finds d33 at 1600 nm. Details are found in that script.
              
            - The 2nd-order nonlinear parameter is found from the pynlo g2_shg
              function found in the utility.chi2 submodule
              
            - The g2_shg function is "weighted for second-harmonic generation"
            
            - The Kerr nonlinearity is found from the paper titled 
              "Integrated photonics on thin-film lithium niobate" by Zhu 2021.
              The value is for light at 1550nm.
              
            - I use the built-in gamma_to_g3 function in chi-3 utility
              submodule. I am following Connors "optical_solitons" example as a
              template.
-------------------------------------------------------------------------------
What I am unsure about:
    
    2nd-order nonlinearity
        - Currently I only input a single d33 value which is the value at
          1600nm. A better option is an array across the entire frequency
          bandwidth.
        - Should the g2_shg function be "weighted" differently? What effects
          would this have?
        - What is g2?
    3rd-prder nonlinearity
        - Same as d323 above --> n2 is the value at 1550nm, but a better option
          is n2 for the entire frequency badnwidth.
        - What is g3?
"""

# First we need to get the data from the mode simulation
tidy3d_folder_path = Path(r"C:\Users\sw8sk\OneDrive\Documents\Academics\Diddams Lab\Blue light generation\Tidy3D (use in Tidy3D-ENV)")
tidy3d_simulation_name = "2026_09_28_10hr39min58sec_Tidy3D_wavelength_sweep_v2_800to400"
tidy3d_target_folder = tidy3d_folder_path / tidy3d_simulation_name

data = {}

# Loop through the target folder
for file_path in tidy3d_target_folder.iterdir():
    
    if file_path.name == "parameters.json":
        with open(file_path, "r") as f:
            data["params"] = json.load(f)
            
    elif file_path.suffix == ".npy":
        # .stem gets the filename without the .npy extension automatically
        data[file_path.stem] = np.load(file_path)

# %% Pulse Properties
"""
What the code is doing:
    
    - Input of nnumber of points, max/min frequencies
    - Input of pulse parameters
    - Creation of sech pulse with the pynlo.light submodule

-------------------------------------------------------------------------------
What I am unsure about:
    
    - The "alias" parameter
        - Should it be 1, 2, or 3? Why?
    
"""
# Get wavelength array from Tidy3D
tidy3d_wvl_m = data['wvl_nm']*1e-9
tidy3d_v_Hz = np.flipud(c/tidy3d_wvl_m)

# Get effective index and area from Tidy3D
if "width" in tidy3d_simulation_name:
    width_index = 7
    n_eff = data['n_eff_TE00_all'][:,width_index]
    a_eff = data['a_eff_ref'][:,width_index]
    wg_width_um = data['params']['wg_widths_um'][width_index]
else:
    n_eff = data['n_eff_TE00']
    a_eff = data['a_eff_ref']

n_points = 2**13 # number of frequency points in simulation
v_min_extra = 50e12
v_min = tidy3d_v_Hz[0] - v_min_extra # minimum frequency in Hz from Tidy3D simulation
v_max_extra = 50e12
v_max = tidy3d_v_Hz[-1] + v_max_extra # maximum frequency in Hz from Tidy3D simulation
v0 = c/1580e-9 # center frequency of pulse in Hz from wavelength in m

# The following number comes from: 145 mW out of RHS lensed fiber on sphere -->
# --> 80% lower --> actual --> ~180 mW --> 6 dB input coupling loss --> 45 mW
# --> 450 pJ from https://www.lasercalculator.com/pulse-train-calculator/
# The actual numnber is likley higher since 6 dB probably includes a fair
# amount of propagation loss, not just coupling loss
e_p = 100e-12 # pulse energy in J --> 450 pJ
t_fwhm = 75e-15 # pulse width/duration in s (from FROG trace)

# Decide the shape of the pulse (just comment out the other line)
# pulse_type = 'Gaussian'
pulse_type = 'Sech'

# Create the pulse using the pynlo.light submodule

if pulse_type == 'Sech':
    pulse = pynlo.light.Pulse.Sech(n_points, v_min, v_max, v0, e_p, t_fwhm, alias = 2)
elif pulse_type == 'Gaussian':
    pulse = pynlo.light.Pulse.Gaussian(n_points, v_min, v_max, v0, e_p, t_fwhm)
else:
    print('Error: Incorrect pulse shape selected')
    
# It is worth looking at an plot of the FROG trace and overlaying a sech or
# gaussian pulse over it to see which shape my actual pulse looks like

# Get a_eff values from Tidy3D simulations (make sure the wavelength/frequency arrays lineup)
a_eff_spl = UnivariateSpline(tidy3d_v_Hz, np.flipud(a_eff), s=1e-11, k=5)
a_eff = a_eff_spl(pulse.v_grid)*1e-6*1e-6 # want in m^2

# Get n_eff values from Tidy3D simulations (again, make sure frequency lines up)
n_eff_spl = UnivariateSpline(tidy3d_v_Hz, np.flipud(n_eff), s=1e-11, k=5)
n_eff = n_eff_spl(pulse.v_grid)

# Propagation constant
beta = n_eff*2*pi*pulse.v_grid/c

# 2nd-order nonlinearity
d33 = 31.4e-12 # in m/V at 1600nm from Nonlinear_coeff_Millers_delta_scaling.py script
# NOTE: 21.4 pm/V is probably what you should use, some sources cite higher by almost 50%
d_eff = 2/pi*d33
chi2_eff = 2*d_eff

g2_fact = 1
g2 = ut.chi2.g2_split(n_eff, a_eff, chi2_eff)
g2 = g2_fact*g2

# 3rd-order nonlinearity
n2 = 1.8e-19
chi3_eff = ut.chi3.n2_to_chi3(n_eff,n2)

g3_fact = 1
g3 = ut.chi3.g3_spm(n_eff, a_eff, chi3_eff)
g3 = g3*g3_fact

# %% Model
"""
What the code is doing:
    
    - I actually have no idea
    
-------------------------------------------------------------------------------
Things I am unsure about:
    
    - What any of this is actually doing
    - I'm compoletely blind at this point

"""
length = 1e-3
mode = pynlo.medium.Mode(pulse.v_grid, beta, g2=g2, g2_inv=None, g3=g3)
model = pynlo.model.UPE(pulse, mode)

#---- Estimate step size
local_error = 1e-6
dz = model.estimate_step_size(local_error=local_error)


# %% Simulate
"""
What the code is doing:
    
    - Run/propagate the simulation
    - The output data is organized as follows:
    
        a_v: complex amplitude in terms of frequency
        a_t: complex amplitude in terms of time
        z: length array of the propagation
    
-------------------------------------------------------------------------------
Things I am unsure about:
    
    - What any of this is actually doing
    - The "pulse_out" variable
    - Here is what Conner says:
        
The model's `simulate` method runs the simulation. We input the total
propagation length, the initial step size, local error, and the number of
simulation steps we wish to record. We receive the output pulse and the
propagations distance, pulse spectrum, and complex envelope at each record
point. To view real-time simulation results (updated whenever the simulation
reaches a record point), set the `plot` keyword to "time", "frq", or "wvl".

"""

sim_start_time = time.time()

pulse_out, z, a_t, a_v = model.simulate(
    length, dz=dz, local_error=local_error, n_records=500, plot='wvl')

sim_end_time = time.time()
sim_time = sim_end_time - sim_start_time

#%% Organize results
"""
The results are organized as follows:

pulse.v_grid: frequency array
pulse.t_grid: time array
    
p_v_dB: power output in terms of frequency in dB
p_v_J: power output in terms of frequency in Joules/Hz (I think)
p_t_dB: power output in terms of time in dB

"""

# Find power in dB
p_v_dB = 10*np.log10(np.abs(a_v)**2)
p_v_dB -= p_v_dB[0,:].max() # normalize to max value in spectrum at START of waveguide (z=0)

p_t_dB = 10*np.log10(np.abs(a_t)**2)
p_t_dB -= p_t_dB[0,:].max()

# Conversion to other units (want to know at the output of waveguide, for now)
rep_rate = 100e6
e_density_output_J = np.abs(a_v[-1,:])**2             # J/Hz
p_density_output_W = e_density_output_J * rep_rate   # W/Hz
p_per_mode_output_W = p_density_output_W * rep_rate   # W/mode

# %% Plot Results
"""

These plots have not been update for awhile. They do the job but organizing
them and making them look better is a wirthwhile endeavor.
    
"""
# Custom display for wavelength and frequency coordinates
def custom_format_coord(x, y):
    wavelength = thz_to_nm(x) if x != 0 else np.inf
    return f'x={x:.2f} THz ({wavelength:.2f} nm), y={y:.2f}'

# Propagation slider
def update_z(val):
    idx = np.argmin(np.abs(z_mm - z_slider.val))
    line_v.set_ydata(p_v_dB[idx])
    line_t.set_ydata(p_t_dB[idx])
    z_line_v.set_ydata([z_mm[idx], z_mm[idx]])
    z_line_t.set_ydata([z_mm[idx], z_mm[idx]])
    fig1.canvas.draw_idle()

fig1 = plt.figure()
fig1.set_figheight(9)
fig1.set_figwidth(12)
fig1.suptitle('Simulation Results', fontsize = 18)
ax1 = plt.subplot2grid((3,2), (0, 0), rowspan=1)
ax2 = plt.subplot2grid((3,2), (0, 1), rowspan=1)
ax3 = plt.subplot2grid((3,2), (1, 0), rowspan=2, sharex=ax1)
ax4 = plt.subplot2grid((3,2), (1, 1), rowspan=2, sharex=ax2)

# ax1.plot((c/pulse.v_grid)*1e9, p_v_dB[0], color='blue', lw=1.5, label = 'Input')
# ax1.plot((c/pulse.v_grid)*1e9, p_v_dB[-1], color='green', lw=1.5, label = 'Output')

ax1.plot(1e-12*pulse.v_grid, p_v_dB[0], color='blue', lw=1.5, label='Input')
line_v, = ax1.plot(1e-12*pulse.v_grid, p_v_dB[-1], color='green', lw=1.5, label='Selected z')
ax1.set_ylim(bottom=-100, top=10)
ax1.set_ylabel('Power (dB)', fontsize=15)
ax1.grid()
ax1.legend()

# Put wavelength values on top of x-axis
sec_ax1 = ax1.secondary_xaxis('top', functions=(thz_to_nm, nm_to_thz))
sec_ax1.set_xlabel('Wavelength (nm)', fontsize=15)

ax3.sharex(ax1)
mesh3 = ax3.pcolormesh(1e-12*pulse.v_grid, 1e3*z, p_v_dB, vmin=-100.0, vmax=0, shading="auto", cmap='jet')
ax3.set_xlabel('Frequency (THz)', fontsize=15)
ax3.set_ylabel('Propagation Distance (mm)', fontsize=15)
z_line_v = ax3.axhline(1e3*z[-1], color='white', lw=1.5, linestyle='--')

# Custom wavelength ticks to align with frequency ticks
plt.draw()
primary_ticks = [t for t in ax1.get_xticks() if t > 0] 
sec_ax1.set_xticks(thz_to_nm(np.array(primary_ticks)))
sec_ax1.xaxis.set_major_formatter(ticker.FormatStrFormatter('%.0f'))

ax1.format_coord = custom_format_coord
ax3.format_coord = custom_format_coord

ax2.plot(1e12*pulse.t_grid, p_t_dB[0], color='blue', lw=1.5, label = 'Input')
line_t, = ax2.plot(1e12*pulse.t_grid, p_t_dB[-1], color='green',lw=1.5, label = 'Selected z')
ax2.set_ylim(bottom=-100, top=10)
ax2.grid()
ax2.legend()

ax4.sharex(ax2)
mesh4 = ax4.pcolormesh(1e12*pulse.t_grid, 1e3*z, p_t_dB, vmin=-100.0, vmax=0, shading="auto",cmap='jet')
ax4.set_xlabel('Time (ps)', fontsize = 15)
z_line_t = ax4.axhline(1e3*z[-1], color='white', lw=1.5, linestyle='--')

plt.tight_layout()
fig1.subplots_adjust(bottom=0.12)

z_mm = 1e3*z
slider_ax = fig1.add_axes([0.20, 0.03, 0.60, 0.025])
z_slider = Slider(
    slider_ax,
    'Propagation Distance (mm)',
    z_mm[0],
    z_mm[-1],
    valinit=z_mm[-1]
)
z_slider.on_changed(update_z)

freq = 1e-12*pulse.v_grid
wvl = thz_to_nm(freq)

def toggle_axis(label):
    global mesh3

    use_wvl = (label == 'Wavelength')
    x = wvl if use_wvl else freq

    # Update 1D spectrum
    ax1.lines[0].set_xdata(x)
    line_v.set_xdata(x)

    # Update 2D spectrum
    mesh3.remove()
    mesh3 = ax3.pcolormesh(
        x, 1e3*z, p_v_dB,
        vmin=-100, vmax=0, shading='auto', cmap='jet'
    )

    # Update primary axis (always linear)
    ax1.set_xlim(x.min(), x.max())
    ax3.set_xlabel('Wavelength (nm)' if use_wvl else 'Frequency (THz)')

    # Update secondary axis (nonlinear conversion)
    sec_ax1.set_functions(
        (nm_to_thz, thz_to_nm) if use_wvl else (thz_to_nm, nm_to_thz)
    )
    sec_ax1.set_xlabel('Frequency (THz)' if use_wvl else 'Wavelength (nm)')
    sec_ax1.xaxis.set_major_locator(ticker.AutoLocator())

    fig1.canvas.draw_idle()

# Create radio buttons in bottom-right corner
radio_ax = fig1.add_axes([0.89, 0.015, 0.10, 0.075])
radio = RadioButtons(
    radio_ax,
    ['Frequency', 'Wavelength'],
    active=0
)

radio.on_clicked(toggle_axis)

# Plot the final spectrum in nW/mode, assuming -6dB output coupling loss
fig2, ax5 = plt.subplots(1, 1)
ax5.set_xlabel('Frequency (THz)',fontsize = 15)
ax5.set_ylabel('Power per Comb Mode (nW)', fontsize=15)
ax5.plot(pulse.v_grid/1e12, p_per_mode_output_W*1e9, linestyle='-', lw=1.5, color = 'blue')
ax5.grid()
ax5.format_coord = custom_format_coord
plt.tight_layout()

#%% Figure(s) for Scott --> can comment out
# from mpl_toolkits.axes_grid1 import make_axes_locatable

# fig2 = plt.figure()
# fig2.set_figheight(9)
# fig2.set_figwidth(12)

# ax5 = plt.subplot2grid((3, 1), (0, 0), rowspan=1)
# ax6 = plt.subplot2grid((3, 1), (1, 0), rowspan=2, sharex=ax5)

# ax5.plot(1e-12*pulse.v_grid, p_v_dB[0], color='blue', lw=1.5, label='Input')
# ax5.plot(1e-12*pulse.v_grid, p_v_dB[-1], color='green', lw=1.5, label='Output')
# ax5.set_ylim(bottom=-100, top=10)
# ax5.set_ylabel('Power (dB)', fontsize=15)
# ax5.grid()
# ax5.legend()

# mesh6 = ax6.pcolormesh(1e-12*pulse.v_grid, 1e3*z, p_v_dB, vmin=-100.0, vmax=0, shading="auto", cmap='jet')
# ax6.set_xlabel('Frequency (THz)', fontsize=15)
# ax6.set_ylabel('Propagation Distance (mm)', fontsize=15) 

# # --- ALIGNMENT FIX ---
# # Carve out space next to the top plot, but make it invisible
# div5 = make_axes_locatable(ax5)
# cax5 = div5.append_axes("right", size="5%", pad=0.1)
# cax5.axis('off') 

# # Carve out the exact same space next to the bottom plot for the colorbar
# div6 = make_axes_locatable(ax6)
# cax6 = div6.append_axes("right", size="5%", pad=0.1)
# cbar = fig2.colorbar(mesh6, cax=cax6)
# cbar.set_label('Power (dB)', fontsize=15)

# plt.tight_layout()

# fig3, ax7 = plt.subplots(1,1, figsize = (8,5))
# ax7.plot(1e-12*pulse.v_grid, p_v_dB[0], color='blue', lw=1.5, label = 'Input')
# ax7.plot(1e-12*pulse.v_grid, p_v_dB[-1], color='green', lw=1.5, label = 'Output')
# ax7.set_ylim(bottom=-100, top=10)
# ax7.set_ylabel('Power (dB)', fontsize = 15)
# ax7.grid()
# ax7.legend()

# fig4, ax8 = plt.subplots(1,1, figsize = (10,5))
# mesh8 = ax8.pcolormesh(1e-12*pulse.v_grid, 1e3*z, p_v_dB, vmin=-100.0, vmax=0, shading="auto",cmap='jet')
# ax8.set_xlabel('Frequency (THz)', fontsize = 15)
# ax8.set_ylabel('Propagation Diastance (mm)', fontsize = 15)
# cbar8 = fig2.colorbar(mesh8, ax=ax8)
# cbar8.set_label('Power (dB)', fontsize=15)

#%% Conversion efficiency calculation

efficiency_cutoff = 1000 # wavelength in nm. Below which efficiency is found

mask_UV = pulse.v_grid > c/(efficiency_cutoff/1e9)

p_in = np.abs(a_v[0])**2
p_out = np.abs(a_v[-1])**2

pump_energy = np.trapezoid(p_in, pulse.v_grid)
masked_energy = np.trapezoid(p_out[mask_UV],pulse.v_grid[mask_UV])
out_energy = np.trapezoid(p_out, pulse.v_grid)

conv_efficiency = masked_energy/pump_energy

#%% Save simulation parameters

simulation_parameters = {
    "num_freq_points": n_points,
    "min_freq_THz": f"{v_min/1e12:0.1f}",
    "max_freq_THz": f"{v_max/1e12:0.1f}",
    "center_freq_THz": f"{v0/1e12:0.1f}",
    "pulse_energy_pJ": e_p*1e12,
    "pulse_width_fs": t_fwhm*1e15,
    "pulse_type": pulse_type,
    "Tidy3D_sim_folder": tidy3d_simulation_name,
    "chi2_used_pm_per_V": f"{chi2_eff*1e12:0.1f}",
    "g2_factor_used": g2_fact,
    "n2_used_m^2_per_W": n2,
    "g3_factor_used": g3_fact,
    "total_waveguide_length_mm": length*1e3,
    "local_error": local_error,
    "Conversion_efficiency_%": f"{conv_efficiency*100:0.3f}",
    "Efficency_cutoff_nm": efficiency_cutoff
    }

os.makedirs(simulation_name, exist_ok=True)
fig1.savefig(os.path.join(simulation_name, "Summary.png"), dpi=300)
fig2.savefig(os.path.join(simulation_name, "Output Power (per mode).png"), dpi=300)

with open(os.path.join(simulation_name, "parameters.json"), "w") as f:
    json.dump(simulation_parameters, f, indent=4)

np.save(os.path.join(simulation_name, "freq_Hz.npy"), pulse.v_grid)
np.save(os.path.join(simulation_name, "p_v_dB.npy"), p_v_dB)
np.save(os.path.join(simulation_name, "time_s.npy"), pulse.t_grid)
np.save(os.path.join(simulation_name, "p_t_dB.npy"), p_t_dB)
np.save(os.path.join(simulation_name, "p_per_mode_W.npy"), p_per_mode_output_W)
np.save(os.path.join(simulation_name, "z_m.npy"), z)

print(f"Data successfully saved to {simulation_name}")