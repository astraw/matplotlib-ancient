"""
This module contains all the 2D line primititive classes, including
the dispatcher class that returns line instances from a format string.
"""

from __future__ import generators
from __future__ import division

import pygtk
pygtk.require('2.0')
import gtk
from gtk import gdk
import Numeric as numpy

from cbook import is_string_like
from colors import ColorDispatcher
from artist import Artist


class Line2D(Artist):
    
    def __init__(self, x, y,
                 lineWidth=1, 
                 color=ColorDispatcher().get('b')):
        Artist.__init__(self)
        #convert sequences to numeric arrays


        self._linewidth = lineWidth
        if is_string_like(color):
            color = ColorDispatcher().get(color)
        self._color = color
        self.verticalOffset = None
        
        self.set_data(x, y)

    def set_data(self, x, y):
        try: x.shape
        except AttributeError: self._x = numpy.array(x, numpy.Float)
        else: self._x = x
        
        try: y.shape
        except AttributeError: self._y = numpy.array(y, numpy.Float)
        else: self._y = y

        if len(self._x.shape)>1 and self._x.shape[1]==1:
            self._x = numpy.resize(self._x, (len(x),))
        if len(self._y.shape)>1 and self._y.shape[1]==1:
            self._y = numpy.resize(self._y, (len(y),))

        self._xsorted = self._is_sorted(self._x)

    def set_vertical_offset(self, voff):
        self.verticalOffset = voff
        
    def _is_sorted(self, x):
        "return true if x is sorted"
        if len(x)<2: return 1
        return numpy.alltrue(x[1:]-x[0:-1]>=0)
    
    def _get_numeric_clipped_data_in_range(self):
        # if the x or y clip is set, only plot the points in the clipping region
        try: self._xc, self._yc
        except AttributeError: x, y = self._x, self._y
        else: x, y = self._xc, self._yc
        # transform into axes coords            

        if self.verticalOffset is not None:
            #print self.verticalOffset, y.typecode()
            y = y + self.verticalOffset
            
        return x, y

    def _draw(self, drawable, *args, **kwargs):
        gc = drawable.new_gc()
        gc.foreground = self._color
        gc.line_width = self._linewidth
        self.clip_gc(gc)
        
        x, y = self._get_numeric_clipped_data_in_range()
        if len(x)==0: return 
        xt, yt = self.transform_points_to_win(x, y)
        self._derived_draw(drawable, gc, xt, yt)

    def _derived_draw(self, drawable, gc, x, y):
        raise NotImplementedError, 'Line2D is a pure base class.  ' + \
              'You must instantiate a derived class'

    def flush_clip(self):
        delList = ['_xmin', '_xmax', '_ymin', '_ymax', '_xc', '_yc']
        for item in delList:
            try: del self.__dict__[item]
            except KeyError: pass

    def get_x(self):
        return self._x

    def get_y(self):
        return self._y


    def get_linewidth(self):
        return self._linewidth

    def get_color(self):
        return self._color

    def get_data_extent(self):
        """
        Return the bounding box as left, bottom, width, height in
        window coords
        """
        x, y = self._get_numeric_clipped_data_in_range()
        minx, maxx = min(x), max(x)
        miny, maxy = min(y), max(y)
        return minx, maxy, maxx-minx, maxy-miny
        
    def _set_clip(self):

        try: self._xmin, self._xmax
        except AttributeError: indx = numpy.arange(len(self._x))
        else:
            if len(self._x)==1:
                indx = 0
            elif self._xsorted:
                # for really long signals, if we know they are sorted
                # on x we can save a lot of time using search sorted
                # since the alternative approach requires 3 O(len(x) ) ops
                inds = numpy.searchsorted(
                    self._x, numpy.array([self._xmin, self._xmax]))
                indx = numpy.arange(inds[0], inds[1])
            else:
                indx = numpy.nonzero(
                    numpy.logical_and( self._x>=self._xmin,
                                       self._x<=self._xmax ))
        

        self._xc = numpy.take(self._x, indx)
        self._yc = numpy.take(self._y, indx)

        # y data clipping for connected lines can introduce horizontal
        # line artifacts near the clip region.  If you really need y
        # clipping for efficiency, consider using plot(y,x) instead.
        # If you must have both x and y data clipping, and can live
        # with the artifacts for high gain y clipping, , do 'if 1'
        # instead of isinstance.
        if ( self._yc.shape==self._xc.shape and 
             not isinstance(self, ConnectedLine2D) ):
            try: self._ymin, self._ymax
            except AttributeError: indy = numpy.arange(len(self._yc))
            else: indy = numpy.nonzero(
                numpy.logical_and(self._yc>=self._ymin,
                                  self._yc<=self._ymax ))
        else:
            indy = numpy.arange(len(self._yc))
            
        self._xc = numpy.take(self._xc, indy)
        self._yc = numpy.take(self._yc, indy)

    def set_color(self, color):
        if is_string_like(color):
            color = ColorDispatcher().get(color)
        self._color = color

    def set_linewidth(self, w):
        self._linewidth = w

    def set_xclip(self, xmin, xmax):
        self._xmin, self._xmax = xmin, xmax
        self._set_clip()

    def set_yclip(self, ymin, ymax):
        self._ymin, self._ymax = ymin, ymax
        self._set_clip()


