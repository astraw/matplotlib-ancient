from __future__ import generators
from __future__ import division
import time
import re, math, os, sys, time
from copy import deepcopy

import pygtk
pygtk.require('2.0')
import gobject
import gtk
from gtk import gdk
import pango
from Numeric import arange, array, ones, zeros, logical_and, \
     nonzero, take, Float, transpose

from gtkutils import error_msg, raise_msg_to_str
from cbook import iterable, is_string_like, flatten, enumerate
from mlab import linspace
from lines import Line2D_Dispatcher, SolidLine2D, \
     Line2D, DottedLine2D, Vline2D
from colors import ColorDispatcher, ColormapJet
from patches import Rectangle, Circle
from text import AxisText
from artist import Artist



def to_arrays(typecode, *args):
    ret = []
    for val in args:
        try: val.shape
        except AttributeError:
            if iterable(val):
                val = array(val, typecode=typecode)
            else:
                val = array([val], typecode=typecode)
        ret.append(val)


    if len(ret)==1:
        return ret[0]
    else:
        return ret

    
        
        
class Axis(Artist):

    def __init__(self):
        Artist.__init__(self)

        self._left = None
        self._right = None
        self._bottom = None
        self._top = None
        self._width = None
        self._height = None
        self._dataLim = None  #min, max of data coords
        self._viewLim = None  #min, max of view in data coords
        self._axisLim = None  #min, max of win coords

        self._updateAxisLines = 1
        self._updateLabel = 1 
        self._ticksize = 0.01  # fraction of win lim
        self._ticklocs = None  # None unless explicity set
        self._ticklabelStrings = None
        
        # strip trailing zeros from ticks
        self._zerorgx = re.compile('^(.*?)\.?0+(e[+-]\d+)?$')        
        
        self._axislines = [SolidLine2D([0,0], [0,0], color='k'),
                          SolidLine2D([0,0], [0,0], color='k')]
        self._ticklines1 = []
        self._ticklines2 = []
        self._gridlines = []
        self._ticklabels = []
        # I want to create persistent refs to the axislines,
        # ticklines, ticklabels and grid lines.  So I am creating a
        # large number of the (100) and just returning the first
        # numTicks number of them when they are requested
        maxTicks = 100
        self._ticklines1 = []
        # 1 and 2 are the left/right axes (or top/bottom)
        for i in range(maxTicks):            
            self._ticklines1.append(SolidLine2D( [0,0], [0,0], color='k'))
            self._ticklines2.append(SolidLine2D( [0,0], [0,0], color='k'))
            self._gridlines.append(DottedLine2D([0,0], [0,0], color='k'))
            self._ticklabels.append(self.default_ticklabel())


    def autoscale_view(self):
        """
        Choose the view limits and number of ticks to make nice tick labels
        """
        vmin, vmax = self.get_view_lim()
        if vmin==vmax:
            vmin-=1
            vmax+=1

        (exponent, remainder) = divmod(math.log10(vmax - vmin), 1)
        if remainder < 0.84:
            exponent -= 1
        scale = 10**(-exponent)

        vmin = math.floor(scale*vmin)/scale
        vmax = math.ceil(scale*vmax)/scale
        self.set_view_lim(vmin, vmax)
        
    def default_ticklabel(self):
        """
        Create an axis text instance with the proper attributes (but
        no x,y,label) info
        """
        raise NotImplementedError, 'Derived must override'

    def _draw(self, drawable, *args, **kwargs):
        'Draw the axis lines, grid lines, tick lines and labels'
        lines = []
        self.update_axis_lines()
        lines.extend(self._axislines)
        lines.extend(self.get_ticklines())
        lines.extend(self.get_gridlines())

        
        for line in lines:
            line.draw(drawable)

        for t in self.get_ticklabels():
            t.erase()
            t.draw(drawable)

        self.update_label_position()
        self._label.draw(drawable)

    def get_ticklines(self):
        'Return a list of tick Line2D tick instances'
        numticks = self.get_numticks()
        lines = self._ticklines1[:numticks]
        lines.extend(self._ticklines2[:numticks])
        return lines

    def get_gridlines(self):
        'Return a list of grid Line2D instances'
        numticks = self.get_numticks()
        lines = self._gridlines[:numticks]
        return lines

    def get_numticks(self):
        'Return the number of ticks'
        raise NotimplementedError, 'Derived must override'

    def get_data_distance(self):
        'Return  the distance max(datalim) - min(datalim)'
        if self._dataLim is None:
            raise RuntimeError, 'No data in range'
        return self._dataLim[1] - self._dataLim[0]

    def get_data_lim(self):
        'Return the tuple min(datalim), max(datalim)'
        if self._dataLim is None:
            raise RuntimeError, 'No data in range'
        return self._dataLim

    def get_label(self):
        'Return the axis label (AxisText instance)'
        return self._label
    
    def get_data_extent(self):
        "Data extent == window extent for Axis because tranfunc is identity"
        if self._left is None:
            raise RuntimeError, 'Extent is not set'
        return self._left, self._right, self._width, self._height

    def get_view_distance(self):
        'Return the distance max(viewlim) - min(viewlim)'
        if self._dataLim is None:
            vmin, vmax = self.get_view_lim()
            return vmax - vmin
        if self._viewLim is None:
            return self.get_data_distance()
        else:
            return self._viewLim[1] - self._viewLim[0]

    def get_view_lim(self):
        'Return the view limits as tuple min(viewlim), max(viewlim)'
        if self._dataLim is None:
            return -1,1
        if self._viewLim is None:
            return self.get_data_lim()
        else:
            return self._viewLim


    def get_window_distance(self):
        'Return the distance max(windolim) - min(windowlim)'
        if self._left is None:
            raise RuntimeError, 'Window range not set range'
        wmin, wmax = self.get_window_lim()
        return wmax - wmin
    
    def get_window_lim(self):
        'Return the window limits as tuple min(winlim), max(winlim)'
        raise NotImplementedError, 'Derived must override'

    def get_label(self):
        'Return the axis label as an AxisText instance'
        return self._label

    def get_ticklocs(self):
        "Get the tick locations in data coordinates as a Numeric array"
        if self._ticklocs is not None: return self._ticklocs
        numticks = self.get_numticks()
        if numticks==0: return []
        vmin, vmax = self.get_view_lim()
        d = self.get_view_distance()
        if numticks==1: 0.5*d
        step = d/(numticks-1)
        # add a small offset to include endpoint
        return arange(vmin, vmax+0.1*d, step)

    def get_ticklocs_win(self):
        "Get the tick locations in window coordinates as a Numeric array"
        if self._ticklocs is None:
            wmin, wmax = self.get_window_lim()
            return linspace(wmin, wmax, self.get_numticks())
        else:
            return self.transform_points(self._ticklocs)

    def get_ticklabels(self):
        'Return a list of tick labels as AxisText instances'
        return self._ticklabels[:self.get_numticks()]

    def get_ticklabel_extent(self):
        """
        Get the extent of all the tick labels as tuple bottom, top,
        width, height
        """
        bottom, top = self._top, self._bottom
        left, right = self._right, self._left
        for l in self.get_ticklabels():
            l,b,w,h = l.get_window_extent()
            r, t = l+w, b+h                        
            if b<bottom: bottom=b
            if t>top: top=t
            if l<left: left = l
            if r>right: right=r

        return left, bottom, right-left, top-bottom

    def pan(self, numsteps):
        'Pan numticks (can be positive or negative)'
        vmin, vmax = self.get_view_lim()
        ticks =  self.get_ticklocs()
        step = (ticks[1]-ticks[0])*numsteps
        vmin += step
        vmax += step
        self.set_view_lim(vmin, vmax)
        
    def set_window_extent(self, l, b, w, h):
        'Set the window extent as left, bottom, width, height'
        self._left, self._right = l, l+w
        self._bottom, self._top = b, b-h
        self._width, self._height = w, h
        self._updateAxisLines = 1
        self._updateLabel = 1

    def get_child_artists(self):
        'Return a list of all Artist instances contained by Axis'
        artists = []
        artists.extend(self._ticklabels)
        artists.extend(self._ticklines1)
        artists.extend(self._ticklines2)
        artists.extend(self._gridlines)
        artists.extend(self._axislines)
        artists.append(self._label)
        return artists

    def set_data_lim(self, dmin, dmax):
        'Set the data limits to dmin, dmax'
        self._dataLim = [dmin, dmax]

    def set_ticks(self, ticks):
        'Set the locations of the tick marks from sequence ticks'
        try: ticks.shape
        except AttributeError: ticks = array(ticks)
        self._ticklocs = ticks
        if self._viewLim is None and len(self._ticklocs)>1:
            self.set_view_lim(min(self._ticklocs), max(self._ticklocs))

    def set_ticklabels(self, ticklabels):
        """
        Set the text values of the tick labels.  ticklabels is a
        sequence of strings
        """
        self._ticklabelStrings = ticklabels
        # init all the tick labels with ''
        for i in range(self.get_numticks()):
            self._ticklabels[i].set_text('')
        # fill with the custom tick labels
        for s, label in zip(self._ticklabelStrings, self._ticklabels):
            label.set_text(s)
            
    def set_view_lim(self, vmin, vmax):
        'Set the view limits (data coords) to vmin, vmax'

        self._viewLim = vmin, vmax
        locs = self.get_ticklocs()
        if self._ticklabelStrings is None:
            for label, loc in zip(self._ticklabels, locs):
                label.set_text(self.format_tickval(loc))

        
    def update_data(self, d):
        """
        Update the min, max of the data lim with values in min(d), max(d)
        if min(d) or max(d) exceed the existing limits
        """
        if len(d)==0: return
        mind = min(d)
        maxd = max(d)
        if self._dataLim is None:
            self._dataLim = [mind, maxd]
            return
        if mind < self._dataLim[0]: self._dataLim[0] = mind
        if maxd > self._dataLim[1]: self._dataLim[1] = maxd


    def transform_points(self, v):
        """
        Transform v data (v can be a scalar or Numeric array) into
        window coords
        """
        if iterable(v) and len(v)==0: return v
        vmin, vmax = self.get_view_lim()
        wmin, wmax = self.get_window_lim()
        wd = self.get_window_distance()        
        vd = self.get_view_distance()
        return wd/vd*(v-vmin)+wmin
        
    def transform_scale(self, v):
        """
        Transform v scale (v can be a scalar or numpy array) into
        window coords
        """
        if iterable(v) and len(v)==0: return v
        wd = self.get_window_distance()        
        vd = self.get_view_distance()
        #print wd, vd
        try: v.shape
        except AttributeError: v = array(v)
        return abs(wd/vd)*v

    def format_tickval(self, x):
        'Format the number x as a string'
        d = self.get_view_distance()
        #if the number is not too big and it's an int, format it as an
        #int
        if abs(x)<1e4 and x==int(x): return '%d' % x

        # if the value is just a fraction off an int, use the int
        if abs(x-int(x))<0.0001*d: return '%d' % int(x)

        # use exponential formatting for really big or small numbers,
        # else use float
        if abs(x) < 1e-4: fmt = '%1.3e'
        elif abs(x) > 1e5: fmt = '%1.3e'
        else: fmt = '%1.3f'
        s =  fmt % x

        # strip trailing zeros, remove '+', and handle exponential formatting
        m = self._zerorgx.match(s)
        if m:
            s = m.group(1)
            if m.group(2) is not None: s += m.group(2)
        s = s.replace('+', '')
        return s

    def update_label_position(self):
        """
        Update the position of the axis label so it doesn't conflict with
        the tick labels
        """
        raise NotImplementedError, 'Derived must override'

    def update_axis_lines(self):
        """
        Update the axis, tick and grid lines
        """
        raise NotImplementedError, 'Derived must override'

    def zoom(self, direction):
        "Zoom in/out on axis"
        vmin, vmax = self.get_view_lim()
        d = self.get_view_distance()
        vmin += 0.1*d*direction
        vmax -= 0.1*d*direction        
        self.set_view_lim(vmin, vmax)
        #self.autoscale_view()
    
