#!/usr/local/bin/python
import os
import vtk

# Create a rectangular cube.  VTK has a number of "source" classes to
# create cubes, cones, cylinders, spheres, grids, images and even
# mandlebrot sets!
cube = vtk.vtkCubeSource()
cube.SetXLength(10)
cube.SetYLength(5)
cube.SetZLength(20)
cube.SetCenter(1,2,3)

# Set up the mappers to extract data primitives.  The output of the
# mapper is polygon data that 
mapper = vtk.vtkPolyDataMapper()
mapper.SetInput(cube.GetOutput())

# The actors are the objects that are added to the scene.  Here you
# can set properties of the actor, eg object (color, translucency,
# etc)
actor = vtk.vtkActor()
actor.SetMapper(mapper)
actor.GetProperty().SetColor(1,0,0)

# Rendering is the process of converting geometry (points, edges,
# polygon faces), lights, camera angles and so on to a 2D image view
# -- what you see on the screen.  The vtkRenderer is an abstract
# interface to concrete implementations, eg vtkOpenGLRenderer for
# hardware accelerated rendering
ren = vtk.vtkRenderer()
ren.AddActor(actor)

# The render window is a graphical user interface window in which the
# renderer above draws the 2D rendered image
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)

# The render window interactor is a platform independent way for
# supporting GUI interaction -- mouse presses, keyborar events, mouse
# motion and so on
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)
renWin.SetSize(450,450)

# Ready, set, go!
iren.Initialize()
iren.Start()



