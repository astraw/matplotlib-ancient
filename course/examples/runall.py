# a unit test driver -- these should ru w/o error

all = (
    'WallisPi.py',
    'weave_callback.py',
    'weave_cplx.py',
    'weave_examples.py',
    'vtk_hello.py',
    'vtk_marching_cubes.py',
    'vtk_slice_viewer.py',
    )

for fname in all:
    print 'running %s'%fname
    os.system('python %s'%fname)

print "That's all folks"