class XAxis(Axis):

    def __init__(self, *args, **kwargs):
        Axis.__init__(self, *args, **kwargs)
        self._label = AxisText(
            fontsize=10,
            verticalalignment='top',
            horizontalalignment='center')

    def default_ticklabel(self):
        "Create a default ticklabel"
        return  AxisText(
            fontsize=8,
            verticalalignment='top',
            horizontalalignment='center')

    def get_numticks(self):
        if self._ticklocs is None:
            if self._width is None: return 0
            else:
                if self._width>200: return 11
                else: return 6
        else: return len(self._ticklocs)

    def get_window_lim(self):
        if self._left is None:
            raise RuntimeError, 'set_window_extent must be called first'
        return self._left, self._right


    def set_window_extent(self, l, b, w, h):

        Axis.set_window_extent(self, l, b, w, h)
        self.winLim = self._left, self._right
        self._axislines[0].set_data(self.winLim, [self._bottom, self._bottom])
        self._axislines[1].set_data(self.winLim, [self._top, self._top])


    def update_axis_lines(self):
        if not self._updateAxisLines: return 
        numticks = self.get_numticks()
        ticklocsData = self.get_ticklocs()
        ticklocsWin = self.get_ticklocs_win()
        ticksize = self._ticksize*self._height
        tickLabels = map(self.format_tickval, ticklocsData)
        for i in range(numticks):
            self._ticklines1[i].set_data(
                [ticklocsWin[i], ticklocsWin[i]],
                [self._bottom, self._bottom-ticksize])
            self._ticklines2[i].set_data(
                [ticklocsWin[i], ticklocsWin[i]],
                [self._top, self._top+ticksize])
            self._gridlines[i].set_data(
                [ticklocsWin[i], ticklocsWin[i]],
                [self._bottom, self._top])
            self._ticklabels[i].set_position(
                ticklocsWin[i], self._bottom+3)
            if self._ticklabelStrings is None:
                self._ticklabels[i].set_text(tickLabels[i])

        self._updateLabel = 1
        self._updateAxisLines = 0

    def update_label_position(self):
        "Update the position of the axis label"
        # this cannot be done in set_window_extent because we can't assume
        # that children know their extent during a set extent call
        if self._left is None:
            raise RuntimeError, 'You must first call set_window_extent on the xaxis'
        if not self._updateLabel: return 
        tickBottom = 0
        for i in range(self.get_numticks()):
            l,b,w,h = self._ticklabels[i].get_window_extent()
            if b>tickBottom: tickBottom = b

        self._label.set_position((self._left+self._right)/2, tickBottom+3)
        self._updateLabel = 0
        

        
            
    
