# using the matplotlib API - look, maw, no matlab!
from matplotlib.backends.backend_svg import FigureCanvasSVG
from matplotlib.figure import Figure
fig = Figure()
ax = fig.add_subplot(211)
ax.plot([1,2,3])
canvas = FigureCanvasSVG(fig)
canvas.print_figure('myfile.svg')
