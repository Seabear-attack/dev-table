import numpy as np
import matplotlib.pyplot as plt
def brewster_angle_rad(n):
    return np.arctan(n)

# Time delay to compensate
t_fs = 100

# Properties of the windows
# T_mm = 1
n = 1.5

# Constants
c_mm_per_fs = 3 * 10 ** -4

def time_compensated(delta_theta, T, n, c):
    return T / c * ((1 - np.sin(brewster_angle_rad(n) + delta_theta/2) ** 2 / n **2) ** -.5 - (1 - np.sin(brewster_angle_rad(n) - delta_theta/2) ** 2 / n **2) ** -.5)


delta_theta_deg = np.linspace(-10, 10, 1000)
plt.plot(delta_theta_deg, time_compensated(np.pi / 180 * delta_theta_deg, 1, n, c_mm_per_fs), label='T = 1 mm')
plt.plot(delta_theta_deg, time_compensated(np.pi / 180 * delta_theta_deg, 5, n, c_mm_per_fs), label='T = 5 mm')

plt.xlabel(r'Angle Difference ($\degree$)')
plt.ylabel('Delay Difference (fs)')
plt.title('Delay Compensation per Angular Offset Between Brewster Plates')
plt.grid()
plt.legend()
plt.xlim(-10, 10)
plt.ylim(-500, 500)
plt.show()