/* numerix.h	-- John Hunter
 */

#ifndef _NUMERIX_H
#define _NUMERIX_H
#ifdef NUMARRAY
#include "numarray/arrayobject.h"
#else
#ifdef NUMERIC
#include "Numeric/arrayobject.h"
#else
#define PY_ARRAY_TYPES_PREFIX NumPy
#include "numpy/arrayobject.h"
#if (NDARRAY_VERSION >= 0x00090908)
#include "numpy/oldnumeric.h"
#endif
#endif
#endif

#endif
