"""Demo of image with contour overlay

This demo displays an HST image of NGC 1275 taken with three different
filters combined as an RGB image with contours of an aligned Chandra
X-Ray image (smoothed) of the same object overplotted

The data for the images are stored as simple binary files and the
necessary shape and type info is added by the loaddata function (as
well as decompression for the HST image).

The demo creates a figure window that is the size of the HST image in
pixels so that no resampling is done, scales the plot window (axes) to
fill the figure window.  Resizing the window will modify the aspect
ratio, but correspondence between the HST image and contour image will
always be correct

The HST image was obtained from the Hubble Heritage web pages 
(http://heritage.stsci.edu/2003/14/index.html)
(Credits: NASA and The Hubble Heritage Team (STScI/AURA))
The Chandra image was obtained from the Chandra web site
http://chandra.harvard.edu/photo/2000/perseus/index.html
(Credits: NASA/CXC/SAo)
"""
import pylab as p
import matplotlib.cm as cm
import matplotlib.numerix as n
import zlib
import sys


def load_hst_data():
    """reconstruct the numerix arrays from the data files"""

    #hst = n.fromfile('hst.dat',typecode=n.UInt8, shape=(812,592,3))/255.
    str = open('data/hst.zdat').read()
    dstr = zlib.decompress(str)
    hst = n.fromstring(dstr, n.UInt8)
    hst.shape = (812, 592, 3)
    hst = hst/255.
    str = open('data/chandra.dat').read()
    chandra = n.fromstring(str, n.Int16)
    chandra.shape = (812,592)
    if sys.byteorder == 'little':
        chandra  = chandra.byteswapped()

    # note that both HST and Chandra data are normalized to be between 0 and 1
    return hst, chandra/16000.

def hstdemo():
    p.rc('image',origin='lower') # correct display requires setting origin to this
    hst, chandra = load_hst_data()
    # set size of figure window to be exactly that of the image so no resampling is done
    h, w, d = hst.shape
    dpi=80.
    p.figure(figsize=(w/dpi, h/dpi), dpi=dpi)
    # set plot region to full window size
    p.axes((0,0,1,1))
    # display rgb HST image
    p.imshow(hst)
    # overplot X-ray contour map
    p.contour(chandra, [.95,.85, .6], linewidths=2, cmap=cm.hot)
    p.clim(0,1.1)
    p.legend(loc='lower right')
    p.text(160, 75, 'HST image of NGC 1275\n with Chandra X-Ray contours',
           color='white', size=22)

           

hstdemo()
p.show()
