#!/usr/local/bin/python
import os

from vtk import *
from colors import *

ren = vtkRenderer()
renWin = vtkRenderWindow()
renWin.AddRenderer(ren)
iren = vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

# create reader
v16 = vtkVolume16Reader()
v16.SetDataDimensions(256,256)
v16.GetOutput().SetOrigin(0.0,0.0,0.0)
v16.SetFilePrefix('../data/images/r')
v16.SetFilePattern( '%s%d.ima')
v16.SetDataByteOrderToBigEndian()
v16.SetImageRange(1001,1060)
v16.SetDataSpacing(1.0,1.0,3.5)
v16.Update()

# 120 vessles near cerebellum
# 100 cortex
# 20 face
iso = vtkMarchingCubes()
iso.SetInput(v16.GetOutput())
iso.SetValue(0,100)


isoMapper = vtkPolyDataMapper()
isoMapper.SetInput(iso.GetOutput())
isoMapper.ScalarVisibilityOff()

isoActor = vtkActor()
isoActor.SetMapper(isoMapper)
isoActor.GetProperty().SetColor(antique_white)

# Add the actors to the renderer, set the background and size
ren.AddActor(isoActor)
ren.SetBackground(0.2,0.3,0.4)
renWin.SetSize(450,450)


iren.Initialize()
iren.Start()
