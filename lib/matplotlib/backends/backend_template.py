"""
This is a fully functional do nothing backend to provide a template to
backend writers.  It is fully functional in that you can select it as
a backend with

  import matplotlib
  matplotlib.use('Template')

and your matplotlib scripts will (should!) run without error, though
no output is produced.  This provides a nice starting point for
backend writers because you can selectively implement methods
(draw_rectangle, draw_lines, etc...) and slowly see your figure come
to life w/o having to have a full blown implementation before getting
any results.

Copy this to backend_xxx.py and replace all instances of 'template'
with 'xxx'.  Then implement the class methods and functions below, and
add 'xxx' to the switchyard in matplotlib/backends/__init__.py and
'xxx' to the _knownBackends dict in matplotlib/__init__.py and you're
off.  You can use your backend with

  import matplotlib
  matplotlib.use('xxx')
  from pylab import *
  plot([1,2,3])
  show()

The files that are most relevant to backend_writers are

  matplotlib/backends/backend_your_backend.py
  matplotlib/backend_bases.py
  matplotlib/backends/__init__.py
  matplotlib/__init__.py
  matplotlib/_pylab_helpers.py
  
Naming Conventions

  * classes MixedUpperCase

  * varables lowerUpper

  * functions underscore_separated

REQUIREMENTS

  matplotlib requires python2.2 and Numeric, and I don't yet want to
  make python2.3 a requirement.  I provide the Python Cookbook version
  of enumerate in cbook.py and define the constants True and False if
  version <=2.3.  Of course as a backend writer, you are free to make
  additional requirements, but the less required the better.

"""

from __future__ import division

from matplotlib._pylab_helpers import Gcf
from matplotlib.backend_bases import RendererBase, GraphicsContextBase,\
     FigureManagerBase, FigureCanvasBase
from matplotlib.cbook import enumerate
from matplotlib.figure import Figure
from matplotlib.transforms import Bbox


class RendererTemplate(RendererBase):
    """
    The renderer handles drawing/rendering operations.

    This is a minimal do-nothing class that can be used to get started when
    writing a new backend. Refer to backend_bases.RendererBase for
    documentation of the classes methods.
    """
    def draw_arc(self, gcEdge, rgbFace, x, y, width, height, angle1, angle2):
        pass
    
    def draw_image(self, x, y, im, origin, bbox):
        pass
    
    def draw_line(self, gc, x1, y1, x2, y2):
        pass
    
    def draw_lines(self, gc, x, y):
        pass

    def draw_point(self, gc, x, y):
        pass

    def draw_polygon(self, gcEdge, rgbFace, points):
        pass

    def draw_rectangle(self, gcEdge, rgbFace, x, y, width, height):
        pass

    def draw_text(self, gc, x, y, s, prop, angle, ismath=False):    
        pass
         
    def flipy(self):
        return True
    
    def get_canvas_width_height(self):
        return 100, 100

    def get_text_width_height(self, s, prop, ismath):
        return 1, 1
                              
    def new_gc(self):
        return GraphicsContextTemplate()

    def points_to_pixels(self, points):
        # if backend doesn't have dpi, eg, postscript or svg
        return points
        # elif backend assumes a value for pixels_per_inch
        #return points/72.0 * self.dpi.get() * pixels_per_inch/72.0
        # else
        #return points/72.0 * self.dpi.get()


class GraphicsContextTemplate(GraphicsContextBase):
    """
    The graphics context provides the color, line styles, etc...  See the gtk
    and postscript backends for examples of mapping the graphics context
    attributes (cap styles, join styles, line widths, colors) to a particular
    backend.  In GTK this is done by wrapping a gtk.gdk.GC object and
    forwarding the appropriate calls to it using a dictionary mapping styles
    to gdk constants.  In Postscript, all the work is done by the renderer,
    mapping line styles to postscript calls.

    If it's more appropriate to do the mapping at the renderer level (as in
    the postscript backend), you don't need to override any of the GC methods.
    If it's more appropriate to wrap an instance (as in the GTK backend) and
    do the mapping here, you'll need to override several of the setter
    methods.

    The base GraphicsContext stores colors as a RGB tuple on the unit
    interval, eg, (0.5, 0.0, 1.0). You may need to map this to colors
    appropriate for your backend.
    """
    pass

        
        
########################################################################
#    
# The following functions and classes are for pylab and implement
# window/figure managers, etc...
#
########################################################################

def draw_if_interactive():
    """
    For image backends - is not required
    For GUI backends - this should be overriden if drawing should be done in
    interactive python mode
    """
    pass

def show():
    """
    For image backends - is not required
    For GUI backends - show() is usually the last line of a pylab script and
    tells the backend that it is time to draw.  In interactive mode, this may
    be a do nothing func.  See the GTK backend for an example of how to handle
    interactive versus batch mode
    """
    for manager in Gcf.get_all_fig_managers():
        # do something to display the GUI
        pass


def new_figure_manager(num, *args, **kwargs):
    """
    Create a new figure manager instance
    """
    thisFig = Figure(*args, **kwargs)
    canvas = FigureCanvasTemplate(thisFig)
    manager = FigureManagerTemplate(canvas, num)
    return manager


class FigureCanvasTemplate(FigureCanvasBase):
    """
    The canvas the figure renders into.  Calls the draw and print fig
    methods, creates the renderers, etc...

    Public attribute

      figure - A Figure instance

    Note GUI templates will want to connect events for button presses,
    mouse movements and key presses to functions that call the base
    class methods button_press_event, button_release_event,
    motion_notify_event, key_press_event, and key_release_event.  See,
    eg backend_gtk.py, backend_wx.py and backend_tkagg.py
    """

    def draw(self):
        """
        Draw the figure using the renderer
        """
        renderer = RendererTemplate()
        self.figure.draw(renderer)
        
    def print_figure(self, filename, dpi=150, facecolor='w', edgecolor='w',
                     orientation='portrait'):
        """
        Render the figure to hardcopy. Set the figure patch face and edge
        colors.  This is useful because some of the GUIs have a gray figure
        face color background and you'll probably want to override this on
        hardcopy.

        orientation - only currently applies to PostScript printing.

        A GUI backend should save and restore the original figure settings.
        An image backend does not need to do this since after the print the
        figure is done
        """
        # save the figure settings, GUI backends only
        #origDPI = self.figure.dpi.get()
        #origfacecolor = self.figure.get_facecolor()
        #origedgecolor = self.figure.get_edgecolor()

        # set the new parameters
        self.figure.dpi.set(dpi)
        self.figure.set_facecolor(facecolor)
        self.figure.set_edgecolor(edgecolor)        

        renderer = RendererTemplate()
        self.figure.draw(renderer)
        # do something to save to hardcopy

        # restore original figure settings, GUI backends only
        #self.figure.dpi.set(origDPI)
        #self.figure.set_facecolor(origfacecolor)
        #self.figure.set_edgecolor(origedgecolor)
        # redraw the screen if necessary
        #self.draw()
        
    
class FigureManagerTemplate(FigureManagerBase):
    """
    Wrap everything up into a window for the pylab interface

    For non interactive backends, the base class does all the work
    """
    pass

########################################################################
#    
# Now just provide the standard names that backend.__init__ is expecting
# 
########################################################################


FigureManager = FigureManagerTemplate

