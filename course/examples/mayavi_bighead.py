#!/usr/bin/env python
import mayavi

bighead = '../data/bighead.vtk'

mv = mayavi.mayavi()
mv.open_vtk(bighead)
for mod in ['Outline','Axes','PolyData']:
    mv.load_module(mod,0)
