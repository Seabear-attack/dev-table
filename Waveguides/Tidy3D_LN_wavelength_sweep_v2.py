# -*- coding: utf-8 -*-
"""
Created on Wed Aug 19 13:59:14 2026

@author: sw8sk

This is a script that uses Tidy3D to simulate the modes of a lithium niobate 
waveguide across a broad spectrum.

It follows Tidy3D_LN_wavelength_sweep.py quite closely, but with a big new
functionality. In that previous script, I was having a lot of issues with
avoided mode crossings. These introduces kinks in the index curves that were
amplified heavily in the GV and GVD curves. To avoid that, thi script also
simulates some reference waveguide. This reference waveguide is designed to
not contain any avoided crossings (hopefully across the entire bandwidth),
giuving us a smooth TE00 mode. While not representative of actual simulations,
this reference is used to gap avoided crossings in the real simulation.

After doing both simulations, I take the mode field profle of the TE00 mode in
the reference simulation, and perform an overlap integral with two modes from
the actual simulation. These two modes from the actual simulation are the two
that engage in the avoided crossing, so one of them is the TE00 mode. Away
from the crossing, the overlap of the reference TE00 with the actual TE00 will
be high, and the actual TM10 (or whichever mode we are crossing with) will be
low. The two overlaps are normalized to sum to 1 (0.99, and 0.01 for example).
These values are then assigned as weights.

The beta value of the artificially curated TE00 mode is then found as a
weighted sum of the other two modes: beta_TE00 = W1*beta_mode0 + W2*beta_mode1
where mode0 is the TE00 mode in the actual simulation, and mode1 is the TM10
mode in the actual simulation (or whichever mode we are crossing with).

Away from the crossing, the weights are nearly 0 and 1. Right in the crossing,
the weights are 0.5 and 0.5.

A lot of this script is AI-generated, and I have not thoroughly gone through
all of it. As of now I have gotten up to the projections but not past that.

A lot of values and variables are calculated, plotted, and saved at the end. I
am not sure all of this is necessary but I will go through it later. This part
is still quite similar to the original sweep script.

"""

# General imports
import os
import json
from datetime import datetime
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from scipy.interpolate import UnivariateSpline
mpl.rcParams['axes.linewidth'] = 3
plt.close('all')

# Tidy3D imports
import tidy3d as td
import tidy3d.web as web
from tidy3d.plugins.mode import ModeSolver

inf = 100 # Used for infinite or semi-infinite shapes in Tidy3D
c = 299792458
n2 = 1.8e-19 # Kerr nonlinearity of LN

#%% File information

# Define a current timestamp to precede the simulation/file name
timestamp = datetime.now().strftime("%Y_%m_%d_%Hhr%Mmin%Ssec")
simulation_name = f"{timestamp}_Tidy3D_wavelength_sweep_v2"
simulation_name_actual = f"{simulation_name}_actual"
simulation_name_reference = f"{simulation_name}_reference"

# Setup paths for the big .hdf5 files
big_file_dir = r"./"
os.makedirs(big_file_dir, exist_ok=True)
big_file_path_actual = os.path.join(big_file_dir, f"{simulation_name_actual}.hdf5")
big_file_path_reference = os.path.join(big_file_dir, f"{simulation_name_reference}.hdf5")

#%% Define the lithium niobate as tidy3.Medium for the refractive index

# Liu 2025 (MgO-doped): This comes from the Tidy3D FastDispersionFitter
# which I use in the script titled "Tidy3D_index_fitter.py"

# Extraordinary index (same as Gayer):
    # max_num_poles (parameter in script) = 3
    # tolerance_rms (parameter in script) = 1e-2
    # Best weighted RMS (the results): 4.56e-07
    # Fit from 500-5000nm using 8192 points, Gayer says valid for 500-4000nm
    # For T = 24.5C such that the f parameter is 0
ln_mgo_e_Liu = td.PoleResidue(
	eps_inf=2.139141066138299, 
	poles=(((-23.276814678337484-9325009824101086j), (48.77457589129564+1.1232342215318052e+16j)),
        ((-116.99682921287327-150495103418244.66j), (-286.06867894536504+90704950811262.86j)),
        ((-70.90498206807679-3290363671202.472j), (287.41805950642805+7122770710863101j))), 
	frequency_range=(74.948e12,599.585e12))

