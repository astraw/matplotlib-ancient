#include <Python.h>
#include "structmember.h"
#include <stdlib.h>
#include <stdio.h>

#include "numerix.h"


/*
  pnpoly license
  Copyright (c) 1970-2003, Wm. Randolph Franklin
  
  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
  
  1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimers.
  2. Redistributions in binary form must reproduce the above copyright notice in the documentation and/or other materials provided with the distribution.
  3. The name of W. Randolph Franklin may not be used to endorse or promote products derived from this Software without specific prior written permission. 
  
  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
*/

int pnpoly_api(int npol, double *xp, double *yp, double x, double y)
{
  int i, j, c = 0;
  for (i = 0, j = npol-1; i < npol; j = i++) {
    if ((((yp[i]<=y) && (y<yp[j])) ||
	 ((yp[j]<=y) && (y<yp[i]))) &&
	(x < (xp[j] - xp[i]) * (y - yp[i]) / (yp[j] - yp[i]) + xp[i]))
      
      c = !c;
  }
  return c;
}


static PyObject *
pnpoly(PyObject *self, PyObject *args)
{
  int npol, i;
  double x, y;
  double *xv, *yv;
  int b;
  PyObject *vertsarg;
  PyArrayObject *verts;
  if (! PyArg_ParseTuple(args, "ddO", &x, &y, &vertsarg))
    return NULL;
  
  verts = (PyArrayObject *) PyArray_FromObject(vertsarg,PyArray_DOUBLE, 2, 2);
  
  if (verts == NULL)
    {
      PyErr_SetString(PyExc_ValueError,
		      "Arguments verts must be a Nx2 array.");
      Py_XDECREF(verts);
      return NULL;
      
    }
  
  npol = verts->dimensions[0];
  //printf ("found %d verts\n", npol);
  if (verts->dimensions[1]!=2) 
    {
      PyErr_SetString(PyExc_ValueError,
		      "Arguments verts must be a Nx2 array.");
      Py_XDECREF(verts);
      return NULL;
      
    }
  
  
  xv = (double *) PyMem_Malloc(sizeof(double) * npol);
  if (xv == NULL)
    {
      Py_XDECREF(verts);
      return NULL;
    }
  
  yv = (double *) PyMem_Malloc(sizeof(double) * npol);
  if (yv == NULL)
    {
      Py_XDECREF(verts);
      PyMem_Free(xv);
      return NULL;
    }
  
  for (i=0; i<npol; ++i) {
    xv[i] = *(double *)(verts->data + i*verts->strides[0]);
    yv[i] = *(double *)(verts->data +  i*verts->strides[0] + verts->strides[1]);
    //printf("adding vert: %1.3f, %1.3f\n", xv[i], yv[i]);
  }
  
  b = pnpoly_api(npol, xv, yv, x, y);
  //printf("in poly %d\n", b);
  
  Py_XDECREF(verts);
  PyMem_Free(xv);
  PyMem_Free(yv);
  return Py_BuildValue("i", b);
  
}

