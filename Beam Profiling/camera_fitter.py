import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from PIL import Image

# Step 1: Load image and convert to grayscale
image = Image.open("/mnt/shredder/Research Projects/UVDCS/Data/5-19-25/spatial profile/profile.png")
data = np.array(image)

# Step 2: Create x and y coordinate arrays
x = np.arange(data.shape[1])
y = np.arange(data.shape[0])
x, y = np.meshgrid(x, y)

# Step 3: Define a 2D Gaussian function
def gaussian_2d(xy, amp, xo, yo, sigma_x, sigma_y, theta, offset):
    x, y = xy
    xo = float(xo)
    yo = float(yo)
    a = (np.cos(theta)**2) / (2*sigma_x**2) + (np.sin(theta)**2) / (2*sigma_y**2)
    b = -(np.sin(2*theta)) / (4*sigma_x**2) + (np.sin(2*theta)) / (4*sigma_y**2)
    c = (np.sin(theta)**2) / (2*sigma_x**2) + (np.cos(theta)**2) / (2*sigma_y**2)
    g = offset + amp * np.exp( - (a*((x - xo)**2) + 2*b*(x - xo)*(y - yo) + c*((y - yo)**2)))
    return g.ravel()

# Step 4: Fit the data
initial_guess = (data.max(), data.shape[1]//2, data.shape[0]//2, 30, 30, 0, data.min())
# Bounds on angle theta
bounds=((-np.inf,-np.inf,-np.inf,-np.inf,-np.inf,-np.pi/8,-np.inf),(np.inf,np.inf,np.inf,np.inf,np.inf,np.pi/8,np.inf))  
popt, pcov = curve_fit(gaussian_2d, (x, y), data.ravel(), p0=initial_guess, bounds=bounds)
# popt, pcov = curve_fit(gaussian_2d, (x, y), data.ravel(), p0=initial_guess)

# Step 5: Display result
fit_data = gaussian_2d((x, y), *popt).reshape(data.shape)

# Print fit parameters
print("Fitted parameters:")
print(f"Amplitude: {popt[0]:.2f}, X0: {popt[1]:.2f}, Y0: {popt[2]:.2f}")
print(f"Sigma X: {popt[3]:.2f}, Sigma Y: {popt[4]:.2f}, Theta: {popt[5]/np.pi*180:.2f} deg, Offset: {popt[6]:.2f}")

plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
plt.title("Original Image")
plt.imshow(data, cmap='gray')

plt.subplot(1, 2, 2)
plt.title("Fitted Gaussian")
plt.imshow(fit_data, cmap='viridis')
plt.colorbar()
plt.show()

