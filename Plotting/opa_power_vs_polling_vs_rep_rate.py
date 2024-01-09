import matplotlib.pyplot as plt
import numpy as np

path = Path()
for period:
    rep_rate = np.genfromtext() 
    power = np.genfromtext()

    plt.plot(rep_rate, power)
    plt.title("Signal power vs. signal repetition rate")
    plt.legend(f'{period} $\mu$m')
    plt.show()
