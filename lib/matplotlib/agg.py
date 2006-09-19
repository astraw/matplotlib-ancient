# This file was created automatically by SWIG 1.3.29.
# Don't modify this file, modify the SWIG interface instead.
# This file is compatible with both classic and new-style classes.

import _agg
import new
new_instancemethod = new.instancemethod
def _swig_setattr_nondynamic(self,class_type,name,value,static=1):
    if (name == "thisown"): return self.this.own(value)
    if (name == "this"):
        if type(value).__name__ == 'PySwigObject':
            self.__dict__[name] = value
            return
    method = class_type.__swig_setmethods__.get(name,None)
    if method: return method(self,value)
    if (not static) or hasattr(self,name):
        self.__dict__[name] = value
    else:
        raise AttributeError("You cannot add attributes to %s" % self)

def _swig_setattr(self,class_type,name,value):
    return _swig_setattr_nondynamic(self,class_type,name,value,0)

def _swig_getattr(self,class_type,name):
    if (name == "thisown"): return self.this.own()
    method = class_type.__swig_getmethods__.get(name,None)
    if method: return method(self)
    raise AttributeError,name

def _swig_repr(self):
    try: strthis = "proxy of " + self.this.__repr__()
    except: strthis = ""
    return "<%s.%s; %s >" % (self.__class__.__module__, self.__class__.__name__, strthis,)

import types
try:
    _object = types.ObjectType
    _newclass = 1
except AttributeError:
    class _object : pass
    _newclass = 0
del types


cover_shift = _agg.cover_shift
cover_size = _agg.cover_size
cover_mask = _agg.cover_mask
cover_none = _agg.cover_none
cover_full = _agg.cover_full
deg2rad = _agg.deg2rad
rad2deg = _agg.rad2deg
path_cmd_stop = _agg.path_cmd_stop
path_cmd_move_to = _agg.path_cmd_move_to
path_cmd_line_to = _agg.path_cmd_line_to
path_cmd_curve3 = _agg.path_cmd_curve3
path_cmd_curve4 = _agg.path_cmd_curve4
path_cmd_curveN = _agg.path_cmd_curveN
path_cmd_catrom = _agg.path_cmd_catrom
path_cmd_ubspline = _agg.path_cmd_ubspline
path_cmd_end_poly = _agg.path_cmd_end_poly
path_cmd_mask = _agg.path_cmd_mask
path_flags_none = _agg.path_flags_none
path_flags_ccw = _agg.path_flags_ccw
path_flags_cw = _agg.path_flags_cw
path_flags_close = _agg.path_flags_close
path_flags_mask = _agg.path_flags_mask
is_vertex = _agg.is_vertex
is_stop = _agg.is_stop
is_move_to = _agg.is_move_to
is_line_to = _agg.is_line_to
is_curve = _agg.is_curve
is_curve3 = _agg.is_curve3
is_curve4 = _agg.is_curve4
is_end_poly = _agg.is_end_poly
is_close = _agg.is_close
is_next_poly = _agg.is_next_poly
is_cw = _agg.is_cw
is_ccw = _agg.is_ccw
is_oriented = _agg.is_oriented
is_closed = _agg.is_closed
get_close_flag = _agg.get_close_flag
clear_orientation = _agg.clear_orientation
get_orientation = _agg.get_orientation
set_orientation = _agg.set_orientation
class point_type(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, point_type, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, point_type, name)
    __repr__ = _swig_repr
    __swig_setmethods__["x"] = _agg.point_type_x_set
    __swig_getmethods__["x"] = _agg.point_type_x_get
    if _newclass:x = property(_agg.point_type_x_get, _agg.point_type_x_set)
    __swig_setmethods__["y"] = _agg.point_type_y_set
    __swig_getmethods__["y"] = _agg.point_type_y_get
    if _newclass:y = property(_agg.point_type_y_get, _agg.point_type_y_set)
    def __init__(self, *args): 
        this = _agg.new_point_type(*args)
        try: self.this.append(this)
        except: self.this = this
    __swig_destroy__ = _agg.delete_point_type
    __del__ = lambda self : None;
point_type_swigregister = _agg.point_type_swigregister
point_type_swigregister(point_type)
cvar = _agg.cvar
pi = cvar.pi

class vertex_type(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, vertex_type, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, vertex_type, name)
    __repr__ = _swig_repr
    __swig_setmethods__["x"] = _agg.vertex_type_x_set
    __swig_getmethods__["x"] = _agg.vertex_type_x_get
    if _newclass:x = property(_agg.vertex_type_x_get, _agg.vertex_type_x_set)
    __swig_setmethods__["y"] = _agg.vertex_type_y_set
    __swig_getmethods__["y"] = _agg.vertex_type_y_get
    if _newclass:y = property(_agg.vertex_type_y_get, _agg.vertex_type_y_set)
    __swig_setmethods__["cmd"] = _agg.vertex_type_cmd_set
    __swig_getmethods__["cmd"] = _agg.vertex_type_cmd_get
    if _newclass:cmd = property(_agg.vertex_type_cmd_get, _agg.vertex_type_cmd_set)
    def __init__(self, *args): 
        this = _agg.new_vertex_type(*args)
        try: self.this.append(this)
        except: self.this = this
    __swig_destroy__ = _agg.delete_vertex_type
    __del__ = lambda self : None;
vertex_type_swigregister = _agg.vertex_type_swigregister
vertex_type_swigregister(vertex_type)

class rect(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, rect, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, rect, name)
    __repr__ = _swig_repr
    __swig_setmethods__["x1"] = _agg.rect_x1_set
    __swig_getmethods__["x1"] = _agg.rect_x1_get
    if _newclass:x1 = property(_agg.rect_x1_get, _agg.rect_x1_set)
    __swig_setmethods__["y1"] = _agg.rect_y1_set
    __swig_getmethods__["y1"] = _agg.rect_y1_get
    if _newclass:y1 = property(_agg.rect_y1_get, _agg.rect_y1_set)
    __swig_setmethods__["x2"] = _agg.rect_x2_set
    __swig_getmethods__["x2"] = _agg.rect_x2_get
    if _newclass:x2 = property(_agg.rect_x2_get, _agg.rect_x2_set)
    __swig_setmethods__["y2"] = _agg.rect_y2_set
    __swig_getmethods__["y2"] = _agg.rect_y2_get
    if _newclass:y2 = property(_agg.rect_y2_get, _agg.rect_y2_set)
    def __init__(self, *args): 
        this = _agg.new_rect(*args)
        try: self.this.append(this)
        except: self.this = this
    def normalize(*args): return _agg.rect_normalize(*args)
    def clip(*args): return _agg.rect_clip(*args)
    def is_valid(*args): return _agg.rect_is_valid(*args)
    __swig_destroy__ = _agg.delete_rect
    __del__ = lambda self : None;
rect_swigregister = _agg.rect_swigregister
rect_swigregister(rect)

class rect_d(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, rect_d, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, rect_d, name)
    __repr__ = _swig_repr
    __swig_setmethods__["x1"] = _agg.rect_d_x1_set
    __swig_getmethods__["x1"] = _agg.rect_d_x1_get
    if _newclass:x1 = property(_agg.rect_d_x1_get, _agg.rect_d_x1_set)
    __swig_setmethods__["y1"] = _agg.rect_d_y1_set
    __swig_getmethods__["y1"] = _agg.rect_d_y1_get
    if _newclass:y1 = property(_agg.rect_d_y1_get, _agg.rect_d_y1_set)
    __swig_setmethods__["x2"] = _agg.rect_d_x2_set
    __swig_getmethods__["x2"] = _agg.rect_d_x2_get
    if _newclass:x2 = property(_agg.rect_d_x2_get, _agg.rect_d_x2_set)
    __swig_setmethods__["y2"] = _agg.rect_d_y2_set
    __swig_getmethods__["y2"] = _agg.rect_d_y2_get
    if _newclass:y2 = property(_agg.rect_d_y2_get, _agg.rect_d_y2_set)
    def __init__(self, *args): 
        this = _agg.new_rect_d(*args)
        try: self.this.append(this)
        except: self.this = this
    def normalize(*args): return _agg.rect_d_normalize(*args)
    def clip(*args): return _agg.rect_d_clip(*args)
    def is_valid(*args): return _agg.rect_d_is_valid(*args)
    __swig_destroy__ = _agg.delete_rect_d
    __del__ = lambda self : None;
rect_d_swigregister = _agg.rect_d_swigregister
rect_d_swigregister(rect_d)

