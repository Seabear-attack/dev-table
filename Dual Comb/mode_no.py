from numpy import arange,log
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import pandas as pd
import seaborn as sns

f_appr = 193.405059 * 1e12

fr_m = 1e8 + 61285.932
fb_m = 40e6
f0_m = -35e6

fr_l = 1e8 + 34.895
fb_l = 30e6
f0_l = -35e6

n_appr_m = round((f_appr - f0_m - fb_m) / fr_m)
n_appr_l = round((f_appr - f0_l - fb_l) / fr_l)

search_range = arange(-100,100)

freqs = []
for n_m in n_appr_m + search_range:
    for n_l in n_appr_l + search_range:
        f_cw_m = n_m * fr_m + fb_m + f0_m
        f_cw_l = n_l * fr_l + fb_l + f0_l
        f_diff = abs(f_cw_m - f_cw_l)
        f_min = min(f_cw_m, f_cw_l) 
        # freqs.append((n_m, n_l, f_cw_m, f_cw_l, f_diff, f_min))
        freqs.append((n_m-n_appr_m, n_l-n_appr_l, f_cw_m, f_cw_l, f_diff, f_min))

df = pd.DataFrame(freqs, columns=['Mikey Mode',
                                  'Leo Mode',
                                  'Mikey CW Calc',
                                  'Leo CW Calc',
                                  'Frequency Diff',
                                  'Frequency Min'])

sorted = df.sort_values(by='Frequency Diff')[:5]
print(abs(f_appr-df.loc[df['Frequency Diff'].idxmin(), "Frequency Min"]))
pivot = df.pivot(index='Mikey Mode', columns='Leo Mode', values='Frequency Diff')
sns.heatmap(pivot, norm=LogNorm(), cmap='icefire', cbar_kws={'label':'CW Frequency Difference (Hz)'})
plt.xlabel(f'Mikey Mode ({n_appr_m}+i)')
plt.ylabel(f'Leo Mode ({n_appr_l}+j)')
plt.title('')
plt.show()