class ConnectedLine2D(Line2D):
    """
    ConnectedLine2D is just a type info holder, so you can, for
    example, ask an axes for all the connected lines it contains
    """
    pass

class SolidLine2D(ConnectedLine2D):
    def __init__(self, x, y, *args, **kargs):
        Line2D.__init__(self, x, y, *args, **kargs)

    def _derived_draw(self, drawable, gc, xt, yt):
        drawable.draw_lines(gc, zip(xt,yt))


class DashedLine2D(ConnectedLine2D):
    def __init__(self, x, y, *args, **kargs):
        Line2D.__init__(self, x, y, *args, **kargs)

    def _derived_draw(self, drawable, gc, xt, yt):
        gc.line_style = gdk.LINE_ON_OFF_DASH
        gc.cap_style =  gdk.CAP_BUTT
        gc.join_style = gdk.JOIN_MITER
        drawable.draw_lines(gc, zip(xt, yt) )

class DashDotLine2D(ConnectedLine2D):
    def __init__(self, x, y, *args, **kargs):
        Line2D.__init__(self, x, y, *args, **kargs)
        raise RuntimeError, 'DashDotLine2D i not yet implemented.  (sorry)'        


class DottedLine2D(ConnectedLine2D):
    "this is connected because there can be dots between the x,y points"
    def __init__(self, x, y, *args, **kargs):
        Line2D.__init__(self, x, y, *args, **kargs)
        self._spacing = 2
        
    def _derived_draw(self, drawable, gc, xt, yt):
        gc.line_style = gdk.LINE_ON_OFF_DASH
        gc.cap_style =  gdk.CAP_BUTT
        gc.join_style = gdk.JOIN_ROUND
        gc.set_dashes(0,[1,self._spacing])
        drawable.draw_lines(gc, zip(xt, yt) )

    def set_spacing(self, spacing):
        self._spacing = spacing

class SymbolLine2D(Line2D):
    def __init__(self, x, y,
                 symbolSize=5, symbolFill=0,
                 *args, **kargs):
        Line2D.__init__(self, x, y, *args, **kargs)
        self._symbolSize = symbolSize
        self._symbolFill = symbolFill
    
    def set_fill(self, fill):
        self._symbolFill = fill

    def set_size(self, size):
        self._symbolSize = size

    def get_fill(self):
        return self._symbolFill

    def get_size(self):
        return self._symbolSize

class Vline2D(SymbolLine2D):
    """
    A special vertical line symbol.  The y values are len(x) x 2 and
    give ymin, ymax for the vertical line
    """
    def __init__(self, x, y,
                 *args, **kargs):
        SymbolLine2D.__init__(self, x, y,
                              *args, **kargs)

    def _derived_draw(self, drawable, gc, xt, yt):
        for (x,y) in zip(xt, yt):
            drawable.draw_line(gc, x, y[0], x, y[1])

    def get_y(self):
        return numpy.reshape(self._y, (2*len(self._x),))


class CircleLine2D(SymbolLine2D):
    def __init__(self, x, y,
                 *args, **kargs):
        SymbolLine2D.__init__(self, x, y,
                              *args, **kargs)

    def _derived_draw(self, drawable, gc, xt, yt):
        offset = self._symbolSize/2
        for (x,y) in zip(xt, yt):
            drawable.draw_arc(gc, self._symbolFill, x-offset, y-offset, 
                            self._symbolSize, self._symbolSize,
                            0, 360*64)



class PointLine2D(SymbolLine2D):
    def __init__(self, x, y,
                 symbolSize=3, symbolFill=1,
                 *args, **kargs):
        SymbolLine2D.__init__(self, x, y,
                              symbolSize=symbolSize,
                              symbolFill=symbolFill,
                              *args, **kargs)

    def _derived_draw(self, drawable, gc, xt, yt):
        offset = self._symbolSize/2
        for (x,y) in zip(xt, yt):
            drawable.draw_arc(gc, self._symbolFill, x-offset, y-offset, 
                            self._symbolSize, self._symbolSize,
                            0, 360*64)

