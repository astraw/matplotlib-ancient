"""
A pure object oriented example using the agg backend
"""
# import the matplotlib backend you want to use and the Figure class
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

# the figure is the center of the action, and the canvas is a backend
# dependent container to hold the figure and make backend specific calls
fig = Figure()
canvas = FigureCanvas(fig)

# you can add multiple subplots and axes
ax = fig.add_subplot(111)

# the simplest plot!
ax.plot([1,2,3])

# you can decorate your plot with text and grids
ax.set_title('hi mom')
ax.grid(True)
ax.set_xlabel('time')
ax.set_ylabel('volts')

# and save it to hardcopy
fig.savefig('../fig/mpl_one_two_three.png')
