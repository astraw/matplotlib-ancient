"""
Figure and Axes text
"""
from __future__ import division
import re
from matplotlib import verbose
import matplotlib
import math
from artist import Artist
from cbook import enumerate, popd, is_string_like, maxdict
from font_manager import FontProperties
from matplotlib import rcParams
from patches import bbox_artist
from numerix import sin, cos, pi, cumsum, dot, asarray, array, \
     where, nonzero, equal, sqrt
from transforms import lbwh_to_bbox, bbox_all
from lines import Line2D

def scanner(s):
    """
    Split a string into mathtext and non-mathtext parts.  mathtext is
    surrounded by $ symbols.  quoted \$ are ignored

    All slash quotes dollar signs are ignored

    The number of unquoted dollar signs must be even

    Return value is a list of (substring, inmath) tuples
    """
    if not len(s): return [(s, False)]
    #print 'testing', s, type(s)
    inddollar = nonzero(asarray(equal(s,'$')))
    quoted = dict([ (ind,1) for ind in nonzero(asarray(equal(s,'\\')))])
    indkeep = [ind for ind in inddollar if not quoted.has_key(ind-1)]
    if len(indkeep)==0:
        return [(s, False)]
    if len(indkeep)%2:
        raise ValueError('Illegal string "%s" (must have balanced dollar signs)'%s)

    Ns = len(s)

    indkeep = [ind for ind in indkeep]
    # make sure we start with the first element
    if indkeep[0]!=0: indkeep.insert(0,0)
    # and end with one past the end of the string
    indkeep.append(Ns+1)

    Nkeep = len(indkeep)
    results = []

    inmath = s[0] == '$'
    for i in range(Nkeep-1):
        i0, i1 = indkeep[i], indkeep[i+1]
        if not inmath:
            if i0>0: i0 +=1
        else:
            i1 += 1
        if i0>=Ns: break

        results.append((s[i0:i1], inmath))
        inmath = not inmath

    return results



def _process_text_args(override, fontdict=None, **kwargs):
    "Return an override dict.  See 'text' docstring for info"

    if fontdict is not None:
        override.update(fontdict)

    override.update(kwargs)
    return override

# Extracted from Text's method to serve as a function
def get_rotation(rotation):
    'return the text angle as float'
    if rotation in ('horizontal', None):
        angle = 0.
    elif rotation == 'vertical':
        angle = 90.
    else:
        angle = float(rotation)
    return angle%360

_unit_box = lbwh_to_bbox(0,0,1,1)

class Text(Artist):
    """
    Handle storing and drawing of text in window or data coordinates

    """
    # special case superscripting to speedup logplots
    _rgxsuper = re.compile('\$([\-+0-9]+)\^\{(-?[0-9]+)\}\$')

    zorder = 3
    def __init__(self,
                 x=0, y=0, text='',
                 color=None,          # defaults to rc params
                 verticalalignment='bottom',
                 horizontalalignment='left',
                 multialignment=None,
                 fontproperties=None, # defaults to FontProperties()
                 rotation=None,
                 ):

        Artist.__init__(self)
        if not is_string_like(text):
            raise TypeError('text must be a string type')
        self.cached = maxdict(5)
        self._x, self._y = x, y

        if color is None: color = rcParams['text.color']
        if fontproperties is None: fontproperties=FontProperties()

        self.set_color(color)
        self.set_text(text)
        self._verticalalignment = verticalalignment
        self._horizontalalignment = horizontalalignment
        self._multialignment = multialignment
        self._rotation = rotation
        self._fontproperties = fontproperties
        self._bbox = None
        self._renderer = None

        #self.set_bbox(dict(pad=0))

    def _get_multialignment(self):
        if self._multialignment is not None: return self._multialignment
        else: return self._horizontalalignment

    def get_rotation(self):
        'return the text angle as float'
        #return 0

