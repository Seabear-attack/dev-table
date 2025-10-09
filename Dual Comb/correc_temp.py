# -*- coding: utf-8 -*-
"""
Created on Wed Sep 17 12:47:30 2025

@author: mathi
"""
import numpy as np
import matplotlib.pyplot as plt;
from scipy.signal import find_peaks, detrend
fs = 200e6
nb_pts_filt = 1024
f_center = 25e6
bfopt = firwin(nb_pts_filt, BW_fopt * 2 / fs, window=('kaiser', 8), pass_zero='lowpass')
angle_shift_filter = 2 * np.pi * f_center / fs * np.arange(nb_pts_filt)
 # Apply phase shift to the IGM filter
b = 2 * bfopt * np.exp(1j * angle_shift_filter)
np.roll(cp_fftconvolve(data_gpu[:, igm_channel], b_gpu[:, igm_channel], mode='same'), -1)
def ffta(x=None, N=None, Dim=None):
    
    if N is None:
        N = np.max(x.shape)
    if Dim is None:
        Dim = np.argmax(x.shape)
    
    y = np.fft.fftshift(np.fft.fft(x, n=N, axis=Dim))
    
    if N % 2 == 0:
        # even
        f = np.arange(-N/2, N/2) / N
    else:
        # odd
        f = np.arange(-(N-1)/2, (N-1)/2 + 1) / N
        
    return y, f



ref1 = self.dataF[:,1]
ref2 = self.dataF[:,2]
ceo1 = self.dataF[:,3]
ceo2 = self.dataF[:,4]
fs = self.fs
[spc_ref1,f] = ffta(ref1[1:5000000]); 
[spc_ref2,f] = ffta(ref2[1:5000000]); 
[spc_ceo1,f] = ffta(ceo1[1:5000000]); 
[spc_ceo2,f] = ffta(ceo2[1:5000000]); 


plt.figure()
plt.plot(f*fs,10*np.log10(np.abs(spc_ref1)))
plt.plot(f*fs,10*np.log10(np.abs(spc_ref2)))



plt.figure();
plt.plot(detrend(np.unwrap(np.angle(ref1[1:5000000]))))
plt.figure()
plt.plot(detrend(np.unwrap(np.angle(ref2[1:5000000]))))
plt.figure()
plt.plot(detrend(np.unwrap(np.angle(ceo1[1:5000000]))))
plt.figure()
plt.plot(detrend(np.unwrap(np.angle(ceo2[1:5000000]))))


t = np.linspace(0,1,10000)
fs_x = 1/np.mean(np.diff(t))
x = 3*np.cos(2*np.pi*200*t)
noise = np.random.randn()
y = 3*(np.exp(1j*2*np.pi*200*t))

[spc,f] = ffta(x); 


plt.figure()
plt.plot(f*fs_x,10*np.log10(np.abs(spc)))

plt.figure()
plt.plot(t,x)
plt.plot(t,y)
plt.figure()
plt.plot(np.unwrap(np.angle(x)))
plt.plot(np.unwrap(np.angle(y)))

plt.figure()
plt.plot(np.abs(x))
plt.plot(np.abs(y))

