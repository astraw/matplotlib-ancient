#!/usr/local/bin/python
import os
import vtk

# Create a rectangule cube
cube = vtk.vtkCubeSource()
cube.SetXLength(10)
cube.SetYLength(5)
cube.SetZLength(20)
cube.SetCenter(1,2,3)

# And a cone
cone = vtk.vtkConeSource()
cone.SetHeight(10)
cone.SetRadius(4)
cone.SetResolution(30)
cone.SetCenter(10,20,5)
cone.SetDirection(1,2,3)

# Set up the mappers to extract data primitives (polygons, etc)
mapper1 = vtk.vtkPolyDataMapper()
mapper1.SetInput(cube.GetOutput())
mapper2 = vtk.vtkPolyDataMapper()
mapper2.SetInput(cone.GetOutput())

# Make the first cube transparent red
actor1 = vtk.vtkActor()
actor1.SetMapper(mapper1)
actor1.GetProperty().SetOpacity(0.5)
actor1.GetProperty().SetColor(1,0,0)

# Make the second cube blue
actor2 = vtk.vtkActor()
actor2.SetMapper(mapper2)
actor2.GetProperty().SetColor(0,0,1)

# Set up the renderer and add the actor1
ren = vtk.vtkRenderer()
ren.AddActor(actor1)
ren.AddActor(actor2)

# Set up the render window and interactor
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)
renWin.SetSize(450,450)

# Ready, set, go!
iren.Initialize()
iren.Start()



