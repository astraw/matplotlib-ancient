import matplotlib
matplotlib.use('GD')
from matplotlib.backends.backend_gd import Figure, show
from matplotlib.axes import Subplot

dpi = 100
figsize = (5, 5)
f = Figure(figsize, dpi)
a = Subplot(f, 111)
f.add_axis(a)
l = a.plot([1,2,3], [4,5,6])

a.set_xlabel('time (s)')
a.set_ylabel('Signal 2')
f.print_figure('gdtest', dpi)
show()

