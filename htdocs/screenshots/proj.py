import os, array, numarray, math, tempfile

_rad2dg = 180./math.pi
_dg2rad = math.pi/180.

class Proj:
    """
 peforms cartographic transformations (converts from longitude,latitude
 to native map projection x,y coordinates and vice versa) using proj 
 (http://www.remotesensing.org/proj/).
 
 __init__ method sets up projection information.
 __call__ method compute transformations.
 See docstrings for __init__ and __call__ for details.

 Jeff Whitaker <jeffrey.s.whitaker@noaa.gov>
 20040711
    """

    def __init__(self,params,projcmd='proj'):
        """
 initialize a Proj class instance.

 Input 'params' is a dictionary containing proj map
 projection control parameter key/value pairs.
 See the proj documentation (http://www.remotesensing.org/proj/)
 for details.

 Optional keyword 'projcmd' is the full path to the proj exectuable.
 Default will work if proj is in the unix PATH.
        """
        # make sure proj parameter specified.
	# (no other checking done in proj parameters)
        if 'proj' not in params.keys():
            raise KeyError, "need to specify proj parameter"
        # build proj command.
        for key,value in map(None,params.keys(),params.values()):
            if key == 'x_0' or key == 'y_0':
                value=10*value # convert false easting, northing to cm.
            projcmd = projcmd + " +"+key+"="+str(value)
	self.projcmd = projcmd + ' -b'

    def __call__(self,lon,lat,inverse=False):
        """
 Calling a Proj class instance with the arguments lon, lat will
 convert lon/lat (in degrees) to x/y native map projection 
 coordinates (in meters).  If optional keyword 'inverse' is
 True (default is False), the inverse transformation from x/y
 to lon/lat is performed.

 Example usage:
 >>> from proj import Proj
 >>> params = {}
 >>> params['proj'] = 'lcc' # lambert conformal conic
 >>> params['lat_1'] = 30.  # standard parallel 1
 >>> params['lat_2'] = 50.  # standard parallel 2
 >>> params['lon_0'] = -96  # central meridian
 >>> map = Proj(params)
 >>> x,y = map(-107,40)     # find x,y coords of lon=-107,lat=40
 >>> print x,y
 -92272.1004461 477477.890988


 lon,lat can be either scalar floats or numarray arrays.
        """
	npts = 1
        # if inputs are numarray arrays, get shape and total number of pts.
	try:
	    shapein = lon.shape
	    npts = reduce(lambda x, y: x*y, shapein)
	    lontypein = lon.typecode()
	    lattypein = lat.typecode()
	except:
            shapein = False
        # make sure inputs have same shape.
	if shapein and lat.shape != shapein:
            raise ValueError, 'lon, lat must be scalars or numarray arrays with the same shape'
        # make a rank 1 array with x/y (or lon/lat) pairs.
        xy = numarray.zeros(2*npts,'d')
        xy[::2] = numarray.ravel(lon)
        xy[1::2] = numarray.ravel(lat)
        # convert degrees to radians, meters to cm.
	if not inverse:
           xy = _dg2rad*xy
        else:
           xy = 10.*xy
        # write input data to binary file.
        xyout = array.array('d')
        xyout.fromlist(xy.tolist())
	# set up cmd string, scale factor for output.
	if inverse:
            cmd = self.projcmd+' -I'
	    scale = _rad2dg
        else:
            cmd = self.projcmd
	    scale = 0.1
	# use pipes for input and output if amount of 
	# data less than default buffer size (usually 8192).
	# otherwise use pipe for input, tempfile for output
	if 2*npts*8 > 8192:
            fd, fn=tempfile.mkstemp(); os.close(fd); stdout=open(fn,'rb')
            cmd = cmd+' > '+fn
            stdin=os.popen(cmd,'w')
	    xyout.tofile(stdin)
	    stdin.close()
            outxy = scale*numarray.fromstring(stdout.read(),'d')
	    stdout.close()
	    os.remove(fn)
        else:
            stdin,stdout=os.popen2(cmd,mode='b')
	    xyout.tofile(stdin)
	    stdin.close()
            outxy = scale*numarray.fromstring(stdout.read(),'d')
	    stdout.close()
        # return numarray arrays or scalars, depending on type of input.
	if shapein:
            outx = numarray.reshape(outxy[::2],shapein).astype(lontypein)
            outy = numarray.reshape(outxy[1::2],shapein).astype(lattypein)
        else:
            outx = outxy[0]; outy = outxy[1]
        return outx,outy

if __name__ == "__main__":
    params = {}
    params['proj'] = 'lcc'
    params['R'] = 63712000
    params['lat_1'] = 50
    params['lat_2'] = 50
    params['lon_0'] = -107
    awips221 = Proj(params)
# AWIPS grid 221 parameters
# (from http://www.nco.ncep.noaa.gov/pmb/docs/on388/tableb.html)
    nx = 349; ny = 277; dx = 32463.41; dy = dx
    llcornerx, llcornery = awips221(-145.5,1.)
    params['x_0'] = -llcornerx # add cartesian offset so llcorner = (0,0)
    params['y_0'] = -llcornery
    awips221 = Proj(params)
# find 4 lon/lat corners of AWIPS grid 221.
    llcornerx = 0.; llcornery = 0.
    lrcornerx = dx*(nx-1); lrcornery = 0.
    ulcornerx = 0.,; ulcornery = dy*(ny-1)
    urcornerx = dx*(nx-1); urcornery = dy*(ny-1)
    llcornerlon, llcornerlat = awips221(llcornerx, llcornery, inverse=True)
    lrcornerlon, lrcornerlat = awips221(lrcornerx, lrcornery, inverse=True)
    urcornerlon, urcornerlat = awips221(urcornerx, urcornery, inverse=True)
    ulcornerlon, ulcornerlat = awips221(ulcornerx, ulcornery, inverse=True)
    print '4 corners of AWIPS grid 221:'
    print llcornerlon, llcornerlat
    print lrcornerlon, lrcornerlat
    print urcornerlon, urcornerlat
    print ulcornerlon, ulcornerlat
    print 'from GRIB docs'
    print '(see http://www.nco.ncep.noaa.gov/pmb/docs/on388/tableb.html)'
    print '   -145.5  1.0'
    print '   -68.318 0.897'
    print '   -2.566 46.352'
    print '   148.639 46.635'
# compute lons and lats for the whole AWIPS grid 221 (377x249).
    x = numarray.zeros((nx,ny),'d')
    y = numarray.zeros((nx,ny),'d')
    x = dx*numarray.indices(x.shape)[0,:,:]
    y = dy*numarray.indices(y.shape)[1,:,:]
    import time; t1 = time.clock()
    lons, lats = awips221(x, y, inverse=True)
    t2 = time.clock()
    print 'compute lats/lons for all points on AWIPS 221 grid (%sx%s)' %(nx,ny)
    print 'max/min lons'
    print min(numarray.ravel(lons)),max(numarray.ravel(lons))
    print 'max/min lats'
    print min(numarray.ravel(lats)),max(numarray.ravel(lats))
    print 'took',t2-t1,'secs'