unite_rectangles = _agg.unite_rectangles
unite_rectangles_d = _agg.unite_rectangles_d
intersect_rectangles = _agg.intersect_rectangles
intersect_rectangles_d = _agg.intersect_rectangles_d
class binary_data(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, binary_data, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, binary_data, name)
    __repr__ = _swig_repr
    __swig_setmethods__["size"] = _agg.binary_data_size_set
    __swig_getmethods__["size"] = _agg.binary_data_size_get
    if _newclass:size = property(_agg.binary_data_size_get, _agg.binary_data_size_set)
    __swig_setmethods__["data"] = _agg.binary_data_data_set
    __swig_getmethods__["data"] = _agg.binary_data_data_get
    if _newclass:data = property(_agg.binary_data_data_get, _agg.binary_data_data_set)
    def __init__(self, *args): 
        this = _agg.new_binary_data(*args)
        try: self.this.append(this)
        except: self.this = this
    __swig_destroy__ = _agg.delete_binary_data
    __del__ = lambda self : None;
binary_data_swigregister = _agg.binary_data_swigregister
binary_data_swigregister(binary_data)

class buffer(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, buffer, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, buffer, name)
    __repr__ = _swig_repr
    def __init__(self, *args): 
        this = _agg.new_buffer(*args)
        try: self.this.append(this)
        except: self.this = this
    __swig_destroy__ = _agg.delete_buffer
    __del__ = lambda self : None;
    def to_string(*args): return _agg.buffer_to_string(*args)
    __swig_getmethods__["width"] = _agg.buffer_width_get
    if _newclass:width = property(_agg.buffer_width_get)
    __swig_getmethods__["height"] = _agg.buffer_height_get
    if _newclass:height = property(_agg.buffer_height_get)
    __swig_getmethods__["stride"] = _agg.buffer_stride_get
    if _newclass:stride = property(_agg.buffer_stride_get)
    __swig_setmethods__["data"] = _agg.buffer_data_set
    __swig_getmethods__["data"] = _agg.buffer_data_get
    if _newclass:data = property(_agg.buffer_data_get, _agg.buffer_data_set)
    __swig_setmethods__["freemem"] = _agg.buffer_freemem_set
    __swig_getmethods__["freemem"] = _agg.buffer_freemem_get
    if _newclass:freemem = property(_agg.buffer_freemem_get, _agg.buffer_freemem_set)
buffer_swigregister = _agg.buffer_swigregister
buffer_swigregister(buffer)

class order_rgb(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, order_rgb, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, order_rgb, name)
    __repr__ = _swig_repr
    R = _agg.order_rgb_R
    G = _agg.order_rgb_G
    B = _agg.order_rgb_B
    rgb_tag = _agg.order_rgb_rgb_tag
    def __init__(self, *args): 
        this = _agg.new_order_rgb(*args)
        try: self.this.append(this)
        except: self.this = this
    __swig_destroy__ = _agg.delete_order_rgb
    __del__ = lambda self : None;
order_rgb_swigregister = _agg.order_rgb_swigregister
order_rgb_swigregister(order_rgb)

class order_bgr(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, order_bgr, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, order_bgr, name)
    __repr__ = _swig_repr
    B = _agg.order_bgr_B
    G = _agg.order_bgr_G
    R = _agg.order_bgr_R
    rgb_tag = _agg.order_bgr_rgb_tag
    def __init__(self, *args): 
        this = _agg.new_order_bgr(*args)
        try: self.this.append(this)
        except: self.this = this
    __swig_destroy__ = _agg.delete_order_bgr
    __del__ = lambda self : None;
order_bgr_swigregister = _agg.order_bgr_swigregister
order_bgr_swigregister(order_bgr)

class order_rgba(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, order_rgba, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, order_rgba, name)
    __repr__ = _swig_repr
    R = _agg.order_rgba_R
    G = _agg.order_rgba_G
    B = _agg.order_rgba_B
    A = _agg.order_rgba_A
    rgba_tag = _agg.order_rgba_rgba_tag
    def __init__(self, *args): 
        this = _agg.new_order_rgba(*args)
        try: self.this.append(this)
        except: self.this = this
    __swig_destroy__ = _agg.delete_order_rgba
    __del__ = lambda self : None;
order_rgba_swigregister = _agg.order_rgba_swigregister
order_rgba_swigregister(order_rgba)

class order_argb(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, order_argb, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, order_argb, name)
    __repr__ = _swig_repr
    A = _agg.order_argb_A
    R = _agg.order_argb_R
    G = _agg.order_argb_G
    B = _agg.order_argb_B
    rgba_tag = _agg.order_argb_rgba_tag
    def __init__(self, *args): 
        this = _agg.new_order_argb(*args)
        try: self.this.append(this)
        except: self.this = this
    __swig_destroy__ = _agg.delete_order_argb
    __del__ = lambda self : None;
order_argb_swigregister = _agg.order_argb_swigregister
order_argb_swigregister(order_argb)

class order_abgr(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, order_abgr, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, order_abgr, name)
    __repr__ = _swig_repr
    A = _agg.order_abgr_A
    B = _agg.order_abgr_B
    G = _agg.order_abgr_G
    R = _agg.order_abgr_R
    rgba_tag = _agg.order_abgr_rgba_tag
    def __init__(self, *args): 
        this = _agg.new_order_abgr(*args)
        try: self.this.append(this)
        except: self.this = this
    __swig_destroy__ = _agg.delete_order_abgr
    __del__ = lambda self : None;
order_abgr_swigregister = _agg.order_abgr_swigregister
order_abgr_swigregister(order_abgr)

class order_bgra(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, order_bgra, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, order_bgra, name)
    __repr__ = _swig_repr
    B = _agg.order_bgra_B
    G = _agg.order_bgra_G
    R = _agg.order_bgra_R
    A = _agg.order_bgra_A
    rgba_tag = _agg.order_bgra_rgba_tag
    def __init__(self, *args): 
        this = _agg.new_order_bgra(*args)
        try: self.this.append(this)
        except: self.this = this
    __swig_destroy__ = _agg.delete_order_bgra
    __del__ = lambda self : None;
order_bgra_swigregister = _agg.order_bgra_swigregister
order_bgra_swigregister(order_bgra)

class rgba(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, rgba, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, rgba, name)
    __repr__ = _swig_repr
    __swig_setmethods__["r"] = _agg.rgba_r_set
    __swig_getmethods__["r"] = _agg.rgba_r_get
    if _newclass:r = property(_agg.rgba_r_get, _agg.rgba_r_set)
    __swig_setmethods__["g"] = _agg.rgba_g_set
    __swig_getmethods__["g"] = _agg.rgba_g_get
    if _newclass:g = property(_agg.rgba_g_get, _agg.rgba_g_set)
    __swig_setmethods__["b"] = _agg.rgba_b_set
    __swig_getmethods__["b"] = _agg.rgba_b_get
    if _newclass:b = property(_agg.rgba_b_get, _agg.rgba_b_set)
    __swig_setmethods__["a"] = _agg.rgba_a_set
    __swig_getmethods__["a"] = _agg.rgba_a_get
    if _newclass:a = property(_agg.rgba_a_get, _agg.rgba_a_set)
    def clear(*args): return _agg.rgba_clear(*args)
    def transparent(*args): return _agg.rgba_transparent(*args)
    def opacity(*args): return _agg.rgba_opacity(*args)
    def premultiply(*args): return _agg.rgba_premultiply(*args)
    def demultiply(*args): return _agg.rgba_demultiply(*args)
    def gradient(*args): return _agg.rgba_gradient(*args)
    __swig_getmethods__["no_color"] = lambda x: _agg.rgba_no_color
    if _newclass:no_color = staticmethod(_agg.rgba_no_color)
    __swig_getmethods__["from_wavelength"] = lambda x: _agg.rgba_from_wavelength
    if _newclass:from_wavelength = staticmethod(_agg.rgba_from_wavelength)
    def __init__(self, *args): 
        this = _agg.new_rgba(*args)
        try: self.this.append(this)
        except: self.this = this
    __swig_destroy__ = _agg.delete_rgba
    __del__ = lambda self : None;
rgba_swigregister = _agg.rgba_swigregister
rgba_swigregister(rgba)
rgba_no_color = _agg.rgba_no_color
rgba_from_wavelength = _agg.rgba_from_wavelength

