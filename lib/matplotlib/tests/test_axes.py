import numpy as np
import matplotlib
from matplotlib.testing.decorators import image_comparison, knownfailureif
import matplotlib.pyplot as plt


@image_comparison(baseline_images=['formatter_ticker_001',
                                   'formatter_ticker_002',
                                   'formatter_ticker_003',
                                   'formatter_ticker_004',
                                   'formatter_ticker_005',
                                   ])
def test_formatter_ticker():
    import matplotlib.testing.jpl_units as units
    units.register()

    # This essentially test to see if user specified labels get overwritten
    # by the auto labeler functionality of the axes.
    xdata = [ x*units.sec for x in range(10) ]
    ydata1 = [ (1.5*y - 0.5)*units.km for y in range(10) ]
    ydata2 = [ (1.75*y - 1.0)*units.km for y in range(10) ]

    fig = plt.figure()
    ax = plt.subplot( 111 )
    ax.set_xlabel( "x-label 001" )
    fig.savefig( 'formatter_ticker_001' )

    ax.plot( xdata, ydata1, color='blue', xunits="sec" )
    fig.savefig( 'formatter_ticker_002' )

    ax.set_xlabel( "x-label 003" )
    fig.savefig( 'formatter_ticker_003' )

    ax.plot( xdata, ydata2, color='green', xunits="hour" )
    ax.set_xlabel( "x-label 004" )
    fig.savefig( 'formatter_ticker_004' )

    # See SF bug 2846058
    # https://sourceforge.net/tracker/?func=detail&aid=2846058&group_id=80706&atid=560720
    ax.set_xlabel( "x-label 005" )
    ax.autoscale_view()
    fig.savefig( 'formatter_ticker_005' )

@image_comparison(baseline_images=['offset_points'])
def test_basic_annotate():
    # Setup some data
    t = np.arange( 0.0, 5.0, 0.01 )
    s = np.cos( 2.0*np.pi * t )

    # Offset Points

    fig = plt.figure()
    ax = fig.add_subplot( 111, autoscale_on=False, xlim=(-1,5), ylim=(-3,5) )
    line, = ax.plot( t, s, lw=3, color='purple' )

    ax.annotate( 'local max', xy=(3, 1), xycoords='data',
                 xytext=(3, 3), textcoords='offset points' )

    fig.savefig( 'offset_points' )

@image_comparison(baseline_images=['polar_axes'])
def test_polar_annotations():
    # you can specify the xypoint and the xytext in different
    # positions and coordinate systems, and optionally turn on a
    # connecting line and mark the point with a marker.  Annotations
    # work on polar axes too.  In the example below, the xy point is
    # in native coordinates (xycoords defaults to 'data').  For a
    # polar axes, this is in (theta, radius) space.  The text in this
    # example is placed in the fractional figure coordinate system.
    # Text keyword args like horizontal and vertical alignment are
    # respected

    # Setup some data
    r = np.arange(0.0, 1.0, 0.001 )
    theta = 2.0 * 2.0 * np.pi * r

    fig = plt.figure()
    ax = fig.add_subplot( 111, polar=True )
    line, = ax.plot( theta, r, color='#ee8d18', lw=3 )

    ind = 800
    thisr, thistheta = r[ind], theta[ind]
    ax.plot([thistheta], [thisr], 'o')
    ax.annotate('a polar annotation',
                xy=(thistheta, thisr),  # theta, radius
                xytext=(0.05, 0.05),    # fraction, fraction
                textcoords='figure fraction',
                arrowprops=dict(facecolor='black', shrink=0.05),
                horizontalalignment='left',
                verticalalignment='bottom',
                )

    fig.savefig( 'polar_axes' )

   #--------------------------------------------------------------------
@image_comparison(baseline_images=['polar_coords'])
def test_polar_coord_annotations():
    # You can also use polar notation on a catesian axes.  Here the
    # native coordinate system ('data') is cartesian, so you need to
    # specify the xycoords and textcoords as 'polar' if you want to
    # use (theta, radius)
    from matplotlib.patches import Ellipse
    el = Ellipse((0,0), 10, 20, facecolor='r', alpha=0.5)

    fig = plt.figure()
    ax = fig.add_subplot( 111, aspect='equal' )

    ax.add_artist( el )
    el.set_clip_box( ax.bbox )

    ax.annotate('the top',
                xy=(np.pi/2., 10.),      # theta, radius
                xytext=(np.pi/3, 20.),   # theta, radius
                xycoords='polar',
                textcoords='polar',
                arrowprops=dict(facecolor='black', shrink=0.05),
                horizontalalignment='left',
                verticalalignment='bottom',
                clip_on=True, # clip to the axes bounding box
                )

    ax.set_xlim( -20, 20 )
    ax.set_ylim( -20, 20 )
    fig.savefig( 'polar_coords' )