class YAxis(Axis):

    def __init__(self, *args, **kwargs):
        Axis.__init__(self, *args, **kwargs)
        self._label = AxisText(
            fontsize=10,
            verticalalignment='center',
            horizontalalignment='right',
            rotation='vertical')        

    def default_ticklabel(self):
        "Create a default ticklabel"
        return  AxisText(
            fontsize=8,
            verticalalignment='center',
            horizontalalignment='right')

    def get_numticks(self):
        if self._ticklocs is None:
            if self._width is None: return 0
            else:
                if self._height>200: return 11
                else: return 6
        else: return len(self._ticklocs)

    def get_window_lim(self):
        if self._top is None:
            raise RuntimeError, 'set_window_extent must be called first'
        return self._bottom, self._top

    def set_window_extent(self, l, b, w, h):
        Axis.set_window_extent(self, l, b, w, h)
        
        self.winLim = b, b-h
        self._axislines[0].set_data([l,l], self.winLim)
        self._axislines[1].set_data([l+w, l+w], self.winLim)

    def update_axis_lines(self):
        if not self._updateAxisLines: return 
        numticks = self.get_numticks()
        ticklocsData = self.get_ticklocs()
        ticklocsWin = self.get_ticklocs_win()
        ticksize = self._ticksize*self._width
        tickLabels = map(self.format_tickval, ticklocsData)

        for i in range(numticks):
            self._ticklines1[i].set_data(
                [self._left, self._left+ticksize],
                [ticklocsWin[i], ticklocsWin[i]])
            self._ticklines2[i].set_data(
                [self._right, self._right-ticksize],
                [ticklocsWin[i], ticklocsWin[i]])
            self._gridlines[i].set_data(
                [self._left, self._right],
                [ticklocsWin[i], ticklocsWin[i]])
            self._ticklabels[i].set_position(
                self._left-3, ticklocsWin[i])
            if self._ticklabelStrings is None:
                self._ticklabels[i].set_text(tickLabels[i])

        self._updateAxisLines = 0
        self._updateLabel = 1

    def update_label_position(self):
        "Update the position of the axis label"
        # this cannot be done in set_window_extent because we can't assume
        # that children know their extent during a set extent call
        if self._left is None:
            raise RuntimeError, 'You must first call set_window_extent on the yaxis'
        if not self._updateLabel: return 
        tickLeft = self._right  # compare false on first comparison
        for i in range(self.get_numticks()):
            l,b,w,h = self._ticklabels[i].get_window_extent()
            if l < tickLeft: tickLeft = l
        self._label.set_position(tickLeft-3, (self._top+self._bottom)/2)
        self._updateLabel = 0

        
def _process_plot_format(fmt):
    """
    Process a matlab style color/line style format string.  Return a
    (lineStyle, color) tuple as a result of the processing.  Default
    values are (solidLine, Blue).  Example format strings include

    'ko'    : black circles
    '.b'    : blue dots
    'r--'   : red dashed lines

    See Line2D_Dispatcher and ColorDispatcher for more info.

    """

    #print 'FMT is: %s' % fmt
    styles = Line2D_Dispatcher()
    colors = ColorDispatcher()
    
    LineClass = styles['-']
    color = colors('b')

    # handle the multi char special cases and strip them from the
    # string
    if fmt.find('--')>=0:
        LineClass = styles['--']
        fmt = fmt.replace('--', '')
    if fmt.find('-.')>=0:
        LineClass = styles['-.']
        fmt = fmt.replace('-.', '')
    
    chars = [c for c in fmt]

    for c in chars:        
        if styles.has_key(c):
            LineClass = styles[c]
        elif ColorDispatcher().has_key(c):
            color = ColorDispatcher().get(c)
        else:
            err = 'Unrecognized character %c in format string' % c
            raise ValueError, err
    return LineClass, color


class _process_plot_var_args:    
    """

    Process variable length arguments to the plot command, so that
    plot commands like the followig are supported

      plot(t, s)
      plot(t1, s1, t2, s2)
      plot(t1, s1, 'ko', t2, s2)
      plot(t1, s1, 'ko', t2, s2, 'r--', t3, e3)

    an arbitrary number of x,y,fmt are allowed
    """
    def __call__(self, *args):
        return self._grab_next_args(*args)
            

    def _plot_1_arg(self, y):
        return SolidLine2D(arange(len(y)), y)

    def _plot_2_args(self, tup2):
        if is_string_like(tup2[1]):
            y, fmt = tup2
            (LineStyleClass, color) = _process_plot_format(fmt)
            return LineStyleClass(x=arange(len(y)),
                                  y=y,
                                  color=color)
        else:
            x,y = tup2
            return SolidLine2D(x, y)

    def _plot_3_args(self, tup3):
        x, y, fmt = tup3
        (LineStyleClass, color) = _process_plot_format(fmt)
        return LineStyleClass(x, y, color=color)



    def _grab_next_args(self, args):
        remaining = args
        while 1:
            if len(remaining)==0: return
            if len(remaining)==1:
                yield self._plot_1_arg(remaining[0])
                remaining = []
                continue
            if len(remaining)==2:
                yield self._plot_2_args(remaining)
                remaining = []
                continue
            if len(remaining)==3:
                if not is_string_like(remaining[2]):
                    raise ValueError, 'third arg must be a format string'
                yield self._plot_3_args(remaining)
                remaining=[]
                continue
            if is_string_like(args[2]):
                yield self._plot_3_args(remaining[:3])
                remaining=remaining[3:]
                continue
            yield self._plot_2_args(remaining[:2])
            remaining=args[2:]
        
    