class rgba8(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, rgba8, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, rgba8, name)
    __repr__ = _swig_repr
    base_shift = _agg.rgba8_base_shift
    base_size = _agg.rgba8_base_size
    base_mask = _agg.rgba8_base_mask
    __swig_setmethods__["r"] = _agg.rgba8_r_set
    __swig_getmethods__["r"] = _agg.rgba8_r_get
    if _newclass:r = property(_agg.rgba8_r_get, _agg.rgba8_r_set)
    __swig_setmethods__["g"] = _agg.rgba8_g_set
    __swig_getmethods__["g"] = _agg.rgba8_g_get
    if _newclass:g = property(_agg.rgba8_g_get, _agg.rgba8_g_set)
    __swig_setmethods__["b"] = _agg.rgba8_b_set
    __swig_getmethods__["b"] = _agg.rgba8_b_get
    if _newclass:b = property(_agg.rgba8_b_get, _agg.rgba8_b_set)
    __swig_setmethods__["a"] = _agg.rgba8_a_set
    __swig_getmethods__["a"] = _agg.rgba8_a_get
    if _newclass:a = property(_agg.rgba8_a_get, _agg.rgba8_a_set)
    def __init__(self, *args): 
        this = _agg.new_rgba8(*args)
        try: self.this.append(this)
        except: self.this = this
    def clear(*args): return _agg.rgba8_clear(*args)
    def transparent(*args): return _agg.rgba8_transparent(*args)
    def opacity(*args): return _agg.rgba8_opacity(*args)
    def premultiply(*args): return _agg.rgba8_premultiply(*args)
    def demultiply(*args): return _agg.rgba8_demultiply(*args)
    def gradient(*args): return _agg.rgba8_gradient(*args)
    __swig_getmethods__["no_color"] = lambda x: _agg.rgba8_no_color
    if _newclass:no_color = staticmethod(_agg.rgba8_no_color)
    __swig_getmethods__["from_wavelength"] = lambda x: _agg.rgba8_from_wavelength
    if _newclass:from_wavelength = staticmethod(_agg.rgba8_from_wavelength)
    __swig_destroy__ = _agg.delete_rgba8
    __del__ = lambda self : None;
rgba8_swigregister = _agg.rgba8_swigregister
rgba8_swigregister(rgba8)
rgba_pre = _agg.rgba_pre
rgba8_no_color = _agg.rgba8_no_color
rgba8_from_wavelength = _agg.rgba8_from_wavelength

rgb8_packed = _agg.rgb8_packed
bgr8_packed = _agg.bgr8_packed
argb8_packed = _agg.argb8_packed
class rgba16(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, rgba16, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, rgba16, name)
    __repr__ = _swig_repr
    base_shift = _agg.rgba16_base_shift
    base_size = _agg.rgba16_base_size
    base_mask = _agg.rgba16_base_mask
    __swig_setmethods__["r"] = _agg.rgba16_r_set
    __swig_getmethods__["r"] = _agg.rgba16_r_get
    if _newclass:r = property(_agg.rgba16_r_get, _agg.rgba16_r_set)
    __swig_setmethods__["g"] = _agg.rgba16_g_set
    __swig_getmethods__["g"] = _agg.rgba16_g_get
    if _newclass:g = property(_agg.rgba16_g_get, _agg.rgba16_g_set)
    __swig_setmethods__["b"] = _agg.rgba16_b_set
    __swig_getmethods__["b"] = _agg.rgba16_b_get
    if _newclass:b = property(_agg.rgba16_b_get, _agg.rgba16_b_set)
    __swig_setmethods__["a"] = _agg.rgba16_a_set
    __swig_getmethods__["a"] = _agg.rgba16_a_get
    if _newclass:a = property(_agg.rgba16_a_get, _agg.rgba16_a_set)
    def __init__(self, *args): 
        this = _agg.new_rgba16(*args)
        try: self.this.append(this)
        except: self.this = this
    def clear(*args): return _agg.rgba16_clear(*args)
    def transparent(*args): return _agg.rgba16_transparent(*args)
    def opacity(*args): return _agg.rgba16_opacity(*args)
    def premultiply(*args): return _agg.rgba16_premultiply(*args)
    def demultiply(*args): return _agg.rgba16_demultiply(*args)
    def gradient(*args): return _agg.rgba16_gradient(*args)
    __swig_getmethods__["no_color"] = lambda x: _agg.rgba16_no_color
    if _newclass:no_color = staticmethod(_agg.rgba16_no_color)
    __swig_getmethods__["from_wavelength"] = lambda x: _agg.rgba16_from_wavelength
    if _newclass:from_wavelength = staticmethod(_agg.rgba16_from_wavelength)
    __swig_destroy__ = _agg.delete_rgba16
    __del__ = lambda self : None;
rgba16_swigregister = _agg.rgba16_swigregister
rgba16_swigregister(rgba16)
rgba8_pre = _agg.rgba8_pre
rgba16_no_color = _agg.rgba16_no_color
rgba16_from_wavelength = _agg.rgba16_from_wavelength

class trans_affine(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, trans_affine, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, trans_affine, name)
    __repr__ = _swig_repr
    def __init__(self, *args): 
        this = _agg.new_trans_affine(*args)
        try: self.this.append(this)
        except: self.this = this
    def parl_to_parl(*args): return _agg.trans_affine_parl_to_parl(*args)
    def rect_to_parl(*args): return _agg.trans_affine_rect_to_parl(*args)
    def parl_to_rect(*args): return _agg.trans_affine_parl_to_rect(*args)
    def reset(*args): return _agg.trans_affine_reset(*args)
    def multiply(*args): return _agg.trans_affine_multiply(*args)
    def premultiply(*args): return _agg.trans_affine_premultiply(*args)
    def invert(*args): return _agg.trans_affine_invert(*args)
    def flip_x(*args): return _agg.trans_affine_flip_x(*args)
    def flip_y(*args): return _agg.trans_affine_flip_y(*args)
    def as_vec6(*args): return _agg.trans_affine_as_vec6(*args)
    def load_from(*args): return _agg.trans_affine_load_from(*args)
    def __imul__(*args): return _agg.trans_affine___imul__(*args)
    def __mul__(*args): return _agg.trans_affine___mul__(*args)
    def __invert__(*args): return _agg.trans_affine___invert__(*args)
    def __eq__(*args): return _agg.trans_affine___eq__(*args)
    def __ne__(*args): return _agg.trans_affine___ne__(*args)
    def transform(*args): return _agg.trans_affine_transform(*args)
    def inverse_transform(*args): return _agg.trans_affine_inverse_transform(*args)
    def determinant(*args): return _agg.trans_affine_determinant(*args)
    def scale(*args): return _agg.trans_affine_scale(*args)
    def is_identity(*args): return _agg.trans_affine_is_identity(*args)
    def is_equal(*args): return _agg.trans_affine_is_equal(*args)
    def get_rotation(*args): return _agg.trans_affine_get_rotation(*args)
    def get_translation(*args): return _agg.trans_affine_get_translation(*args)
    def get_scaling(*args): return _agg.trans_affine_get_scaling(*args)
    __swig_destroy__ = _agg.delete_trans_affine
    __del__ = lambda self : None;
trans_affine_swigregister = _agg.trans_affine_swigregister
trans_affine_swigregister(trans_affine)
rgba16_pre = _agg.rgba16_pre

class trans_affine_rotation(trans_affine):
    __swig_setmethods__ = {}
    for _s in [trans_affine]: __swig_setmethods__.update(_s.__swig_setmethods__)
    __setattr__ = lambda self, name, value: _swig_setattr(self, trans_affine_rotation, name, value)
    __swig_getmethods__ = {}
    for _s in [trans_affine]: __swig_getmethods__.update(_s.__swig_getmethods__)
    __getattr__ = lambda self, name: _swig_getattr(self, trans_affine_rotation, name)
    __repr__ = _swig_repr
    def __init__(self, *args): 
        this = _agg.new_trans_affine_rotation(*args)
        try: self.this.append(this)
        except: self.this = this
    __swig_destroy__ = _agg.delete_trans_affine_rotation
    __del__ = lambda self : None;
trans_affine_rotation_swigregister = _agg.trans_affine_rotation_swigregister
trans_affine_rotation_swigregister(trans_affine_rotation)

class trans_affine_scaling(trans_affine):
    __swig_setmethods__ = {}
    for _s in [trans_affine]: __swig_setmethods__.update(_s.__swig_setmethods__)
    __setattr__ = lambda self, name, value: _swig_setattr(self, trans_affine_scaling, name, value)
    __swig_getmethods__ = {}
    for _s in [trans_affine]: __swig_getmethods__.update(_s.__swig_getmethods__)
    __getattr__ = lambda self, name: _swig_getattr(self, trans_affine_scaling, name)
    __repr__ = _swig_repr
    def __init__(self, *args): 
        this = _agg.new_trans_affine_scaling(*args)
        try: self.this.append(this)
        except: self.this = this
    __swig_destroy__ = _agg.delete_trans_affine_scaling
    __del__ = lambda self : None;