# Ordinary index (different from Gayer):
    # max_num_poles (parameter in script) = 3
    # tolerance_rms (parameter in script) = 1e-2
    # Best weighted RMS (the results) = 2.99e-05 (4 poles does not reduce this)
    # Fit from 500-5000nm using 8192 points, Liu says valid for 500-10000nm
    # For T = 24.5C such that the f parameter is 0
ln_mgo_o_Liu = td.PoleResidue(
	eps_inf=1.0, 
	poles=(((-8731331.28055385-1.4275271648708018e+16j), (5668241.130995026+1.898785339734069e+16j)),
        ((-1302212.9780643438-7875767318328215j), (6953320.959890388+4862944734536151j)),
        ((-12.411965072287108-56871499210320.04j), (-0.7958053011457766+897898687001414.4j))), 
	frequency_range=(29.979e12,599.585e12))
# ln_mgo_Liu = td.AnisotropicMedium(xx=ln_mgo_e_Liu,yy=ln_mgo_o_Liu,zz=ln_mgo_o_Liu)
ln_mgo_Liu = td.material_library["LiNbO3"]["Zelmon1997"](2)

# Define SiO2 and air as tidy3d.Medium's for their bulk index
sio2 = td.material_library['SiO2']['Palik_Lossless']
# sio2 = td.material_library["FusedSilica"]["ZemaxSellmeier"]
air = td.Medium(permittivity = 1.006)

#%% Define my actual waveguide(s)

# Geometry
wg_width = 1.8
LN_thickness = 0.7
wg_height = 0.35
ln_slab_height = LN_thickness - wg_height
sidewall_angle = np.deg2rad(20)
sio2_height = 1
top_clad_height = 1
sim_Lx = 5
sim_Ly = sio2_height + ln_slab_height + wg_height + top_clad_height
sim_Lz = 0
bottom = -sim_Ly/2
top_sio2 = bottom + sio2_height
top_slab = top_sio2 + ln_slab_height
top_wg = top_slab + wg_height
wg_dx = wg_height*np.tan(sidewall_angle)
wg_vertices = [(-(wg_width/2 + wg_dx), top_slab),
               (-wg_width/2, top_wg),
               (wg_width/2, top_wg),
               (wg_width/2 + wg_dx, top_slab)]

# Material(s)
wg_material_actual = ln_mgo_Liu
wg_material_reference = ln_mgo_e_Liu

top_clad_material = 'air'

if top_clad_material == 'air':
    background_material = air
elif top_clad_material == 'sio2':
    background_material = sio2

# Define the wavelength grid to simulate
wvl_nm_start = 350
wvl_nm_end = 2000
wvl_nm = np.linspace(wvl_nm_start,wvl_nm_end,256)

# Define the frequency organized with wavelength (so this variable is DESCENDING)
frequency_Hz = c/(wvl_nm/1e9)

# Frequencies are supplied to Tidy3D in ASCENDING frequency order
solver_frequency_Hz = np.flipud(frequency_Hz)

# Angular frequency in ascending order
omega = 2*np.pi*solver_frequency_Hz
pump_wvl_nm = 1600
center_omega = 2*np.pi*c/(pump_wvl_nm*1e-9)

#%% Prepare the simulation

min_steps_per_wvl = 15 # determines the transverse spatial resolution (15+ for accurate simulations)
num_modes_actual = 4 # number of modes to simulate in the real simulation
num_modes_reference = 1 # number of modes in the reference simulation
reference_mode_index = 0 # Index of the TE00 at the lowest frequency (overlap tracking keeps this label)

# Define the symmetry of the real and reference waveguides
symmetry_actual = (-1,0,0) # symmetric across x, not y
symmetry_reference = (-1,0,0) # symmetric across x and y (idk why they are -/+)

# Define the simulation grid based on the resolution
grid_wavelength_um = 0.4
grid_spec_actual = td.GridSpec(
    grid_x=td.AutoGrid(min_steps_per_wvl=min_steps_per_wvl),
    grid_y=td.AutoGrid(min_steps_per_wvl=min_steps_per_wvl),
    grid_z=td.UniformGrid(dl=0.01),
    wavelength = grid_wavelength_um)

# I do not really know what this is but I define it based on tidy3d's reccomendation
run_time = 2*(sim_Lx/1e6)*3/c + 0 # (a few)*(largest domain dimension)*(group index)/c + (source_time)

