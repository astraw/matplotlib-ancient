"""
This module contains all the 2D line class which can draw with a
variety of line styles, markers and colors
"""

# TODO: expose cap and join style attrs
from __future__ import division

import sys, math, warnings

import agg
from numerix import Float, alltrue, arange, array, logical_and,\
     nonzero, searchsorted, take, asarray, ones, where, less, ravel, \
     greater, logical_and, cos, sin, pi, sqrt, less_equal, \
     compress, zeros, concatenate, cumsum, typecode, NewAxis
import numerix.ma as ma
from matplotlib import verbose
import artist
from artist import Artist, setp
from cbook import iterable, is_string_like, is_numlike
from colors import colorConverter

from transforms import lbwh_to_bbox, LOG10
from matplotlib import rcParams
TICKLEFT, TICKRIGHT, TICKUP, TICKDOWN = range(4)

def unmasked_index_ranges(mask, compressed = True):
    '''
    Calculate the good data ranges in a masked 1-D array, based on mask.

    Returns Nx2 array with each row the start and stop indices
    for slices of the compressed array corresponding to each of N
    uninterrupted runs of unmasked values.
    If optional argument compressed is False, it returns the
    start and stop indices into the original array, not the
    compressed array.
    Returns None if there are no unmasked values.

    Example:

    y = ma.array(arange(5), mask = [0,0,1,0,0])
    #ii = unmasked_index_ranges(y.mask())
    ii = unmasked_index_ranges(ma.getmask(y))
        # returns [[0,2,] [2,4,]]

    y.compressed().filled()[ii[1,0]:ii[1,1]]
        # returns array [3,4,]
        # (The 'filled()' method converts the masked array to a numerix array.)

    #i0, i1 = unmasked_index_ranges(y.mask(), compressed=False)
    i0, i1 = unmasked_index_ranges(ma.getmask(y), compressed=False)
        # returns [[0,3,] [2,5,]]

    y.filled()[ii[1,0]:ii[1,1]]
        # returns array [3,4,]

    '''
    m = concatenate(((1,), mask, (1,)))
    indices = arange(len(mask) + 1)
    mdif = m[1:] - m[:-1]
    i0 = compress(mdif == -1, indices)
    i1 = compress(mdif == 1, indices)
    assert len(i0) == len(i1)
    if len(i1) == 0:
        return None
    if not compressed:
        return concatenate((i0[:, NewAxis], i1[:, NewAxis]), axis=1)
    seglengths = i1 - i0
    breakpoints = cumsum(seglengths)
    ic0 = concatenate(((0,), breakpoints[:-1]))
    ic1 = breakpoints
    return concatenate((ic0[:, NewAxis], ic1[:, NewAxis]), axis=1)


