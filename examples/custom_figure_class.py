"""
You can pass a custom Figure constructor to figure if youy want to derive from the default Figure.  This simple example creates a figure with a figure title
"""
from pylab import figure, show, nx
from matplotlib.figure import Figure

class MyFigure(Figure):
    def __init__(self, *args, **kwargs):
        """
        custom kwarg figtitle is a figure title
        """
        figtitle = kwargs.pop('figtitle', 'hi mom')
        Figure.__init__(self, *args, **kwargs)
        self.text(0.5, 0.95, figtitle, ha='center')

fig = figure(FigureClass=MyFigure, figtitle='my title')
ax = fig.add_subplot(111)
ax.plot([1,2,3])
fig.savefig('test.png')
fig.savefig('test.ps')
show()
            