# Specify perfectly matched layers (absorbing) boundaries in x and y, then periodic in z (though z should not matter)
boundary_spec = td.BoundarySpec(
    x=td.Boundary.pml(50),
    y=td.Boundary.pml(50),
    z = td.Boundary.periodic())

# Define strings of the boundary conditions to save later
BC_x = boundary_spec.x.plus.type
BC_y = boundary_spec.y.plus.type
BC_z = boundary_spec.z.plus.type

# Define the transverse plane to view
plane = td.Box(center=(0, 0, 0), size=(sim_Lx, sim_Ly, sim_Lz))

# Filter modes by highest n_eff value (mode 0 is highest, mode 1 is 2nd, etc.)
mode_sort = td.ModeSortSpec(track_freq = 'lowest')

mode_spec = td.ModeSpec(num_modes=num_modes_actual,
                        sort_spec=mode_sort,
                        precision = 'double')
mode_spec_reference = td.ModeSpec(num_modes=num_modes_reference,
                                  sort_spec=mode_sort,
                                  precision = 'double')

#%% Build the geometry

# Create the sio2
sio2_clad = td.Structure(
    geometry=td.Box.from_bounds(rmin=(-inf,-inf,-inf),
                                rmax=(inf,top_sio2,inf)),
    medium=sio2,
    name = 'SiO2_bottom_clad')

# Create the unetched lithium niobate slab
ln_slab_actual = td.Structure(
    geometry=td.Box.from_bounds(rmin=(-inf,top_sio2,-inf),
                                rmax=(inf,top_slab,inf)),
    medium=wg_material_actual,
    name = 'LN_actual_slab')

# Create the waveguide core
wg_core_actual = td.Structure(geometry=td.PolySlab(vertices=wg_vertices, axis=2,
                                              slab_bounds=(-td.inf, td.inf),
                                              reference_plane="top"),
                          medium = wg_material_actual,
                          name = 'LN_actual_waveguide')

# Create the reference waveguide (non-birefringent LN, same geometry)
ln_slab_reference = td.Structure(
    geometry=td.Box.from_bounds(rmin=(-inf,top_sio2,-inf),
                                rmax=(inf,top_slab,inf)),
    medium=wg_material_reference,
    name = 'LN_reference_slab')
wg_core_reference = td.Structure(geometry=td.PolySlab(vertices=wg_vertices, axis=2,
                                              slab_bounds=(-td.inf, td.inf),
                                              reference_plane="top"),
                          medium = wg_material_reference,
                          name = 'LN_reference_waveguide')

# Setup the real simulation
sim_actual = td.Simulation(
    size=(sim_Lx, sim_Ly, sim_Lz),
    grid_spec=grid_spec_actual,
    structures=[sio2_clad,ln_slab_actual,wg_core_actual],
    run_time=run_time,
    boundary_spec=boundary_spec,
    symmetry = symmetry_actual,
    medium = background_material) # this last one is the background medium

# Use the same grid in the reference as used in the real
grid_spec_reference = td.GridSpec.from_grid(sim_actual.grid)

# Setup the reference simulation
sim_reference = td.Simulation(
    size=(sim_Lx, sim_Ly, sim_Lz),
    grid_spec=grid_spec_reference,
    structures=[sio2_clad,ln_slab_reference,wg_core_reference],
    run_time=run_time,
    boundary_spec=boundary_spec,
    symmetry = symmetry_reference,
    medium = background_material)

# Preview both geometries before moving on
fig_geometry, (ax_actual,ax_reference) = plt.subplots(1, 2, figsize=(11,5))
sim_actual.plot(z=0, ax=ax_actual)
ax_actual.set_title('Actual waveguide')
sim_reference.plot(z=0, ax=ax_reference)
ax_reference.set_title('Reference waveguide')
plt.tight_layout()
plt.show(block = True)

#%% Target wavelengths to save fields if desired

# # Create target wavelengths:
#     # These are wavelengths for which we save the spatial mode profile to be saved and viewed
#     # Currently I am doing this every 50nm but it could be whatever
#     # We then define their inidices in the array and a dict to describe them
# target_wvls = np.array([400,500,600,1000,1600])
# target_indices = [int(np.argmin(np.abs(wvl_nm - tw))) for tw in target_wvls]
# target_dict = {idx: int(np.round(wvl_nm[idx])) for idx in target_indices}