trans_affine_scaling_swigregister = _agg.trans_affine_scaling_swigregister
trans_affine_scaling_swigregister(trans_affine_scaling)

class trans_affine_translation(trans_affine):
    __swig_setmethods__ = {}
    for _s in [trans_affine]: __swig_setmethods__.update(_s.__swig_setmethods__)
    __setattr__ = lambda self, name, value: _swig_setattr(self, trans_affine_translation, name, value)
    __swig_getmethods__ = {}
    for _s in [trans_affine]: __swig_getmethods__.update(_s.__swig_getmethods__)
    __getattr__ = lambda self, name: _swig_getattr(self, trans_affine_translation, name)
    __repr__ = _swig_repr
    def __init__(self, *args): 
        this = _agg.new_trans_affine_translation(*args)
        try: self.this.append(this)
        except: self.this = this
    __swig_destroy__ = _agg.delete_trans_affine_translation
    __del__ = lambda self : None;
trans_affine_translation_swigregister = _agg.trans_affine_translation_swigregister
trans_affine_translation_swigregister(trans_affine_translation)

class trans_affine_skewing(trans_affine):
    __swig_setmethods__ = {}
    for _s in [trans_affine]: __swig_setmethods__.update(_s.__swig_setmethods__)
    __setattr__ = lambda self, name, value: _swig_setattr(self, trans_affine_skewing, name, value)
    __swig_getmethods__ = {}
    for _s in [trans_affine]: __swig_getmethods__.update(_s.__swig_getmethods__)
    __getattr__ = lambda self, name: _swig_getattr(self, trans_affine_skewing, name)
    __repr__ = _swig_repr
    def __init__(self, *args): 
        this = _agg.new_trans_affine_skewing(*args)
        try: self.this.append(this)
        except: self.this = this
    __swig_destroy__ = _agg.delete_trans_affine_skewing
    __del__ = lambda self : None;
trans_affine_skewing_swigregister = _agg.trans_affine_skewing_swigregister
trans_affine_skewing_swigregister(trans_affine_skewing)

class path_storage(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, path_storage, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, path_storage, name)
    __repr__ = _swig_repr
    __swig_destroy__ = _agg.delete_path_storage
    __del__ = lambda self : None;
    def __init__(self, *args): 
        this = _agg.new_path_storage(*args)
        try: self.this.append(this)
        except: self.this = this
    def remove_all(*args): return _agg.path_storage_remove_all(*args)
    def last_vertex(*args): return _agg.path_storage_last_vertex(*args)
    def prev_vertex(*args): return _agg.path_storage_prev_vertex(*args)
    def rel_to_abs(*args): return _agg.path_storage_rel_to_abs(*args)
    def move_to(*args): return _agg.path_storage_move_to(*args)
    def move_rel(*args): return _agg.path_storage_move_rel(*args)
    def line_to(*args): return _agg.path_storage_line_to(*args)
    def line_rel(*args): return _agg.path_storage_line_rel(*args)
    def arc_to(*args): return _agg.path_storage_arc_to(*args)
    def arc_rel(*args): return _agg.path_storage_arc_rel(*args)
    def curve3(*args): return _agg.path_storage_curve3(*args)
    def curve3_rel(*args): return _agg.path_storage_curve3_rel(*args)
    def curve4(*args): return _agg.path_storage_curve4(*args)
    def curve4_rel(*args): return _agg.path_storage_curve4_rel(*args)
    def end_poly(*args): return _agg.path_storage_end_poly(*args)
    def close_polygon(*args): return _agg.path_storage_close_polygon(*args)
    def add_poly(*args): return _agg.path_storage_add_poly(*args)
    def start_new_path(*args): return _agg.path_storage_start_new_path(*args)
    def copy_from(*args): return _agg.path_storage_copy_from(*args)
    def total_vertices(*args): return _agg.path_storage_total_vertices(*args)
    def command(*args): return _agg.path_storage_command(*args)
    def rewind(*args): return _agg.path_storage_rewind(*args)
    def vertex(*args): return _agg.path_storage_vertex(*args)
    def arrange_orientations(*args): return _agg.path_storage_arrange_orientations(*args)
    def arrange_orientations_all_paths(*args): return _agg.path_storage_arrange_orientations_all_paths(*args)
    def flip_x(*args): return _agg.path_storage_flip_x(*args)
    def flip_y(*args): return _agg.path_storage_flip_y(*args)
    def add_vertex(*args): return _agg.path_storage_add_vertex(*args)
    def modify_vertex(*args): return _agg.path_storage_modify_vertex(*args)
    def modify_command(*args): return _agg.path_storage_modify_command(*args)
path_storage_swigregister = _agg.path_storage_swigregister
path_storage_swigregister(path_storage)

butt_cap = _agg.butt_cap
square_cap = _agg.square_cap
round_cap = _agg.round_cap
miter_join = _agg.miter_join
miter_join_revert = _agg.miter_join_revert
round_join = _agg.round_join
bevel_join = _agg.bevel_join
class rendering_buffer(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, rendering_buffer, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, rendering_buffer, name)
    __repr__ = _swig_repr
    __swig_destroy__ = _agg.delete_rendering_buffer
    __del__ = lambda self : None;
    def __init__(self, *args): 
        this = _agg.new_rendering_buffer(*args)
        try: self.this.append(this)
        except: self.this = this
    def attach(*args): return _agg.rendering_buffer_attach(*args)
    def buf(*args): return _agg.rendering_buffer_buf(*args)
    def width(*args): return _agg.rendering_buffer_width(*args)
    def height(*args): return _agg.rendering_buffer_height(*args)
    def stride(*args): return _agg.rendering_buffer_stride(*args)
    def stride_abs(*args): return _agg.rendering_buffer_stride_abs(*args)
    def row(*args): return _agg.rendering_buffer_row(*args)
    def next_row(*args): return _agg.rendering_buffer_next_row(*args)
    def rows(*args): return _agg.rendering_buffer_rows(*args)
    def copy_from(*args): return _agg.rendering_buffer_copy_from(*args)
    def clear(*args): return _agg.rendering_buffer_clear(*args)
    def attachb(*args): return _agg.rendering_buffer_attachb(*args)
rendering_buffer_swigregister = _agg.rendering_buffer_swigregister
rendering_buffer_swigregister(rendering_buffer)
stroke_theta = cvar.stroke_theta

comp_op_clear = _agg.comp_op_clear
comp_op_src = _agg.comp_op_src
comp_op_dst = _agg.comp_op_dst
comp_op_src_over = _agg.comp_op_src_over
comp_op_dst_over = _agg.comp_op_dst_over
comp_op_src_in = _agg.comp_op_src_in
comp_op_dst_in = _agg.comp_op_dst_in
comp_op_src_out = _agg.comp_op_src_out
comp_op_dst_out = _agg.comp_op_dst_out
comp_op_src_atop = _agg.comp_op_src_atop
comp_op_dst_atop = _agg.comp_op_dst_atop
comp_op_xor = _agg.comp_op_xor
comp_op_plus = _agg.comp_op_plus
comp_op_minus = _agg.comp_op_minus
comp_op_multiply = _agg.comp_op_multiply
comp_op_screen = _agg.comp_op_screen
comp_op_overlay = _agg.comp_op_overlay
comp_op_darken = _agg.comp_op_darken
comp_op_lighten = _agg.comp_op_lighten
comp_op_color_dodge = _agg.comp_op_color_dodge
comp_op_color_burn = _agg.comp_op_color_burn
comp_op_hard_light = _agg.comp_op_hard_light
comp_op_soft_light = _agg.comp_op_soft_light
comp_op_difference = _agg.comp_op_difference
comp_op_exclusion = _agg.comp_op_exclusion
comp_op_contrast = _agg.comp_op_contrast
end_of_comp_op_e = _agg.end_of_comp_op_e
class pixel64_type(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, pixel64_type, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, pixel64_type, name)
    __repr__ = _swig_repr
    __swig_setmethods__["c"] = _agg.pixel64_type_c_set
    __swig_getmethods__["c"] = _agg.pixel64_type_c_get
    if _newclass:c = property(_agg.pixel64_type_c_get, _agg.pixel64_type_c_set)
    def __init__(self, *args): 
        this = _agg.new_pixel64_type(*args)
        try: self.this.append(this)
        except: self.this = this
    __swig_destroy__ = _agg.delete_pixel64_type
    __del__ = lambda self : None;
pixel64_type_swigregister = _agg.pixel64_type_swigregister
pixel64_type_swigregister(pixel64_type)

