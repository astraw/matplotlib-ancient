# a unit test driver -- these should ru w/o error

all = (
    'WallisPi.py',
    'scipy_least_squares_fit.py',
    'weave_callback.py',
    'weave_cplx.py',
    'weave_examples.py',
    'mpl_agg_oo.py',
    'mpl_imshow.py',
    'mpl_pylab.py',
    'mpl_set_get.py',
    'mpl_subplot_demo.py',
    'parse_file.py',
    'vtk_hello.py',
    'vtk_marching_cubes.py',
    'vtk_slice_viewer.py',
    )

for fname in all:
    print 'running %s'%fname
    os.system('python %s'%fname)

print "That's all folks"
