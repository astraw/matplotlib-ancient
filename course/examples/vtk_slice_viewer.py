#!/usr/local/bin/python
import os
import vtk
from WindowLevelInterface import WindowLevelInterface

# Create reader - you have total flexibility to specify the file
# naming pattern, the byte order, the size of the header and so on
reader = vtk.vtkVolume16Reader()
reader.SetDataDimensions(256,256)
reader.GetOutput().SetOrigin(0.0,0.0,0.0)
reader.SetFilePrefix('../data/images/r')
reader.SetFilePattern( '%s%d.ima')
reader.SetDataByteOrderToBigEndian()
reader.SetImageRange(1001,1060)
reader.SetDataSpacing(1.0,1.0,3.5)
reader.Update()

# VTK comes with a helper class to view slice data
viewer = vtk.vtkImageViewer()
viewer.SetInput(reader.GetOutput())
viewer.SetZSlice(30)
viewer.SetColorWindow(600)
viewer.SetColorLevel(270)
viewer.Render()
viewer.SetPosition(50,50)

# A helper class to set the window level, etc
WindowLevelInterface(viewer)



