import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np


filepath = Path(r"C:\Users\Splinter\Documents\Data\1-9-25 Leo HNLF\Lock tracking\mikey_frep.txt")

data = np.genfromtxt(filepath,skip_header=1, delimiter = "\t")
fig, axs = plt.subplots(1,1)

axs.plot(data[:,0]/3600, data[:,1])

axs.set_xlabel('Time (hr)')
axs.set_ylabel('$f_{rep}$ Frequency (Hz)')
axs.grid()

plt.tight_layout()
plt.show()