@image_comparison(baseline_images=['fill_units'])
def test_fill_units():
    from datetime import datetime
    import matplotlib.testing.jpl_units as units
    units.register()

    # generate some data
    t = units.Epoch( "ET", dt=datetime(2009, 4, 27) )
    value = 10.0 * units.deg
    day = units.Duration( "ET", 24.0 * 60.0 * 60.0 )

    fig = plt.figure()

    # Top-Left
    ax1 = fig.add_subplot( 221 )
    ax1.plot( [t], [value], yunits='deg', color='red' )
    ax1.fill( [733525.0, 733525.0, 733526.0, 733526.0],
              [0.0, 0.0, 90.0, 0.0], 'b' )

    # Top-Right
    ax2 = fig.add_subplot( 222 )
    ax2.plot( [t], [value], yunits='deg', color='red' )
    ax2.fill( [t,      t,      t+day,     t+day],
              [0.0,  0.0,  90.0,    0.0], 'b' )

    # Bottom-Left
    ax3 = fig.add_subplot( 223 )
    ax3.plot( [t], [value], yunits='deg', color='red' )
    ax1.fill( [733525.0, 733525.0, 733526.0, 733526.0],
              [0*units.deg,  0*units.deg,  90*units.deg,    0*units.deg], 'b' )

    # Bottom-Right
    ax4 = fig.add_subplot( 224 )
    ax4.plot( [t], [value], yunits='deg', color='red' )
    ax4.fill( [t,      t,      t+day,     t+day],
              [0*units.deg,  0*units.deg,  90*units.deg,    0*units.deg],
              facecolor="blue" )

    fig.autofmt_xdate()
    fig.savefig( 'fill_units' )

@image_comparison(baseline_images=['single_point'])
def test_single_point():
    fig = plt.figure()
    plt.subplot( 211 )
    plt.plot( [0], [0], 'o' )

    plt.subplot( 212 )
    plt.plot( [1], [1], 'o' )

    fig.savefig( 'single_point' )

@image_comparison(baseline_images=['single_date'])
def test_single_date():
    time1=[ 721964.0 ]
    data1=[ -65.54 ]

    fig = plt.figure()
    plt.subplot( 211 )
    plt.plot_date( time1, data1, 'o', color='r' )

    plt.subplot( 212 )
    plt.plot( time1, data1, 'o', color='r' )

    fig.savefig( 'single_date' )

@image_comparison(baseline_images=['single_date'])
def test_shaped_data():
    xdata = np.array([[ 0.53295185,  0.23052951,  0.19057629,  0.66724975,  0.96577916,
                        0.73136095,  0.60823287,  0.017921  ,  0.29744742,  0.27164665],
                      [ 0.2798012 ,  0.25814229,  0.02818193,  0.12966456,  0.57446277,
                        0.58167607,  0.71028245,  0.69112737,  0.89923072,  0.99072476],
                      [ 0.81218578,  0.80464528,  0.76071809,  0.85616314,  0.12757994,
                        0.94324936,  0.73078663,  0.09658102,  0.60703967,  0.77664978],
                      [ 0.28332265,  0.81479711,  0.86985333,  0.43797066,  0.32540082,
                        0.43819229,  0.92230363,  0.49414252,  0.68168256,  0.05922372],
                      [ 0.10721335,  0.93904142,  0.79163075,  0.73232848,  0.90283839,
                        0.68408046,  0.25502302,  0.95976614,  0.59214115,  0.13663711],
                      [ 0.28087456,  0.33127607,  0.15530412,  0.76558121,  0.83389773,
                        0.03735974,  0.98717738,  0.71432229,  0.54881366,  0.86893953],
                      [ 0.77995937,  0.995556  ,  0.29688434,  0.15646162,  0.051848  ,
                        0.37161935,  0.12998491,  0.09377296,  0.36882507,  0.36583435],
                      [ 0.37851836,  0.05315792,  0.63144617,  0.25003433,  0.69586032,
                        0.11393988,  0.92362096,  0.88045438,  0.93530252,  0.68275072],
                      [ 0.86486596,  0.83236675,  0.82960664,  0.5779663 ,  0.25724233,
                        0.84841095,  0.90862812,  0.64414887,  0.3565272 ,  0.71026066],
                      [ 0.01383268,  0.3406093 ,  0.76084285,  0.70800694,  0.87634056,
                        0.08213693,  0.54655021,  0.98123181,  0.44080053,  0.86815815]])

    y1 = np.arange( 10 )
    y1.shape = 1, 10

    y2 = np.arange( 10 )
    y2.shape = 10, 1

    fig = plt.figure()
    plt.subplot( 411 )
    plt.plot( y1 )
    plt.subplot( 412 )
    plt.plot( y2 )

    plt.subplot( 413 )
    from nose.tools import assert_raises
    assert_raises(ValueError,plt.plot, (y1,y2))

    plt.subplot( 414 )
    plt.plot( xdata[:,1], xdata[1,:], 'o' )

    fig.savefig( 'shaped data' )