class pixel_format_rgba(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, pixel_format_rgba, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, pixel_format_rgba, name)
    __repr__ = _swig_repr
    base_shift = _agg.pixel_format_rgba_base_shift
    base_size = _agg.pixel_format_rgba_base_size
    base_mask = _agg.pixel_format_rgba_base_mask
    def __init__(self, *args): 
        this = _agg.new_pixel_format_rgba(*args)
        try: self.this.append(this)
        except: self.this = this
    def attach(*args): return _agg.pixel_format_rgba_attach(*args)
    def width(*args): return _agg.pixel_format_rgba_width(*args)
    def height(*args): return _agg.pixel_format_rgba_height(*args)
    def pixel(*args): return _agg.pixel_format_rgba_pixel(*args)
    def row(*args): return _agg.pixel_format_rgba_row(*args)
    def span(*args): return _agg.pixel_format_rgba_span(*args)
    def copy_pixel(*args): return _agg.pixel_format_rgba_copy_pixel(*args)
    def blend_pixel(*args): return _agg.pixel_format_rgba_blend_pixel(*args)
    def copy_hline(*args): return _agg.pixel_format_rgba_copy_hline(*args)
    def copy_vline(*args): return _agg.pixel_format_rgba_copy_vline(*args)
    def blend_hline(*args): return _agg.pixel_format_rgba_blend_hline(*args)
    def blend_vline(*args): return _agg.pixel_format_rgba_blend_vline(*args)
    def blend_solid_hspan(*args): return _agg.pixel_format_rgba_blend_solid_hspan(*args)
    def blend_solid_vspan(*args): return _agg.pixel_format_rgba_blend_solid_vspan(*args)
    def copy_color_hspan(*args): return _agg.pixel_format_rgba_copy_color_hspan(*args)
    def blend_color_hspan(*args): return _agg.pixel_format_rgba_blend_color_hspan(*args)
    def blend_color_vspan(*args): return _agg.pixel_format_rgba_blend_color_vspan(*args)
    def premultiply(*args): return _agg.pixel_format_rgba_premultiply(*args)
    def demultiply(*args): return _agg.pixel_format_rgba_demultiply(*args)
    def copy_from(*args): return _agg.pixel_format_rgba_copy_from(*args)
    __swig_destroy__ = _agg.delete_pixel_format_rgba
    __del__ = lambda self : None;
pixel_format_rgba_swigregister = _agg.pixel_format_rgba_swigregister
pixel_format_rgba_swigregister(pixel_format_rgba)

class renderer_base_rgba(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, renderer_base_rgba, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, renderer_base_rgba, name)
    __repr__ = _swig_repr
    def __init__(self, *args): 
        this = _agg.new_renderer_base_rgba(*args)
        try: self.this.append(this)
        except: self.this = this
    def attach(*args): return _agg.renderer_base_rgba_attach(*args)
    def ren(*args): return _agg.renderer_base_rgba_ren(*args)
    def width(*args): return _agg.renderer_base_rgba_width(*args)
    def height(*args): return _agg.renderer_base_rgba_height(*args)
    def reset_clipping(*args): return _agg.renderer_base_rgba_reset_clipping(*args)
    def clip_box_naked(*args): return _agg.renderer_base_rgba_clip_box_naked(*args)
    def inbox(*args): return _agg.renderer_base_rgba_inbox(*args)
    def first_clip_box(*args): return _agg.renderer_base_rgba_first_clip_box(*args)
    def next_clip_box(*args): return _agg.renderer_base_rgba_next_clip_box(*args)
    def clip_box(*args): return _agg.renderer_base_rgba_clip_box(*args)
    def xmin(*args): return _agg.renderer_base_rgba_xmin(*args)
    def ymin(*args): return _agg.renderer_base_rgba_ymin(*args)
    def xmax(*args): return _agg.renderer_base_rgba_xmax(*args)
    def ymax(*args): return _agg.renderer_base_rgba_ymax(*args)
    def bounding_clip_box(*args): return _agg.renderer_base_rgba_bounding_clip_box(*args)
    def bounding_xmin(*args): return _agg.renderer_base_rgba_bounding_xmin(*args)
    def bounding_ymin(*args): return _agg.renderer_base_rgba_bounding_ymin(*args)
    def bounding_xmax(*args): return _agg.renderer_base_rgba_bounding_xmax(*args)
    def bounding_ymax(*args): return _agg.renderer_base_rgba_bounding_ymax(*args)
    def clear(*args): return _agg.renderer_base_rgba_clear(*args)
    def copy_pixel(*args): return _agg.renderer_base_rgba_copy_pixel(*args)
    def blend_pixel(*args): return _agg.renderer_base_rgba_blend_pixel(*args)
    def pixel(*args): return _agg.renderer_base_rgba_pixel(*args)
    def copy_hline(*args): return _agg.renderer_base_rgba_copy_hline(*args)
    def copy_vline(*args): return _agg.renderer_base_rgba_copy_vline(*args)
    def blend_hline(*args): return _agg.renderer_base_rgba_blend_hline(*args)
    def blend_vline(*args): return _agg.renderer_base_rgba_blend_vline(*args)
    def copy_bar(*args): return _agg.renderer_base_rgba_copy_bar(*args)
    def blend_bar(*args): return _agg.renderer_base_rgba_blend_bar(*args)
    def span(*args): return _agg.renderer_base_rgba_span(*args)
    def blend_solid_hspan(*args): return _agg.renderer_base_rgba_blend_solid_hspan(*args)
    def blend_solid_vspan(*args): return _agg.renderer_base_rgba_blend_solid_vspan(*args)
    def copy_color_hspan(*args): return _agg.renderer_base_rgba_copy_color_hspan(*args)
    def blend_color_hspan(*args): return _agg.renderer_base_rgba_blend_color_hspan(*args)
    def blend_color_vspan(*args): return _agg.renderer_base_rgba_blend_color_vspan(*args)
    def copy_color_hspan_no_clip(*args): return _agg.renderer_base_rgba_copy_color_hspan_no_clip(*args)
    def blend_color_hspan_no_clip(*args): return _agg.renderer_base_rgba_blend_color_hspan_no_clip(*args)
    def blend_color_vspan_no_clip(*args): return _agg.renderer_base_rgba_blend_color_vspan_no_clip(*args)
    def clip_rect_area(*args): return _agg.renderer_base_rgba_clip_rect_area(*args)
    def copy_from(*args): return _agg.renderer_base_rgba_copy_from(*args)
    def clear_rgba8(*args): return _agg.renderer_base_rgba_clear_rgba8(*args)
    def clear_rgba(*args): return _agg.renderer_base_rgba_clear_rgba(*args)
    __swig_destroy__ = _agg.delete_renderer_base_rgba
    __del__ = lambda self : None;
renderer_base_rgba_swigregister = _agg.renderer_base_rgba_swigregister
renderer_base_rgba_swigregister(renderer_base_rgba)

class conv_curve_path(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, conv_curve_path, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, conv_curve_path, name)
    __repr__ = _swig_repr
    def __init__(self, *args): 
        this = _agg.new_conv_curve_path(*args)
        try: self.this.append(this)
        except: self.this = this
    def set_source(*args): return _agg.conv_curve_path_set_source(*args)
    def approximation_scale(*args): return _agg.conv_curve_path_approximation_scale(*args)
    def rewind(*args): return _agg.conv_curve_path_rewind(*args)
    def vertex(*args): return _agg.conv_curve_path_vertex(*args)
    __swig_destroy__ = _agg.delete_conv_curve_path
    __del__ = lambda self : None;
conv_curve_path_swigregister = _agg.conv_curve_path_swigregister
conv_curve_path_swigregister(conv_curve_path)

class conv_curve_trans(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, conv_curve_trans, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, conv_curve_trans, name)
    __repr__ = _swig_repr
    def __init__(self, *args): 
        this = _agg.new_conv_curve_trans(*args)
        try: self.this.append(this)
        except: self.this = this
    def set_source(*args): return _agg.conv_curve_trans_set_source(*args)
    def approximation_scale(*args): return _agg.conv_curve_trans_approximation_scale(*args)
    def rewind(*args): return _agg.conv_curve_trans_rewind(*args)
    def vertex(*args): return _agg.conv_curve_trans_vertex(*args)
    __swig_destroy__ = _agg.delete_conv_curve_trans
    __del__ = lambda self : None;
conv_curve_trans_swigregister = _agg.conv_curve_trans_swigregister
conv_curve_trans_swigregister(conv_curve_trans)

