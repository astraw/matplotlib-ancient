from matplotlib.matlab import *
from matplotlib.lines import Line2D

# I use if 1 to break up the different regions of code visually
basedir = '../../examples/'
if 1:
    # load the data - these are in the examples/data dir of the src
    # distro. The MRI data are 256x256 16 bit integers

    dfile = basedir + 'data/s1045.ima'
    im = fromstring(file(dfile).read(), Int16).astype(Float)
    im.shape = 256, 256
    im = array([im[i] for i in arange(255,-1,-1)]) # flip upside down

    # The EEG data are 800 rows by 4 columns
    numSamples, numRows = 800,4
    eeg = fromstring(file(basedir + 'data/eeg.dat').read(), Float)
    eeg.shape = numSamples, numRows


if 1: # plot the MRI in pcolor
    subplot(221)
    pcolor(im, shading='flat')
    axis('off')

if 1:  # plot the histogram of MRI intensity
    subplot(222)
    im.shape = 256*256,
    im = take(im, nonzero(im)) # ignore the background
    im = im/(2.0**15) # normalize
    hist(im, 100)
    set(gca(), 'xticks', [-1, -.5, 0, .5, 1])
    set(gca(), 'yticks', [])
    xlabel('intensity')
    ylabel('MRI density')

if 1:   # plot the EEG

    t = arange(numSamples)/float(numSamples)*10.0
    ticklocs = []
    ax = subplot(212)
    for i in range(numRows):
        thisLine = Line2D(ax.dpi, ax.bbox, t, eeg[:,i],
                          transx=ax.xaxis.transData,
                          transy=ax.yaxis.transData)
        # offset each voltage trace from baseline
        thisLine.set_vertical_offset(3*i)
        ax.add_line(thisLine)
        ticklocs.append(3*i)

    set(gca(), 'xticks', arange(11))
    set(gca(), 'yticks', ticklocs)
    set(gca(), 'yticklabels', ['PG3', 'PG5', 'PG7', 'PG9'])
    axis( [0,10,-3, 12] )
    grid('on')
    xlabel('time (s)')


savefig('mri_with_eeg_small', dpi=75)
savefig('mri_with_eeg_large', dpi=150)

show()
