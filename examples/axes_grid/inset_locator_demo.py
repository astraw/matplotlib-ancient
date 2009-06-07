import matplotlib.pyplot as plt

from mpl_toolkits.axes_grid.inset_locator import inset_axes, zoomed_inset_axes
from mpl_toolkits.axes_grid.anchored_artists import AnchoredSizeBar


def add_sizebar(ax, size):
   asb =  AnchoredSizeBar(ax.transData,
                         size,
                         str(size),
                         loc=8,
                         pad=0.1, borderpad=0.5, sep=5,
                         frameon=False)
   ax.add_artist(asb)


fig = plt.figure(1, [5.5, 3])

# first subplot
ax = fig.add_subplot(1,2,1)
ax.set_aspect(1.)

axins = inset_axes(ax,
                   width="30%", # width = 30% of parent_bbox
                   height=1., # height : 1 inch
                   loc=3)

plt.xticks(visible=False)
plt.yticks(visible=False)


# second subplot
ax = fig.add_subplot(1,2,2)
ax.set_aspect(1.)

axins = zoomed_inset_axes(ax, 0.5, loc=1) # zoom = 0.5

plt.xticks(visible=False)
plt.yticks(visible=False)

add_sizebar(ax, 0.5)
add_sizebar(axins, 0.5)

plt.draw()
plt.show()