class conv_transform_path(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, conv_transform_path, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, conv_transform_path, name)
    __repr__ = _swig_repr
    def __init__(self, *args): 
        this = _agg.new_conv_transform_path(*args)
        try: self.this.append(this)
        except: self.this = this
    def set_source(*args): return _agg.conv_transform_path_set_source(*args)
    def rewind(*args): return _agg.conv_transform_path_rewind(*args)
    def vertex(*args): return _agg.conv_transform_path_vertex(*args)
    def transformer(*args): return _agg.conv_transform_path_transformer(*args)
    __swig_destroy__ = _agg.delete_conv_transform_path
    __del__ = lambda self : None;
conv_transform_path_swigregister = _agg.conv_transform_path_swigregister
conv_transform_path_swigregister(conv_transform_path)

class conv_transform_curve(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, conv_transform_curve, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, conv_transform_curve, name)
    __repr__ = _swig_repr
    def __init__(self, *args): 
        this = _agg.new_conv_transform_curve(*args)
        try: self.this.append(this)
        except: self.this = this
    def set_source(*args): return _agg.conv_transform_curve_set_source(*args)
    def rewind(*args): return _agg.conv_transform_curve_rewind(*args)
    def vertex(*args): return _agg.conv_transform_curve_vertex(*args)
    def transformer(*args): return _agg.conv_transform_curve_transformer(*args)
    __swig_destroy__ = _agg.delete_conv_transform_curve
    __del__ = lambda self : None;
conv_transform_curve_swigregister = _agg.conv_transform_curve_swigregister
conv_transform_curve_swigregister(conv_transform_curve)

class vcgen_stroke(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, vcgen_stroke, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, vcgen_stroke, name)
    __repr__ = _swig_repr
    def __init__(self, *args): 
        this = _agg.new_vcgen_stroke(*args)
        try: self.this.append(this)
        except: self.this = this
    def line_cap(*args): return _agg.vcgen_stroke_line_cap(*args)
    def line_join(*args): return _agg.vcgen_stroke_line_join(*args)
    def inner_line_join(*args): return _agg.vcgen_stroke_inner_line_join(*args)
    def miter_limit_theta(*args): return _agg.vcgen_stroke_miter_limit_theta(*args)
    def width(*args): return _agg.vcgen_stroke_width(*args)
    def miter_limit(*args): return _agg.vcgen_stroke_miter_limit(*args)
    def inner_miter_limit(*args): return _agg.vcgen_stroke_inner_miter_limit(*args)
    def approximation_scale(*args): return _agg.vcgen_stroke_approximation_scale(*args)
    def shorten(*args): return _agg.vcgen_stroke_shorten(*args)
    def remove_all(*args): return _agg.vcgen_stroke_remove_all(*args)
    def add_vertex(*args): return _agg.vcgen_stroke_add_vertex(*args)
    def rewind(*args): return _agg.vcgen_stroke_rewind(*args)
    def vertex(*args): return _agg.vcgen_stroke_vertex(*args)
    __swig_destroy__ = _agg.delete_vcgen_stroke
    __del__ = lambda self : None;
vcgen_stroke_swigregister = _agg.vcgen_stroke_swigregister
vcgen_stroke_swigregister(vcgen_stroke)

class null_markers(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, null_markers, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, null_markers, name)
    __repr__ = _swig_repr
    def remove_all(*args): return _agg.null_markers_remove_all(*args)
    def add_vertex(*args): return _agg.null_markers_add_vertex(*args)
    def prepare_src(*args): return _agg.null_markers_prepare_src(*args)
    def rewind(*args): return _agg.null_markers_rewind(*args)
    def vertex(*args): return _agg.null_markers_vertex(*args)
    def __init__(self, *args): 
        this = _agg.new_null_markers(*args)
        try: self.this.append(this)
        except: self.this = this
    __swig_destroy__ = _agg.delete_null_markers
    __del__ = lambda self : None;
null_markers_swigregister = _agg.null_markers_swigregister
null_markers_swigregister(null_markers)

class conv_adaptor_vcgen_path(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, conv_adaptor_vcgen_path, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, conv_adaptor_vcgen_path, name)
    __repr__ = _swig_repr
    def __init__(self, *args): 
        this = _agg.new_conv_adaptor_vcgen_path(*args)
        try: self.this.append(this)
        except: self.this = this
    def set_source(*args): return _agg.conv_adaptor_vcgen_path_set_source(*args)
    def generator(*args): return _agg.conv_adaptor_vcgen_path_generator(*args)
    def markers(*args): return _agg.conv_adaptor_vcgen_path_markers(*args)
    def rewind(*args): return _agg.conv_adaptor_vcgen_path_rewind(*args)
    def vertex(*args): return _agg.conv_adaptor_vcgen_path_vertex(*args)
    __swig_destroy__ = _agg.delete_conv_adaptor_vcgen_path
    __del__ = lambda self : None;
conv_adaptor_vcgen_path_swigregister = _agg.conv_adaptor_vcgen_path_swigregister
conv_adaptor_vcgen_path_swigregister(conv_adaptor_vcgen_path)

class conv_adaptor_vcgen_transpath(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, conv_adaptor_vcgen_transpath, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, conv_adaptor_vcgen_transpath, name)
    __repr__ = _swig_repr
    def __init__(self, *args): 
        this = _agg.new_conv_adaptor_vcgen_transpath(*args)
        try: self.this.append(this)
        except: self.this = this
    def set_source(*args): return _agg.conv_adaptor_vcgen_transpath_set_source(*args)
    def generator(*args): return _agg.conv_adaptor_vcgen_transpath_generator(*args)
    def markers(*args): return _agg.conv_adaptor_vcgen_transpath_markers(*args)
    def rewind(*args): return _agg.conv_adaptor_vcgen_transpath_rewind(*args)
    def vertex(*args): return _agg.conv_adaptor_vcgen_transpath_vertex(*args)
    __swig_destroy__ = _agg.delete_conv_adaptor_vcgen_transpath
    __del__ = lambda self : None;
conv_adaptor_vcgen_transpath_swigregister = _agg.conv_adaptor_vcgen_transpath_swigregister
conv_adaptor_vcgen_transpath_swigregister(conv_adaptor_vcgen_transpath)

class conv_adaptor_vcgen_curve(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, conv_adaptor_vcgen_curve, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, conv_adaptor_vcgen_curve, name)
    __repr__ = _swig_repr
    def __init__(self, *args): 
        this = _agg.new_conv_adaptor_vcgen_curve(*args)
        try: self.this.append(this)
        except: self.this = this
    def set_source(*args): return _agg.conv_adaptor_vcgen_curve_set_source(*args)
    def generator(*args): return _agg.conv_adaptor_vcgen_curve_generator(*args)
    def markers(*args): return _agg.conv_adaptor_vcgen_curve_markers(*args)
    def rewind(*args): return _agg.conv_adaptor_vcgen_curve_rewind(*args)
    def vertex(*args): return _agg.conv_adaptor_vcgen_curve_vertex(*args)
    __swig_destroy__ = _agg.delete_conv_adaptor_vcgen_curve
    __del__ = lambda self : None;
conv_adaptor_vcgen_curve_swigregister = _agg.conv_adaptor_vcgen_curve_swigregister
conv_adaptor_vcgen_curve_swigregister(conv_adaptor_vcgen_curve)

class conv_adaptor_vcgen_transcurve(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, conv_adaptor_vcgen_transcurve, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, conv_adaptor_vcgen_transcurve, name)
    __repr__ = _swig_repr
    def __init__(self, *args): 
        this = _agg.new_conv_adaptor_vcgen_transcurve(*args)
        try: self.this.append(this)
        except: self.this = this
    def set_source(*args): return _agg.conv_adaptor_vcgen_transcurve_set_source(*args)
    def generator(*args): return _agg.conv_adaptor_vcgen_transcurve_generator(*args)
    def markers(*args): return _agg.conv_adaptor_vcgen_transcurve_markers(*args)
    def rewind(*args): return _agg.conv_adaptor_vcgen_transcurve_rewind(*args)
    def vertex(*args): return _agg.conv_adaptor_vcgen_transcurve_vertex(*args)
    __swig_destroy__ = _agg.delete_conv_adaptor_vcgen_transcurve
    __del__ = lambda self : None;
conv_adaptor_vcgen_transcurve_swigregister = _agg.conv_adaptor_vcgen_transcurve_swigregister
conv_adaptor_vcgen_transcurve_swigregister(conv_adaptor_vcgen_transcurve)