# # Initialize where we will save the field array data
# fields = {}

#%% Setup the solvers

# Setup the real and reference solvers. Colocated fields are used for the mode
# overlap integral. Both simulations use the exact same frequency array.
solver_actual = ModeSolver(
    simulation=sim_actual,
    plane=plane,
    mode_spec=mode_spec,
    freqs=solver_frequency_Hz,
    colocate=True)

solver_reference = ModeSolver(
    simulation=sim_reference,
    plane=plane,
    mode_spec=mode_spec_reference,
    freqs=solver_frequency_Hz,
    colocate=True)

#%% Run both simulations through the cloud

solver_start_time = time.time() # start a timer

# Run the real-waveguide solver
# All data stored in mode_data which is HUGE
mode_data_actual = web.run(
    solver_actual,
    task_name=simulation_name_actual,
    path=big_file_path_actual,
    folder_name=simulation_name)

solver_actual_end_time = time.time()
solver_actual_time = solver_actual_end_time - solver_start_time

# Run the reference-waveguide solver
mode_data_reference = web.run(
    solver_reference,
    task_name=simulation_name_reference,
    path=big_file_path_reference,
    folder_name=simulation_name)

solver_reference_end_time = time.time() # end the timer
solver_reference_time = solver_reference_end_time - solver_actual_end_time

solver_time = solver_reference_end_time - solver_start_time # total time for both simulations

#%% Extract spatial field data if desired

# This loop is used to extract the spatial field data from each mode
# for idx, clean_key in target_dict.items():
#     fields[clean_key] = {}
    
#     # Extract spatial coordinates just once per frequency
#     base_slice = mode_data.Ex.isel(mode_index=0, f=idx).squeeze()
#     fields[clean_key]['x'] = base_slice.x.to_numpy()
#     fields[clean_key]['y'] = base_slice.y.to_numpy()
    
#     # 3. Inner loop for modes 0, 1, and 2
#     for m in range(num_modes): 
#         Ex_slice = mode_data.Ex.isel(mode_index=m, f=idx).squeeze()
#         Ey_slice = mode_data.Ey.isel(mode_index=m, f=idx).squeeze()
        
#         # Save nested under the specific mode
#         fields[clean_key][f'mode_{m}'] = {
#             'Ex': Ex_slice.to_numpy(),
#             'Ey': Ey_slice.to_numpy()}

#%% Extract the desired data from mode_data of each simulation

extraction_time = time.time()

# Turn the needed data into a dataframe
df_actual = mode_data_actual.to_dataframe().reset_index()
df_reference = mode_data_reference.to_dataframe().reset_index()

extraction_time = time.time() - extraction_time

# Extract some important parameters
to_keep = ['mode_index', 'n eff', 'mode area']
df_actual = df_actual[to_keep]
df_reference = df_reference[to_keep]

#%% Project the physical modes onto the reference TE00 mode

projection_time = time.time()

# Compute E/H field overlap between the actual modes and the reference modes
"""
The integral is calculated using a power-flux based overlap. An ordinary
overlap integral does overlap = integral(E1_star*E2*dA). Tidy3D's outer_dot
function does...
    
 overlap = 1/4*integral{[(Ei^a_star X Hr_j) + (Ej^r X Hi^a_star)] dot zhat*dA}
 
essentially. Only tangential components (x and y) are used. More here:
    https://docs.flexcompute.com/projects/tidy3d/en/latest/_modules/tidy3d/components/data/monitor_data.html#ElectromagneticFieldData.outer_dot

This variable (overlap_actual_reference) is shaped as:
    (x,y,z) = (num_wavelengths, num_actual_modes, num_references_modes)
    
Each entry is the overlap integral at x frequency index between actual mode
index y and reference mode index z. x is the actual mode because we did
mode_data_ACTUAL.outer_dot(mode_data_REFERENCE).

In other words, that variable contains x 2x2 matrices. The 1st entry of that
2x2 matrix is the overlap between actual mode 0 and reference mode 0, the 2nd
(top right) is actual mode 0 with reference mode 1. The 3rd (bottom-left) is
actual mode 1 with reference mode 1.

We do not really need the overlap between reference mode 1 (as that one does
not represent TE00), but it is calcuated anyway.

We then isolate the overlap between the actual modes and TE00 reference mode.
"""
overlap_actual_reference = mode_data_actual.outer_dot(
    mode_data_reference,
    conjugate=True).to_numpy()

