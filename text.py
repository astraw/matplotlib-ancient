from __future__ import division

import pygtk
pygtk.require('2.0')
import gtk
import gobject
from gtk import gdk
import pango

from colors import ColorDispatcher
from artist import Artist

class AxisText(Artist):
    """
    Handle storing and drawing of text in window or data coordinates
    """
    fontweights = {'normal' : pango.WEIGHT_NORMAL,
                   'bold' : pango.WEIGHT_BOLD,
                   'heavy' : pango.WEIGHT_HEAVY,
                   'light' : pango.WEIGHT_LIGHT,
                   'normal' : pango.WEIGHT_NORMAL,
                   'ultrabold' : pango.WEIGHT_ULTRABOLD,
                   'ultralight' : pango.WEIGHT_ULTRALIGHT,
                   }
    fontangles = {
        'italic': pango.STYLE_ITALIC,
        'normal' : pango.STYLE_NORMAL,
        'oblique' : pango.STYLE_OBLIQUE,
        }

    def __init__(self, x=0, y=0, text='',
                 color='k',
                 verticalalignment='bottom',
                 horizontalalignment='left',
                 fontname='Sans',
                 fontsize=10,
                 fontweight='bold',
                 fontangle='normal',
                 rotation=None,
                 ):
        Artist.__init__(self)
        self._x, self._y = x, y

        self._color = color
        self._text = text
        self._verticalalignment = verticalalignment
        self._horizontalalignment = horizontalalignment
        self._rotation = rotation
        self._fontname = fontname
        self._fontsize = fontsize
        self._fontweight = fontweight
        self._fontangle = fontangle


        self._reset=1
        self._drawn = 0
        self._eraseImg = None
        self._lastXY = 0,0
        
    def _compute_offsets(self):
        """
        Return the (x,y) offsets to comensate for the alignment
        specifications
        """
        if self._drawingArea is None: return 
        try: self._width
        except AttributeError: self._set_font()
        
        if self._rotation=='vertical':
            w, h = self._height, self._width
            if self._horizontalalignment=='center': offsetx = -w/2
            elif self._horizontalalignment=='right': offsetx = -w
            else: offsetx = 0

            if self._verticalalignment=='center': offsety = -h/2
            elif self._verticalalignment=='top': offsety = 0
            else: offsety = -h
        else:
            if self._horizontalalignment=='center': offsetx = -self._width/2
            elif self._horizontalalignment=='right': offsetx = -self._width
            else: offsetx = 0

            if self._verticalalignment=='center': offsety = -self._height/2
            elif self._verticalalignment=='top': offsety = 0
            else: offsety = -self._height

        return (offsetx, offsety)

    def _draw(self, drawable, *args, **kwargs):
        """
        Render the text to the drawable (or defaul drawable is drawable is None
        """
        if self._text=='': return
        if self._drawn: return 
        if self._reset: self._set_font()

        self.erase()
        
        fg = ColorDispatcher().get(self._color)

        x, y = self.transform_points_to_win(self._x, self._y)
        ox, oy = self._compute_offsets()


        if self._rotation=='vertical':            
            drawn = self.draw_rotated(drawable, fg)
            if not drawn: return 
        else:
            inkRect, logicalRect = self._layout.get_pixel_extents()
            w, h = logicalRect[2], logicalRect[3]
            if y+oy<0 or x+ox<0:
                return 
            img = drawable.get_image(x+ox, y+oy, w, h)
            self._eraseImg = ( (x+ox, y+oy, w, h), img)

            gc = drawable.new_gc()
            self.clip_gc(gc)
            gc.foreground = fg
            drawable.draw_layout(
                gc, x=x+ox, y=y+oy,
                layout=self._layout)
        self._drawn = 1
        self._reset = 0
        self._lastXY = x,y
        
            
    def draw_rotated(self, drawable, fg):
        """
        Draw the text rotated 90 degrees
        """

        inkRect, logicalRect = self._layout.get_pixel_extents()
        x, y, w, h = logicalRect

        # get the bacground image
        ox, oy = self._compute_offsets()
        x, y = self.transform_points_to_win(self._x, self._y)

        if y+oy<0 or x+ox<0:
            return 0

        imgBack = drawable.get_image(x+ox, y+oy, h, w)
        rect = (x+ox, y+oy, h, w)
        self._eraseImg = ( rect, imgBack)

        

        pixmap = gtk.gdk.Pixmap(self._drawingArea.window, w, h)

        # rotate the background image to horizontal to fill the pixmap
        # background
        imageHoriz = gtk.gdk.Image(type=0,
                                 visual=pixmap.get_visual(),
                                 width=w, height=h)
        imageHoriz.set_colormap(imgBack.get_colormap())
        for i in range(w):
            for j in range(h):
                imageHoriz.put_pixel(i, j, imgBack.get_pixel(j,w-i-1) )


        gc = drawable.new_gc()
        self.clip_gc(gc)

        pixmap.draw_image(gc, imageHoriz, 0, 0, 0, 0, w, h)
        gc.foreground = fg
        pixmap.draw_layout(gc, x=0, y=0, layout=self._layout)
        imageIn = pixmap.get_image(x=0, y=0, width=w, height=h)
        imageOut = gtk.gdk.Image(type=0,
                                 visual=pixmap.get_visual(),
                                 width=h, height=w)
        imageOut.set_colormap(imageIn.get_colormap())
        for i in range(w):
            for j in range(h):
                imageOut.put_pixel(j, i, imageIn.get_pixel(w-i-1,j) )


        pixbuf = gtk.gdk.Pixbuf(colorspace=gtk.gdk.COLORSPACE_RGB,
                                has_alpha=0, bits_per_sample=8,
                                width=h, height=w)
        pixbuf.get_from_image(src=imageOut, cmap=imageIn.get_colormap(),
                              src_x=0, src_y=0, dest_x=0, dest_y=0,
                              width=h, height=w)

        pixbuf.render_to_drawable(drawable, gc,
                                  src_x=0, src_y=0,
                                  dest_x=x+ox, dest_y=y+oy,
                                  width=h, height=w,
                                  dither=0, x_dither=0, y_dither=0)
        return 1


    def erase(self):
        "Erase the last draw"

        if self._eraseImg is None or not self._drawn: return
        gc = self._drawable.new_gc()
        self.clip_gc(gc)
        rect, img = self._eraseImg 
        if img is None: return 
        x,y,w,h = rect
        self._drawable.draw_image(gc, img, 0, 0, x, y, w, h)
        self._drawn = 0
        self._reset = 1
        self._eraseImg = None

        
    def get_data_extent(self):
        'Get the pixel extents left, bottom, width, height'
        if self._drawingArea is None:
            msg = 'You must first set the drawing area for ' + self._text
            raise RuntimeError, msg
        try: self._width
        except AttributeError: self._set_font()
        ox, oy = self._compute_offsets()
        inkRect, logicalRect = self._layout.get_pixel_extents()
        x, y = self._x, self._y
        if self._rotation=='vertical':
            return (x+ox, y+oy+logicalRect[2], logicalRect[3], logicalRect[2])
        else:    
            return (x+ox, y+oy+logicalRect[3], logicalRect[2], logicalRect[3])
        
    def get_fontname(self):
        "Return the font name as string"
        return self._fontname

    def get_fontsize(self):
        "Return the font size as integer"
        return self._fontsize

    def get_fontweight(self):
        "Get the font weight as string"
        return self._fontweight

    def get_fontangle(self):
        "Get the font angle as string"
        return self._fontangle

    def get_horizontalalignment(self):
        "Return the horizontal alignment as string"
        return self._horizontalalignment

    def get_text(self):
        "Get the text as string"
        return self._text

    def get_verticalalignment(self):
        "Return the vertical alignment as string"
        return self._verticalalignment

    def get_left_right(self):
        "get the left, right boundaries of the text in in win coords"
        if self._drawingArea is None:
            raise RuntimeError, 'You must first set the drawing area with set_drawing_area'
        ox,oy = self._compute_offsets()
        return self._x + ox, self._x + ox + self._width

    def get_bottom_top(self):
        "get the  bottom, top boundaries of the text in win coords"
        if self._drawingArea is None:
            raise RuntimeError, 'You must first set the drawing area with set_drawing_area'

        ox,oy = self._compute_offsets()
        return self._y + oy + self._height, self._y

    def get_position(self):
        "Return x, y as tuple"
        return self._x, self._y


    def wash_brushes(self):
        "Flush all state vars and prepare for a clean redraw"
        self._reset = 1
        self._drawn = 0
        self._lastXY = 0,0
        self._eraseImg = None
        
    def set_backgroundcolor(self, color):
        "Set the background color of the text"
        if color == self._backgroundcolor: return 
        self._state_change()
        self._backgroundcolor = color

        
    def set_color(self, color):
        "Set the foreground color of the text"
        if self._color == color: return 
        self._state_change()
        self._color = color

    def set_horizontalalignment(self, align):
        """
        Set the horizontal alignment to one of
        'center', 'right', or 'left'
        """
        legal = ('center', 'right', 'left')
        if align not in legal:
            raise ValueError,\
                  'Horizontal alignment must be one of %s' % legal
        if self._horizontalalignment == align: return     
        self._state_change()
        self._horizontalalignment = align


    def _set_font(self):
        "Update the pango layout"
        if self._drawingArea is None:
            msg = 'You must first call set_drawing_area() for', self._text
            raise RuntimeError, msg

        self._font = pango.FontDescription(
            '%s %d' % (self._fontname, self._fontsize))
        self._font.set_weight(self.fontweights[self._fontweight])
        self._font.set_style(self.fontangles[self._fontangle])
    
        self._context = self._drawingArea.create_pango_context()
        self._layout  = self._drawingArea.create_pango_layout(self._text)
        self._layout.set_font_description(self._font)    

        inkRect, logicalRect = self._layout.get_pixel_extents()
        
        self._width = logicalRect[2]
        self._height = logicalRect[3]


    def set_fontname(self, fontname):
        """
        Set the font name, eg, 'Sans', 'Courier', 'Helvetica'
        """
        if self._fontname == fontname: return
        self._state_change()
        self._fontname = fontname
        

    def set_fontsize(self, fontsize):
        """
        Set the font size, eg, 8, 10, 12, 14...
        """
        if self._fontsize == fontsize: return
        self._state_change()
        self._fontsize = fontsize
        
        
    def set_fontweight(self, weight):
        """
        Set the font weight, one of:
        'normal', 'bold', 'heavy', 'light', 'ultrabold',  'ultralight'
        """
        if self._fontweight == weight: return
        self._state_change()
        self._fontweight = weight
        
        
    def set_fontangle(self, angle):
        """
        Set the font angle, one of 'normal', 'italic', 'oblique'
        """
        if self._fontangle == angle: return  
        self._state_change()
        self._fontangle = angle
        
        
    def set_position(self, x, y):
        if (x,y) == (self._x, self._y): return
        self._state_change()
        self._x = x
        self._y = y
        
        
    def set_rotation(self, s):
        "Currently only s='vertical', or s='horizontal' are supported"
        if s==self._rotation: return
        self._state_change()
        self._rotation = s
        
        
    def set_verticalalignment(self, align):
        """
        Set the vertical alignment to one of
        'center', 'top', or 'bottom'
        """

        legal = ('top', 'bottom', 'center')
        if align not in legal:
            raise ValueError,\
                  'Vertical alignment must be one of %s' % legal

        if self._verticalalignment == align: return
        self._state_change()
        self._verticalalignment = align
        
        
    def set_drawing_area(self, da):
        "Update the drawing area the widget renders into"

        if self._drawingArea == da: return 
        #print 'Setting da for', self._text
        Artist.set_drawing_area(self, da)

        self._state_change()

    def set_text(self, text):
        "Set the text"
        if self._text == text: return
        self._state_change()
        self._text = text
        
    def _state_change(self):
        self._reset = 1
    

    def update_properties(self, d):
        "Update the font attributes with the dictionary in d"
        #check the keys
        
        legal = ('color', 'verticalalignment', 'horizontalalignment',
                 'fontname', 'fontsize', 'fontweight',
                 'fontangle', 'rotation')
        for k,v in d.items():
            if k not in legal:
                raise ValueError, 'Illegal key %s.  Legal values are %s' % (
                    k, legal)
            self.__dict__['_' + k] = v
            #print self.__dict__
        self._state_change()
        
    def __del__(self):
        "Bye bye"
        self.erase()
