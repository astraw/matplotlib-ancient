#!/usr/local/bin/python
import os
from vtk import vtkVolume16Reader, vtkImageViewer
from WindowLevelInterface import *

# create reader
reader = vtkVolume16Reader()
reader.SetDataDimensions(256,256)
reader.GetOutput().SetOrigin(0.0,0.0,0.0)
reader.SetFilePrefix('../data/images/r')
reader.SetFilePattern( '%s%d.ima')
reader.SetDataByteOrderToBigEndian()
reader.SetImageRange(1001,1060)
reader.SetDataSpacing(1.0,1.0,3.5)
reader.Update()

viewer = vtkImageViewer()
viewer.SetInput(reader.GetOutput())
viewer.SetZSlice(30)
viewer.SetColorWindow(600)
viewer.SetColorLevel(270)
viewer.Render()

viewer.SetPosition(50,50)

#make interface
WindowLevelInterface(viewer)