# This next line is isolating the overlap with just the single TE00 reference
overlap_amplitude = overlap_actual_reference[:,:,reference_mode_index]

# Compute E/H field self-overlaps
"""
This step serves as a normalization check. Obviously, the self overlaps should
be 1, as Tidy3D normalizes the fields before they're returned, but this just
makes sure small devations due to interpolation or numerical errors do not
affect the final projection weights.

Again, these variables (overlap_actual_actual and overlap_reference_reference)
are x 2x2 arrays. The diagonal entries should be very close to 1 and off 
diagonal entries should be very close to 0. We don't need the off-diagonal
entries, so we then isolate the diagonal ones.

(The arrays are 2x2 if num_actual_modes and num_reference_modes are both 2).

We do this for both the actual and reference simulations.

We also do this for all reference modes, but we don't need the one that does
not represent the TE00 mode. When we take the product of the two norms, we
only take the self-overlap of the reference TE00 mode. We call that product
normalization_denominator.

Normalization_denominator is a (x=num_wavelengths, y=num_actual_modes) array
with entries correspdonding to the product of self-overlaps between the actual
modes and the reference TE00 mode.
"""
overlap_actual_actual = mode_data_actual.outer_dot(
    mode_data_actual,
    conjugate=True).to_numpy()
overlap_reference_reference = mode_data_reference.outer_dot(
    mode_data_reference,
    conjugate=True).to_numpy()

# Here is where we isolate the diagonal entries
actual_mode_norm = np.abs(np.diagonal(
    overlap_actual_actual,
    axis1=1,
    axis2=2))
reference_mode_norm = np.abs(np.diagonal(
    overlap_reference_reference,
    axis1=1,
    axis2=2))

# Here is where we take the product of norms and isolate the reference TE00
normalization_denominator = (
    actual_mode_norm*
    reference_mode_norm[:,reference_mode_index,None])

# Calculate projection weights
"""
We first calculate projection_power_raw, which is just the overlaps between
the actual modes and TE00 reference mode (squared) divided by the normalization
factor found just above. The 1e-30 is just to prevent division by 0. This
variable is shaped (x=num_wavelengths, y=num_actual_modes) with each entry
corresponding to the normalized overlap of each actual mode with the reference
TE00 mode at each wavelength/frequency.

We then take the sum at each wavelength/frequency. This is what we call
projection_completeness. This is a num_wavelengthsx1 array with each entry
representing how much the reference TE00 mode lies within the subspace spanned
by the actual modes. In other words, how well can a linear combination of the
actual mode field profiles can recreate the reference TE00 mode. A value of 1
means the reference TE00 mode is spanned perfectly by the subspace of the
actual modes, while a value of 0 means the reference TE00 mode is not well-
represented at all by the subspace of the actual mode field profiles.

We then calculate projection_weights, which is a normalized array of shape
(x=num_wavelengths, y=num_actual_modes) with entries representing the amount of
the reference TE00 mode that is represented by each actual mode. So away from
an avoided crossing, where a single actual mode embodies the TE00 mode,
projection_weights, at each frequency, would have a single entry very close to
1, and all others very close to 0. Right in the middle of an avoided crossing,
it would include two entries each very close to 0.5, and all others 0 (if more
than 2 actual modes exist). The sum of projection_weights at each freeuqnency
should always be 1.

In sum, completeness tells us whether the subspace spanned by the actual mode
field profiles is sufficient to represent the reference TE00 mode, while the
weights tell us how to divide the TE00 character between the actual mode field
profiles in order to accurately represent the reference TE00 mode.
"""

projection_power_raw = (
    np.abs(overlap_amplitude)**2 /
    np.maximum(normalization_denominator, 1e-30))

# Find the completeness
projection_completeness = np.sum(projection_power_raw, axis=1)

if np.any(projection_completeness <= 1e-12): # Just check if completeness is good
    raise RuntimeError(
        'The reference TE00 has poor overlap with the retained '
        'physical-mode subspace at one or more wavelengths.')

# Here is where get the weights
projection_weights = (projection_power_raw / projection_completeness[:,None])

# Run a quick safety check
if np.min(projection_completeness) < 0.90:
    print(
        'WARNING: Projection completeness falls below 0.90. Increase num_modes '
        'or reconsider the reference geometry in that wavelength region.')

projection_time = time.time() - projection_time

