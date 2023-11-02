"""
sellmeier_eq(lam, temp, pol):   Sellmeier equation for given crystal
per:                            Polling period (um)
l:                              pump, signal, and idler wavelengths
t:                              High/low oven temperatures
pol:                            "o"-ordinary, "e"-extraordinary

returns:
"""

def qpm_condition(sellmeier_eq, per, l_p, l_s, l_i, t_high, t_low, pol):
    # n[pump, signal, idler][lowT, highT]
    n = np.array([[sellmeier_eq(l_p, t_lo, pol), sellmeier_eq(l_p, t_hi, pol)],
                  [sellmeier_eq(l_s, t_lo, pol), sellmeier_eq(l_s, t_hi, pol)],
                  [sellmeier_eq(l_i, t_lo, pol), sellmeier_eq(l_i, t_hi, pol)]])
    lam = np.array([l_p, l_s, l_i])
    k = 2 * np.pi * n / lam
    delta_k = k[0] - k[1] - k[2]



if __name__ == '__main__':
    import numpy as np
    import pandas as pd
    from pathlib import Path
    import seaborn as sns
    import matplotlib.pyplot as plt
    from quasi_phase_match import sellmeier_MgOPPLN

    datPath = Path('Data/QPM.DAT').resolve()
    colNames = ['lam1', 'lam2', 'period', 'tempbw', 'grpvel1', 'grpvel2', 'grpvelblue', 'gdd1', 'gdd2', 'gddblue']
    df = pd.read_table(datPath,
                       names=colNames,
                       sep='\s+')
    sns.lineplot(data=df, x='period', y='lam1')

    plt.show()
    l_hi =
    l_lo =

    t_hi = 150 # C
    t_lo = 50 # C

    sns.scatterplot(x=, y=)

    l = np.linspace(1.030, 2.000, 250)
    temp = 80
    n_sig_o = sellmeier_MgOPPLN(l, temp, 'o')
    n_pump_o = sellmeier_MgOPPLN(1.035, temp, 'o')
    n_sig_e = sellmeier_MgOPPLN(l, temp, 'e')
    n_pump_e = sellmeier_MgOPPLN(1.035, temp, 'e')

    sns.lineplot(x=l, y=n_sig_o, label='o-axis')
    sns.lineplot(x=l, y=n_sig_e, label='e-axis')
    plt.scatter([1.035,1.035],[n_pump_o,n_pump_e], label = 'pump')
    plt.xlabel(r'Signal wavelength [$\mu$m]')
    plt.ylabel('Refractive index')
    plt.title(f'5% MgO-PPLN, {temp} C')
    plt.tight_layout()
    plt.show()

    sns.lineplot(x=l, y=groupvel_MgOPPLN(l, temp, 'o'), label='o-axis')
    sns.lineplot(x=l, y=groupvel_MgOPPLN(l, temp, 'e'), label='e-axis')
    plt.scatter([1.035,1.035],[groupvel_MgOPPLN(1.035, temp, 'o'),groupvel_MgOPPLN(1.035, temp, 'e')], label = 'pump')
    plt.xlabel(r'Signal wavelength [$\mu$m]')
    plt.ylabel(r'Group velocity [$\mu$m/fs]')
    plt.title(f'5% MgO-PPLN, {temp} C')
    plt.tight_layout()
    plt.show()

    vbar_pump =  (groupvel_MgOPPLN(1.035, temp, 'o') + groupvel_MgOPPLN(1.035, temp, 'e'))/2

    vbar_sig = (groupvel_MgOPPLN(l, temp, 'o') + groupvel_MgOPPLN(l, temp, 'e')) /2
    t_walkoff = 1000 * (1 / vbar_pump - 1 / vbar_sig)
    sns.lineplot(x=l, y=t_walkoff)
    plt.xlabel(r'Signal wavelength [$\mu$m]')
    plt.ylabel('Temporal walkoff [fs/mm]')
    plt.title(f'5% MgO-PPLN, 1035 nm pump, {temp} C')
    plt.tight_layout()
    plt.show()
