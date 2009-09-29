import sys
import os
import glob

# TODO: handle this properly
provide_pytz = False
provide_dateutil = True

#=====================
# Copied from setup.py
packages = [
    'matplotlib',
    'matplotlib.backends',
    'matplotlib.projections',
    'matplotlib.testing',
    'matplotlib.testing.jpl_units',
    'matplotlib.tests',
#   'matplotlib.toolkits',
    'mpl_toolkits',
    'mpl_toolkits.mplot3d',
    'mpl_toolkits.axes_grid',
    'matplotlib.sphinxext',
    # The following are deprecated and will be removed.
    'matplotlib.numerix',
    'matplotlib.numerix.mlab',
    'matplotlib.numerix.ma',
    'matplotlib.numerix.linear_algebra',
    'matplotlib.numerix.random_array',
    'matplotlib.numerix.fft']

package_data = {'matplotlib':['mpl-data/fonts/afm/*.afm',
                              'mpl-data/fonts/pdfcorefonts/*.afm',
                              'mpl-data/fonts/pdfcorefonts/*.txt',
                              'mpl-data/fonts/ttf/*.ttf',
                              'mpl-data/images/*.xpm',
                              'mpl-data/images/*.svg',
                              'mpl-data/images/*.png',
                              'mpl-data/images/*.ppm',
                              'mpl-data/example/*.npy',
                              'mpl-data/matplotlibrc',
                              'mpl-data/matplotlib.conf',
                              'mpl-data/*.glade',
                              'backends/Matplotlib.nib/*',
                              ]}

if 1:
    # TODO: exclude these when making release?
    baseline_images = glob.glob(os.path.join('lib','matplotlib','tests',
                                             'baseline_images','*','*'))
    def chop_package(fname):
        badstr = os.path.join('lib','matplotlib','')
        assert fname.startswith(badstr)
        result = fname[ len(badstr): ]
        return result
    baseline_images = [chop_package(f) for f in baseline_images]
    package_data['matplotlib'].extend(baseline_images)

def add_pytz():
    packages.append('pytz')

    resources = ['zone.tab', 'locales/pytz.pot']
    for dirpath, dirnames, filenames in os.walk(os.path.join('lib', 'pytz', 'zoneinfo')):

        if '.svn' in dirpath: continue
        # remove the 'pytz' part of the path
        basepath = os.path.join(*dirpath.split(os.path.sep)[2:])
        #print dirpath, basepath
        resources.extend([os.path.join(basepath, filename)
                          for filename in filenames])
    package_data['pytz'] = resources
    #print resources
    assert len(resources) > 10, 'zoneinfo files not found!'


def add_dateutil():
    packages.append('dateutil')
    packages.append('dateutil/zoneinfo')
    package_data['dateutil'] = ['zoneinfo/zoneinfo*.tar.*']

if sys.platform=='win32':
    # always add these to the win32 installer
    add_pytz()
    add_dateutil()
else:
    # only add them if we need them
    if provide_pytz:
        add_pytz()
        print 'adding pytz'
    if provide_dateutil: add_dateutil()

# end of setup.py copy
#======================

packages.append('matplotlib.delaunay')

def configuration(parent_package='', top_path=None):
    from numpy.distutils.misc_util import Configuration

    config = Configuration(None, parent_package, top_path)

    config.set_options(ignore_setup_xxx_py=True,
                       assume_default_configuration=True,
                       delegate_options_to_subpackages=True,
                       quiet=True)

    config.add_sconscript('SConstruct')

    return config

def setup_package():

    from numpy.distutils.core import setup

    for line in file('lib/matplotlib/__init__.py').readlines():
        if (line.startswith('__version__')):
            exec(line.strip())

    setup(
      name='matplotlib',
      version= __version__,
      description = "Python plotting package",
      author = "John D. Hunter",
      author_email="jdh2358@gmail.com",
      url = "http://matplotlib.sourceforge.net",
      long_description = """
      matplotlib strives to produce publication quality 2D graphics
      for interactive graphing, scientific publishing, user interface
      development and web application servers targeting multiple user
      interfaces and hardcopy output formats.  There is a 'pylab' mode
      which emulates matlab graphics
      """,
      packages=packages,
      package_dir = {'': 'lib'},
      package_data = package_data,
      configuration=configuration)
    return

if __name__ == '__main__':
    setup_package()
