from __future__ import generators
from __future__ import division

import pygtk
pygtk.require('2.0')
import gtk
from gtk import gdk
import Numeric as numpy

from cbook import is_string_like

class ColorDispatcher:
    __shared_state = {}  # borg
    def __init__(self):
        self.__dict__ = self.__shared_state
        # only init once
        try: self._colors
        except AttributeError: self._init()
        
    def _init(self):
        da = gtk.DrawingArea()
        cmap = da.get_colormap()
        self._colorOrder =['b', 'g', 'r', 'c', 'm', 'y', 'k']
        self._N = len(self._colorOrder)
        self._colors = {}
        self._colors['b'] = cmap.alloc_color(0, 0, 65025)
        self._colors['g'] = cmap.alloc_color(0, 0.5*65025, 0)
        self._colors['r'] = cmap.alloc_color(65025, 0, 0)
        self._colors['c'] = cmap.alloc_color(0, 0.75*65025, 0.75*65025)
        self._colors['m'] = cmap.alloc_color(0.75*65025, 0, 0.7500*65025)
        self._colors['y'] = cmap.alloc_color(0.75*65025, 0.75*65025, 0)
        self._colors['k'] = cmap.alloc_color(0.25*65025, 0.25*65025, 0.25*65025)
        self._colors['w'] = cmap.alloc_color(65025, 65025, 65025)

    def has_key(self, key):
        return self._colors.has_key(key)
    

    def __call__(self, arg):
        return self.get(arg)
    
    def get(self, arg):
        """
        Get a color by arg if arg is a char in the colors dict, or by
        integer index using a ring buffer if arg is an int
        """

        if isinstance(arg,gtk.gdk.Color):
            return arg
        if is_string_like(arg):
            color =  self._colors.get(arg)
            if color is None:
                raise KeyError, 'Unrecognized color string %s' % arg
            else: return color
        try: ind = arg % self._N
        except TypeError:
            raise TypeError, 'arg must be a string or int'
        else: return self._colors[self._colorOrder[ind]]




class ColormapJet:
   def __init__(self, N, cmap):
      self.N = N      
      self.indmax = self.N-1
      self.cmap = cmap
      self._jet_make_red()
      self._jet_make_blue()
      self._jet_make_green()
      self.colors = []
      self.rgbs = []
      for (R,G,B) in zip(self.red, self.green, self.blue):
          #pass
          self.rgbs.append((R/65535, G/65535, B/65535))
          self.colors.append(self.cmap.alloc_color(R,G,B))
      
   def _jet_make_red(self):

      fracon = 0.35
      fracmax = 0.66
      fracdown = 0.89
      mup = 1/(fracmax - fracon)
      mdown = -0.5/(1-fracdown)
      self.red = []
      for i in range(self.N):
         frac = i/self.N
         if frac < fracon: thisval = 0
         elif frac >=fracon and frac<=fracmax: thisval = mup * (frac-fracon)
         elif frac > fracmax and frac<fracdown: thisval = 1.0
         else: thisval = 1+mdown*(frac-fracdown)
         self.red.append( int(thisval*65535) )

   def _jet_make_blue(self):
       #blue is just red flipped left/right
       if not self.__dict__.has_key('red'):
          s = 'You must call _jet_make_red before _jet_make_blue'
          raise RuntimeError, s
                 
       self.blue = [self.red[i] for i in range(self.indmax,-1,-1)]


   def _jet_make_green(self):

      fracon = 0.1250
      fracmax = 0.375
      fracdown = 0.64
      fracoff = 0.91
      mup = 1/(fracmax - fracon)
      mdown = -1/(fracoff-fracdown)
      self.green = []
      for i in range(self.N):
         frac = i/self.N
         if frac < fracon: thisval = 0
         elif frac >=fracon and frac<=fracmax: thisval = mup * (frac-fracon)
         elif frac > fracmax and frac<fracdown: thisval = 1.0
         elif frac >= fracdown and frac<fracoff:
             thisval = 1+mdown*(frac-fracdown)
         else: thisval = 0.0
         self.green.append( int(thisval*65535) )
      #scatter(range(self.N), self.green)

   def get_color(self, val, valmin, valmax):
       # map val to a range from 0 to 1
       if len(val)>1:
          s = "val must be a scalar.  Perhaps you meant to call get_colors?"
          raise ValueError, s
       ind = self.indmax*(val-valmin)/(valmax-valmin)
       return self.colors[self._bound_ind(ind)]


   def _bound_ind(self, ind):
      if ind < 0: return 0
      if ind > self.indmax: return self.indmax
      return int(ind)
      
   def get_colors(self, vals, valmin=None, valmax=None):
      # map Numeric array vals to colors
      if valmin is None: valmin = min(vals)
      if valmax is None: valmax = max(vals)
      ind = (self.N-1.0)/(valmax-valmin)*(vals-valmin)
      return [self.colors[self._bound_ind(i)] for i in ind]


   def get_rgbs(self, vals, valmin, valmax):
      # map Numeric array vals to colors
      if valmin is None: valmin = min(vals)
      if valmax is None: valmax = max(vals)
      ind = (self.N-1.0)/(valmax-valmin)*(vals-valmin)
      return [self.rgbs[self._bound_ind(i)] for i in ind]