#         if self._rotation in ('horizontal', None):
#             angle = 0.
#         elif self._rotation == 'vertical':
#             angle = 90.
#         else:
#             angle = float(self._rotation)
#         return angle%360

        # Since the get_rotation logic was extracted
        # into a function for TextWithDash, this
        # method could now read as follows.
        return get_rotation(self._rotation)

    def update_from(self, other):
        'Copy properties from other to self'
        Artist.update_from(self, other)
        self._color = other._color
        self._multialignment = other._multialignment
        self._verticalalignment = other._verticalalignment
        self._horizontalalignment = other._horizontalalignment
        self._fontproperties = other._fontproperties.copy()
        self._rotation = other._rotation


    def _get_layout(self, renderer):

        # layout the xylocs in display coords as if angle = zero and
        # then rotate them around self._x, self._y
        #return _unit_box
        key = self.get_prop_tup()
        if self.cached.has_key(key): return self.cached[key]
        horizLayout = []
        pad =2
        thisx, thisy = self._transform.xy_tup( (self._x, self._y) )
        width = 0
        height = 0

        xmin, ymin = thisx, thisy
        if self.is_math_text():
            lines = [self._text]
        else:
            lines = self._text.split('\n')

        whs = []
        tmp, heightt = renderer.get_text_width_height(
                'T', self._fontproperties, ismath=False)

        heightt += 3  # 3 pixel pad
        for line in lines:
            w,h = renderer.get_text_width_height(
                line, self._fontproperties, ismath=self.is_math_text())

            whs.append( (w,h) )
            offsety = heightt+pad
            horizLayout.append((line, thisx, thisy, w, h))
            thisy -= offsety  # now translate down by text height, window coords
            width = max(width, w)

        ymin = horizLayout[-1][2]
        ymax = horizLayout[0][2] + horizLayout[0][-1]
        height = ymax-ymin

        xmax = xmin + width
        # get the rotation matrix
        M = self.get_rotation_matrix(xmin, ymin)

        # the corners of the unrotated bounding box
        cornersHoriz = ( (xmin, ymin), (xmin, ymax), (xmax, ymax), (xmax, ymin) )
        offsetLayout = []
        # now offset the individual text lines within the box
        if len(lines)>1: # do the multiline aligment
            malign = self._get_multialignment()
            for line, thisx, thisy, w, h in horizLayout:
                if malign=='center': offsetx = width/2.0-w/2.0
                elif malign=='right': offsetx = width-w
                else: offsetx = 0
                thisx += offsetx
                offsetLayout.append( (thisx, thisy ))
        else: # no additional layout needed
            offsetLayout = [ (thisx, thisy) for line, thisx, thisy, w, h in horizLayout]

        # now rotate the bbox

        cornersRotated = [dot(M,array([[thisx],[thisy],[1]])) for thisx, thisy in cornersHoriz]

        txs = [float(v[0][0]) for v in cornersRotated]
        tys = [float(v[1][0]) for v in cornersRotated]

        # compute the bounds of the rotated box
        xmin, xmax = min(txs), max(txs)
        ymin, ymax = min(tys), max(tys)
        width  = xmax - xmin
        height = ymax - ymin

        # Now move the box to the targe position offset the display bbox by alignment
        halign = self._horizontalalignment
        valign = self._verticalalignment

        # compute the text location in display coords and the offsets
        # necessary to align the bbox with that location
        tx, ty = self._transform.xy_tup( (self._x, self._y) )

        if halign=='center':  offsetx = tx - (xmin + width/2.0)
        elif halign=='right': offsetx = tx - (xmin + width)
        else: offsetx = tx - xmin

        if valign=='center': offsety = ty - (ymin + height/2.0)
        elif valign=='top': offsety  = ty - (ymin + height)
        else: offsety = ty - ymin

        xmin += offsetx
        xmax += offsetx
        ymin += offsety
        ymax += offsety

        bbox = lbwh_to_bbox(xmin, ymin, width, height)


        # now rotate the positions around the first x,y position
        xys = [dot(M,array([[thisx],[thisy],[1]])) for thisx, thisy in offsetLayout]


        tx = [float(v[0][0])+offsetx for v in xys]
        ty = [float(v[1][0])+offsety for v in xys]

        # now inverse transform back to data coords
        xys = [self._transform.inverse_xy_tup( xy ) for xy in zip(tx, ty)]

        xs, ys = zip(*xys)

        ret = bbox, zip(lines, whs, xs, ys)
        self.cached[key] = ret
        return ret


    def set_bbox(self, rectprops):
        """
        Draw a bounding box around self.  rect props are any settable
        properties for a rectangle, eg color='r', alpha=0.5

        ACCEPTS: rectangle prop dict plus key 'pad' which is a pad in points
        """
        self._bbox = rectprops

    def draw(self, renderer):
        #return
        if renderer is not None:
            self._renderer = renderer
        if not self.get_visible(): return
        if self._text=='': return

        gc = renderer.new_gc()
        gc.set_foreground(self._color)
        gc.set_alpha(self._alpha)
        if self.get_clip_on():
            gc.set_clip_rectangle(self.clipbox.get_bounds())



        if self._bbox:
            bbox_artist(self, renderer, self._bbox)
        angle = self.get_rotation()

        ismath = self.is_math_text()

        if angle==0:
            if ismath=='TeX': m = None
            else: m = self._rgxsuper.match(self._text)
            if m is not None:
                bbox, info = self._get_layout_super(self._renderer, m)
                base, xt, yt = info[0]
                renderer.draw_text(gc, xt, yt, base,
                                   self._fontproperties, angle,
                                   ismath=False)

                exponent, xt, yt, fp = info[1]
                renderer.draw_text(gc, xt, yt, exponent,
                                   fp, angle,
                                   ismath=False)
                return


        if len(self._substrings)>1:
            # embedded mathtext
            thisx, thisy = self._transform.xy_tup((self._x, self._y))
            for s,ismath in self._substrings:
                w, h = renderer.get_text_width_height(
                    s, self._fontproperties, ismath)

                renderx, rendery = thisx, thisy
                if renderer.flipy():
                    canvasw, canvash = renderer.get_canvas_width_height()
                    rendery = canvash-rendery

                renderer.draw_text(gc, renderx, rendery, s,
                                   self._fontproperties, angle,
                                   ismath)
                thisx += w


            return
        bbox, info = self._get_layout(renderer)

        if ismath=='TeX':
            canvasw, canvash = renderer.get_canvas_width_height()
            for line, wh, x, y in info:
                x, y = self._transform.xy_tup((x, y))
                if renderer.flipy():
                    y = canvash-y

                renderer.draw_tex(gc, x, y, line,
                                  self._fontproperties, angle)
            return

        #print 'xy', self._x, self._y, info
        for line, wh, x, y in info:
            x, y = self._transform.xy_tup((x, y))
            #renderer.draw_arc(gc, (1,0,0),
            #                  x, y, 2, 2, 0.0, 360.0)

            if renderer.flipy():
                canvasw, canvash = renderer.get_canvas_width_height()
                y = canvash-y

            renderer.draw_text(gc, x, y, line,
                               self._fontproperties, angle,
                               ismath=self.is_math_text())

    def get_color(self):
        "Return the color of the text"
        return self._color

    def get_font_properties(self):
        "Return the font object"
        return self._fontproperties

    def get_name(self):
        "Return the font name as string"
        return self._fontproperties.get_family()[-1]  #  temporary hack.

    def get_style(self):
        "Return the font style as string"
        return self._fontproperties.get_style()

    def get_size(self):
        "Return the font size as integer"
        return self._fontproperties.get_size_in_points()

    def get_weight(self):
        "Get the font weight as string"
        return self._fontproperties.get_weight()

    def get_fontname(self):
        'alias for get_name'
        return self._fontproperties.get_family()[-1]  #  temporary hack.

    def get_fontstyle(self):
        'alias for get_style'
        return self._fontproperties.get_style()

    def get_fontsize(self):
        'alias for get_size'
        return self._fontproperties.get_size_in_points()

    def get_fontweight(self):
        'alias for get_weight'
        return self._fontproperties.get_weight()


    def get_ha(self):
        'alias for get_horizontalalignment'
        return self.get_horizontalalignment()

    def get_horizontalalignment(self):
        "Return the horizontal alignment as string"
        return self._horizontalalignment

    def get_position(self):
        "Return x, y as tuple"
        return self._x, self._y

    def get_prop_tup(self):
        """
        Return a hashable tuple of properties

        Not intended to be human readable, but useful for backends who
        want to cache derived information about text (eg layouts) and
        need to know if the text has changed
        """

        return (self._x, self._y, self._text, self._color,
                self._verticalalignment, self._horizontalalignment,
                hash(self._fontproperties), self._rotation,
                self._transform.as_vec6_val(),
                )

    def get_text(self):
        "Get the text as string"
        return self._text

    def get_va(self):
        'alias for getverticalalignment'
        return self.get_verticalalignment()

    def get_verticalalignment(self):
        "Return the vertical alignment as string"
        return self._verticalalignment

    def get_window_extent(self, renderer=None):
        #return _unit_box
        if not self.get_visible(): return _unit_box
        if self._text == '':
            tx, ty = self._transform.xy_tup( (self._x, self._y) )
            return lbwh_to_bbox(tx,ty,0,0)

        if renderer is not None:
            self._renderer = renderer
        if self._renderer is None:
            raise RuntimeError('Cannot get window extent w/o renderer')

        angle = self.get_rotation()
        if angle==0:
            ismath = self.is_math_text()
            if ismath=='TeX': m = None
            else: m = self._rgxsuper.match(self._text)
            if m is not None:
                bbox, tmp = self._get_layout_super(self._renderer, m)
                return bbox
        bbox, info = self._get_layout(self._renderer)
        return bbox



    def get_rotation_matrix(self, x0, y0):

        theta = pi/180.0*self.get_rotation()
        # translate x0,y0 to origin
        Torigin = array([ [1, 0, -x0],
                           [0, 1, -y0],
                           [0, 0, 1  ]])

        # rotate by theta
        R = array([ [cos(theta),  -sin(theta), 0],
                     [sin(theta), cos(theta), 0],
                     [0,           0,          1]])

        # translate origin back to x0,y0
        Tback = array([ [1, 0, x0],
                         [0, 1, y0],
                         [0, 0, 1  ]])


        return dot(dot(Tback,R), Torigin)

    def set_backgroundcolor(self, color):
        """
        Set the background color of the text

        ACCEPTS: any matplotlib color - see help(colors)
        """
        self._backgroundcolor = color


    def set_color(self, color):
        """
        Set the foreground color of the text

        ACCEPTS: any matplotlib color - see help(colors)
        """
        # Make sure it is hashable, or get_prop_tup will fail.
        try:
            hash(color)
        except TypeError:
            color = tuple(color)
        self._color = color

    def set_ha(self, align):
        'alias for set_horizontalalignment'
        self.set_horizontalalignment(align)

    def set_horizontalalignment(self, align):
        """
        Set the horizontal alignment to one of

        ACCEPTS: [ 'center' | 'right' | 'left' ]
        """
        legal = ('center', 'right', 'left')
        if align not in legal:
            raise ValueError('Horizontal alignment must be one of %s' % str(legal))
        self._horizontalalignment = align

    def set_ma(self, align):
        'alias for set_verticalalignment'
        self.set_multialignment(align)


    def set_multialignment(self, align):
        """
        Set the alignment for multiple lines layout.  The layout of the
        bounding box of all the lines is determined bu the horizontalalignment
        and verticalalignment properties, but the multiline text within that
        box can be

        ACCEPTS: ['left' | 'right' | 'center' ]
        """
        legal = ('center', 'right', 'left')
        if align not in legal:
            raise ValueError('Horizontal alignment must be one of %s' % str(legal))
        self._multialignment = align

    def set_family(self, fontname):
        """
        Set the font family

        ACCEPTS: [ 'serif' | 'sans-serif' | 'cursive' | 'fantasy' | 'monospace' ]
        """
        self._fontproperties.set_family(fontname)

    def set_variant(self, variant):
        """
        Set the font variant, eg,

        ACCEPTS: [ 'normal' | 'small-caps' ]
        """
        self._fontproperties.set_variant(variant)

    def set_name(self, fontname):
        """
        Set the font name,

        ACCEPTS: string eg, ['Sans' | 'Courier' | 'Helvetica' ...]
        """
        self._fontproperties.set_name(fontname)

    def set_fontname(self, fontname):
        'alias for set_name'
        self.set_name(fontname)

    def set_style(self, fontstyle):
        """
        Set the font style

        ACCEPTS: [ 'normal' | 'italic' | 'oblique']
        """
        self._fontproperties.set_style(fontstyle)

    def set_fontstyle(self, fontstyle):
        'alias for set_style'
        self._fontproperties.set_style(fontstyle)

    def set_size(self, fontsize):
        """
        Set the font size, eg, 8, 10, 12, 14...

        ACCEPTS: [ size in points | relative size eg 'smaller', 'x-large' ]
        """
        self._fontproperties.set_size(fontsize)

    def set_fontsize(self, fontsize):
        'alias for set_size'
        self._fontproperties.set_size(fontsize)

    def set_fontweight(self, weight):
        'alias for set_weight'
        self._fontproperties.set_weight(weight)

    def set_weight(self, weight):
        """
        Set the font weight

        ACCEPTS: [ 'normal' | 'bold' | 'heavy' | 'light' | 'ultrabold' | 'ultralight']
        """
        self._fontproperties.set_weight(weight)

    def set_position(self, xy):
        """
        Set the xy position of the text

        ACCEPTS: (x,y)
        """
        self.set_x(xy[0])
        self.set_y(xy[1])

    def set_x(self, x):
        """
        Set the x position of the text

        ACCEPTS: float
        """
        self._x = float(x)


    def set_y(self, y):
        """
        Set the y position of the text

        ACCEPTS: float
        """
        self._y = float(y)


    def set_rotation(self, s):
        """
        Set the rotation of the text

        ACCEPTS: [ angle in degrees 'vertical' | 'horizontal'
        """
        self._rotation = s



    def set_va(self, align):
        'alias for set_verticalalignment'
        self.set_verticalalignment(align)

    def set_verticalalignment(self, align):
        """
        Set the vertical alignment

        ACCEPTS: [ 'center' | 'top' | 'bottom' ]
        """
        legal = ('top', 'bottom', 'center')
        if align not in legal:
            raise ValueError('Vertical alignment must be one of %s' % str(legal))

        self._verticalalignment = align

    def set_text(self, s):
        """
        Set the text string s

        ACCEPTS: string
        """
        if not is_string_like(s):
            raise TypeError("This doesn't look like a string: '%s'"%s)
        self._text = s
        #self._substrings = scanner(s)  # support embedded mathtext
        self._substrings = []           # ignore embedded mathtext for now

    def is_math_text(self):
        if rcParams['text.usetex']: return 'TeX'
        if not matplotlib._havemath: return False
        if len(self._text)<2: return False
        return ( self._text.startswith('$') and
                 self._text.endswith('$') )

    def set_fontproperties(self, fp):
        """
        Set the font properties that control the text

        ACCEPTS: a matplotlib.font_manager.FontProperties instance
        """
        self._fontproperties = fp




    def _get_layout_super(self, renderer, m):
        """
        a special case optimization if a log super and angle = 0
        Basically, mathtext is slow and we can do simple superscript layout "by hand"
        """

        key = self.get_prop_tup()
        if self.cached.has_key(key): return self.cached[key]

        base, exponent = m.group(1), m.group(2)
        size =  self._fontproperties.get_size_in_points()
        fpexp = self._fontproperties.copy()
        fpexp.set_size(0.7*size)
        wb,hb = renderer.get_text_width_height(base, self._fontproperties, False)
        we,he = renderer.get_text_width_height(exponent, fpexp, False)

        w = wb+we

        xb, yb = self._transform.xy_tup((self._x, self._y))
        xe = xb+1.1*wb
        ye = yb+0.5*hb
        h = ye+he-yb




        if self._horizontalalignment=='center':  xo = -w/2.
        elif self._horizontalalignment=='right':  xo = -w
        else: xo = 0
        if self._verticalalignment=='center':    yo = -hb/2.
        elif self._verticalalignment=='top':  yo = -hb
        else: yo = 0

        xb += xo
        yb += yo
        xe += xo
        ye += yo
        bbox = lbwh_to_bbox(xb, yb, w, h)

        if renderer.flipy():
            canvasw, canvash = renderer.get_canvas_width_height()
            yb = canvash-yb
            ye = canvash-ye


        val = ( bbox, ((base, xb, yb), (exponent, xe, ye, fpexp)))
        self.cached[key] = val

        return val