class Axes(Artist):
    """
    Emulate matlab's axes command, creating axes with

      Axes(position=[left, bottom, width, height])

    where all the arguments are fractions in [0,1] which specify the
    fraction of the total figure window.  

    figbg is the color background of the figure
    axisbg is the color of the axis background
    """

    _colors = ColorDispatcher()
    def __init__(self, position, figbg='w', axisbg = 'w'):
        Artist.__init__(self)
        self._position = position
        self._figbg = figbg
        self._axisbg = axisbg
        self._gridState = 0
        self._lines = []
        self._patches = []
        self._text = []     # text in axis coords
        self._get_lines = _process_plot_var_args()

        self._xaxis = XAxis()
        self._yaxis = YAxis()


        self._title =  AxisText(
            x=0, y=0, text='', fontsize=11,
            verticalalignment='bottom',
            horizontalalignment='center')

        
    def _pass_func(self, *args, **kwargs):
        pass
    
    def add_line(self, line):
        "Add a line to the list of plot lines"
        self._xaxis.update_data(line.get_x())
        self._yaxis.update_data(line.get_y())
        line.transform_points_to_win = self.transform_points_to_win
        line.transform_scale_to_win = self.transform_scale_to_win
        line.clip_gc = self.clip_gc
        self._lines.append(line)

    def add_patch(self, patch):
        "Add a line to the list of plot lines"
        patch.transform_points_to_win = self.transform_points_to_win
        patch.transform_scale_to_win = self.transform_scale_to_win
        patch.clip_gc = self.clip_gc
        l, b, w, h = patch.get_data_extent()
        self._xaxis.update_data((l, l+w))
        self._yaxis.update_data((b, b+h))

        #patch.clip_gc = self.clip_gc

        self._patches.append(patch)


    def bar(self, x, y, width=0.8):
        """
        Make a bar plot with rectangles at x, x+width, 0, y
        x and y are Numeric arrays

        Return value is a list of Rectangle patch instances
        """
        patches = []
        for thisX,thisY in zip(x,y):
            r = Rectangle( (thisX,0), width=width, height=thisY)
            self.add_patch(r)
            patches.append(r)
        return patches


        return gtk.TRUE

    def clip_gc(self, gc):
        gc.set_clip_rectangle( (self._left, self._top+1,
                                self._width, self._height) )


    def clear(self):
        self._lines = []
        self._patches = []
        self._xaxis.clear()
        self._yaxis.clear()
        
    def _draw(self, drawable, *args, **kwargs):
        "Draw everything (plot lines, axes, labels)"
        gc = drawable.new_gc()
        gc.foreground = self._colors.get(self._axisbg)
        drawable.draw_rectangle(gc, gtk.TRUE,
                                      self._left, self._top,
                                      self._width, self._height)
        
        self._xaxis.draw(drawable)
        self._yaxis.draw(drawable)
        self._draw_lines(drawable)
        self._draw_patches(drawable)

        for t in self._text:
            t.erase()
            t.draw(drawable)

        self._title.set_position(
            x=(self._left+self._right)/2,y=self._top-10)
        self._title.draw(drawable)

            
        
    def _draw_lines(self, drawable):
        "Draw the plot lines"
        for line in self._lines:
            line.draw(drawable)

    def _draw_patches(self, drawable):
        "Draw the plot lines"
        for p in self._patches:
            p.draw(drawable)
            #print 'drew a patch!'

    def get_child_artists(self):
        artists = []
        artists.append(self._title)
        artists.append(self._xaxis)
        artists.append(self._yaxis)
        artists.extend(self._lines)
        artists.extend(self._patches)
        artists.extend(self._text)
        return artists
    
    def get_lines(self, type=Line2D):        
        """
        Get all lines of type type, where type is Line2D (all lines)
        or a derived class, eg, CircleLine2D

        You can use this function to set properties of several plot
        lines at once, as in the following

            a1.plot(t1, s1, 'gs', t1, e1, 'bo', t1, p1)
            def fmt_line(l):
               l.set_linewidth(2)
               l.set_size(10)
               l.set_fill(1)
            map(fmt_line, a1.get_lines(SymbolLine2D))


        """
        return [line for line in self._lines if isinstance(line, type)]


    def get_xaxis(self):
        "Return the XAxis instance"
        return self._xaxis

    def get_xlim(self):
        "Get the x axis range [xmin, xmax]"
        return self._xaxis.get_view_lim()

    def get_xticklabels(self):
        "Get the xtick labels as a list of strings"
        return self._xaxis.get_ticklabels()

    def get_xticks(self):
        "Return the y ticks as a list of locations"
        return self._xaxis.get_ticklocs()


    def get_yaxis(self):
        "Return the YAxis instance"
        return self._yaxis

    def get_ylim(self):
        "Get the y axis range [ymin, ymax]"
        return self._yaxis.get_view_lim()


    def get_yticklabels(self):
        "Get the ytick labels as a list of strings"
        return self._yaxis.get_ticklabels()

    def get_yticks(self):
        "Return the y ticks as a list of locations"
        return self._yaxis.get_ticklocs()
        
    def in_axes(self, xwin, ywin):
        if xwin<self._left or xwin > self._right:
            return 0
        if ywin>self._bottom or ywin<self._top:
            return 0
        return 1


    def hlines(self, y, xmin, xmax, fmt='k-'):
        """
        plot horizontal lines at each y from xmin to xmax.  xmin or
        xmax can be scalars or len(x) numpy arrays.  If they are
        scalars, then the respective values are constant, else the
        widths of the lines are determined by xmin and xmax

        Returns a list of line instances that were added
        """
        (LineClass, color) = _process_plot_format(fmt)

        y = to_arrays(Float, y)
        if not iterable(xmin):
            xmin = xmin*ones(y.shape, y.typecode())
        if not iterable(xmax):
            xmax = xmax*ones(y.shape, y.typecode())

        xmin, xmax = to_arrays(Float, xmin, xmax)
        if len(xmin)!=len(y):
            raise ValueError, 'xmin and y are unequal sized sequences'
        if len(xmax)!=len(y):
            raise ValueError, 'xmax and y are unequal sized sequences'

        lines = []
        for (thisY, thisMin, thisMax) in zip(y,xmin,xmax):            
            line = LineClass( [thisMin, thisMax], [thisY, thisY],
                              color=color)
            self.add_line( line )
            lines.append(line)
        return lines

        
    def plot(self, *args):
        """
        Emulate matlab's plot command.  *args is a variable length
        argument, allowing for multiple x,y pairs with an optional
        format string.  For example, all of the following are legal,
        assuming a is the Axis instance:
        
          a.plot(x,y)            # plot Numeric arrays y vs x
          a.plot(x,y, 'bo')      # plot Numeric arrays y vs x with blue circles
          a.plot(y)              # plot y using x = arange(len(y))
          a.plot(y, 'r+')        # ditto with red plusses

        An arbitrary number of x, y, fmt groups can be specified, as in 
          a.plot(x1, y1, 'g^', x2, y2, 'l-')  

        Returns a list of lines that were added
        """

        lines = []
        for line in self._get_lines(args):
            self.add_line(line)
            lines.append(line)
        self._xaxis.autoscale_view()
        self._yaxis.autoscale_view()
        return lines
    
    def scatter(self, x, y, s=None, c='b'):
        """
        Make a scatter plot of x versus y.  s is a size (in data
        coords) and can be either a scalar or an array of the same
        length as x or y.  c is a color and can be a single color
        format string or an length(x) array of intensities which will
        be mapped by the colormap jet.        

        If size is None a default size will be used
        """

        if is_string_like(c):
            c = [self._colors.get(c)]*len(x)
        elif not iterable(c):
            c = [c]*len(x)
        else:
            da = gtk.DrawingArea()
            cmap = da.get_colormap()
            jet = ColormapJet(1000, cmap)
            c = jet.get_colors(c)

        if s is None:
            s = [abs(0.015*(max(y)-min(y)))]*len(x)
        elif not iterable(s):
            s = [s]*len(x)
        
        if len(c)!=len(x):
            raise ValueError, 'c and x are not equal lengths'
        if len(s)!=len(x):
            raise ValueError, 's and x are not equal lengths'

        patches = []
        for thisX, thisY, thisS, thisC in zip(x,y,s,c):
            circ = Circle( (thisX, thisY), radius=thisS)
            #print thisC
            circ.set_facecolor(thisC)
            self.add_patch(circ)
            patches.append(circ)
        return patches


    def set_axis_bgcolor(self, color):
        self._axisbg = color

    def set_fig_bgcolor(self, color):
        self._figbg = color
                        
    def set_size(self, width, height):
        "Reset the window params"
        self._left = self._position[0] * width
        self._bottom = (1-self._position[1]) * height
        self._width = self._position[2] * width
        self._height = self._position[3] * height
        self._right = self._left + self._width
        self._top = self._bottom - self._height

        # set the new axis information
        self._xaxis.set_window_extent(self._left, self._bottom,
                               self._width, self._height)
        self._yaxis.set_window_extent(self._left, self._bottom,
                               self._width, self._height)


    def set_title(self, label, *args, **kwargs):
        """
        Set the title for the xaxis

        See the text docstring for information of how override and the
        optional args work

        """
        
        self._title.set_text(label)
        override = self._process_text_args({}, *args, **kwargs)
        self._title.update_properties(override)
        return self._title


    def set_xlabel(self, xlabel, *args, **kwargs):
        """
        Set the label for the xaxis

        See the text docstring for information of how override and the
        optional args work

        """

        label = self._xaxis.get_label()
        label.set_text(xlabel)
        override = self._process_text_args({}, *args, **kwargs)
        label.update_properties(override)
        return label

    def set_xlim(self, v):
        "Set the limits for the xaxis; v = [xmin, xmax]"
        xmin, xmax = v
        self._xaxis.set_view_lim(xmin, xmax)
        map(lambda l: l.set_xclip(xmin, xmax), self._lines)
        
    def set_xticklabels(self, labels):
        "Set the xtick labels with list of strings labels"
        self._xaxis.set_ticklabels(labels)

    def set_xticks(self, ticks):
        "Set the x ticks with list of ticks"
        self._xaxis.set_ticks(ticks)
        

    def set_ylabel(self, ylabel, *args, **kwargs):
        """
        Set the label for the yaxis

        Defaults override is

            override = {
               'fontsize'            : 10,
               'verticalalignment'   : 'center',
               'horizontalalignment' : 'right',
               'rotation'='vertical' : }

        See the text doctstring for information of how override and
        the optional args work
        """
        label = self._yaxis.get_label()
        label.set_text(ylabel)
        override = self._process_text_args({}, *args, **kwargs)
        label.update_properties(override)
        return label

    def set_ylim(self, v):
        "Set the limits for the xaxis; v = [ymin, ymax]"
        ymin, ymax = v
        self._yaxis.set_view_lim(ymin, ymax)

        # I set the gc clip to be just outside the actual range so
        # that the flat, artifactual lines caused by the fact that the
        # x data clip is done first will be drawn outside the gc clip
        # rectangle .  5% is an arbitrary factor chosen so that only a
        # fraction of unnessecary data is plotted, since the data
        # clipping is done for plot efficiency.  See _set_clip in
        # lines.py for more info.  [ Note: now that I have disabled y
        # clipping for connected lines in lines.py, this hack is no
        # longer needed, but I'm going to preserve it since I may want
        # to re-enable y clipping for conencted lines and I can afford
        # the small performance hit. ]
        offset = 0.05*(ymax-ymin)
        map(lambda l: l.set_yclip(ymin-offset, ymax+offset), self._lines)


    def set_yticklabels(self, labels):
        "Set the ytick labels with list of strings labels"
        self._yaxis.set_ticklabels(labels)

    def set_yticks(self, ticks):
        "Set the y ticks with list of ticks"
        self._yaxis.set_ticks(ticks)

    def _process_text_args(self, override, *args, **kwargs):
        "Return an override dict.  See 'text' docstring for info"
        
        if len(args)>1:
            raise ValueError, 'Only a single optional arg can be supplied to text'
        if len(args)==1:
            override = deepcopy(args[0])
            if not isinstance(override, dict):
                msg = 'The optional nonkeyword argument to text must be a dict'
                raise TypeError, msg

        override.update(kwargs)
        return override
    
    def text(self, x, y, text, *args, **kwargs):
        """
        Add text to axis at location x,y (data coords)
        
        args, if present, must be a single argument which is a
        dictionary to override the default text properties

        If len(args) the override dictionary will be:

          'fontsize'            : 9,
          'verticalalignment'   : 'bottom',
          'horizontalalignment' : 'left'


        **kwargs can in turn be used to override the override, as in

          a.text(x,y,label, fontsize=12)
        
        will have verticalalignment=bottom and
        horizontalalignment=left but will have a fontsize of 12
        
        
        The AxisText defaults are
            'color'               : 'k',
            'fontname'            : 'Sans',
            'fontsize'            : 10,
            'fontweight'          : 'bold',
            'fontangle'           : 'normal',
            'horizontalalignment' : 'left'
            'rotation'            : 'horizontal',
            'verticalalignment'   : 'bottom',

        """
        override = {
            'fontsize' : 9,
            'verticalalignment' : 'bottom',
            'horizontalalignment' : 'left'
            }

        override = self._process_text_args(override, *args, **kwargs)
        t = AxisText(
            x=x, y=y, text=text,
            **override)
        if self._drawingArea is not None:
            t.set_drawing_area(self._drawingArea)
        t.transform_points_to_win = self.transform_points_to_win
        t.transform_scale_to_win = self.transform_scale_to_win
        t.clip_gc = self.clip_gc

        self._text.append(t)
        return t
    
    def transform_points_to_win(self, x, y):
        return (self._xaxis.transform_points(x),
                self._yaxis.transform_points(y))
    
    def transform_scale_to_win(self, x, y):
        return (self._xaxis.transform_scale(x),
                self._yaxis.transform_scale(y))
            
    def vlines(self, x, ymin, ymax, color='k'):
        """
        Plot vertical lines at each x from ymin to ymax.  ymin or ymax
        can be scalars or len(x) numpy arrays.  If they are scalars,
        then the respective values are constant, else the heights of
        the lines are determined by ymin and ymax

        Returns a list of lines that were added
        """
        
        if is_string_like(color):
            color = self._colors.get(color)

        x = to_arrays(Float, x)
        if not iterable(ymin):
            ymin = ymin*ones(x.shape, x.typecode())
        if not iterable(ymax):
            ymax = ymax*ones(x.shape, x.typecode())

        ymin, ymax = to_arrays(Float, ymin, ymax)

        if len(ymin)!=len(x):
            raise ValueError, 'ymin and x are unequal sized sequences'
        if len(ymax)!=len(x):
            raise ValueError, 'ymax and x are unequal sized sequences'

        Y = transpose(array([ymin, ymax]))
        line = Vline2D(x, Y, color=color)
        self.add_line(line)
        return [line]