@image_comparison(baseline_images=['const_xy'])
def test_const_xy():
    fig = plt.figure()

    plt.subplot( 311 )
    plt.plot( np.arange(10), np.ones( (10,) ) )

    plt.subplot( 312 )
    plt.plot( np.ones( (10,) ), np.arange(10) )

    plt.subplot( 313 )
    plt.plot( np.ones( (10,) ), np.ones( (10,) ), 'o' )

    fig.savefig( 'const_xy' )

@image_comparison(baseline_images=['polar_wrap_180',
                                   'polar_wrap_360',
                                   ])
def test_polar_wrap():
    D2R = np.pi / 180.0

    fig = plt.figure()

    #NOTE: resolution=1 really should be the default
    plt.subplot( 111, polar=True, resolution=1 )
    plt.polar( [179*D2R, -179*D2R], [0.2, 0.1], "b.-" )
    plt.polar( [179*D2R,  181*D2R], [0.2, 0.1], "g.-" )
    plt.rgrids( [0.05, 0.1, 0.15, 0.2, 0.25, 0.3] )

    fig.savefig( 'polar_wrap_180' )

    fig = plt.figure()

    #NOTE: resolution=1 really should be the default
    plt.subplot( 111, polar=True, resolution=1 )
    plt.polar( [2*D2R, -2*D2R], [0.2, 0.1], "b.-" )
    plt.polar( [2*D2R,  358*D2R], [0.2, 0.1], "g.-" )
    plt.polar( [358*D2R,  2*D2R], [0.2, 0.1], "r.-" )
    plt.rgrids( [0.05, 0.1, 0.15, 0.2, 0.25, 0.3] )

    fig.savefig( 'polar_wrap_360' )

@image_comparison(baseline_images=['polar_units'])
def test_polar_units():
    import matplotlib.testing.jpl_units as units
    units.register()

    pi = np.pi
    deg = units.UnitDbl( 1.0, "deg" )

    x1 = [ pi/6.0, pi/4.0, pi/3.0, pi/2.0 ]
    x2 = [ 30.0*deg, 45.0*deg, 60.0*deg, 90.0*deg ]

    y1 = [ 1.0, 2.0, 3.0, 4.0]
    y2 = [ 4.0, 3.0, 2.0, 1.0 ]

    fig = plt.figure()

    plt.polar( x2, y1, color = "blue" )

    # polar( x2, y1, color = "red", xunits="rad" )
    # polar( x2, y2, color = "green" )

    fig.savefig( 'polar_units' )

@image_comparison(baseline_images=['axvspan_epoch'])
def test_axvspan_epoch():
    from datetime import datetime
    import matplotlib.testing.jpl_units as units
    units.register()

    # generate some data
    t0 = units.Epoch( "ET", dt=datetime(2009, 1, 20) )
    tf = units.Epoch( "ET", dt=datetime(2009, 1, 21) )

    dt = units.Duration( "ET", units.day.convert( "sec" ) )

    fig = plt.figure()

    plt.axvspan( t0, tf, facecolor="blue", alpha=0.25 )

    ax = plt.gca()
    ax.set_xlim( t0 - 5.0*dt, tf + 5.0*dt )

    fig.savefig( 'axvspan_epoch' )

@image_comparison(baseline_images=['axhspan_epoch'])
def test_axhspan_epoch():
    from datetime import datetime
    import matplotlib.testing.jpl_units as units
    units.register()

    # generate some data
    t0 = units.Epoch( "ET", dt=datetime(2009, 1, 20) )
    tf = units.Epoch( "ET", dt=datetime(2009, 1, 21) )

    dt = units.Duration( "ET", units.day.convert( "sec" ) )

    fig = plt.figure()

    plt.axhspan( t0, tf, facecolor="blue", alpha=0.25 )

    ax = plt.gca()
    ax.set_ylim( t0 - 5.0*dt, tf + 5.0*dt )

    fig.savefig( 'axhspan_epoch' )


@image_comparison(baseline_images=['hexbin_extent'])
def test_hexbin_extent():
    # this test exposes sf bug 2856228
    fig = plt.figure()

    ax = fig.add_subplot(111)
    data = np.arange(2000.)/2000.
    data.shape = 2, 1000
    x, y = data

    ax.hexbin(x, y, extent=[.1, .3, .6, .7])
    fig.savefig('hexbin_extent')



if __name__=='__main__':
    import nose
    nose.runmodule(argv=['-s','--with-doctest'], exit=False)
