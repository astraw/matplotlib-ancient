#This is a ported version of a Matlab example from the signal processing
#toolbox that showed some difference at one time between Matplotlib's and
#MatLab's scaling of the PSD.  This differs from psd_demo3.py in that
#this uses a complex signal, so we can see that complex PSD's work properly
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab

fs = 1000
t = np.linspace(0, 0.3, 301)
A = np.array([2, 8]).reshape(-1, 1)
f = np.array([150, 140]).reshape(-1, 1)
xn = (A * np.exp(2j * np.pi * f * t)).sum(axis=0) + 5 * np.random.randn(*t.shape)

yticks = np.arange(-50, 30, 10)
xticks = np.arange(-500,550,100)
plt.subplots_adjust(hspace=0.45, wspace=0.3)
ax = plt.subplot(1, 2, 1)

plt.psd(xn, NFFT=301, Fs=fs, window=mlab.window_none, pad_to=1024,
    scale_by_freq=True)
plt.title('Periodogram')
plt.yticks(yticks)
plt.xticks(xticks)
plt.grid(True)
plt.xlim(-500, 500)

plt.subplot(1, 2, 2, sharex=ax, sharey=ax)
plt.psd(xn, NFFT=150, Fs=fs, window=mlab.window_none, noverlap=75, pad_to=512,
    scale_by_freq=True)
plt.title('Welch')
plt.xticks(xticks)
plt.yticks(yticks)
plt.ylabel('')
plt.grid(True)
plt.xlim(-500, 500)

plt.show()