class Subplot(Axes):
    """
    Emulate matlab's subplot command, creating axes with

      Subplot(numRows, numCols, plotNum)

    where plotNum=1 is the first plot number and increasing plotNums
    fill rows first.  max(plotNum)==numRows*numCols

    You can leave out the commas if numRows<=numCols<=plotNum<10, as
    in

      Subplot(211)    # 2 rows, 1 column, first (upper) plot
    """
    
    def __init__(self, *args):
        if len(args)==1:
            s = str(*args)
            if len(s) != 3:
                raise ValueError, 'Argument to subplot must be a 3 digits long'
            rows, cols, num = map(int, s)
        elif len(args)==3:
            rows, cols, num = args
        else:
            raise ValueError, 'Illegal argument to subplot'
        total = rows*cols
        num -= 1    # convert from matlab to python indexing ie num in range(0,total)
        if num >= total:
            raise ValueError, 'Subplot number exceeds total subplots'
        left, right = .11, .9
        bottom, top = .11, .9
        rat = 0.2             # ratio of fig to seperator for multi row/col figs
        totWidth = right-left
        totHeight = top-bottom
    
        figH = totHeight/(rows + rat*(rows-1))
        sepH = rat*figH
    
        figW = totWidth/(cols + rat*(cols-1))
        sepW = rat*figW
    
        rowNum, colNum =  divmod(num, cols)
        
        figBottom = top - (rowNum+1)*figH - rowNum*sepH
        figLeft = left + colNum*(figW + sepH)
        Axes.__init__(self, [figLeft, figBottom, figW, figH])

        self.rowNum = rowNum
        self.colNum = colNum
        self.numRows = rows
        self.numCols = cols

    def is_first_col(self):
        return self.colNum==0

    def is_first_row(self):
        return self.rowNum==0

    def is_last_row(self):
        return self.rowNum==self.numRows-1


    def is_last_col(self):
        return self.colNum==self.numCols-1




