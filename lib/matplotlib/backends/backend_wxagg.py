from __future__ import division 
"""

 backend_wxagg.py

 A wxPython backend for Agg.  This uses the GUI widgets written by
 Jeremy O'Donoghue (jeremy@o-donoghue.com) and the Agg backend by John
 Hunter (jdhunter@ace.bsd.uchicago.edu)

 Copyright (C) 2003-5 Jeremy O'Donoghue, John Hunter, Illinois Institute of 
 Technology

  
 License: This work is licensed under the matplotlib license( PSF
 compatible). A copy should be included with this source code.

"""

import wx
import matplotlib
from matplotlib.figure import Figure
from matplotlib.transforms import Bbox, Point, Value

from backend_agg import FigureCanvasAgg
import backend_wx
from backend_wx import FigureManager, FigureManagerWx, FigureCanvasWx, \
    FigureFrameWx, DEBUG_MSG, NavigationToolbar2Wx, error_msg_wx, \
    draw_if_interactive, show, Toolbar, backend_version


class FigureFrameWxAgg(FigureFrameWx):
    def get_canvas(self, fig):
        return FigureCanvasWxAgg(self, -1, fig)

    def _get_toolbar(self, statbar):
        if matplotlib.rcParams['toolbar']=='classic':
            toolbar = NavigationToolbarWx(self.canvas, True)
        elif matplotlib.rcParams['toolbar']=='toolbar2':
            toolbar = NavigationToolbar2WxAgg(self.canvas)
            toolbar.set_status_bar(statbar)
        else:
            toolbar = None
        return toolbar 

class FigureCanvasWxAgg(FigureCanvasWx,FigureCanvasAgg):
    """
    The FigureCanvas contains the figure and does event handling.
    
    In the wxPython backend, it is derived from wxPanel, and (usually)
    lives inside a frame instantiated by a FigureManagerWx. The parent
    window probably implements a wxSizer to control the displayed
    control size - but we give a hint as to our preferred minimum
    size.
    """

    def draw(self, repaint=True):
        """
        Render the figure using agg.
        """
        DEBUG_MSG("draw()", 1, self)
        FigureCanvasAgg.draw(self)

        self.bitmap = _convert_agg_to_wx_bitmap(self.get_renderer(), None)
        if repaint:
            self.gui_repaint()

    def blit(self, bbox=None):
        """
        Transfer the region of the agg buffer defined by bbox to the display.
        If bbox is None, the entire buffer is transferred.
        """
        if bbox is None:
            self.bitmap = _convert_agg_to_wx_bitmap(self.get_renderer(), None)
            self.gui_repaint()
            return

        l, b, w, h = bbox.get_bounds()
        r = l + w
        t = b + h
        x = int(l)
        y = int(self.bitmap.GetHeight() - t)

        srcBmp = _convert_agg_to_wx_bitmap(self.get_renderer(), bbox)
        srcDC = wx.MemoryDC()
        srcDC.SelectObject(srcBmp)

        destDC = wx.MemoryDC()
        destDC.SelectObject(self.bitmap)

        destDC.BeginDrawing()
        destDC.Blit(x, y, w, h, srcDC, 0, 0)
        destDC.EndDrawing()

        destDC.SelectObject(wx.NullBitmap)
        srcDC.SelectObject(wx.NullBitmap)
        self.gui_repaint()

    def print_figure(self, filename, dpi=150, facecolor='w', edgecolor='w',
                     orientation='portrait', **kwargs):
        """
        Render the figure to hardcopy
        """
        agg = self.switch_backends(FigureCanvasAgg)
        agg.print_figure(filename, dpi, facecolor, edgecolor, orientation,
                         **kwargs)
        self.figure.set_canvas(self)

    def _get_imagesave_wildcards(self):
        'return the wildcard string for the filesave dialog'
        return "PS (*.ps)|*.ps|"     \
               "EPS (*.eps)|*.eps|"  \
               "SVG (*.svg)|*.svg|"  \
               "BMP (*.bmp)|*.bmp|"  \
               "PNG (*.png)|*.png"  \