#%% Gather and organize all the data we need (all in ASCENDING frequency)

# Angular-frequency grid used by the solver
omega = 2*np.pi*solver_frequency_Hz

# Physical-mode data organized with ascending frequency
n_eff_omega = df_actual['n eff'].to_numpy().reshape(len(omega),num_modes_actual)
a_eff_omega = df_actual['mode area'].to_numpy().reshape(len(omega),num_modes_actual)

n_eff_ref_omega = df_reference['n eff'].to_numpy().reshape(len(omega),num_modes_reference)
a_eff_ref_omega = df_reference['mode area'].to_numpy().reshape(len(omega),num_modes_reference)

# Calculate projected TE00 mode from projection_weights and add to n_eff_omega
beta_modes = n_eff_omega*omega[:,None]/c
beta_te00 = np.sum(projection_weights*beta_modes,axis=1)
n_eff_te00 = c*beta_te00/omega
n_eff_omega = np.column_stack((n_eff_omega,n_eff_te00))

a_eff_te00 = np.sum(projection_weights*a_eff_omega,axis=1)

#%% Calculate dispersion and other parameters (all calculated vs ascending frequency)

beta0_arr, beta1_arr, beta2_arr = [], [], []
GV_arr, GVD_arr = [], []
Dhat_arr, Dhat_nl_arr = [], []

# Nonlinear phase-shift term for the dispersion operator
P0 = 5e3 # peak pulse power in [W]. ~7kW for 45 mW, 60 fs, 100 MHz, ~5kW for 40mW, 75 fs, 100 MHz
C = 0.5 # pre-factor for nonlinear phase shift
a_eff_m2 = a_eff_ref_omega/1e6/1e6
gamma = omega*n2/(c*np.flipud(a_eff_m2)[:,0])
dbeta_nl = C*gamma*P0


# Calculate dispersion for all physical modes AND projected TE00
for i in range(n_eff_omega.shape[1]):

    n_eff_curr = n_eff_omega[:,i]

    n_eff_spl = UnivariateSpline(omega, n_eff_curr, s=1e-11, k=5)
    n_eff_spl_1d = n_eff_spl.derivative(n=1)
    n_eff_spl_2d = n_eff_spl.derivative(n=2)
    
    # Beta evaluated on the simulation grid
    beta = omega*n_eff_spl(omega)/c
    
    # Group properties on the simulation grid
    ng = n_eff_spl(omega) + omega*n_eff_spl_1d(omega)
    beta1 = ng/c
    GV = 1/beta1
    
    beta2 = (2*n_eff_spl_1d(omega) + omega*n_eff_spl_2d(omega))/c
    GVD = beta2*1e12*1e12/1e-3
    
    # Beta and beta1 evaluated at the central pump frequency
    beta0 = center_omega*n_eff_spl(center_omega)/c
    beta1_pump = (n_eff_spl(center_omega) + center_omega*n_eff_spl_1d(center_omega))/c
    
    # Dispersion operator
    Dhat = beta - beta0 - beta1_pump*(omega-center_omega)
    Dhat_nl = (beta - beta0 - beta1_pump*(omega-center_omega) - dbeta_nl)

    beta0_arr.append(beta0)
    beta1_arr.append(beta1)
    beta2_arr.append(beta2)
    GV_arr.append(GV)
    GVD_arr.append(GVD)
    Dhat_arr.append(Dhat)
    Dhat_nl_arr.append(Dhat_nl)

# Stack the results: one column per physical/projected mode
beta0 = np.column_stack(beta0_arr)
beta1 = np.column_stack(beta1_arr)
beta2 = np.column_stack(beta2_arr)
GV = np.column_stack(GV_arr)
GVD = np.column_stack(GVD_arr)
Dhat = np.column_stack(Dhat_arr)
Dhat_nl = np.column_stack(Dhat_nl_arr)

#%% Reorganize everything into ascending wavelength for plotting/saving

n_eff = np.flipud(n_eff_omega)
a_eff = np.flipud(a_eff_omega)
n_eff_reference = np.flipud(n_eff_ref_omega)
a_eff_reference = np.flipud(a_eff_ref_omega)
a_eff_te00 = np.flipud(a_eff_te00)

projection_weights = np.flipud(projection_weights)
projection_completeness = np.flipud(projection_completeness)

