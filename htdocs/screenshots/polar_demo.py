#!/usr/bin/env python
from matplotlib.matlab import *

# radar green, solid grid lines
rc('grid', color='#316931', linewidth=1, linestyle='-')
rc('tick', labelsize=15)
# force square figure and square axes looks better for polar, IMO
figure(figsize=(8,8))
ax = axes([0.1, 0.1, 0.8, 0.8], polar=True, axisbg='#d5de9c')

r = arange(0,1,0.001)
theta = 2*2*pi*r
polar(theta, r, color='#ee8d18', lw=3)
set(ax.thetagridlabels, y=1.075) # the radius of the grid labels

title("And there was much rejoicing!", fontsize=20)
#savefig('polar_demo')
show()