class Dialog_MeasureTool(gtk.Dialog):
    def __init__(self):
        gtk.Dialog.__init__(self)
        self.set_title("Axis measurement tool")
        self.vbox.set_spacing(1)
        tooltips = gtk.Tooltips()

        self.posFmt =   'Position: x=%1.4f y=%1.4f'
        self.deltaFmt = 'Delta   : x=%1.4f y=%1.4f'

        self.positionLabel = gtk.Label(self.posFmt % (0,0))
        self.vbox.pack_start(self.positionLabel)
        self.positionLabel.show()
        tooltips.set_tip(self.positionLabel,
                         "Move the mouse to data point over axis")

        self.deltaLabel = gtk.Label(self.deltaFmt % (0,0))
        self.vbox.pack_start(self.deltaLabel)
        self.deltaLabel.show()

        tip = "Left click and hold while dragging mouse to measure " + \
              "delta x and delta y"
        tooltips.set_tip(self.deltaLabel, tip)
                         
        self.show()

    def update_position(self, x, y):
        self.positionLabel.set_text(self.posFmt % (x,y))

    def update_delta(self, dx, dy):
        self.deltaLabel.set_text(self.deltaFmt % (dx,dy))


class NavigationToolbar(gtk.Toolbar):
    def __init__(self, figure, win=None):
        gtk.Toolbar.__init__(self)
        self.win = win
        self.figure = figure
        iconSize = gtk.ICON_SIZE_SMALL_TOOLBAR
        self.set_border_width(5)
        self.set_style(gtk.TOOLBAR_ICONS)


        iconw = gtk.Image()
        iconw.set_from_stock(gtk.STOCK_GO_BACK, iconSize)
        self.bLeft = self.append_item(
            'Left',
            'Pan left with click or wheel mouse (bidirectional)',
            'Private',
            iconw,
            self.panx,
            -1)
        self.bLeft.connect("scroll_event", self.panx)

        iconw = gtk.Image()
        iconw.set_from_stock(gtk.STOCK_GO_FORWARD, iconSize)
        self.bRight = self.append_item(
            'Right',
            'Pan right with click or wheel mouse (bidirectional)',
            'Private',
            iconw,
            self.panx,
            1)
        self.bRight.connect("scroll_event", self.panx)

        iconw = gtk.Image()
        iconw.set_from_stock(gtk.STOCK_ZOOM_IN, iconSize)
        self.bZoomInX = self.append_item(
            'Zoom In X',
            'Zoom in X (shrink the x axis limits) with click or wheel mouse (bidirectional)',
            'Private',
            iconw,
            self.zoomx,
            -1)
        self.bZoomInX.connect("scroll_event", self.zoomx)

        iconw = gtk.Image()
        iconw.set_from_stock(gtk.STOCK_ZOOM_OUT, iconSize)
        self.bZoomOutX = self.append_item(
            'Zoom Out X',
            'Zoom Out X (expand the x axis limits) with click or wheel mouse (bidirectional)',
            'Private',
            iconw,
            self.zoomx,
            1)
        self.bZoomOutX.connect("scroll_event", self.zoomx)

        self.append_space()
        
        iconw = gtk.Image()
        iconw.set_from_stock(gtk.STOCK_GO_UP, iconSize)
        self.bUp = self.append_item(
            'Up',
            'Pan up with click or wheel mouse (bidirectional)',
            'Private',
            iconw,
            self.pany,
            1)
        self.bUp.connect("scroll_event", self.pany)


        iconw = gtk.Image()
        iconw.set_from_stock(gtk.STOCK_GO_DOWN, iconSize)
        self.bDown = self.append_item(
            'Down',
            'Pan down with click or wheel mouse (bidirectional)',
            'Private',
            iconw,
            self.pany,
            -1)
        self.bDown.connect("scroll_event", self.pany)

        iconw = gtk.Image()
        iconw.set_from_stock(gtk.STOCK_ZOOM_IN, iconSize)
        self.bZoomInY = self.append_item(
            'Zoom In Y',
            'Zoom in Y (shrink the y axis limits) with click or wheel mouse (bidirectional)',
            'Private',
            iconw,
            self.zoomy,
            -1)
        self.bZoomInY.connect("scroll_event", self.zoomy)

        iconw = gtk.Image()
        iconw.set_from_stock(gtk.STOCK_ZOOM_OUT, iconSize)
        self.bZoomOutY = self.append_item(
            'Zoom Out Y',
            'Zoom Out Y (expand the y axis limits) with click or wheel mouse (bidirectional)',
            'Private',
            iconw,
            self.zoomy,
            1)
        self.bZoomOutY.connect("scroll_event", self.zoomy)

        self.append_space()

        def draw(button):
            # prepare the axes for a clean redraw
            for a in figure.axes:
                a.wash_brushes()
            figure.draw()
        iconw = gtk.Image()
        iconw.set_from_stock(gtk.STOCK_CLEAR, iconSize)
        b = self.append_item(
            'Draw',
            'Redraw the figure',
            'Private',
            iconw,
            draw)

        iconw = gtk.Image()
        iconw.set_from_stock(gtk.STOCK_SAVE, iconSize)
        self.bSave = self.append_item(
            'Save',
            'Save the figure',
            'Private',
            iconw,
            self.save_figure)

        self.append_space()


        def destroy(button):
            if win is not None: win.destroy()
            else: gtk.mainquit()
        iconw = gtk.Image()
        iconw.set_from_stock(gtk.STOCK_QUIT, iconSize)
        self.bQuit = self.append_item(
            'Quit',
            'Exit the program',
            'Private',
            iconw,
            destroy)

        self.append_space()

        self.update()
    def make_axis_menu(self):

        def toggled(item, label):
            if item==itemAll:
                for item in items: item.set_active(1)
            elif item==itemInvert:
                for item in items:
                    item.set_active(not item.get_active())

            ind = [i for i,item in enumerate(items) if item.get_active()]
            self.set_active(ind)


                        
            
        menu = gtk.Menu()

        label = "All"
        itemAll = gtk.MenuItem(label)
        menu.append(itemAll)
        itemAll.connect("activate", toggled, label)
        itemAll.show()

        label = "Invert"
        itemInvert = gtk.MenuItem(label)
        menu.append(itemInvert)
        itemInvert.connect("activate", toggled, label)
        itemInvert.show()

        items = []
        for i in range(len(self._axes)):
            
            label = "Axis %d" % (i+1)
            item = gtk.CheckMenuItem(label)
            menu.append(item)
            item.connect("toggled", toggled, label)
            item.show()
            item.set_active(1)
            items.append(item)

        return menu

    def set_active(self, ind):
        self._ind = ind
        self._active = [ self._axes[i] for i in self._ind ]
        #for a in self._axes:
        #    a.wash_brushes()
        #self.figure.draw()
        
    def panx(self, button, arg):
        try: arg.direction
        except AttributeError: direction = arg
        else:
            if arg.direction == gdk.SCROLL_UP: direction=1
            else: direction=-1

        for a in self._active:
            a.get_xaxis().pan(direction)
            a.draw()
        return gtk.TRUE

    def pany(self, button, arg):
        try: arg.direction
        except AttributeError: direction = arg
        else:
            if arg.direction == gdk.SCROLL_UP: direction=1
            else: direction=-1
        for a in self._active:
            a.get_yaxis().pan(direction)
            a.draw()

    def zoomx(self, button, arg):
        try: arg.direction
        except AttributeError: direction = arg
        else:            
            if arg.direction == gdk.SCROLL_UP: direction=1
            else: direction=-1

        for a in self._active:
            a.get_xaxis().zoom(direction)
            a.draw()
        return gtk.TRUE

    def zoomy(self, button, arg):
        try: arg.direction
        except AttributeError: direction = arg
        else:
            if arg.direction == gdk.SCROLL_UP: direction=1
            else: direction=-1

        for a in self._active:
            a.get_yaxis().zoom(direction)
            a.draw()
        return gtk.TRUE

    def menu_clicked(self, button):
        if event.button==3:
            self._axisMenu.popup(None, None, None, 0, 0)


    def save_figure(self, button):
                
        def print_ok(button):
            fname = fs.get_filename()
            self.lastDir = os.path.dirname(fname)
            fs.destroy()
            try: self.figure.print_figure(fname)
            except IOError, msg:                
                err = '\n'.join(map(str, msg))
                msg = 'Failed to save %s: Error msg was\n\n%s' % (
                    fname, err)
            
        fs = gtk.FileSelection(title='Save the figure')
        if self.win is not None:
            fs.set_transient_for(self.win)
        try: self.lastDir
        except AttributeError: pass
        else: fs.set_filename(self.lastDir + os.sep)

        fs.ok_button.connect("clicked", print_ok)
        fs.cancel_button.connect("clicked", lambda b: fs.destroy())
        fs.show()


    def update(self):
        self._axes = self.figure.get_axes()
        self.set_active(range(len(self._axes)))
        if len(self._axes)>1:

            try: self.omenu
            except AttributeError:
                self.omenu = gtk.OptionMenu()
                self.omenu.set_border_width(3)
                self.omenu.show()
                self.insert_widget(
                    self.omenu,
                    'Select axes that controls affect',
                    'Private', 0)
                
            # set up the axis menu
            menu = self.make_axis_menu()
            self.omenu.set_menu(menu)
        self.set_active(range(len(self._axes)))
    
    
