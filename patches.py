from __future__ import division
import pygtk
pygtk.require('2.0')
import gtk
from Numeric import array, arange, sin, cos, pi
from colors import ColorDispatcher
from cbook import is_string_like
from artist import Artist


class Patch(Artist):
    """
    A patch is a 2D thingy with a face color and an edge color
    """
    
    def __init__(self,
                 edgeColor=ColorDispatcher().get('k'),
                 faceColor=ColorDispatcher().get('b'),
                 fill=1,
                 ):

        Artist.__init__(self)
        self._edgecolor = edgeColor
        self._facecolor = faceColor
        self.fill = fill
        self._linewidth=1


    def get_data_extent(self):
        """
        Return the bounding box as left, bottom, width, height in
        data coords
        """
        raise NotImplementedError, "Derived must override"

    def set_edgecolor(self, color):
        if is_string_like(color):
            color = ColorDispatcher().get(color)

        self._edgecolor = color

    def set_facecolor(self, color):
        if is_string_like(color):
            color = ColorDispatcher().get(color)
        self._facecolor = color

    def set_linewidth(self, w):
        self._linewidth = w

    def set_fill(self, b):
        self.fill = b

    def _draw(self, drawable, *args, **kwargs):
        gcFace = drawable.new_gc()
        gcFace.foreground = self._facecolor
        gcFace.line_width = self._linewidth
        self.clip_gc(gcFace)
        gcEdge = drawable.new_gc()
        gcEdge.foreground = self._edgecolor
        gcEdge.line_width = self._linewidth
        self.clip_gc(gcEdge)
        self._derived_draw(drawable, gcFace, gcEdge)

    def _derived_draw(self, drawable, gcFace, gcEdge):
        raise NotImplementedError, 'Derived must override'

class Rectangle(Patch):
    """
    Draw a rectangle with lower left at xy=(x,y) with specified
    width and height
    """

    def __init__(self, xy, width, height, *args, **kargs):
        Patch.__init__(self, *args, **kargs)

        self.xy  = xy
        self.width, self.height = width, height
        
    def _derived_draw(self, drawable, gcFace, gcEdge):
        # x,y for the Rectangle specifies the lower left, but for
        # draw_rectange it is the upper left.  So add height to
        # get upper left
        l, t  = self.transform_points_to_win(self.xy[0],
                                             self.xy[1]+self.height)
        w, h = self.transform_scale_to_win(self.width, self.height)

        if self.fill:
            drawable.draw_rectangle(gcFace, filled=1,
                                    x=l, y=t, width=w, height=h)
        drawable.draw_rectangle(gcEdge, filled=0,
                                x=l, y=t, width=w, height=h)

    def get_data_extent(self):
        """
        Return the bounding box as left, bottom, width, height in
        window coords
        """
        x, y  = self.xy[0], self.xy[1]
        w, h = self.width, self.height
        return x, y, w, h


class RegularPolygon(Patch):
    """
    A regular polygon patch.  xy is a length 2 tuple (the center)
    numVertices is the number of vertices.  Radius is the distance
    from the center to each of the vertices.  Orientation is in
    radians and rotates the polygon.
    """
    def __init__(self, xy, numVertices, radius=5, orientation=0,
                 *args, **kargs):

        Patch.__init__(self, *args, **kargs)
        self.xy = xy
        self.numVertices = numVertices
        self.radius = radius
        self.orientation = orientation
        self._compute_vertices()

    def _compute_vertices(self):

        theta = 2*pi/self.numVertices*arange(self.numVertices) + \
                self.orientation

        self.xs = self.xy[0] + self.radius*cos(theta)
        self.ys = self.xy[1] + self.radius*sin(theta)

        

    def _derived_draw(self, drawable, gcFace, gcEdge):

        xs, ys = self.transform_points_to_win(self.xs, self.ys)
        vertices = zip(xs, ys)
        if self.fill:
            drawable.draw_polygon(gcFace, filled=1,
                                  points=vertices)
        drawable.draw_polygon(gcFace, filled=0,
                              points=vertices)


    def get_data_extent(self):
        """
        Return the bounding box as left, bottom, width, height in
        data coords
        """
        xs, ys = self.xs, self.ys
        xmin, xmax = min(xs), max(xs)
        ymin, ymax = min(xy), max(ys)
        w = maxx - minx
        h = maxy - miny
        return xmin, ymax, w, h




class Circle(Patch):
    def __init__(self, xy, radius=5,
                 *args, **kargs):

        Patch.__init__(self, *args, **kargs)
        self.xy = xy
        self.radius = radius

    def _derived_draw(self, drawable, gcFace, gcEdge):
        
        x, y = self.transform_points_to_win(self.xy[0], self.xy[1])
        w, h = self.transform_scale_to_win(self.radius, self.radius)
        
        if self.fill:
            drawable.draw_arc(gcFace, 1, x-w/2, y-h/2, w, h, 0, 360*64)

        drawable.draw_arc(gcEdge, 0, x-w/2, y-h/2, w, h, 0, 360*64)
        

    def get_data_extent(self):
        """
        Return the bounding box as left, bottom, width, height in
        data coords
        """
        
        x, y = self.xy[0], self.xy[1]
        w, h = self.radius, self.radius
        return x-w, y+w, w, h