class _TextWithDash(Artist):
    """
    This is basically a Text with a dash (drawn with a Line2D)
    before/after it. It is intended to be a drop-in replacement
    for Text (implemented using delegation and get/setattr),
    and should behave identically to Text when dashlength=0.0.

    The dash always comes between the point specified by
    set_position() and the text. When a dash exists, the
    text alignment arguments (horizontalalignment,
    verticalalignment) are ignored.

    dashlength is the length of the dash in canvas units.
    (default=0.0).

    dashdirection is one of 0 or 1, where 0 draws the dash
    after the text and 1 before.
    (default=0).

    dashrotation specifies the rotation of the dash, and
    should generally stay None. In this case
    self.get_dashrotation() returns self.get_rotation().
    (I.e., the dash takes its rotation from the text's
    rotation). Because the text center is projected onto
    the dash, major deviations in the rotation cause
    what may be considered visually unappealing results.
    (default=None).

    dashpad is a padding length to add (or subtract) space
    between the text and the dash, in canvas units.
    (default=3).

    dashpush "pushes" the dash and text away from the point
    specified by set_position() by the amount in canvas units.
    (default=0)

    NOTE: The alignment of the two objects is based on the
    bbox of the Text, as obtained by get_window_extent().
    This, in turn, appears to depend on the font metrics
    as given by the rendering backend. Hence the quality
    of the "centering" of the label text with respect to
    the dash varies depending on the backend used.

    NOTE2: I'm not sure that I got the get_window_extent()
    right, or whether that's sufficient for providing the
    object bbox.
    """
    __name__ = 'textwithdash'

    def __init__(self,
                 x=0, y=0, text='',
                 color=None,          # defaults to rc params
                 verticalalignment='center',
                 horizontalalignment='center',
                 multialignment=None,
                 fontproperties=None, # defaults to FontProperties()
                 rotation=None,
                 dashlength=0.0,
                 dashdirection=0,
                 dashrotation=None,
                 dashpad=3,
                 dashpush=0,
                 xaxis=True,
                 ):
        Artist.__init__(self)
        # The position (x,y) values for _mytext and dashline
        # are bogus as given in the instantiation; they will
        # be set correctly by update_coords() in draw()
        self._mytext = Text(
                      x=x, y=y, text=text,
                      color=color,
                      verticalalignment=verticalalignment,
                      horizontalalignment=horizontalalignment,
                      multialignment=multialignment,
                      fontproperties=fontproperties,
                      rotation=rotation,
                      )
        self.dashline = Line2D(xdata=(x, x),
                               ydata=(y, y),
                               color='k',
                               linestyle='-')
        self._x = x
        self._y = y
        self._dashlength = dashlength
        self._dashdirection = dashdirection
        self._dashrotation = dashrotation
        self._dashpad = dashpad
        self._dashpush = dashpush

    def __getattr__(self, name):
        """Delegate most things to self._mytext.
        """
        # We need to protect for the __init__ case
        if '_mytext' in self.__dict__:
            return getattr(self._mytext, name)

    def __setattr__(self, name, value):
        """Capture only a few things as necessary
        and send the rest off to self._mytext
        """
        if name in ['_mytext', '_dashlength',
                    '_dashdirection', '_dashrotation',
                    '_dashpad', '_dashpush',
                    '_x', '_y',
                    '_transform', '_transformSet',
                    'figure',                    ]:
            self.__dict__[name] = value
        else:
            # We need to protect for the init case
            text = self._mytext
            if text != None:
                setattr(self._mytext, name, value)

    def draw(self, renderer):
        if not self.get_visible(): return
        self.update_coords(renderer)
        self._mytext.draw(renderer)
        #bbox_artist(self._mytext, renderer, props={'pad':0}, fill=False)
        if self.get_dashlength() > 0.0:
            self.dashline.draw(renderer)

    def update_coords(self, renderer):
        """Computes the actual x,y coordinates for
        self._mytext based on the input x,y and the
        dashlength. Since the rotation is with respect
        to the actual canvas's coordinates we need to
        map back and forth.
        """
        (x, y) = self.get_position()
        dashlength = self.get_dashlength()

        # Shortcircuit this process if we don't have a dash
        if dashlength == 0.0:
            self._mytext.set_position((x, y))
            return

        dashrotation = self.get_dashrotation()
        dashdirection = self.get_dashdirection()
        dashpad = self.get_dashpad()
        dashpush = self.get_dashpush()
        transform = self.get_transform()

        angle = get_rotation(dashrotation)
        theta = pi*(angle/180.0+dashdirection-1)
        cos_theta, sin_theta = cos(theta), sin(theta)

        # Compute the dash end points
        # The 'c' prefix is for canvas coordinates
        cxy = array(transform.xy_tup((x, y)))
        print cxy
        cd = array([cos_theta, sin_theta])
        print cd
        c1 = cxy+dashpush*cd
        print c1
        c2 = cxy+(dashpush+dashlength)*cd
        print c2
        print
        (x1, y1) = transform.inverse_xy_tup(tuple(c1))
        (x2, y2) = transform.inverse_xy_tup(tuple(c2))
        self.dashline.set_data((x1, x2), (y1, y2))

        # We now need to extend this vector out to
        # the center of the text area.
        # The basic problem here is that we're "rotating"
        # two separate objects but want it to appear as
        # if they're rotated together.
        # This is made non-trivial because of the
        # interaction between text rotation and alignment -
        # text alignment is based on the bbox after rotation.
        # We reset/force both alignments to 'center'
        # so we can do something relatively reasonable.
        # There's probably a better way to do this by
        # embedding all this in the object's transformations,
        # but I don't grok the transformation stuff
        # well enough yet.
        we = self._mytext.get_window_extent(renderer=renderer)
        w, h = we.width(), we.height()
        # Watch for zeros
        if sin_theta == 0.0:
            dx = w
            dy = 0.0
        elif cos_theta == 0.0:
            dx = 0.0
            dy = h
        else:
            tan_theta = sin_theta/cos_theta
            dx = w
            dy = w*tan_theta
            if dy > h or dy < -h:
                dy = h
                dx = h/tan_theta
        cwd = array([dx, dy])/2
        cwd *= 1+dashpad/sqrt(dot(cwd,cwd))
        cw = c2+(dashdirection*2-1)*cwd
        self._mytext.set_position(transform.inverse_xy_tup(tuple(cw)))

        # Now set the window extent
        # I'm not at all sure this is the right way to do this.
        we = self._mytext.get_window_extent(renderer=renderer)
        self._window_extent = we.deepcopy()
        self._window_extent.update(((c1[0], c1[1]),), False)

        # Finally, make text align center
        self._mytext.set_horizontalalignment('center')
        self._mytext.set_verticalalignment('center')

    def get_window_extent(self, renderer=None):
        if self.get_dashlength() == 0.0:
            return self._mytext.get_window_extent(renderer=renderer)
        else:
            self.update_coords(renderer)
            return self._window_extent

    def get_dashlength(self):
        return self._dashlength

    def set_dashlength(self, dl):
        """
        Set the length of the dash.

        ACCEPTS: float
        """
        self._dashlength = dl

    def get_dashdirection(self):
        return self._dashdirection

    def set_dashdirection(self, dd):
        """
        Set the direction of the dash following the text.
        1 is before the text and 0 is after. The default
        is 0, which is what you'd want for the typical
        case of ticks below and on the left of the figure.

        ACCEPTS: int
        """
        self._dashdirection = dd

    def get_dashrotation(self):
        if self._dashrotation == None:
            return self.get_rotation()
        else:
            return self._dashrotation

    def set_dashrotation(self, dr):
        """
        Set the rotation of the dash.

        ACCEPTS: float
        """
        self._dashrotation = dr

    def get_dashpad(self):
        return self._dashpad

    def set_dashpad(self, dp):
        """
        Set the "pad" of the TextWithDash, which
        is the extra spacing between the dash and
        the text, in canvas units.

        ACCEPTS: float
        """
        self._dashpad = dp

    def get_dashpush(self):
        return self._dashpush

    def set_dashpush(self, dp):
        """
        Set the "push" of the TextWithDash, which
        is the extra spacing between the beginning
        of the dash and the specified position.

        ACCEPTS: float
        """
        self._dashpush = dp

    def get_position(self):
        "Return x, y as tuple"
        return self._x, self._y

    def set_position(self, xy):
        """
        Set the xy position of the TextWithDash.

        ACCEPTS: (x,y)
        """
        self.set_x(xy[0])
        self.set_y(xy[1])

    def set_x(self, x):
        """
        Set the x position of the TextWithDash.

        ACCEPTS: float
        """
        try: self._x.set(x)
        except AttributeError: self._x = x

    def set_y(self, y):
        """
        Set the y position of the TextWithDash.

        ACCEPTS: float
        """
        try: self._y.set(y)
        except AttributeError: self._y = y

    def set_transform(self, t):
        """
        Set the Transformation instance used by this artist.

        ACCEPTS: a matplotlib.transform transformation instance
        """
        self._transform = t
        self._transformSet = True
        self._mytext.set_transform(t)
        self.dashline.set_transform(t)

    def get_figure(self):
        'return the figure instance'
        return self.figure

    def set_figure(self, fig):
        """
        Set the figure instance the artist belong to.

        ACCEPTS: a matplotlib.figure.Figure instance
        """
        self.figure = fig
        self._mytext.set_figure(fig)
        self.dashline.set_figure(fig)


