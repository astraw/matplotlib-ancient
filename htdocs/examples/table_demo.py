
import matplotlib
#matplotlib.use('PS')
#import matplotlib.backends.backend_ps as backend_ps
#backend_ps.defaultPaperSize = 11,8.5

from RandomArray import exponential
from Numeric import sum

from matplotlib.matlab import *
from matplotlib.table import Table
from matplotlib.cell import Cell
from matplotlib.backend_bases import arg_to_rgb

axes([0.2, 0.3, 0.6, 0.5])
means = {
    'Quake': 1e6,
    'Wind':  7e5,
    'Flood': 5e5,
    'Freeze': 4e5,
    'Hail': 3e5,
    }
perils = means.keys()
perils.sort()

my_colours=(
    [0,0,1],
    [.5,0,1],
    [1,0,1],
    [1,0,.5],
    [1,0,0])

def fix_colours(colours):
    results = []
    for colour in colours:
        results.append(pastel(colour))
    return results


def pastel(colour):
    """ Convert colour into a nice pastel shade"""
    weight = 2.4
    rgb = asarray(arg_to_rgb(colour))
    # scale colour 
    maxc = max(rgb)
    if maxc < 1.0 and maxc > 0:
        # scale colour
        scale = 1.0 / maxc
        rgb = rgb * scale
    # now decrease saturation
    total = sum(rgb)
    slack = 0
    for x in rgb:
        slack += 1.0 - x

    # want to increase weight from total to weight
    # pick x s.t.  slack * x == weight - total
    # x = (weight - total) / slack
    x = (weight - total) / slack

    rgb = [c + (x * (1.0-c)) for c in rgb]

    return rgb

my_colours = fix_colours(my_colours)

rows = len(my_colours)
plot_data = {}
for peril in perils:
    data = exponential(means[peril], rows)
    data = sort(data)
    plot_data[peril] = data

N = len(perils)
yoff = array([0.0] * N)
ind = arange(N)  # the x locations for the groups
ind = ind + .3
width = 0.4     # the width of the bars

labels = []
colours = []

# add the data to the plot
for row in xrange(rows):

    data = [plot_data[peril][row] for peril in perils]
    data = data - yoff
    patches = bar(ind, data, width, bottom=yoff, color=my_colours[row])
    yoff = data + yoff
    labels.append(['%d' % (val / 1000,) for val in yoff])
    colours.append(patches[0].get_facecolor())

labels.append(perils)
colours.reverse()
set(gca(), 'xticks', [])
set(gca(), 'yticklabels', [])
table = Table(gca(), loc='bottom')
labels.reverse()
width = 1.0 / N
height = table._approx_text_height()
loc='center'
pastels = colours

# add the table
for row, pastel in zip(range(len(labels)), ['w'] + pastels):
    for col in xrange(N):
        table.add_cell(row, col, width, height, text=labels[row][col],
                       loc=loc, facecolor=pastel)
    loc='right'

# add row labels to the table
row_labels = []
for x in range(rows):
    row_labels.append('%d year' % ((rows / (1.0 + x)) + 0.5,))

for colour, pastel, label, row in zip(colours, pastels,
                                      row_labels, range(len(labels))):
    table.add_cell(row+1, -1, width, height,
                   text=label, loc='left',
                   facecolor=pastel)

# set row label width auto-magically
table.auto_set_column_width(-1)
gca().add_table(table)

savefig('table2')
show()