class PixelLine2D(SymbolLine2D):
    def __init__(self, x, y,
                 *args, **kargs):
        "Draw the points with the smallest point available: a pixel"
        SymbolLine2D.__init__(self, x, y,
                              *args, **kargs)

    def _derived_draw(self, drawable, gc, xt, yt):
        for (x,y) in zip(xt, yt):
            drawable.draw_point(gc, x, y)


#Note I am not making triangles are squares with patches because I
#want the symbol sizes to be scale invariant, unlike patches
class SquareLine2D(SymbolLine2D):
    def __init__(self, x, y, *args, **kargs):
        SymbolLine2D.__init__(self, x, y, *args, **kargs)

    def _derived_draw(self, drawable, gc, xt, yt):
        offset = self._symbolSize/2        
        for (x,y) in zip(xt, yt):            
            drawable.draw_rectangle(gc, self._symbolFill,
                                         x-offset, y-offset,
                                         self._symbolSize, self._symbolSize) 


class TriangleUpLine2D(SymbolLine2D):
    def __init__(self, x, y, *args, **kargs):
        SymbolLine2D.__init__(self, x, y, *args, **kargs)

    def _derived_draw(self, drawable, gc, xt, yt):
        offset = self._symbolSize/2        
        for (x,y) in zip(xt, yt):            
            drawable.draw_polygon(gc, self._symbolFill,
                                ( (x, y-offset),
                                  (x-offset, y+offset),
                                  (x+offset, y+offset)
                                ))
        


class TriangleDownLine2D(SymbolLine2D):
    def __init__(self, x, y,*args, **kargs):
        SymbolLine2D.__init__(self, x, y, *args, **kargs)

    def _derived_draw(self, drawable, gc, xt, yt):
        offset = self._symbolSize/2        
        for (x,y) in zip(xt, yt):            
            drawable.draw_polygon(gc, self._symbolFill,
                                ( (x, y+offset),
                                  (x-offset, y-offset),
                                  (x+offset, y-offset)
                                ))
    

class TriangleLeftLine2D(SymbolLine2D):
    def __init__(self, x, y,*args, **kargs):
        SymbolLine2D.__init__(self, x, y, *args, **kargs)

    def _derived_draw(self, drawable, gc, xt, yt):
        offset = self._symbolSize/2        
        for (x,y) in zip(xt, yt):            
            drawable.draw_polygon(gc, self._symbolFill,
                                ( (x-offset, y),
                                  (x+offset, y-offset),
                                  (x+offset, y+offset)
                                ))


class TriangleRightLine2D(SymbolLine2D):
    def __init__(self, x, y,*args, **kargs):
        SymbolLine2D.__init__(self, x, y, *args, **kargs)

    def _derived_draw(self, drawable, gc, xt, yt):
        offset = self._symbolSize/2        
        for (x,y) in zip(xt, yt):            
            drawable.draw_polygon(gc, self._symbolFill,
                                ( (x+offset, y),
                                  (x-offset, y-offset),
                                  (x-offset, y+offset)
                                ))

class PlusLine2D(SymbolLine2D):
    def __init__(self, x, y,*args, **kargs):
        SymbolLine2D.__init__(self, x, y, *args, **kargs)

    def _derived_draw(self, drawable, gc, xt, yt):
        offset = self._symbolSize/2
        for (x,y) in zip(xt, yt):
            drawable.draw_line(gc, x-offset, y, x+offset, y)
            drawable.draw_line(gc, x, y-offset, x, y+offset)
    


class Line2D_Dispatcher(dict):
    _dispatcher =  {'-' : SolidLine2D,
                    '--' : DashedLine2D, 
                    '-.' : DashDotLine2D, 
                    ':' : DottedLine2D,
                    '|' : Vline2D,
                    '.' : PointLine2D,
                    ',' : PixelLine2D, 
                    'o' : CircleLine2D, 
                    '^' : TriangleUpLine2D, 
                    'v' : TriangleDownLine2D, 
                    '<' : TriangleLeftLine2D, 
                    '>' : TriangleRightLine2D, 
                    's' : SquareLine2D,
                    '+' : PlusLine2D,
                    }
    _sharedState = {}

    def __init__(self):
        self.__dict__ = self._sharedState
        self.update(self._dispatcher)    
4
