
class Artist:
    "Abstract base class for someone who renders into a Figure"
    def __init__(self):
        self._drawingArea = None
        self._drawable = None

    def clip_gc(self, gc):
        "The gc clipping function; no clip by default"        
        pass

    def get_child_artists(self):
        'Return all artists contained in self'
        return []


    def get_window_extent(self):
        """
        Return the bounding box as left, bottom, width, height in
        window coords
        """
        l, b, w, h = self.get_data_extent()
        w, h = self.transform_scale_to_win(w, h)
        l, b = self.transform_points_to_win(l, b)
        return l, b, w, h
        

    def get_data_extent(self):
        """
        Return the bounding box as left, bottom, width, height in
        data coords of the area
        """
        raise NotImplementedError, "Derived must override"

    def transform_points_to_win(self, x, y):
        "Transform the points x, y to window coords. Default is do nothing"
        return x, y

    def transform_scale_to_win(self, xscale, yscale):
        "Transform the xscale, yscale to window coords. Default is do nothing"
        return xscale, yscale

    def draw(self, drawable=None, *args, **kwargs):
        'Derived classes drawing method'
        if drawable is None: drawable = self._drawable
        if drawable is None: return
        self._draw(drawable, *args, **kwargs)

    def _draw(self, drawable, *args, **kwargs):
        'Derived classes drawing method'
        raise NotImplementedError, 'Derived must override'

    def set_drawing_area(self, da):
        'Set the drawing area that you render into'
        self._drawingArea = da
        self._drawable = da.window
        for artist in self.get_child_artists():
            artist.set_drawing_area(da)

    def wash_brushes(self):
        'Erase any state vars that would impair a draw to a clean palette'

        for artist in self.get_child_artists():
            artist.wash_brushes()

            