beta0 = np.flipud(beta0)
beta1 = np.flipud(beta1)
beta2 = np.flipud(beta2)
GV = np.flipud(GV)
GVD = np.flipud(GVD)
Dhat = np.flipud(Dhat)
Dhat_nl = np.flipud(Dhat_nl)

#%% Plot data in one huge picture to save with the file

mode_labels = [f'Mode {i}' for i in range(num_modes_actual)]
os.makedirs(simulation_name, exist_ok=True)

fig1, (ax1,ax2,ax3,ax4,ax5) = plt.subplots(5, 1, figsize=(12,15), sharex=True)
ax1.set_xlabel('Wavelength (nm)', fontsize=15)
ax1.set_ylabel('Effective Index', fontsize=15)
ax1.plot(wvl_nm, n_eff[:,:num_modes_actual], linestyle='-', lw=1.5, label=mode_labels)
ax1.plot(wvl_nm, n_eff[:,-1], linestyle='-', lw=2.5, label='TE00')
ax1.grid()
ax1.legend()
ax2.set_xlabel('Wavelength (nm)', fontsize=15)
ax2.set_ylabel('Group Velocity [m/s]', fontsize=15)
ax2.plot(wvl_nm, GV[:,:num_modes_actual], linestyle='-', lw=1.5, label=mode_labels)
ax2.plot(wvl_nm, GV[:,-1], linestyle='-', lw=2.5, label='TE00')
ax2.set_ylim([0.8e8,1.8e8])
ax2.grid()
ax2.legend()
ax3.set_xlabel('Wavelength (nm)', fontsize=15)
ax3.set_ylabel('GVD [ps^2/km=fs^2/mm]', fontsize=15)
ax3.plot(wvl_nm, GVD[:,:num_modes_actual], linestyle='-', lw=1.5, label=mode_labels)
ax3.plot(wvl_nm, GVD[:,-1], linestyle='-', lw=2.5, label='TE00')
ax3.grid()
ax3.legend()
ax3.set_ylim([-1000, 2000])
ax4.set_xlabel('Wavelength (nm)', fontsize=15)
ax4.set_ylabel('D-hat Operator [1/m]', fontsize=15)
ax4.plot(wvl_nm, Dhat[:,:num_modes_actual], linestyle='-', lw=1.5, label=mode_labels)
ax4.plot(wvl_nm, Dhat[:,-1], linestyle='-', lw=2.5, label='TE00')
ax4.grid()
ax4.legend()
ax4.set_ylim([-40000, 40000])
ax5.set_xlabel('Wavelength (nm)', fontsize=15)
ax5.set_ylabel('Nonlinear D-hat Operator[1/m]', fontsize=15)
ax5.plot(wvl_nm, Dhat_nl[:,:num_modes_actual], linestyle='-', lw=1.5, label=mode_labels)
ax5.plot(wvl_nm, Dhat_nl[:,-1], linestyle='-', lw=2.5, label='TE00')
ax5.grid()
ax5.legend()
ax5.set_ylim([-40000, 40000])
plt.tight_layout()

# Plot the reference candidates, projection weights, and completeness diagnostic
reference_labels = [f'Reference mode {i}' for i in range(num_modes_reference)]
projection_labels = [f'Actual mode {i}' for i in range(num_modes_actual)]

fig2, (ax5,ax6,ax7) = plt.subplots(3, 1, figsize=(9,8), sharex=True)
ax5.set_ylabel('Reference index', fontsize=15)
ax5.plot(wvl_nm, n_eff_reference, linestyle='-', lw=1.5,
         label=reference_labels)
ax5.grid()
ax5.legend()
ax6.set_ylabel('Projection Weights', fontsize=15)
ax6.plot(wvl_nm, projection_weights, linestyle='-', lw=1.5,
         label=projection_labels)
ax6.set_ylim([-0.05,1.05])
ax6.grid()
ax6.legend()
ax7.set_xlabel('Wavelength (nm)', fontsize=15)
ax7.set_ylabel('Completeness', fontsize=15)
ax7.plot(wvl_nm, projection_completeness, linestyle='-', lw=1.5)
ax7.axhline(0.90, linestyle='--', lw=1)
ax7.grid()
plt.tight_layout()

