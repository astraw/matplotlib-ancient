"""
This module contains the instantiations of color mapping classes
"""

import matplotlib as mpl
import matplotlib.colors as colors
import matplotlib.numerix.npyma as ma
import matplotlib.cbook as cbook
from matplotlib._cm import *



def get_cmap(name=None, lut=None):
    """
    Get a colormap instance, defaulting to rc values if name is None
    """
    if name is None: name = mpl.rcParams['image.cmap']
    if lut is None: lut = mpl.rcParams['image.lut']

    assert(name in datad.keys())
    return colors.LinearSegmentedColormap(name,  datad[name], lut)

class ScalarMappable:
    """
    This is a mixin class to support scalar -> RGBA mapping.  Handles
    normalization and colormapping
    """

    def __init__(self, norm=None, cmap=None):
        """
        norm is a colors.normalize instance to map luminance to 0-1
        cmap is a cm colormap instance
        """

        if cmap is None: cmap = get_cmap()
        if norm is None: norm = colors.Normalize()

        self._A = None
        self.norm = norm
        self.cmap = cmap
        self.observers = []
        self.colorbar = None

    def set_colorbar(self, im, ax):
        'set the colorbar image and axes associated with mappable'
        self.colorbar = im, ax

    def to_rgba(self, x, alpha=1.0):
        '''Return a normalized rgba array corresponding to x.
        If x is already an rgb or rgba array, return it unchanged.
        '''
        if hasattr(x, 'shape') and len(x.shape)>2: return x
        x = ma.asarray(x)
        x = self.norm(x)
        x = self.cmap(x, alpha)
        return x

    def set_array(self, A):
        'Set the image array from numeric/numarray A'
        self._A = A

    def get_array(self):
        'Return the array'
        return self._A

    def get_clim(self):
        'return the min, max of the color limits for image scaling'
        return self.norm.vmin, self.norm.vmax

    def set_clim(self, vmin=None, vmax=None):
        """
        set the norm limits for image scaling; if vmin is a length2
        sequence, interpret it as (vmin, vmax) which is used to
        support setp

        ACCEPTS: a length 2 sequence of floats
        """
        if (vmin is not None and vmax is None and
                                cbook.iterable(vmin) and len(vmin)==2):
            vmin, vmax = vmin

        if vmin is not None: self.norm.vmin = vmin
        if vmax is not None: self.norm.vmax = vmax
        self.changed()

    def set_cmap(self, cmap):
        """
        set the colormap for luminance data

        ACCEPTS: a colormap
        """
        if cmap is None: cmap = get_cmap()
        self.cmap = cmap
        self.changed()

    def set_norm(self, norm):
        'set the normalization instance'
        if norm is None: norm = colors.Normalize()
        self.norm = norm
        self.changed()

    def autoscale(self):
        """
        Autoscale the scalar limits on the norm instance using the
        current array
        """
        if self._A is None:
            raise TypeError('You must first set_array for mappable')
        self.norm.autoscale(self._A)
        self.changed()

    def autoscale_None(self):
        """
        Autoscale the scalar limits on the norm instance using the
        current array, changing only limits that are None
        """
        if self._A is None:
            raise TypeError('You must first set_array for mappable')
        self.norm.autoscale_None(self._A)
        self.changed()



    def add_observer(self, mappable):
        """
        whenever the norm, clim or cmap is set, call the notify
        instance of the mappable observer with self.

        This is designed to allow one image to follow changes in the
        cmap of another image
        """
        self.observers.append(mappable)
        try:
            self.add_callback(mappable.notify)
        except AttributeError:
            pass

    def notify(self, mappable):
        """
        If this is called then we are pegged to another mappable.
        Update our cmap, norm, alpha from the other mappable.
        """
        self.set_cmap(mappable.cmap)
        self.set_norm(mappable.norm)
        try:
            self.set_alpha(mappable.get_alpha())
        except AttributeError:
            pass

    def changed(self):
        """
        Call this whenever the mappable is changed so observers can
        update state
        """
        for observer in self.observers:
            observer.notify(self)
