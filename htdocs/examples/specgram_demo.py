from __future__ import division
import os, sys
from matplotlib.matlab import specgram, show, meshgrid, pcolor, set, gca
from matplotlib.backends.backend_gtk import show_xvfb
from Numeric import fromstring, arange, Int16, Float, log10

filename = '/cruncher1/data/Seizure/Patients/2104212/eegs/ictal_2000_06_19.eeg'
channels = 128
Fs = 400

def read_nicolet(tmin, tmax):
    """Load Nicolet BMSI data."""
    if tmin<0: tmin=0
    fh = file(filename, 'rb')
    indmin = Fs*tmin
    numsamples = os.path.getsize(filename)/(channels*2)
    indmax = min(numsamples, Fs*tmax)



    byte0 = int(indmin*channels*2)
    numbytes = int( (indmax-indmin)*channels*2 )

    fh.seek(byte0)
    data = fromstring(fh.read(numbytes), Int16).astype(Float)
    data.shape = -1, channels



    t = (1/Fs)*arange(indmin, indmax)

    return t, data



t, data = read_nicolet(0,10)

x = data[:,5] 

Pxx, freqs, t = specgram(x, NFFT=512, Fs=Fs, noverlap=412)

T, F = meshgrid(t,freqs)
pcolor(T, F, 10*log10(Pxx), shading='flat')
set(gca(), 'ylim', [0,100])
#print Pxx.shape, freqs.shape, t.shape
show()
