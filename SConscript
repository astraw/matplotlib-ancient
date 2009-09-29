import os
import sys

from numscons import GetNumpyEnvironment

AGG_VERSION = 'agg24'

env = GetNumpyEnvironment(ARGUMENTS)

config = env.NumpyConfigure()
if not config.NumpyCheckLibAndHeader(libs='freetype', symbols='FT_Get_Kerning', headers='ft2build.h', section='freetype2'):
	pass
config.Finish()

env.Append(CPPPATH=["%s/include" % AGG_VERSION, "."])
env.Append(CPPDEFINES={"PY_ARRAY_UNIQUE_SYMBOL": "MPL_ARRAY_API"})

common_cxx = [env.PythonObject(i) for i in env.Glob("CXX/*.cxx")]
env.NumpyPythonExtension("ft2font", source=common_cxx)

src = ['src/_ttconv.cpp', 'ttconv/pprdrv_tt.cpp', 'ttconv/pprdrv_tt2.cpp',
    'ttconv/ttutil.cpp']
env.NumpyPythonExtension("ttconv", source=src, CXXFILESUFFIX=".cpp")

env.NumpyPythonExtension("_cntr", source="src/cntr.c")

src = ["_delaunay.cpp", "VoronoiDiagramGenerator.cpp",
       "delaunay_utils.cpp", "natneighbors.cpp"]
src = [os.path.join('lib/matplotlib/delaunay',s) for s in src]
env.NumpyPythonExtension("_delaunay", source=src, CXXFILESUFFIX=".cpp")

src = "src/nxutils.c"
env.NumpyPythonExtension('nxutils', source=src)

agg = ['agg_curves.cpp', 'agg_bezier_arc.cpp', 'agg_trans_affine.cpp', 'agg_vcgen_stroke.cpp']

src = ['%s/src/%s' % (AGG_VERSION, name) for name in agg]
src.extend(env.Glob('CXX/*.c'))
src.extend(common_cxx)

src.extend(['src/agg_py_transforms.cpp',
            'src/path_cleanup.cpp',
            'src/_path.cpp'])
env.NumpyPythonExtension('_path', source=src, CXXFILESUFFIX=".cpp")
