"""
Cartographic mapping - Thanks to Jeff Whitaker <jswhit@fastmail.fm>
for this example.  Requires data files and modules provided by
http://whitaker.homeunix.org/~jeff/plotmap.tar.gz, which in turn
require the proj library from http://www.remotesensing.org/proj/
"""
from matplotlib.matlab import *
from matplotlib.collections import LineCollection 
from proj import Proj
import numarray, cPickle
from numarray import nd_image

# example to demonstrate plotting data on a map projection.
# requires numarray, proj module (which in turn requires 
# proj command from http://proj.maptools.org)

# set up map projection parameters (lambert conformal conic,
# standard parallels at 50 deg N, center longitued 107 deg W.
params = {}
params['proj'] = 'lcc'
params['R'] = 63712000
params['lat_1'] = 50
params['lat_2'] = 50
params['lon_0'] = -107
proj = Proj(params)
llcornerx, llcornery = proj(-145.5,1.)
xmax=11297266.68; ymax=8959901.16
params['x_0'] = -llcornerx # add cartesian offset so lower left corner = (0,0)
params['y_0'] = -llcornery
# create a Proj instance for desired map.
proj = Proj(params)

# define grid (nx x ny regularly spaced native projection grid)
nx = 349; ny = 277                                                              
dx = xmax/(nx-1); dy = ymax/(ny-1)
xgrid = dx*numarray.indices((ny,nx))[1,:,:]
ygrid = dy*numarray.indices((ny,nx))[0,:,:]
# compute lons, lats of regular projection grid.
lonout, latout = proj(xgrid, ygrid, inverse=True)
# make sure lons are between 0 and 360
lonout = numarray.where(lonout < 0, lonout+360, lonout)
# make lat into colat (monotonically increasing from 0 at S Pole
# to 180 at N Pole).
latout = latout+90

# read in topo data from pickle (on a regular lat/lon grid)
topodict = cPickle.load(file('data/etopo20.pickle','rb'))        
lons = topodict['lons']
lats = topodict['lats']
topoin = topodict['topo']

# find coordinates of native projection grid.
xcoords = (len(lons)-1)*(lonout-lons[0])/(lons[-1]-lons[0])
ycoords = (len(lats)-1)*(latout-lats[0])/(lats[-1]-lats[0])
coords = [ycoords,xcoords]
# interpolate to projection grid using numarray.nd_image spline filter.
topodat = numarray.nd_image.map_coordinates(topoin,coords,mode='nearest')

ax = subplot(111)                                          
# use imshow rather than pcolor for speed                                       
# set the default params for imshow                                             
rc('image', origin='lower', cmap='jet')   
im = ax.imshow(topodat, interpolation='nearest',extent=(0, xmax, 0, ymax))     
#pcolor(xgrid, ygrid, topodat, shading='flat')

# read in coastline data from pickle.
wcl = cPickle.load(file('data/wcl.pickle','rb'))
ind = wcl['segment_index']; lons = wcl['lons']; lats = wcl['lats']
# transform coastline segements to map projection coordinates.                  
xs, ys = proj(lons,lats)
# a sequence of xy tuples                                                   
segments = [zip(xs[i0:i1], ys[i0:i1]) for i0, i1 in zip(ind[:-1], ind[1:])]    

# line collection
collection = LineCollection(                                                    
    segments,                                                                   
    colors       = ( (0,0,0,1), ), # black                                      
    linewidths   = (1.5,),                                                      
    antialiaseds = (1,),)  # turn off aa for speed                              

ax.add_collection(collection)                                                   
corners = (min(xs), min(ys)), (max(xs), max(ys))                                
ax.update_datalim( corners )                                                    
axis([0, xmax, 0, ymax])                                                        
ax.set_xticks([]) # no ticks                                                    
ax.set_yticks([])                                                               
title('20-minute Topography: Lambert Conformal Conic Projection') 

savefig('plotmap_small', dpi=60)
savefig('plotmap_large', dpi=123)
show()                  