class NavigationToolbar2WxAgg(NavigationToolbar2Wx):
    def get_canvas(self, frame, fig):
        return FigureCanvasWxAgg(frame, -1, fig)


def new_figure_manager(num, *args, **kwargs):
    """
    Create a new figure manager instance
    """
    # in order to expose the Figure constructor to the pylab
    # interface we need to create the figure here
    DEBUG_MSG("new_figure_manager()", 3, None)

    if backend_wx.wxapp is None:
        backend_wx.wxapp = wx.GetApp()
        if backend_wx.wxapp is None:
            backend_wx.wxapp = wx.PySimpleApp()
            backend_wx.wxapp.SetExitOnFrameDelete(True)
    
    fig = Figure(*args, **kwargs)
    frame = FigureFrameWxAgg(num, fig)
    figmgr = frame.get_figure_manager()
    if matplotlib.is_interactive():
        figmgr.canvas.realize()
        figmgr.frame.Show() 
    return figmgr


#
# agg/wxPython image conversion functions
#

def _py_convert_agg_to_wx_image(agg, bbox):
    """
    Convert the region of the agg buffer bounded by bbox to a wx.Image.  If
    bbox is None, the entire buffer is converted.

    Note: agg must be a backend_agg.RendererAgg instance.
    """
    wPx = agg.width
    hPx = agg.height
    image = wx.EmptyImage(wPx, hPx)
    image.SetData(agg.tostring_rgb())

    if bbox is None:
        # agg => rgb -> image
        return image
    else:
        # agg => rgb -> image => bitmap => clipped bitmap => image
        return wx.ImageFromBitmap(_clipped_image_as_bitmap(image, bbox))


def _py_convert_agg_to_wx_bitmap(agg, bbox):
    """
    Convert the region of the agg buffer bounded by bbox to a wx.Bitmap.  If
    bbox is None, the entire buffer is converted.

    Note: agg must be a backend_agg.RendererAgg instance.
    """
    if bbox is None:
        # agg => rgb -> image => bitmap
        return wx.BitmapFromImage(_py_convert_agg_to_wx_image(agg, None))
    else:
        # agg => rgb -> image => bitmap => clipped bitmap
        return _clipped_image_as_bitmap(
            _py_convert_agg_to_wx_image(agg, None),
            bbox)


def _clipped_image_as_bitmap(image, bbox):
    """
    Convert the region of a wx.Image described by bbox to a wx.Bitmap.
    """
    l, b, width, height = bbox.get_bounds()
    r = l + width
    t = b + height

    srcBmp = wx.BitmapFromImage(image)
    srcDC = wx.MemoryDC()
    srcDC.SelectObject(srcBmp)

    destBmp = wx.EmptyBitmap(width, height)
    destDC = wx.MemoryDC()
    destDC.SelectObject(destBmp)
 
    destDC.BeginDrawing()
    x = int(l)
    y = int(image.GetHeight() - t)
    destDC.Blit(0, 0, width, height, srcDC, x, y)
    destDC.EndDrawing()

    srcDC.SelectObject(wx.NullBitmap)
    destDC.SelectObject(wx.NullBitmap)

    return destBmp


def _use_accelerator(state):
    """
    Enable or disable the WXAgg accelerator, if it is present.
    """
    global _convert_agg_to_wx_image
    global _convert_agg_to_wx_bitmap

    if state and _wxagg is not None:
        _convert_agg_to_wx_image  = _wxagg.convert_agg_to_wx_image
        _convert_agg_to_wx_bitmap = _wxagg.convert_agg_to_wx_bitmap
    else:
        _convert_agg_to_wx_image  = _py_convert_agg_to_wx_image
        _convert_agg_to_wx_bitmap = _py_convert_agg_to_wx_bitmap


# try to load the WXAgg accelerator
try:
    import _wxagg
except ImportError:
    _wxagg = None

# if it's present, use it
_use_accelerator(True)

