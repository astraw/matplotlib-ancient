# working directly with renderer and graphics contexts primitives
from matplotlib.font_manager import FontProperties
from matplotlib.backends.backend_agg import RendererAgg
from matplotlib.transforms import Value

# a 400x400 canvas at 72dpi canvas
dpi = Value(72.0)
o = RendererAgg(400,400, dpi)  

# the graphics context 
gc = o.new_gc()

# draw the background white
gc.set_foreground('w')
face = (1,1,1)  # white
o.draw_rectangle(gc, face, 0, 0, 400, 400)

# the gc's know about color strings, and can handle any matplotlib
# color arguments (hex strings, rgb, format strings, etc)
gc.set_foreground('g')
gc.set_linewidth(4)
face = (1,0,0)  # must be rgb
o.draw_rectangle(gc, face, 10, 50, 100, 200)

# draw a translucent ellipse
rgb = (0,0,1)
gc.set_alpha(0.5)
o.draw_arc(gc, rgb,  100, 100, 100, 100, 360, 360)

# draw a dashed line
gc.set_dashes(0, [5, 10])
gc.set_joinstyle('miter')
gc.set_capstyle('butt')
gc.set_linewidth(3.0)
o.draw_lines( gc, (50, 100, 150, 200, 250), (400, 100, 300, 200, 250))

# draw some text using the matplotlib font manager
prop = FontProperties(size=40)
gc.set_foreground('b')
o.draw_text( gc, 100, 300, "That's all folks!", prop, -45, 0)

# there is no standard renderer interface to save the input to a file,
# as this is the job of the figure canvas.  Here I make the call that
# the figure canvas would make for the antigrain render
o._renderer.write_png('renderer_agg.png')