static PyObject *
points_inside_poly(PyObject *self, PyObject *args)
{
  int npol, npoints, i;
  double *xv, *yv, x, y;
  int b;
  PyObject *xypointsarg, *vertsarg;
  PyArrayObject *xypoints, *verts;
  PyArrayObject *mask;
  int dimensions[1];

  if (! PyArg_ParseTuple(args, "OO", &xypointsarg, &vertsarg))
    return NULL;
  
  verts = (PyArrayObject *) PyArray_FromObject(vertsarg,PyArray_DOUBLE, 2, 2);
  
  if (verts == NULL)
    {
      PyErr_SetString(PyExc_ValueError,
		      "Argument verts must be a Nx2 array.");
      Py_XDECREF(verts);
      return NULL;
      
    }
  
  npol = verts->dimensions[0];
  //printf ("found %d verts\n", npol);
  if (verts->dimensions[1]!=2) 
    {
      PyErr_SetString(PyExc_ValueError,
		      "Arguments verts must be a Nx2 array.");
      Py_XDECREF(verts);
      return NULL;
      
    }
  
  
  xv = (double *) PyMem_Malloc(sizeof(double) * npol);
  if (xv == NULL)
    {
      Py_XDECREF(verts);
      return NULL;
    }
  
  yv = (double *) PyMem_Malloc(sizeof(double) * npol);
  if (yv == NULL)
    {
      Py_XDECREF(verts);
      PyMem_Free(xv);
      return NULL;
    }
  
  // fill the verts arrays
  for (i=0; i<npol; ++i) {
    xv[i] = *(double *)(verts->data + i*verts->strides[0]);
    yv[i] = *(double *)(verts->data +  i*verts->strides[0] + verts->strides[1]);
    //printf("adding vert: %1.3f, %1.3f\n", xv[i], yv[i]);
  }

  xypoints = (PyArrayObject *) PyArray_FromObject(xypointsarg,PyArray_DOUBLE, 2, 2);
  
  if (xypoints == NULL)
    {
      PyErr_SetString(PyExc_ValueError,
		      "Arguments xypoints must an Nx2 array.");
      Py_XDECREF(verts);
      Py_XDECREF(xypoints);
      PyMem_Free(xv);
      PyMem_Free(yv);
      return NULL;
      
    }
  
  if (xypoints->dimensions[1]!=2) 
    {
      PyErr_SetString(PyExc_ValueError,
		      "Arguments xypoints must be a Nx2 array.");
      
      Py_XDECREF(verts);
      Py_XDECREF(xypoints);
      PyMem_Free(xv);
      PyMem_Free(yv);
      return NULL;
    }
  
  npoints = xypoints->dimensions[0];
  dimensions[0] = npoints;

  mask = (PyArrayObject *)PyArray_FromDims(1,dimensions,PyArray_INT);
  if (mask==NULL) {
      Py_XDECREF(verts);
      Py_XDECREF(xypoints);
      PyMem_Free(xv);
      PyMem_Free(yv);
      return NULL;  }

  for (i=0; i<npoints; ++i) {
    x = *(double *)(xypoints->data + i*xypoints->strides[0]);
    y = *(double *)(xypoints->data +  i*xypoints->strides[0] + xypoints->strides[1]);
    b = pnpoly_api(npol, xv, yv, x, y);
    //printf("checking %d, %d, %1.3f, %1.3f, %d\n", npol, npoints, x, y, b);
    *(int *)(mask->data+i*mask->strides[0]) = b;

  }
  
  
  Py_XDECREF(verts);
  Py_XDECREF(xypoints);

  PyMem_Free(xv);
  PyMem_Free(yv);
  PyObject* ret =  Py_BuildValue("O", mask);
  Py_XDECREF(mask);
  return ret;

  
}




static PyMethodDef module_methods[] = {
  {"pnpoly",  pnpoly, METH_VARARGS, "inside = pnpoly(x, y, xyverts)\nreturn 1 if x,y is inside the polygon defined by the sequence of x,y vertices in xyverts"},
  {"points_inside_poly",  points_inside_poly, METH_VARARGS, "mask = points_inside_poly(xypoints, xyverts)\nreturn a mask of length xypoints indicating whether each x,y point is inside the polygon defined by the sequence of x,y vertices in xyverts"},
  {NULL}  /* Sentinel */
}


#ifdef NUMARRAY
#if PY_MINOR_VERSION > 2
PyMODINIT_FUNC
#else
DL_EXPORT(void)
#endif
     init_na_nxutils(void)
{
  PyObject* m;
  
  
  m = Py_InitModule3("_na_nxutils", module_methods,
		     "general purpose utilities (numarray).");
  
  if (m == NULL)
    return;
  
  import_array();
  
}
#endif
#ifdef NUMERIC
#if PY_MINOR_VERSION > 2
PyMODINIT_FUNC
#else
DL_EXPORT(void)
#endif
     init_nc_nxutils(void)
{
  PyObject* m;
  
  m = Py_InitModule3("_nc_nxutils", module_methods,
		     "general purpose utilities (Numeric).");
  
  if (m == NULL)
    return;
  
  import_array();
}
#endif

#ifdef SCIPY
#if PY_MINOR_VERSION > 2
PyMODINIT_FUNC
#else
DL_EXPORT(void)
#endif
     init_ns_nxutils(void)
{
  PyObject* m;
  
  m = Py_InitModule3("_ns_nxutils", module_methods,
		     "general purpose utilities (numpy).");
  
  if (m == NULL)
    return;
  
  import_array();
}
#endif