fig3, ax8 = plt.subplots(1,1, figsize = (6,4))
ax8.set_xlabel('Wavelength (nm)', fontsize=15)
ax8.set_ylabel('Effective area', fontsize=15)
ax8.plot(wvl_nm, a_eff[:,:num_modes_actual], linestyle='--', lw=1.5, label=mode_labels)
ax8.plot(wvl_nm, a_eff_reference, linestyle='-', lw=1.5, label='Reference TE00')
ax8.grid()
ax8.legend()
plt.tight_layout()

#%% Save simulation parameters

simulation_parameters = {
    "sim_Lx_um": sim_Lx,
    "sim_Ly_um": sim_Ly,
    "sim_Lz_um": sim_Lz,
    "min_steps_per_wvl": min_steps_per_wvl,
    "num_modes_actual": num_modes_actual,
    "num_modes_reference": num_modes_reference,
    "reference_mode_index": reference_mode_index,
    "symmetry_actual": symmetry_actual,
    "symmetry_reference": symmetry_reference,
    "boundary_conditions": (BC_x,BC_y,BC_z),
    "wg_width_um": wg_width,
    "wg_height_um": wg_height,
    "LN_slab_height_um": f"{ln_slab_height:0.3f}",
    "sio2_height_um": sio2_height,
    "top_clad_height_um": top_clad_height,
    "top_clad_material": top_clad_material,
    "sidewall_angle_deg": f"{np.rad2deg(sidewall_angle):0.1f}",
    "wavelength_start_nm": float(wvl_nm_start),
    "wavelength_end_nm": float(wvl_nm_end),
    "wavelength_step_nm": f"{float(wvl_nm[1]-wvl_nm[0]):0.3f}",
    "wavelength_num_points": len(wvl_nm),
    "center_pump_wvl_nm": pump_wvl_nm,
    "Dhat_peak_power_W": P0,
    "Dhat_C": C,
    "solver_actual_time_s": f"{solver_actual_time:0.1f}",
    "solver_reference_time_s": f"{solver_reference_time:0.1f}",
    "solver_total_time_s": f"{solver_time:0.1f}",
    "extraction_time_s": f"{extraction_time:0.1f}",
    "projection_time_s": f"{projection_time:0.1f}",
    "total_time_s": f"{(solver_time+extraction_time+projection_time):0.1f}"}


#%% Save data to folder titled by the timestamp

fig1.savefig(os.path.join(simulation_name, "Summary.png"), dpi=300)
fig2.savefig(os.path.join(simulation_name, "Reference_projection_diagnostics.png"), dpi=300)

os.makedirs(simulation_name, exist_ok=True)

# Save the parameters as a human-readable JSON file
with open(os.path.join(simulation_name, "parameters.json"), "w") as f:
    json.dump(simulation_parameters, f, indent=4)

# Save the numerical arrays as efficient numpy binary files
# These are all saved versus wavelength
np.save(os.path.join(simulation_name, "wvl_nm.npy"), wvl_nm)
np.save(os.path.join(simulation_name, "n_eff.npy"), n_eff)
np.save(os.path.join(simulation_name, "n_eff_TE00.npy"), n_eff[:,-1])
np.save(os.path.join(simulation_name, "a_eff.npy"), a_eff)
np.save(os.path.join(simulation_name, "a_eff_ref.npy"), a_eff_reference)

# if fields:
#     # Create the 'fields' subfolder inside your main simulation folder
#     fields_dir = os.path.join(simulation_name, "fields")
#     os.makedirs(fields_dir, exist_ok=True)
    
#     # 1. Save the spatial coordinates just once into the new subfolder
#     first_key = list(fields.keys())[0]
#     np.save(os.path.join(fields_dir, "spatial_x.npy"), fields[first_key]['x'])
#     np.save(os.path.join(fields_dir, "spatial_y.npy"), fields[first_key]['y'])
    
#     # 2. Loop through wavelengths and modes to save individual .npy files
#     for wvl, wvl_data in fields.items():
#         for m in range(num_modes):
#             mode_key = f'mode_{m}'
            
#             # Format: Ex_400nm_mode_0.npy
#             Ex_filename = os.path.join(fields_dir, f"Ex_{wvl}nm_{mode_key}.npy")
#             Ey_filename = os.path.join(fields_dir, f"Ey_{wvl}nm_{mode_key}.npy")
            
#             np.save(Ex_filename, wvl_data[mode_key]['Ex'])
#             np.save(Ey_filename, wvl_data[mode_key]['Ey'])

print(f"Data successfully saved to {simulation_name}")