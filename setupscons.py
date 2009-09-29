import sys
import os

def configuration(parent_package='', top_path=None):
    from numpy.distutils.misc_util import Configuration

    config = Configuration(None, parent_package, top_path, setup_name = 'setupscons.py')
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
      configuration=configuration)
    return

if __name__ == '__main__':
    setup_package()