class Line2D(Artist):
    lineStyles = _lineStyles =  { # hidden names deprecated
        '-'    : '_draw_solid',
        '--'   : '_draw_dashed',
        '-.'   : '_draw_dash_dot',
        ':'    : '_draw_dotted',
        'steps': '_draw_steps',
        'None' : '_draw_nothing',
        ' '    : '_draw_nothing',
        ''     : '_draw_nothing',
    }

    markers = _markers =  {  # hidden names deprecated
        '.'  : '_draw_point',
        ','  : '_draw_pixel',
        'o'  : '_draw_circle',
        'v'  : '_draw_triangle_down',
        '^'  : '_draw_triangle_up',
        '<'  : '_draw_triangle_left',
        '>'  : '_draw_triangle_right',
        '1'  : '_draw_tri_down',
        '2'  : '_draw_tri_up',
        '3'  : '_draw_tri_left',
        '4'  : '_draw_tri_right',
        's'  : '_draw_square',
        'p'  : '_draw_pentagon',
        'h'  : '_draw_hexagon1',
        'H'  : '_draw_hexagon2',
        '+'  : '_draw_plus',
        'x'  : '_draw_x',
        'D'  : '_draw_diamond',
        'd'  : '_draw_thin_diamond',
        '|'  : '_draw_vline',
        '_'  : '_draw_hline',
        TICKLEFT    : '_draw_tickleft',
        TICKRIGHT   : '_draw_tickright',
        TICKUP      : '_draw_tickup',
        TICKDOWN    : '_draw_tickdown',
        'None' : '_draw_nothing',
        ' ' : '_draw_nothing',
        '' : '_draw_nothing',
    }

    filled_markers = ('o', '^', 'v', '<', '>', 's', 'd', 'D', 'h', 'H', 'p')

    zorder = 2
    validCap = ('butt', 'round', 'projecting')
    validJoin =   ('miter', 'round', 'bevel')

    def __init__(self, xdata, ydata,
                 linewidth       = None, # all Nones default to rc
                 linestyle       = None,
                 color           = None,
                 marker          = None,
                 markersize      = None,
                 markeredgewidth = None,
                 markeredgecolor = None,
                 markerfacecolor = None,
                 antialiased     = None,
                 dash_capstyle = None,
                 solid_capstyle = None,
                 dash_joinstyle = None,
                 solid_joinstyle = None,
                 **kwargs
                 ):
        """
        Create a Line2D instance with x and y data in sequences xdata,
        ydata

        The kwargs are Line2D properties:
          alpha: float
          animated: [True | False]
          antialiased or aa: [True | False]
          clip_box: a matplotlib.transform.Bbox instance
          clip_on: [True | False]
          color or c: any matplotlib color
          dash_capstyle: ['butt' | 'round' | 'projecting']
          dash_joinstyle: ['miter' | 'round' | 'bevel']
          dashes: sequence of on/off ink in points
          data: (array xdata, array ydata)
          figure: a matplotlib.figure.Figure instance
          label: any string
          linestyle or ls: [ '-' | '--' | '-.' | ':' | 'steps' | 'None' | ' ' | '' ]
          linewidth or lw: float value in points
          lod: [True | False]
          marker: [ '+' | ',' | '.' | '1' | '2' | '3' | '4'
          markeredgecolor or mec: any matplotlib color
          markeredgewidth or mew: float value in points
          markerfacecolor or mfc: any matplotlib color
          markersize or ms: float
          solid_capstyle: ['butt' | 'round' |  'projecting']
          solid_joinstyle: ['miter' | 'round' | 'bevel']
          transform: a matplotlib.transform transformation instance
          visible: [True | False]
          xdata: array
          ydata: array
          zorder: any number
        """
        Artist.__init__(self)

        #convert sequences to numeric arrays
        if not iterable(xdata):
            raise RuntimeError('xdata must be a sequence')
        if not iterable(ydata):
            raise RuntimeError('ydata must be a sequence')

        if linewidth is None   : linewidth=rcParams['lines.linewidth']

        if linestyle is None   : linestyle=rcParams['lines.linestyle']
        if marker is None      : marker=rcParams['lines.marker']
        if color is None       : color=rcParams['lines.color']
        if markeredgecolor is None :
            markeredgecolor='auto'
        if markerfacecolor is None :
            markerfacecolor='auto'
        if markeredgewidth is None :
            markeredgewidth=rcParams['lines.markeredgewidth']

        if markersize is None  : markersize=rcParams['lines.markersize']
        if antialiased is None : antialiased=rcParams['lines.antialiased']
        if dash_capstyle is None : dash_capstyle=rcParams['lines.dash_capstyle']
        if dash_joinstyle is None : dash_joinstyle=rcParams['lines.dash_joinstyle']
        if solid_capstyle is None : solid_capstyle=rcParams['lines.solid_capstyle']
        if solid_joinstyle is None : solid_joinstyle=rcParams['lines.solid_joinstyle']

        self.set_dash_capstyle(dash_capstyle)
        self.set_dash_joinstyle(dash_joinstyle)
        self.set_solid_capstyle(solid_capstyle)
        self.set_solid_joinstyle(solid_joinstyle)


        self.set_linestyle(linestyle)
        self.set_linewidth(linewidth)
        self.set_color(color)
        self.set_marker(marker)
        self.set_antialiased(antialiased)
        self.set_markersize(markersize)
        self._dashSeq = None


        self.set_markerfacecolor(markerfacecolor)
        self.set_markeredgecolor(markeredgecolor)
        self.set_markeredgewidth(markeredgewidth)
        self._point_size_reduction = 0.5

        self.verticalOffset = None

        # update kwargs before updating data to give the caller a
        # chance to init axes (and hence unit support)
        self.update(kwargs)

        self.set_data(xdata, ydata)
        self._logcache = None

    def pick(self, mouseevent):
        """
        If mouseevent is over data that satisifies the picker, fire
        off a backend_bases.PickEvent with the additional attribute "ind"
        which is a sequence of indices into the data that meet the criteria
        """
        if not self.pickable(): return

        if self._newstyle:
            # transform in backend
            x = self._x
            y = self._y
        else:
            x, y = self._get_plottable()

        picker = self.get_picker()
        if is_numlike(picker):
            eps = picker # epsilon tolerance in points
            if len(x)==0: return
            xt, yt = self.get_transform().numerix_x_y(x, y)

            d = sqrt((xt-mouseevent.x)**2. + (yt-mouseevent.y)**2.)
            pixels = self.figure.dpi.get()/72. * eps
            ind = nonzero(less_equal(d, pixels))
            if 0:
                print 'xt', xt, mouseevent.x
                print 'yt', yt, mouseevent.y
                print 'd', (xt-mouseevent.x)**2., (yt-mouseevent.y)**2.
                print d, pixels, ind
            if len(ind):
                self.figure.canvas.pick_event(mouseevent, self, ind=ind)
        elif callable(picker):
            hit, props = picker(self, mouseevent)
            if hit:
                self.figure.canvas.pick_event(mouseevent, self, **props)



    def get_window_extent(self, renderer):
        self._newstyle = hasattr(renderer, 'draw_markers')
        if self._newstyle:
            x = self._x
            y = self._y
        else:
            x, y = self._get_plottable()


        x, y = self.get_transform().numerix_x_y(x, y)
        #x, y = self.get_transform().seq_x_y(x, y)

        left = min(x)
        bottom = min(y)
        width = max(x) - left
        height = max(y) - bottom

        # correct for marker size, if any
        if self._marker is not None:
            ms = self._markersize/72.0*self.figure.dpi.get()
            left -= ms/2
            bottom -= ms/2
            width += ms
            height += ms
        return lbwh_to_bbox( left, bottom, width, height)


    def set_axes(self, ax):
        Artist.set_axes(self, ax)
        if ax.xaxis is not None:
            self._xcid = ax.xaxis.callbacks.connect('units', self.recache)
        if ax.yaxis is not None:
            self._ycid = ax.yaxis.callbacks.connect('units', self.recache)

    def set_data(self, *args):
        """
        Set the x and y data

        ACCEPTS: (array xdata, array ydata)
        """

        if len(args)==1:
            x, y = args[0]
        else:
            x, y = args

        self._xorig = x
        self._yorig = y
        self.recache()

    def recache(self):
        #if self.axes is None: print 'recache no axes'
        #else: print 'recache units', self.axes.xaxis.units, self.axes.yaxis.units
        x = ma.asarray(self.convert_xunits(self._xorig), Float)
        y = ma.asarray(self.convert_yunits(self._yorig), Float)

        x = ma.ravel(x)
        y = ma.ravel(y)
        if len(x)==1 and len(y)>1:
            x = x * ones(y.shape, Float)
        if len(y)==1 and len(x)>1:
            y = y * ones(x.shape, Float)

        if len(x) != len(y):
            raise RuntimeError('xdata and ydata must be the same length')

        mx = ma.getmask(x)
        my = ma.getmask(y)
        mask = ma.mask_or(mx, my)
        if mask is not ma.nomask:
            x = ma.masked_array(x, mask=mask).compressed()
            y = ma.masked_array(y, mask=mask).compressed()
            self._segments = unmasked_index_ranges(mask)
        else:
            self._segments = None

        self._x = asarray(x, Float)
        self._y = asarray(y, Float)

        self._logcache = None



    def _is_sorted(self, x):
        "return true if x is sorted"
        if len(x)<2: return 1
        return alltrue(x[1:]-x[0:-1]>=0)

    def _get_plottable(self):
        # If log scale is set, only pos data will be returned

        x, y = self._x, self._y

        try: logx = self.get_transform().get_funcx().get_type()==LOG10
        except RuntimeError: logx = False  # non-separable

        try: logy = self.get_transform().get_funcy().get_type()==LOG10
        except RuntimeError: logy = False  # non-separable

        if not logx and not logy:
            return x, y

        if self._logcache is not None:
            waslogx, waslogy, xcache, ycache = self._logcache
            if logx==waslogx and waslogy==logy:
                return xcache, ycache

        Nx = len(x)
        Ny = len(y)

        if logx: indx = greater(x, 0)
        else:    indx = ones(len(x))

        if logy: indy = greater(y, 0)
        else:    indy = ones(len(y))

        ind = nonzero(logical_and(indx, indy))
        x = take(x, ind)
        y = take(y, ind)

        self._logcache = logx, logy, x, y
        return x, y


    def draw(self, renderer):
        #renderer.open_group('line2d')

        if not self._visible: return
        self._newstyle = hasattr(renderer, 'draw_markers')
        gc = renderer.new_gc()
        self._set_gc_clip(gc)

        gc.set_foreground(self._color)
        gc.set_antialiased(self._antialiased)
        gc.set_linewidth(self._linewidth)
        gc.set_alpha(self._alpha)
        if self.is_dashed():
            cap = self._dashcapstyle
            join = self._dashjoinstyle
        else:
            cap = self._solidcapstyle
            join = self._solidjoinstyle
        gc.set_joinstyle(join)
        gc.set_capstyle(cap)

        if self._newstyle:
            # transform in backend
            xt = self._x
            yt = self._y
        else:
            x, y = self._get_plottable()
            if len(x)==0: return
            xt, yt = self.get_transform().numerix_x_y(x, y)



        funcname = self._lineStyles.get(self._linestyle, '_draw_nothing')
        lineFunc = getattr(self, funcname)

        if self._segments is not None:
            for ii in self._segments:
                lineFunc(renderer, gc, xt[ii[0]:ii[1]], yt[ii[0]:ii[1]])

        else:
            lineFunc(renderer, gc, xt, yt)


        if self._marker is not None:

            gc = renderer.new_gc()
            self._set_gc_clip(gc)
            gc.set_foreground(self.get_markeredgecolor())
            gc.set_linewidth(self._markeredgewidth)
            gc.set_alpha(self._alpha)
            funcname = self._markers.get(self._marker, '_draw_nothing')
            markerFunc = getattr(self, funcname)
            markerFunc(renderer, gc, xt, yt)

        #renderer.close_group('line2d')

    def get_antialiased(self): return self._antialiased
    def get_color(self): return self._color
    def get_linestyle(self): return self._linestyle

    def get_linewidth(self): return self._linewidth
    def get_marker(self): return self._marker

    def get_markeredgecolor(self):
        if (is_string_like(self._markeredgecolor) and
            self._markeredgecolor == 'auto'):
            if self._marker in self.filled_markers:
                return 'k'
            else:
                return self._color
        else:
            return self._markeredgecolor


        return self._markeredgecolor
    def get_markeredgewidth(self): return self._markeredgewidth

    def get_markerfacecolor(self):
        if (self._markerfacecolor is None or
            (is_string_like(self._markerfacecolor) and
             self._markerfacecolor.lower()=='none') ):
            return self._markerfacecolor
        elif (is_string_like(self._markerfacecolor) and
              self._markerfacecolor.lower() == 'auto'):
            return self._color
        else:
            return self._markerfacecolor

        
    def get_markersize(self): return self._markersize

    def get_xdata(self, orig=True):
        """
        return the xdata; if orig is true return the original data,
        else the processed data
        """
        if orig:
            return self._xorig
        return self._x

    def get_ydata(self, orig=True):
        """
        return the ydata; if orig is true return the original data,
        else the processed data
        """
        if orig:
            return self._yorig
        return self._y

    def set_antialiased(self, b):
        """
        True if line should be drawin with antialiased rendering

        ACCEPTS: [True | False]
        """
        self._antialiased = b

    def set_color(self, color):
        """
        Set the color of the line

        ACCEPTS: any matplotlib color
        """
        self._color = color

    def set_linewidth(self, w):
        """
        Set the line width in points

        ACCEPTS: float value in points
        """
        self._linewidth = w

    def set_linestyle(self, linestyle):
        """
        Set the linestyle of the line

        ACCEPTS: [ '-' | '--' | '-.' | ':' | 'steps' | 'None' | ' ' | '' ]
        """
        if linestyle not in self._lineStyles:
            verbose.report('Unrecognized line style %s, %s' %
                                            (linestyle, type(linestyle)))
        if linestyle in [' ','']:
            linestyle = 'None'
        self._linestyle = linestyle
        self._lineFunc = self._lineStyles[linestyle]

    def set_marker(self, marker):
        """
        Set the line marker

        ACCEPTS: [ '+' | ',' | '.' | '1' | '2' | '3' | '4'
                 | '<' | '>' | 'D' | 'H' | '^' | '_' | 'd'
                 | 'h' | 'o' | 'p' | 's' | 'v' | 'x' | '|'
                 | TICKUP | TICKDOWN | TICKLEFT | TICKRIGHT
                 | 'None' | ' ' | '' ]

        """
        if marker not in self._markers:
            verbose.report('Unrecognized marker style %s, %s' %
                                            (marker, type(marker)))
        if marker in [' ','']:
            marker = 'None'
        self._marker = marker
        self._markerFunc = self._markers[marker]

    def set_markeredgecolor(self, ec):
        """
        Set the marker edge color

        ACCEPTS: any matplotlib color
        """
        self._markeredgecolor = ec

    def set_markeredgewidth(self, ew):
        """
        Set the marker edge width in points

        ACCEPTS: float value in points
        """
        self._markeredgewidth = ew

    def set_markerfacecolor(self, fc):
        """
        Set the marker face color

        ACCEPTS: any matplotlib color
        """
        self._markerfacecolor = fc

    def set_markersize(self, sz):
        """
        Set the marker size in points

        ACCEPTS: float
        """
        self._markersize = sz

    def set_xdata(self, x):
        """
        Set the data array for x

        ACCEPTS: array
        """
        try: del self._xsorted
        except AttributeError: pass

        self.set_data(x, self.get_ydata())

    def set_ydata(self, y):
        """
        Set the data array for y

        ACCEPTS: array
        """

        self.set_data(self.get_xdata(), y)


    def set_dashes(self, seq):
        """
        Set the dash sequence, sequence of dashes with on off ink in
        points.  If seq is empty or if seq = (None, None), the
        linestyle will be set to solid.

        ACCEPTS: sequence of on/off ink in points
        """
        if seq == (None, None) or len(seq)==0:
            self.set_linestyle('-')
        else:
            self.set_linestyle('--')
        self._dashSeq = seq  # TODO: offset ignored for now

    def _draw_nothing(self, renderer, gc, xt, yt):
        pass

    def _draw_steps(self, renderer, gc, xt, yt):
        siz=len(xt)
        if siz<2: return
        xt2=ones((2*siz,), typecode(xt))
        xt2[0:-1:2], xt2[1:-1:2], xt2[-1]=xt, xt[1:], xt[-1]
        yt2=ones((2*siz,), typecode(yt))
        yt2[0:-1:2], yt2[1::2]=yt, yt
        gc.set_linestyle('solid')

        if self._newstyle:
            renderer.draw_lines(gc, xt2, yt2, self.get_transform())
        else:
            renderer.draw_lines(gc, xt2, yt2)

    def _draw_solid(self, renderer, gc, xt, yt):
        if len(xt)<2: return
        gc.set_linestyle('solid')
        if self._newstyle:
            renderer.draw_lines(gc, xt, yt, self.get_transform())
        else:
            renderer.draw_lines(gc, xt, yt)


    def _draw_dashed(self, renderer, gc, xt, yt):
        if len(xt)<2: return
        gc.set_linestyle('dashed')
        if self._dashSeq is not None:
            gc.set_dashes(0, self._dashSeq)

        if self._newstyle:
            renderer.draw_lines(gc, xt, yt, self.get_transform())
        else:
            renderer.draw_lines(gc, xt, yt)


    def _draw_dash_dot(self, renderer, gc, xt, yt):
        if len(xt)<2: return
        gc.set_linestyle('dashdot')
        if self._newstyle:
            renderer.draw_lines(gc, xt, yt, self.get_transform())
        else:
            renderer.draw_lines(gc, xt, yt)

    def _draw_dotted(self, renderer, gc, xt, yt):

        if len(xt)<2: return
        gc.set_linestyle('dotted')
        if self._newstyle:
            renderer.draw_lines(gc, xt, yt, self.get_transform())
        else:
            renderer.draw_lines(gc, xt, yt)

    def _draw_point(self, renderer, gc, xt, yt):

        r = 0.5 * renderer.points_to_pixels(self._markersize)
        r *= self._point_size_reduction
        gc.set_linewidth(0)
        if r <= 0.5:
            self._draw_pixel(renderer, gc, xt, yt)
        elif r <= 2:
            self._draw_hexagon1(renderer, gc, xt, yt, point=True)
        else:
            self._draw_circle(renderer, gc, xt, yt, point=True)

    def _draw_pixel(self, renderer, gc, xt, yt):
        if self._newstyle:
            rgbFace = self._get_rgb_face()
            path = agg.path_storage()
            path.move_to(-0.5, -0.5)
            path.line_to(-0.5, 0.5)
            path.line_to(0.5, 0.5)
            path.line_to(0.5, -0.5)
            renderer.draw_markers(gc, path, rgbFace, xt, yt, self.get_transform())
        else:
            for (x,y) in zip(xt, yt):
                renderer.draw_point(gc, x, y)


    def _draw_circle(self, renderer, gc, xt, yt, point=False):

        w = renderer.points_to_pixels(self._markersize)
        if point:
            w *= self._point_size_reduction


        rgbFace = self._get_rgb_face()

        if self._newstyle:
            N = 50.0
            r = w/2.
            rads = (2*math.pi/N)*arange(N)
            xs = r*cos(rads)
            ys = r*sin(rads)
            # todo: use curve3!
            path = agg.path_storage()
            path.move_to(xs[0], ys[0])
            for x, y in zip(xs[1:], ys[1:]):
                path.line_to(x, y)

            path.end_poly()
            renderer.draw_markers(gc, path, rgbFace, xt, yt, self.get_transform())
        else:
            for (x,y) in zip(xt,yt):
                renderer.draw_arc(gc, rgbFace,
                                  x, y, w, w, 0.0, 360.0, 0.0)



    def _draw_triangle_up(self, renderer, gc, xt, yt):


        offset = 0.5*renderer.points_to_pixels(self._markersize)
        rgbFace = self._get_rgb_face()

        if self._newstyle:
            path = agg.path_storage()
            path.move_to(0, offset)
            path.line_to(-offset, -offset)
            path.line_to(offset, -offset)
            path.end_poly()
            renderer.draw_markers(gc, path, rgbFace, xt, yt, self.get_transform())
        else:
            for (x,y) in zip(xt, yt):
                verts = ( (x, y+offset),
                          (x-offset, y-offset),
                          (x+offset, y-offset) )
                renderer.draw_polygon(gc, rgbFace, verts)


    def _draw_triangle_down(self, renderer, gc, xt, yt):
        offset = 0.5*renderer.points_to_pixels(self._markersize)
        rgbFace = self._get_rgb_face()

        if self._newstyle:

            path = agg.path_storage()
            path.move_to(-offset, offset)
            path.line_to(offset, offset)
            path.line_to(0, -offset)
            path.end_poly()

            renderer.draw_markers(gc, path, rgbFace, xt, yt, self.get_transform())
        else:
            for (x,y) in zip(xt, yt):
                verts = ( (x-offset, y+offset),
                          (x+offset, y+offset),
                          (x, y-offset))
                renderer.draw_polygon(gc, rgbFace, verts)

    def _draw_triangle_left(self, renderer, gc, xt, yt):
        offset = 0.5*renderer.points_to_pixels(self._markersize)
        rgbFace = self._get_rgb_face()

        if self._newstyle:

            path = agg.path_storage()
            path.move_to(-offset, 0)
            path.line_to(offset, -offset)
            path.line_to(offset, offset)
            path.end_poly()

            renderer.draw_markers(gc, path, rgbFace, xt, yt, self.get_transform())
        else:
            for (x,y) in zip(xt, yt):
                verts = ( (x-offset, y),
                          (x+offset, y-offset),
                          (x+offset, y+offset))
                renderer.draw_polygon(gc, rgbFace, verts)


    def _draw_triangle_right(self, renderer, gc, xt, yt):
        offset = 0.5*renderer.points_to_pixels(self._markersize)
        rgbFace = self._get_rgb_face()
        if self._newstyle:
            path = agg.path_storage()
            path.move_to(offset, 0)
            path.line_to(-offset, -offset)
            path.line_to(-offset, offset)
            path.end_poly()
            renderer.draw_markers(gc, path, rgbFace, xt, yt, self.get_transform())
        else:
            for (x,y) in zip(xt, yt):
                verts = ( (x+offset, y),
                          (x-offset, y-offset),
                          (x-offset, y+offset))
                renderer.draw_polygon(gc, rgbFace, verts)



    def _draw_square(self, renderer, gc, xt, yt):
        side = renderer.points_to_pixels(self._markersize)
        offset = side*0.5
        rgbFace = self._get_rgb_face()

        if self._newstyle:

            path = agg.path_storage()
            path.move_to(-offset, -offset)
            path.line_to(-offset, offset)
            path.line_to(offset, offset)
            path.line_to(offset, -offset)
            path.end_poly()

            renderer.draw_markers(gc, path, rgbFace, xt, yt, self.get_transform())
        else:

            for (x,y) in zip(xt, yt):
                renderer.draw_rectangle(
                    gc, rgbFace,
                    x-offset, y-offset, side, side)

    def _draw_diamond(self, renderer, gc, xt, yt):
        offset = 0.6*renderer.points_to_pixels(self._markersize)
        rgbFace = self._get_rgb_face()
        if self._newstyle:
            path = agg.path_storage()
            path.move_to(offset, 0)
            path.line_to(0, -offset)
            path.line_to(-offset, 0)
            path.line_to(0, offset)
            path.end_poly()

            renderer.draw_markers(gc, path, rgbFace, xt, yt, self.get_transform())
        else:


            for (x,y) in zip(xt, yt):
                verts = ( (x+offset, y),
                          (x, y-offset),
                          (x-offset, y),
                          (x, y+offset))
                renderer.draw_polygon(gc, rgbFace, verts)

    def _draw_thin_diamond(self, renderer, gc, xt, yt):
        offset = 0.7*renderer.points_to_pixels(self._markersize)
        xoffset = 0.6*offset
        rgbFace = self._get_rgb_face()

        if self._newstyle:
            path = agg.path_storage()
            path.move_to(xoffset, 0)
            path.line_to(0, -offset)
            path.line_to(-xoffset, 0)
            path.line_to(0, offset)
            path.end_poly()
            renderer.draw_markers(gc, path, rgbFace, xt, yt, self.get_transform())
        else:
            for (x,y) in zip(xt, yt):
                verts = ( (x+xoffset, y),
                          (x, y-offset),
                          (x-xoffset, y),
                          (x, y+offset))
                renderer.draw_polygon(gc, rgbFace, verts)

    def _draw_pentagon(self, renderer, gc, xt, yt):
        offset = 0.6*renderer.points_to_pixels(self._markersize)
        offsetX1 = offset*0.95
        offsetY1 = offset*0.31
        offsetX2 = offset*0.59
        offsetY2 = offset*0.81
        rgbFace = self._get_rgb_face()

        if self._newstyle:
            path = agg.path_storage()
            path.move_to(0, offset)
            path.line_to(-offsetX1, offsetY1)
            path.line_to(-offsetX2, -offsetY2)
            path.line_to(+offsetX2, -offsetY2)
            path.line_to(+offsetX1, offsetY1)
            path.end_poly()

            renderer.draw_markers(gc, path, rgbFace, xt, yt, self.get_transform())
        else:
            for (x,y) in zip(xt, yt):
                verts = ( (x, y+offset),
                          (x-offsetX1, y+offsetY1),
                          (x-offsetX2, y-offsetY2),
                          (x+offsetX2, y-offsetY2),
                          (x+offsetX1, y+offsetY1))
                renderer.draw_polygon(gc, rgbFace, verts)

    def _draw_hexagon1(self, renderer, gc, xt, yt, point=False):
        offset = 0.6*renderer.points_to_pixels(self._markersize)
        if point:
            offset *= self._point_size_reduction
        offsetX1 = offset*0.87
        offsetY1 = offset*0.5
        rgbFace = self._get_rgb_face()

        if self._newstyle:
            path = agg.path_storage()
            path.move_to(0, offset)
            path.line_to(-offsetX1, offsetY1)
            path.line_to(-offsetX1, -offsetY1)
            path.line_to(0, -offset)
            path.line_to(offsetX1, -offsetY1)
            path.line_to(offsetX1, offsetY1)
            path.end_poly()
            renderer.draw_markers(gc, path, rgbFace, xt, yt, self.get_transform())
        else:
            for (x,y) in zip(xt, yt):
                verts = ( (x, y+offset),
                          (x-offsetX1, y+offsetY1),
                          (x-offsetX1, y-offsetY1),
                          (x, y-offset),
                          (x+offsetX1, y-offsetY1),
                          (x+offsetX1, y+offsetY1))
                renderer.draw_polygon(gc, rgbFace, verts)

    def _draw_hexagon2(self, renderer, gc, xt, yt):
        offset = 0.6*renderer.points_to_pixels(self._markersize)
        offsetX1 = offset*0.5
        offsetY1 = offset*0.87
        rgbFace = self._get_rgb_face()
        if self._newstyle:
            path = agg.path_storage()
            path.move_to(offset, 0)
            path.line_to(offsetX1, offsetY1)
            path.line_to(-offsetX1, offsetY1)
            path.line_to(-offset, 0)
            path.line_to(-offsetX1, -offsetY1)
            path.line_to(offsetX1, -offsetY1)
            path.end_poly()

            renderer.draw_markers(gc, path, rgbFace, xt, yt, self.get_transform())
        else:
            for (x,y) in zip(xt, yt):
                verts = ( (x+offset, y),
                          (x+offsetX1, y+offsetY1),
                          (x-offsetX1, y+offsetY1),
                          (x-offset, y),
                          (x-offsetX1, y-offsetY1),
                          (x+offsetX1, y-offsetY1))
                renderer.draw_polygon(gc, rgbFace, verts)

    def _draw_vline(self, renderer, gc, xt, yt):
        offset = 0.5*renderer.points_to_pixels(self._markersize)
        if self._newstyle:
            path = agg.path_storage()
            path.move_to(0, -offset)
            path.line_to(0, offset)
            renderer.draw_markers(gc, path, None, xt, yt, self.get_transform())
        else:
            for (x,y) in zip(xt, yt):
                renderer.draw_line(gc, x, y-offset, x, y+offset)

    def _draw_hline(self, renderer, gc, xt, yt):
        offset = 0.5*renderer.points_to_pixels(self._markersize)
        if self._newstyle:
            path = agg.path_storage()
            path.move_to(-offset, 0)
            path.line_to(offset, 0)
            renderer.draw_markers(gc, path, None, xt, yt, self.get_transform())
        else:
            for (x,y) in zip(xt, yt):
                renderer.draw_line(gc, x-offset, y, x+offset, y)

    def _draw_tickleft(self, renderer, gc, xt, yt):
        offset = renderer.points_to_pixels(self._markersize)
        if self._newstyle:
            path = agg.path_storage()
            path.move_to(-offset, 0.5)
            path.line_to(0, 0.5)
            renderer.draw_markers(gc, path, None, xt, yt, self.get_transform())
        else:
            for (x,y) in zip(xt, yt):
                renderer.draw_line(gc, x-offset, y, x, y)

    def _draw_tickright(self, renderer, gc, xt, yt):

        offset = renderer.points_to_pixels(self._markersize)
        if self._newstyle:
            path = agg.path_storage()
            path.move_to(0, 0.5)
            path.line_to(offset, 0.5)
            renderer.draw_markers(gc, path, None, xt, yt, self.get_transform())
        else:
            for (x,y) in zip(xt, yt):
                renderer.draw_line(gc, x, y, x+offset, y)

    def _draw_tickup(self, renderer, gc, xt, yt):
        offset = renderer.points_to_pixels(self._markersize)
        if self._newstyle:
            path = agg.path_storage()
            path.move_to(-0.5, 0)
            path.line_to(-0.5, offset)
            renderer.draw_markers(gc, path, None, xt, yt, self.get_transform())
        else:
            for (x,y) in zip(xt, yt):
                renderer.draw_line(gc, x, y, x, y+offset)

    def _draw_tickdown(self, renderer, gc, xt, yt):
        offset = renderer.points_to_pixels(self._markersize)
        if self._newstyle:
            path = agg.path_storage()
            path.move_to(-0.5, -offset)
            path.line_to(-0.5, 0)
            renderer.draw_markers(gc, path, None, xt, yt, self.get_transform())
        else:
            for (x,y) in zip(xt, yt):
                renderer.draw_line(gc, x, y-offset, x, y)

    def _draw_plus(self, renderer, gc, xt, yt):
        offset = 0.5*renderer.points_to_pixels(self._markersize)
        if self._newstyle:

            path = agg.path_storage()
            path.move_to(-offset, 0)
            path.line_to( offset, 0)
            path.move_to( 0, -offset)
            path.line_to( 0, offset)
            renderer.draw_markers(gc, path, None, xt, yt, self.get_transform())
        else:
            for (x,y) in zip(xt, yt):
                renderer.draw_line(gc, x-offset, y, x+offset, y)
                renderer.draw_line(gc, x, y-offset, x, y+offset)

    def _draw_tri_down(self, renderer, gc, xt, yt):
        offset = 0.5*renderer.points_to_pixels(self._markersize)
        offset1 = offset*0.8
        offset2 = offset*0.5
        if self._newstyle:
            path = agg.path_storage()
            path.move_to(0, 0)
            path.line_to(0, -offset)
            path.move_to(0, 0)
            path.line_to(offset1, offset2)
            path.move_to(0, 0)
            path.line_to(-offset1, offset2)
            renderer.draw_markers(gc, path, None, xt, yt, self.get_transform())
        else:
            for (x,y) in zip(xt, yt):
                renderer.draw_line(gc, x, y, x, y-offset)
                renderer.draw_line(gc, x, y, x+offset1, y+offset2)
                renderer.draw_line(gc, x, y, x-offset1, y+offset2)

    def _draw_tri_up(self, renderer, gc, xt, yt):
        offset = 0.5*renderer.points_to_pixels(self._markersize)
        offset1 = offset*0.8
        offset2 = offset*0.5
        if self._newstyle:
            path = agg.path_storage()
            path.move_to(0, 0)
            path.line_to(0, offset)
            path.move_to(0, 0)
            path.line_to(offset1, -offset2)
            path.move_to(0, 0)
            path.line_to(-offset1, -offset2)
            renderer.draw_markers(gc, path, None, xt, yt, self.get_transform())
        else:
            for (x,y) in zip(xt, yt):
                renderer.draw_line(gc, x, y, x, y+offset)
                renderer.draw_line(gc, x, y, x+offset1, y-offset2)
                renderer.draw_line(gc, x, y, x-offset1, y-offset2)

    def _draw_tri_left(self, renderer, gc, xt, yt):
        offset = 0.5*renderer.points_to_pixels(self._markersize)
        offset1 = offset*0.8
        offset2 = offset*0.5
        if self._newstyle:
            path = agg.path_storage()
            path.move_to(0, 0)
            path.line_to(-offset, 0)
            path.move_to(0, 0)
            path.line_to(offset2, offset1)
            path.move_to(0, 0)
            path.line_to(offset2, -offset1)
            renderer.draw_markers(gc, path, None, xt, yt, self.get_transform())
        else:
            for (x,y) in zip(xt, yt):
                renderer.draw_line(gc, x, y, x-offset, y)
                renderer.draw_line(gc, x, y, x+offset2, y+offset1)
                renderer.draw_line(gc, x, y, x+offset2, y-offset1)

    def _draw_tri_right(self, renderer, gc, xt, yt):
        offset = 0.5*renderer.points_to_pixels(self._markersize)
        offset1 = offset*0.8
        offset2 = offset*0.5
        if self._newstyle:
            path = agg.path_storage()
            path.move_to(0, 0)
            path.line_to(offset, 0)
            path.move_to(0, 0)
            path.line_to(-offset2, offset1)
            path.move_to(0, 0)
            path.line_to(-offset2, -offset1)
            renderer.draw_markers(gc, path, None, xt, yt, self.get_transform())
        else:
            for (x,y) in zip(xt, yt):
                renderer.draw_line(gc, x, y, x+offset, y)
                renderer.draw_line(gc, x, y, x-offset2, y+offset1)
                renderer.draw_line(gc, x, y, x-offset2, y-offset1)

    def _draw_x(self, renderer, gc, xt, yt):
        offset = 0.5*renderer.points_to_pixels(self._markersize)

        if self._newstyle:
            path = agg.path_storage()
            path.move_to(-offset, -offset)
            path.line_to(offset, offset)
            path.move_to(-offset, offset)
            path.line_to(offset, -offset)
            renderer.draw_markers(gc, path, None, xt, yt, self.get_transform())
        else:
            for (x,y) in zip(xt, yt):
                renderer.draw_line(gc, x-offset, y-offset, x+offset, y+offset)
                renderer.draw_line(gc, x-offset, y+offset, x+offset, y-offset)

    def update_from(self, other):
        'copy properties from other to self'
        Artist.update_from(self, other)
        self._linestyle = other._linestyle
        self._linewidth = other._linewidth
        self._color = other._color
        self._markersize = other._markersize
        self._markerfacecolor = other._markerfacecolor
        self._markeredgecolor = other._markeredgecolor
        self._markeredgewidth = other._markeredgewidth
        self._dashSeq = other._dashSeq
        self._dashcapstyle = other._dashcapstyle
        self._dashjoinstyle = other._dashjoinstyle
        self._solidcapstyle = other._solidcapstyle
        self._solidjoinstyle = other._solidjoinstyle

        self._linestyle = other._linestyle
        self._marker = other._marker


    def _get_rgb_face(self):
        facecolor = self.get_markerfacecolor()
        if is_string_like(facecolor) and facecolor.lower()=='none':
            rgbFace = None
        else:
            rgbFace = colorConverter.to_rgb(facecolor)
        return rgbFace

    # some aliases....
    def set_aa(self, val):
        'alias for set_antialiased'
        self.set_antialiased(val)

    def set_c(self, val):
        'alias for set_color'
        self.set_color(val)


    def set_ls(self, val):
        'alias for set_linestyle'
        self.set_linestyle(val)


    def set_lw(self, val):
        'alias for set_linewidth'
        self.set_linewidth(val)


    def set_mec(self, val):
        'alias for set_markeredgecolor'
        self.set_markeredgecolor(val)


    def set_mew(self, val):
        'alias for set_markeredgewidth'
        self.set_markeredgewidth(val)


    def set_mfc(self, val):
        'alias for set_markerfacecolor'
        self.set_markerfacecolor(val)


    def set_ms(self, val):
        'alias for set_markersize'
        self.set_markersize(val)

    def get_aa(self):
        'alias for get_antialiased'
        return self.get_antialiased()

    def get_c(self):
        'alias for get_color'
        return self.get_color()


    def get_ls(self):
        'alias for get_linestyle'
        return self.get_linestyle()


    def get_lw(self):
        'alias for get_linewidth'
        return self.get_linewidth()


    def get_mec(self):
        'alias for get_markeredgecolor'
        return self.get_markeredgecolor()


    def get_mew(self):
        'alias for get_markeredgewidth'
        return self.get_markeredgewidth()


    def get_mfc(self):
        'alias for get_markerfacecolor'
        return self.get_markerfacecolor()


    def get_ms(self):
        'alias for get_markersize'
        return self.get_markersize()

    def set_dash_joinstyle(self, s):
        """
        Set the join style for dashed linestyles
        ACCEPTS: ['miter' | 'round' | 'bevel']
        """
        s = s.lower()
        if s not in self.validJoin:
            raise ValueError('set_dash_joinstyle passed "%s";\n' % (s,)
                  + 'valid joinstyles are %s' % (self.validJoin,))
        self._dashjoinstyle = s

    def set_solid_joinstyle(self, s):
        """
        Set the join style for solid linestyles
        ACCEPTS: ['miter' | 'round' | 'bevel']
        """
        s = s.lower()
        if s not in self.validJoin:
            raise ValueError('set_solid_joinstyle passed "%s";\n' % (s,)
                  + 'valid joinstyles are %s' % (self.validJoin,))
        self._solidjoinstyle = s


    def get_dash_joinstyle(self):
        """
        Get the join style for dashed linestyles
        """
        return self._dashjoinstyle

    def get_solid_joinstyle(self):
        """
        Get the join style for solid linestyles
        """
        return self._solidjoinstyle

    def set_dash_capstyle(self, s):
        """
        Set the cap style for dashed linestyles
        ACCEPTS: ['butt' | 'round' | 'projecting']
        """
        s = s.lower()
        if s not in self.validCap:
            raise ValueError('set_dash_capstyle passed "%s";\n' % (s,)
                  + 'valid capstyles are %s' % (self.validCap,))

        self._dashcapstyle = s


    def set_solid_capstyle(self, s):
        """
        Set the cap style for solid linestyles
        ACCEPTS: ['butt' | 'round' |  'projecting']
        """
        s = s.lower()
        if s not in self.validCap:
            raise ValueError('set_solid_capstyle passed "%s";\n' % (s,)
                  + 'valid capstyles are %s' % (self.validCap,))

        self._solidcapstyle = s


    def get_dash_capstyle(self):
        """
        Get the cap style for dashed linestyles
        """
        return self._dashcapstyle

    def get_solid_capstyle(self):
        """
        Get the cap style for solid linestyles
        """
        return self._solidcapstyle

    def is_dashed(self):
        'return True if line is dashstyle'
        return self._linestyle in ('--', '-.', ':')


lineStyles = Line2D._lineStyles
lineMarkers = Line2D._markers

artist.kwdocd['Line2D'] = artist.kwdoc(Line2D)
