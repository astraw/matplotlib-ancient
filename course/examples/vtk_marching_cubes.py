#!/usr/local/bin/python
import os
import vtk
import colors


# Create the volume reader
reader = vtk.vtkVolume16Reader()
reader.SetDataDimensions(256,256)
reader.GetOutput().SetOrigin(0.0,0.0,0.0)
reader.SetFilePrefix('../data/images/r')
reader.SetFilePattern( '%s%d.ima')
reader.SetDataByteOrderToBigEndian()
reader.SetImageRange(1001,1060)
reader.SetDataSpacing(1.0,1.0,3.5)
reader.Update()

# Marching cubes generates iso-surfaces
iso = vtk.vtkMarchingCubes()
iso.SetInput(reader.GetOutput())

# We'll run it though the decimation filter to make it a little
# smaller.
decimate = vtk.vtkDecimate()
decimate.SetInput(iso.GetOutput())

# Some iso values
#   vessles : 120
#   cortex  : 100
#   face    :  20
iso.SetValue(0,100)
isoMapper = vtk.vtkPolyDataMapper()
isoMapper.SetInput(decimate.GetOutput())

# You can assign scalars to voxels, eg to map things onto the cortex
# Here we are just dislpaying the anatomy so we turn scalars off
isoMapper.ScalarVisibilityOff()

isoActor = vtk.vtkActor()
isoActor.SetMapper(isoMapper)
# this is the color of the surface
isoActor.GetProperty().SetColor(colors.antique_white)


# Let's save the data to a VTK file for external processing. The
# Update command is used to make sure the pipeline is up-to-date
# before writing

decimate.Update()
writer = vtk.vtkDataSetWriter()
writer.SetInput(decimate.GetOutput())
writer.SetFileName('../data/bighead.vtk')
writer.SetFileTypeToASCII()
writer.Write()

# Now visualize it; set up the renderer and add the actor
ren = vtk.vtkRenderer()
ren.AddActor(isoActor)
ren.SetBackground(0.2,0.3,0.4)

# Set up the render window and interactor
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)
renWin.SetSize(450,450)

# Ready, set, go!
iren.Initialize()
iren.Start()
