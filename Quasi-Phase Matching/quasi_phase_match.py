"""
T [C]
lam [um]
"""


def sellmeier_MgOPPLN(lam, T, axis='o'):
    a = None
    b = None
    if axis == 'o':
        a = (5.653, .1185, .2091, 89.61, 10.85, 1.97e-2)
        b = (7.941e-7, 3.134e-8, -4.641e-9, -2.188e-6)
    elif axis == 'e':
        a = (5.756, .0983, .202, 189.32, 12.52, 1.32e-2)
        b = (2.86e-6, 4.7e-8, 6.113e-8, 1.516e-4)
    f = (T - 24.5) * (T + 570.82)
    return (a[0] + b[0] * f + (a[1] + b[1] * f) / (lam ** 2 - (a[2] + b[2] * f) ** 2) + (a[3] + b[3] * f) / (
            lam ** 2 - a[4] ** 2) - a[5] * lam ** 2) ** .5


"""
T [C]
lam [um]
returns: [um/fs]
"""


def groupvel_MgOPPLN(lam, T, axis='o'):
    n = sellmeier_MgOPPLN(lam, T, axis=axis)
    x = Symbol('x')
    nprime = sellmeier_MgOPPLN(x, T, axis=axis)
    nprime = nprime.diff(x)
    nprime = lambdify(x, nprime, 'numpy')
    nprime = nprime(lam)
    return c_um_per_fs / n * (1 + lam / n * nprime)


if __name__ == '__main__':
    import numpy as np
    import pandas as pd
    from pathlib import Path
    import seaborn as sns
    import matplotlib.pyplot as plt
    from sympy import diff, lambdify, Symbol

    datPath = Path('Data/QPM.DAT').resolve()
    colNames = ['lam1', 'lam2', 'period', 'tempbw', 'grpvel1', 'grpvel2', 'grpvelblue', 'gdd1', 'gdd2', 'gddblue']
    df = pd.read_table(datPath,
                       names=colNames,
                       sep='\s+')
    # sns.lineplot(data=df, x='period', y='lam1')
    c_mm_per_ps = 2.9979e-1  # mm/ps
    c_um_per_fs = 2.9979e-1  # um/fs
    # yData = df['period']
    # xData = df['lam2']
    # f=interp1d(xData,yData,kind='
    # cubic')
    # print(f(2000),f(1330))

    # plt.show()
    #
    # sns.lineplot(data=df, x='lam2', y='grpvel2')
    # plt.show()

    l = np.linspace(1.3, 2.000, 250)
    temp = 25
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