class conv_adaptor_vcgen_curvetrans(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, conv_adaptor_vcgen_curvetrans, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, conv_adaptor_vcgen_curvetrans, name)
    __repr__ = _swig_repr
    def __init__(self, *args): 
        this = _agg.new_conv_adaptor_vcgen_curvetrans(*args)
        try: self.this.append(this)
        except: self.this = this
    def set_source(*args): return _agg.conv_adaptor_vcgen_curvetrans_set_source(*args)
    def generator(*args): return _agg.conv_adaptor_vcgen_curvetrans_generator(*args)
    def markers(*args): return _agg.conv_adaptor_vcgen_curvetrans_markers(*args)
    def rewind(*args): return _agg.conv_adaptor_vcgen_curvetrans_rewind(*args)
    def vertex(*args): return _agg.conv_adaptor_vcgen_curvetrans_vertex(*args)
    __swig_destroy__ = _agg.delete_conv_adaptor_vcgen_curvetrans
    __del__ = lambda self : None;
conv_adaptor_vcgen_curvetrans_swigregister = _agg.conv_adaptor_vcgen_curvetrans_swigregister
conv_adaptor_vcgen_curvetrans_swigregister(conv_adaptor_vcgen_curvetrans)

class conv_stroke_path(conv_adaptor_vcgen_path):
    __swig_setmethods__ = {}
    for _s in [conv_adaptor_vcgen_path]: __swig_setmethods__.update(_s.__swig_setmethods__)
    __setattr__ = lambda self, name, value: _swig_setattr(self, conv_stroke_path, name, value)
    __swig_getmethods__ = {}
    for _s in [conv_adaptor_vcgen_path]: __swig_getmethods__.update(_s.__swig_getmethods__)
    __getattr__ = lambda self, name: _swig_getattr(self, conv_stroke_path, name)
    __repr__ = _swig_repr
    def __init__(self, *args): 
        this = _agg.new_conv_stroke_path(*args)
        try: self.this.append(this)
        except: self.this = this
    def line_cap(*args): return _agg.conv_stroke_path_line_cap(*args)
    def line_join(*args): return _agg.conv_stroke_path_line_join(*args)
    def inner_line_join(*args): return _agg.conv_stroke_path_inner_line_join(*args)
    def miter_limit_theta(*args): return _agg.conv_stroke_path_miter_limit_theta(*args)
    def width(*args): return _agg.conv_stroke_path_width(*args)
    def miter_limit(*args): return _agg.conv_stroke_path_miter_limit(*args)
    def inner_miter_limit(*args): return _agg.conv_stroke_path_inner_miter_limit(*args)
    def approximation_scale(*args): return _agg.conv_stroke_path_approximation_scale(*args)
    def shorten(*args): return _agg.conv_stroke_path_shorten(*args)
    __swig_destroy__ = _agg.delete_conv_stroke_path
    __del__ = lambda self : None;
conv_stroke_path_swigregister = _agg.conv_stroke_path_swigregister
conv_stroke_path_swigregister(conv_stroke_path)

class conv_stroke_transpath(conv_adaptor_vcgen_transpath):
    __swig_setmethods__ = {}
    for _s in [conv_adaptor_vcgen_transpath]: __swig_setmethods__.update(_s.__swig_setmethods__)
    __setattr__ = lambda self, name, value: _swig_setattr(self, conv_stroke_transpath, name, value)
    __swig_getmethods__ = {}
    for _s in [conv_adaptor_vcgen_transpath]: __swig_getmethods__.update(_s.__swig_getmethods__)
    __getattr__ = lambda self, name: _swig_getattr(self, conv_stroke_transpath, name)
    __repr__ = _swig_repr
    def __init__(self, *args): 
        this = _agg.new_conv_stroke_transpath(*args)
        try: self.this.append(this)
        except: self.this = this
    def line_cap(*args): return _agg.conv_stroke_transpath_line_cap(*args)
    def line_join(*args): return _agg.conv_stroke_transpath_line_join(*args)
    def inner_line_join(*args): return _agg.conv_stroke_transpath_inner_line_join(*args)
    def miter_limit_theta(*args): return _agg.conv_stroke_transpath_miter_limit_theta(*args)
    def width(*args): return _agg.conv_stroke_transpath_width(*args)
    def miter_limit(*args): return _agg.conv_stroke_transpath_miter_limit(*args)
    def inner_miter_limit(*args): return _agg.conv_stroke_transpath_inner_miter_limit(*args)
    def approximation_scale(*args): return _agg.conv_stroke_transpath_approximation_scale(*args)
    def shorten(*args): return _agg.conv_stroke_transpath_shorten(*args)
    __swig_destroy__ = _agg.delete_conv_stroke_transpath
    __del__ = lambda self : None;
conv_stroke_transpath_swigregister = _agg.conv_stroke_transpath_swigregister
conv_stroke_transpath_swigregister(conv_stroke_transpath)

class conv_stroke_curve(conv_adaptor_vcgen_curve):
    __swig_setmethods__ = {}
    for _s in [conv_adaptor_vcgen_curve]: __swig_setmethods__.update(_s.__swig_setmethods__)
    __setattr__ = lambda self, name, value: _swig_setattr(self, conv_stroke_curve, name, value)
    __swig_getmethods__ = {}
    for _s in [conv_adaptor_vcgen_curve]: __swig_getmethods__.update(_s.__swig_getmethods__)
    __getattr__ = lambda self, name: _swig_getattr(self, conv_stroke_curve, name)
    __repr__ = _swig_repr
    def __init__(self, *args): 
        this = _agg.new_conv_stroke_curve(*args)
        try: self.this.append(this)
        except: self.this = this
    def line_cap(*args): return _agg.conv_stroke_curve_line_cap(*args)
    def line_join(*args): return _agg.conv_stroke_curve_line_join(*args)
    def inner_line_join(*args): return _agg.conv_stroke_curve_inner_line_join(*args)
    def miter_limit_theta(*args): return _agg.conv_stroke_curve_miter_limit_theta(*args)
    def width(*args): return _agg.conv_stroke_curve_width(*args)
    def miter_limit(*args): return _agg.conv_stroke_curve_miter_limit(*args)
    def inner_miter_limit(*args): return _agg.conv_stroke_curve_inner_miter_limit(*args)
    def approximation_scale(*args): return _agg.conv_stroke_curve_approximation_scale(*args)
    def shorten(*args): return _agg.conv_stroke_curve_shorten(*args)
    __swig_destroy__ = _agg.delete_conv_stroke_curve
    __del__ = lambda self : None;
conv_stroke_curve_swigregister = _agg.conv_stroke_curve_swigregister
conv_stroke_curve_swigregister(conv_stroke_curve)

class conv_stroke_transcurve(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, conv_stroke_transcurve, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, conv_stroke_transcurve, name)
    __repr__ = _swig_repr
    def __init__(self, *args): 
        this = _agg.new_conv_stroke_transcurve(*args)
        try: self.this.append(this)
        except: self.this = this
    def line_cap(*args): return _agg.conv_stroke_transcurve_line_cap(*args)
    def line_join(*args): return _agg.conv_stroke_transcurve_line_join(*args)
    def inner_line_join(*args): return _agg.conv_stroke_transcurve_inner_line_join(*args)
    def miter_limit_theta(*args): return _agg.conv_stroke_transcurve_miter_limit_theta(*args)
    def width(*args): return _agg.conv_stroke_transcurve_width(*args)
    def miter_limit(*args): return _agg.conv_stroke_transcurve_miter_limit(*args)
    def inner_miter_limit(*args): return _agg.conv_stroke_transcurve_inner_miter_limit(*args)
    def approximation_scale(*args): return _agg.conv_stroke_transcurve_approximation_scale(*args)
    def shorten(*args): return _agg.conv_stroke_transcurve_shorten(*args)
    __swig_destroy__ = _agg.delete_conv_stroke_transcurve
    __del__ = lambda self : None;
conv_stroke_transcurve_swigregister = _agg.conv_stroke_transcurve_swigregister
conv_stroke_transcurve_swigregister(conv_stroke_transcurve)

class conv_stroke_curvetrans(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, conv_stroke_curvetrans, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, conv_stroke_curvetrans, name)
    __repr__ = _swig_repr
    def __init__(self, *args): 
        this = _agg.new_conv_stroke_curvetrans(*args)
        try: self.this.append(this)
        except: self.this = this
    def line_cap(*args): return _agg.conv_stroke_curvetrans_line_cap(*args)
    def line_join(*args): return _agg.conv_stroke_curvetrans_line_join(*args)
    def inner_line_join(*args): return _agg.conv_stroke_curvetrans_inner_line_join(*args)
    def miter_limit_theta(*args): return _agg.conv_stroke_curvetrans_miter_limit_theta(*args)
    def width(*args): return _agg.conv_stroke_curvetrans_width(*args)
    def miter_limit(*args): return _agg.conv_stroke_curvetrans_miter_limit(*args)
    def inner_miter_limit(*args): return _agg.conv_stroke_curvetrans_inner_miter_limit(*args)
    def approximation_scale(*args): return _agg.conv_stroke_curvetrans_approximation_scale(*args)
    def shorten(*args): return _agg.conv_stroke_curvetrans_shorten(*args)
    __swig_destroy__ = _agg.delete_conv_stroke_curvetrans
    __del__ = lambda self : None;