class Figure(gtk.DrawingArea):
    def __init__(self, size=(600, 500)):
        gtk.DrawingArea.__init__(self)
        self.axes = []
        self._lastDir = os.getcwd()
        self.set_size_request(size[0], size[1])

        #self.connect('focus_in_event', self.focus_in_event)
        self.connect('expose_event', self.expose_event)
        self.connect('configure_event', self.configure_event)
        self.connect('realize', self.realize)
        self.connect('motion_notify_event', self.motion_notify_event)
        self.connect('button_press_event', self.button_press_event)
        self.connect('button_release_event', self.button_release_event)

        self.set_events(
            #gdk.FOCUS_CHANGE_MASK|
                        gdk.EXPOSURE_MASK |
                        gdk.LEAVE_NOTIFY_MASK |
                        gdk.BUTTON_PRESS_MASK |
                        gdk.BUTTON_RELEASE_MASK |
                        gdk.POINTER_MOTION_MASK )
        

        self.inExpose = 0
        self.isConfigured=0
        self.isRealized=0
        self.printQued = None
        self.drawingArea = None
        self.drawable = None
        self.count = 0
    def add_axis(self, a):

        self.axes.append(a)
        if self.isRealized:
            a.set_drawing_area(self.drawingArea)
            a.set_fig_bgcolor(self.grey)
            a.set_size(self.width, self.height)


    def button_press_event(self, widget, event):
        win = widget.window

        if event.button==1:
            for a in self.axes:
                if not a.in_axes(event.x, event.y): continue
                self._in_x, self._in_y = \
                            a.transform_win_to_data(event.x, event.y)
                break
        return gtk.TRUE

    def button_release_event(self, widget, event):

        if event.button==1:
            try: del self._in_x, self._in_y
            except AttributeError: pass
        
        return gtk.TRUE

    def motion_notify_event(self, widget, event):

        try: self.measureDialog
        except AttributeError: return gtk.TRUE

        for a in self.axes:
            if not a.in_axes(event.x, event.y): continue
            x, y = a.transform_win_to_data(event.x, event.y)
            self.measureDialog.update_position(x,y)


            try: self.measureDialog.update_delta( x-self._in_x,
                                                  y-self._in_y)
            except AttributeError: pass
            break

        return gtk.TRUE

    def clear(self):
        self.axes = []
        self.draw()
        
    def configure_event(self, widget, event):
        self.drawingArea = widget
        self.drawable = self.drawingArea.window

        cmap = self.drawingArea.get_colormap()
        self.width, self.height = self.drawable.get_size()
        self.grey = cmap.alloc_color(197*255,202*255,197*255)
        self.black = cmap.alloc_color(0,0,0)
        for a in self.axes:
            a.set_fig_bgcolor(self.grey)
            a.set_size(self.width, self.height)

        self.isConfigured=1
        if self.isConfigured and self.isRealized:
            self.draw()
        return gtk.TRUE
        
    def draw(self, drawable=None, *args, **kwargs):
        if drawable is None: drawable=self.drawable
        if drawable is None: return 
        if not self.isRealized: return 
        
        gc = drawable.new_gc()

        if self.inExpose:
            # override the clip
            gc.set_clip_rectangle((0, 0, self.width, self.height))
        #colors = ('r', 'b', 'g', 'y')
        gc.foreground = self.grey
        #gc.foreground = ColorDispatcher().get(colors[self.count])
        drawable.draw_rectangle(gc, 1, 0, 0, self.width, self.height)

        for a in self.axes:
            a.draw(drawable)
        self.count += 1        

    def expose_event(self, widget, event):
        if self.isConfigured and self.isRealized:
            self.inExpose = 1
            for a in self.axes:
                a.wash_brushes()
            self.draw()
            self.inExpose = 0
        return gtk.TRUE

    def focus_in_event(self, widget, event):
        return gtk.TRUE

    def get_axes(self):
        return self.axes

    def print_figure(self, filename, size=(800,600)):
        "Print figure to filename; png only"


        root, ext = os.path.splitext(filename)
        ext = ext.lower()[1:]
        if ext=='png': type = 'png'
        elif ext in ('jpg', 'jpeg'): type = 'jpeg'
        else:
            error_msg('Can only save to formats png or jpeg')            
            return

        if not self.isRealized:
            self.printQued = filename
            return
        for a in self.axes:
            a.wash_brushes()
        width, height = size
        pixmap = gtk.gdk.Pixmap(self.drawable, width, height)
        gc = self.drawable.new_gc()
        gc.foreground = ColorDispatcher().get('w')
        
        pixmap.draw_rectangle(gc, gtk.TRUE, 0, 0, width, height)
        for axis in self.axes:
             axis.set_size(width, height)

        for axis in self.axes:
             axis.draw(pixmap)
             
        pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, 0, 8, width, height)
        pixbuf.get_from_drawable(pixmap, self.drawable.get_colormap(),
                                 0, 0, 0, 0, width, height)

        try: pixbuf.save(filename, type)
        except gobject.GError, msg:
            self.printQued = None
            self.configure_event(self.drawingArea, 'configure')
            self.draw()
            msg = raise_msg_to_str(msg)
            # note the error must be displayed here because trapping
            # the error on a call or print_figure may not work because
            # printing can be qued and called from realize
            error_msg('Could not save figure to %s\n\n%s' % (
                filename, msg))
        else:
            self.printQued = None
            self.configure_event(self.drawingArea, 'configure')
            for a in self.axes:
                a.wash_brushes()
            self.draw()

    def realize(self, widget):
        for a in self.axes:
            a.set_drawing_area(widget)
        self.isRealized=1
        
        if self.printQued is not None:
            self.print_figure(self.printQued)

        
if __name__=='__main__':
    import _simple_demo
    _simple_demo.subplot_demo()
    