class TextWithDash(Text):
    """
    This is basically a Text with a dash (drawn with a Line2D)
    before/after it. It is intended to be a drop-in replacement
    for Text, and should behave identically to Text when
    dashlength=0.0.

    The dash always comes between the point specified by
    set_position() and the text. When a dash exists, the
    text alignment arguments (horizontalalignment,
    verticalalignment) are ignored.

    dashlength is the length of the dash in canvas units.
    (default=0.0).

    dashdirection is one of 0 or 1, where 0 draws the dash
    after the text and 1 before.
    (default=0).

    dashrotation specifies the rotation of the dash, and
    should generally stay None. In this case
    self.get_dashrotation() returns self.get_rotation().
    (I.e., the dash takes its rotation from the text's
    rotation). Because the text center is projected onto
    the dash, major deviations in the rotation cause
    what may be considered visually unappealing results.
    (default=None).

    dashpad is a padding length to add (or subtract) space
    between the text and the dash, in canvas units.
    (default=3).

    dashpush "pushes" the dash and text away from the point
    specified by set_position() by the amount in canvas units.
    (default=0)

    NOTE: The alignment of the two objects is based on the
    bbox of the Text, as obtained by get_window_extent().
    This, in turn, appears to depend on the font metrics
    as given by the rendering backend. Hence the quality
    of the "centering" of the label text with respect to
    the dash varies depending on the backend used.

    NOTE2: I'm not sure that I got the get_window_extent()
    right, or whether that's sufficient for providing the
    object bbox.
    """
    __name__ = 'textwithdash'

    def __init__(self,
                 x=0, y=0, text='',
                 color=None,          # defaults to rc params
                 verticalalignment='center',
                 horizontalalignment='center',
                 multialignment=None,
                 fontproperties=None, # defaults to FontProperties()
                 rotation=None,
                 dashlength=0.0,
                 dashdirection=0,
                 dashrotation=None,
                 dashpad=3,
                 dashpush=0,
                 xaxis=True,
                 ):

        Text.__init__(self, x=x, y=y, text=text, color=color,
                      verticalalignment=verticalalignment,
                      horizontalalignment=horizontalalignment,
                      multialignment=multialignment,
                      fontproperties=fontproperties, rotation=rotation)
        
        # The position (x,y) values for text and dashline
        # are bogus as given in the instantiation; they will
        # be set correctly by update_coords() in draw()

        self.dashline = Line2D(xdata=(x, x),
                               ydata=(y, y),
                               color='k',
                               linestyle='-')
        
        self._dashx = float(x)
        self._dashy = float(y)
        self._dashlength = dashlength
        self._dashdirection = dashdirection
        self._dashrotation = dashrotation
        self._dashpad = dashpad
        self._dashpush = dashpush

        #self.set_bbox(dict(pad=0))

    def draw(self, renderer):
        self.update_coords(renderer)
        Text.draw(self, renderer)
        if self.get_dashlength() > 0.0:
            self.dashline.draw(renderer)

    def update_coords(self, renderer):
        """Computes the actual x,y coordinates for
        text based on the input x,y and the
        dashlength. Since the rotation is with respect
        to the actual canvas's coordinates we need to
        map back and forth.
        """
        dashx, dashy = self.get_position()
        dashlength = self.get_dashlength()
        # Shortcircuit this process if we don't have a dash
        if dashlength == 0.0:
            self._x, self._y = dashx, dashy
            return
        
        dashrotation = self.get_dashrotation()
        dashdirection = self.get_dashdirection()
        dashpad = self.get_dashpad()
        dashpush = self.get_dashpush()

        angle = get_rotation(dashrotation)
        theta = pi*(angle/180.0+dashdirection-1)
        cos_theta, sin_theta = cos(theta), sin(theta)

        transform = self.get_transform()
        
        # Compute the dash end points
        # The 'c' prefix is for canvas coordinates
        cxy = array(transform.xy_tup((dashx, dashy)))
        cd = array([cos_theta, sin_theta])
        c1 = cxy+dashpush*cd
        c2 = cxy+(dashpush+dashlength)*cd
        
        (x1, y1) = transform.inverse_xy_tup(tuple(c1))
        (x2, y2) = transform.inverse_xy_tup(tuple(c2))
        self.dashline.set_data((x1, x2), (y1, y2))

        # We now need to extend this vector out to
        # the center of the text area.
        # The basic problem here is that we're "rotating"
        # two separate objects but want it to appear as
        # if they're rotated together.
        # This is made non-trivial because of the
        # interaction between text rotation and alignment -
        # text alignment is based on the bbox after rotation.
        # We reset/force both alignments to 'center'
        # so we can do something relatively reasonable.
        # There's probably a better way to do this by
        # embedding all this in the object's transformations,
        # but I don't grok the transformation stuff
        # well enough yet.
        we = Text.get_window_extent(self, renderer=renderer)
        w, h = we.width(), we.height()
        # Watch for zeros
        if sin_theta == 0.0:
            dx = w
            dy = 0.0
        elif cos_theta == 0.0:
            dx = 0.0
            dy = h
        else:
            tan_theta = sin_theta/cos_theta
            dx = w
            dy = w*tan_theta
            if dy > h or dy < -h:
                dy = h
                dx = h/tan_theta
        cwd = array([dx, dy])/2
        cwd *= 1+dashpad/sqrt(dot(cwd,cwd))
        cw = c2+(dashdirection*2-1)*cwd
        
        self._x, self._y = transform.inverse_xy_tup(tuple(cw))

        # Now set the window extent
        # I'm not at all sure this is the right way to do this.
        we = Text.get_window_extent(self, renderer=renderer)
        self._twd_window_extent = we.deepcopy()
        self._twd_window_extent.update(((c1[0], c1[1]),), False)

        # Finally, make text align center
        Text.set_horizontalalignment(self, 'center')
        Text.set_verticalalignment(self, 'center')

    def get_window_extent(self, renderer=None):
        self.update_coords(renderer)
        if self.get_dashlength() == 0.0:
            return Text.get_window_extent(self, renderer=renderer)
        else:
            return self._twd_window_extent

    def get_dashlength(self):
        return self._dashlength

    def set_dashlength(self, dl):
        """
        Set the length of the dash.

        ACCEPTS: float
        """
        self._dashlength = dl

    def get_dashdirection(self):
        return self._dashdirection

    def set_dashdirection(self, dd):
        """
        Set the direction of the dash following the text.
        1 is before the text and 0 is after. The default
        is 0, which is what you'd want for the typical
        case of ticks below and on the left of the figure.

        ACCEPTS: int
        """
        self._dashdirection = dd

    def get_dashrotation(self):
        if self._dashrotation == None:
            return self.get_rotation()
        else:
            return self._dashrotation

    def set_dashrotation(self, dr):
        """
        Set the rotation of the dash.

        ACCEPTS: float
        """
        self._dashrotation = dr

    def get_dashpad(self):
        return self._dashpad

    def set_dashpad(self, dp):
        """
        Set the "pad" of the TextWithDash, which
        is the extra spacing between the dash and
        the text, in canvas units.

        ACCEPTS: float
        """
        self._dashpad = dp

    def get_dashpush(self):
        return self._dashpush

    def set_dashpush(self, dp):
        """
        Set the "push" of the TextWithDash, which
        is the extra spacing between the beginning
        of the dash and the specified position.

        ACCEPTS: float
        """
        self._dashpush = dp

    def get_position(self):
        "Return x, y as tuple"
        return self._dashx, self._dashy

    def set_position(self, xy):
        """
        Set the xy position of the TextWithDash.

        ACCEPTS: (x,y)
        """
        self.set_x(xy[0])
        self.set_y(xy[1])

    def set_x(self, x):
        """
        Set the x position of the TextWithDash.

        ACCEPTS: float
        """
        self._dashx = float(x)

    def set_y(self, y):
        """
        Set the y position of the TextWithDash.

        ACCEPTS: float
        """
        self._dashy = float(y)

    def set_transform(self, t):
        """
        Set the Transformation instance used by this artist.

        ACCEPTS: a matplotlib.transform transformation instance
        """
        Text.set_transform(self, t)
        self.dashline.set_transform(t)

    def get_figure(self):
        'return the figure instance'
        return self.figure

    def set_figure(self, fig):
        """
        Set the figure instance the artist belong to.

        ACCEPTS: a matplotlib.figure.Figure instance
        """
        Text.set_figure(self, fig)
        self.dashline.set_figure(fig)