conv_stroke_curvetrans_swigregister = _agg.conv_stroke_curvetrans_swigregister
conv_stroke_curvetrans_swigregister(conv_stroke_curvetrans)

class rasterizer_scanline_aa(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, rasterizer_scanline_aa, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, rasterizer_scanline_aa, name)
    __repr__ = _swig_repr
    def __init__(self, *args): 
        this = _agg.new_rasterizer_scanline_aa(*args)
        try: self.this.append(this)
        except: self.this = this
    def reset(*args): return _agg.rasterizer_scanline_aa_reset(*args)
    def filling_rule(*args): return _agg.rasterizer_scanline_aa_filling_rule(*args)
    def clip_box(*args): return _agg.rasterizer_scanline_aa_clip_box(*args)
    def reset_clipping(*args): return _agg.rasterizer_scanline_aa_reset_clipping(*args)
    def apply_gamma(*args): return _agg.rasterizer_scanline_aa_apply_gamma(*args)
    def add_vertex(*args): return _agg.rasterizer_scanline_aa_add_vertex(*args)
    def move_to(*args): return _agg.rasterizer_scanline_aa_move_to(*args)
    def line_to(*args): return _agg.rasterizer_scanline_aa_line_to(*args)
    def close_polygon(*args): return _agg.rasterizer_scanline_aa_close_polygon(*args)
    def move_to_d(*args): return _agg.rasterizer_scanline_aa_move_to_d(*args)
    def line_to_d(*args): return _agg.rasterizer_scanline_aa_line_to_d(*args)
    def min_x(*args): return _agg.rasterizer_scanline_aa_min_x(*args)
    def min_y(*args): return _agg.rasterizer_scanline_aa_min_y(*args)
    def max_x(*args): return _agg.rasterizer_scanline_aa_max_x(*args)
    def max_y(*args): return _agg.rasterizer_scanline_aa_max_y(*args)
    def calculate_alpha(*args): return _agg.rasterizer_scanline_aa_calculate_alpha(*args)
    def sort(*args): return _agg.rasterizer_scanline_aa_sort(*args)
    def rewind_scanlines(*args): return _agg.rasterizer_scanline_aa_rewind_scanlines(*args)
    def hit_test(*args): return _agg.rasterizer_scanline_aa_hit_test(*args)
    def add_path(*args): return _agg.rasterizer_scanline_aa_add_path(*args)
    __swig_destroy__ = _agg.delete_rasterizer_scanline_aa
    __del__ = lambda self : None;
rasterizer_scanline_aa_swigregister = _agg.rasterizer_scanline_aa_swigregister
rasterizer_scanline_aa_swigregister(rasterizer_scanline_aa)

class renderer_scanline_aa_solid_rgba(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, renderer_scanline_aa_solid_rgba, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, renderer_scanline_aa_solid_rgba, name)
    __repr__ = _swig_repr
    def __init__(self, *args): 
        this = _agg.new_renderer_scanline_aa_solid_rgba(*args)
        try: self.this.append(this)
        except: self.this = this
    def attach(*args): return _agg.renderer_scanline_aa_solid_rgba_attach(*args)
    def color(*args): return _agg.renderer_scanline_aa_solid_rgba_color(*args)
    def prepare(*args): return _agg.renderer_scanline_aa_solid_rgba_prepare(*args)
    def color_rgba8(*args): return _agg.renderer_scanline_aa_solid_rgba_color_rgba8(*args)
    def color_rgba(*args): return _agg.renderer_scanline_aa_solid_rgba_color_rgba(*args)
    __swig_destroy__ = _agg.delete_renderer_scanline_aa_solid_rgba
    __del__ = lambda self : None;
renderer_scanline_aa_solid_rgba_swigregister = _agg.renderer_scanline_aa_solid_rgba_swigregister
renderer_scanline_aa_solid_rgba_swigregister(renderer_scanline_aa_solid_rgba)

class renderer_scanline_bin_solid_rgba(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, renderer_scanline_bin_solid_rgba, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, renderer_scanline_bin_solid_rgba, name)
    __repr__ = _swig_repr
    def __init__(self, *args): 
        this = _agg.new_renderer_scanline_bin_solid_rgba(*args)
        try: self.this.append(this)
        except: self.this = this
    def attach(*args): return _agg.renderer_scanline_bin_solid_rgba_attach(*args)
    def color(*args): return _agg.renderer_scanline_bin_solid_rgba_color(*args)
    def prepare(*args): return _agg.renderer_scanline_bin_solid_rgba_prepare(*args)
    def color_rgba8(*args): return _agg.renderer_scanline_bin_solid_rgba_color_rgba8(*args)
    def color_rgba(*args): return _agg.renderer_scanline_bin_solid_rgba_color_rgba(*args)
    __swig_destroy__ = _agg.delete_renderer_scanline_bin_solid_rgba
    __del__ = lambda self : None;
renderer_scanline_bin_solid_rgba_swigregister = _agg.renderer_scanline_bin_solid_rgba_swigregister
renderer_scanline_bin_solid_rgba_swigregister(renderer_scanline_bin_solid_rgba)

class scanline_p8(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, scanline_p8, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, scanline_p8, name)
    __repr__ = _swig_repr
    __swig_destroy__ = _agg.delete_scanline_p8
    __del__ = lambda self : None;
    def __init__(self, *args): 
        this = _agg.new_scanline_p8(*args)
        try: self.this.append(this)
        except: self.this = this
    def reset(*args): return _agg.scanline_p8_reset(*args)
    def add_cell(*args): return _agg.scanline_p8_add_cell(*args)
    def add_cells(*args): return _agg.scanline_p8_add_cells(*args)
    def add_span(*args): return _agg.scanline_p8_add_span(*args)
    def finalize(*args): return _agg.scanline_p8_finalize(*args)
    def reset_spans(*args): return _agg.scanline_p8_reset_spans(*args)
    def y(*args): return _agg.scanline_p8_y(*args)
    def num_spans(*args): return _agg.scanline_p8_num_spans(*args)
    def begin(*args): return _agg.scanline_p8_begin(*args)
scanline_p8_swigregister = _agg.scanline_p8_swigregister
scanline_p8_swigregister(scanline_p8)

class scanline_bin(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, scanline_bin, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, scanline_bin, name)
    __repr__ = _swig_repr
    __swig_destroy__ = _agg.delete_scanline_bin
    __del__ = lambda self : None;
    def __init__(self, *args): 
        this = _agg.new_scanline_bin(*args)
        try: self.this.append(this)
        except: self.this = this
    def reset(*args): return _agg.scanline_bin_reset(*args)
    def add_cell(*args): return _agg.scanline_bin_add_cell(*args)
    def add_span(*args): return _agg.scanline_bin_add_span(*args)
    def add_cells(*args): return _agg.scanline_bin_add_cells(*args)
    def finalize(*args): return _agg.scanline_bin_finalize(*args)
    def reset_spans(*args): return _agg.scanline_bin_reset_spans(*args)
    def y(*args): return _agg.scanline_bin_y(*args)
    def num_spans(*args): return _agg.scanline_bin_num_spans(*args)
scanline_bin_swigregister = _agg.scanline_bin_swigregister
scanline_bin_swigregister(scanline_bin)

class scanline32_bin(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, scanline32_bin, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, scanline32_bin, name)
    __repr__ = _swig_repr
    __swig_destroy__ = _agg.delete_scanline32_bin
    __del__ = lambda self : None;
    def __init__(self, *args): 
        this = _agg.new_scanline32_bin(*args)
        try: self.this.append(this)
        except: self.this = this
    def reset(*args): return _agg.scanline32_bin_reset(*args)
    def add_cell(*args): return _agg.scanline32_bin_add_cell(*args)
    def add_span(*args): return _agg.scanline32_bin_add_span(*args)
    def add_cells(*args): return _agg.scanline32_bin_add_cells(*args)
    def finalize(*args): return _agg.scanline32_bin_finalize(*args)
    def reset_spans(*args): return _agg.scanline32_bin_reset_spans(*args)
    def y(*args): return _agg.scanline32_bin_y(*args)
    def num_spans(*args): return _agg.scanline32_bin_num_spans(*args)
scanline32_bin_swigregister = _agg.scanline32_bin_swigregister
scanline32_bin_swigregister(scanline32_bin)

render_scanlines_rgba = _agg.render_scanlines_rgba


