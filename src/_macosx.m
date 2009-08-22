#include <Cocoa/Cocoa.h>
#include <ApplicationServices/ApplicationServices.h>
#include <sys/socket.h>
#include <Python.h>
#include "numpy/arrayobject.h"
#include "path_cleanup.h"

/* Proper way to check for the OS X version we are compiling for, from
   http://developer.apple.com/documentation/DeveloperTools/Conceptual/cross_development */
#if __MAC_OS_X_VERSION_MIN_REQUIRED >= 1050
#define COMPILING_FOR_10_5
#endif

static int nwin = 0;   /* The number of open windows */

/* Use Atsui for Mac OS X 10.4, CoreText for Mac OS X 10.5 */
#ifndef COMPILING_FOR_10_5
static int ngc = 0;    /* The number of graphics contexts in use */


/* For drawing Unicode strings with ATSUI */
static ATSUStyle style = NULL;
static ATSUTextLayout layout = NULL;
#endif

/* CGFloat was defined in Mac OS X 10.5 */
#ifndef CGFLOAT_DEFINED
#define CGFloat float
#endif


/* Various NSApplicationDefined event subtypes */
#define STDIN_READY 0
#define SIGINT_CALLED 1
#define STOP_EVENT_LOOP 2
#define WINDOW_CLOSING 3

/* Path definitions */
#define STOP      0
#define MOVETO    1
#define LINETO    2
#define CURVE3    3
#define CURVE4    4
#define CLOSEPOLY 0x4f

/* Hatching */
#define HATCH_SIZE 72

/* -------------------------- Helper function ---------------------------- */

static void stdin_ready(CFReadStreamRef readStream, CFStreamEventType eventType, void* context)
{
    NSEvent* event = [NSEvent otherEventWithType: NSApplicationDefined
                                        location: NSZeroPoint
                                   modifierFlags: 0
                                       timestamp: 0.0
                                    windowNumber: 0
                                         context: nil
                                         subtype: STDIN_READY
                                           data1: 0
                                           data2: 0];
    [NSApp postEvent: event atStart: true];
}

static int sigint_fd = -1;

static void _sigint_handler(int sig)
{
    const char c = 'i';
    write(sigint_fd, &c, 1);
}

static void _callback(CFSocketRef s,
                      CFSocketCallBackType type,
                      CFDataRef address,
                      const void * data,
                      void *info)
{
    char c;
    CFSocketNativeHandle handle = CFSocketGetNative(s);
    read(handle, &c, 1);
    NSEvent* event = [NSEvent otherEventWithType: NSApplicationDefined
                                        location: NSZeroPoint
                                   modifierFlags: 0
                                       timestamp: 0.0
                                    windowNumber: 0
                                         context: nil
                                         subtype: SIGINT_CALLED
                                           data1: 0
                                           data2: 0];
    [NSApp postEvent: event atStart: true];
}

static int wait_for_stdin(void)
{
    const UInt8 buffer[] = "/dev/fd/0";
    const CFIndex n = (CFIndex)strlen((char*)buffer);
    CFRunLoopRef runloop = CFRunLoopGetCurrent();
    CFURLRef url = CFURLCreateFromFileSystemRepresentation(kCFAllocatorDefault,
                                                           buffer,
                                                           n,
                                                           false);
    CFReadStreamRef stream = CFReadStreamCreateWithFile(kCFAllocatorDefault,
                                                        url);
    CFRelease(url);

    CFReadStreamOpen(stream);
    if (!CFReadStreamHasBytesAvailable(stream))
    /* This is possible because of how PyOS_InputHook is called from Python */
    {
        int error;
        int interrupted = 0;
        int channel[2];
        CFSocketRef sigint_socket = NULL;
        PyOS_sighandler_t py_sigint_handler = NULL;
        CFStreamClientContext clientContext = {0, NULL, NULL, NULL, NULL};
        CFReadStreamSetClient(stream,
                              kCFStreamEventHasBytesAvailable,
                              stdin_ready,
                              &clientContext);
        CFReadStreamScheduleWithRunLoop(stream, runloop, kCFRunLoopCommonModes);
        error = pipe(channel);
        if (error==0)
        {
            fcntl(channel[1], F_SETFL, O_WRONLY | O_NONBLOCK);

            sigint_socket = CFSocketCreateWithNative(kCFAllocatorDefault,
                                                     channel[0],
                                                     kCFSocketReadCallBack,
                                                     _callback,
                                                     NULL);
            if (sigint_socket)
            {
                CFRunLoopSourceRef source;
                source = CFSocketCreateRunLoopSource(kCFAllocatorDefault,
                                                     sigint_socket,
                                                     0);
                CFRelease(sigint_socket);
                if (source)
                {
                    CFRunLoopAddSource(runloop, source, kCFRunLoopDefaultMode);
                    CFRelease(source);
                    sigint_fd = channel[1];
                    py_sigint_handler = PyOS_setsig(SIGINT, _sigint_handler);
                }
            }
            else
                close(channel[0]);
        }

        NSAutoreleasePool* pool = [[NSAutoreleasePool alloc] init];
        NSDate* date = [NSDate distantFuture];
        while (true)
        {   NSEvent* event = [NSApp nextEventMatchingMask: NSAnyEventMask
                                                untilDate: date
                                                   inMode: NSDefaultRunLoopMode
                                                  dequeue: YES];
           if (!event) break; /* No windows open */
           if ([event type]==NSApplicationDefined)
           {   short subtype = [event subtype];
               if (subtype==STDIN_READY) break;
               if (subtype==SIGINT_CALLED)
               {   interrupted = true;
                   break;
               }
           }
           [NSApp sendEvent: event];
        }
        [pool release];

        if (py_sigint_handler) PyOS_setsig(SIGINT, py_sigint_handler);
        CFReadStreamUnscheduleFromRunLoop(stream,
                                          runloop,
                                          kCFRunLoopCommonModes);
        if (sigint_socket) CFSocketInvalidate(sigint_socket);
        if (error==0) close(channel[1]);
        if (interrupted) raise(SIGINT);
    }
    CFReadStreamClose(stream);
    return 1;
}

#ifndef COMPILING_FOR_10_5
static int _init_atsui(void)
{
    OSStatus status;

    status = ATSUCreateStyle(&style);
    if (status!=noErr)
    {
        PyErr_SetString(PyExc_RuntimeError, "ATSUCreateStyle failed");
        return 0;
    }

    status = ATSUCreateTextLayout(&layout);
    if (status!=noErr)
    {
        status = ATSUDisposeStyle(style);
        if (status!=noErr)
            PyErr_WarnEx(PyExc_RuntimeWarning, "ATSUDisposeStyle failed", 1);
        PyErr_SetString(PyExc_RuntimeError, "ATSUCreateTextLayout failed");
        return 0;
    }


    return 1;
}

static void _dealloc_atsui(void)
{
    OSStatus status;

    status = ATSUDisposeStyle(style);
    if (status!=noErr)
        PyErr_WarnEx(PyExc_RuntimeWarning, "ATSUDisposeStyle failed", 1);

    status = ATSUDisposeTextLayout(layout);
    if (status!=noErr)
        PyErr_WarnEx(PyExc_RuntimeWarning, "ATSUDisposeTextLayout failed", 1);
}
#endif

static int _draw_path(CGContextRef cr, void* iterator)
{
    double x1, y1, x2, y2, x3, y3;
    int n = 0;
    unsigned code;

    while (true)
    {
        code = get_vertex(iterator, &x1, &y1);
        if (code == CLOSEPOLY)
        {
            CGContextClosePath(cr);
            n++;
        }
        else if (code == STOP)
        {
            break;
        }
        else if (code == MOVETO)
        {
            CGContextMoveToPoint(cr, x1, y1);
            n++;
        }
        else if (code==LINETO)
        {
            CGContextAddLineToPoint(cr, x1, y1);
            n++;
        }
        else if (code==CURVE3)
        {
            get_vertex(iterator, &x2, &y2);
            CGContextAddQuadCurveToPoint(cr, x1, y1, x2, y2);
            n+=2;
        }
        else if (code==CURVE4)
        {
            get_vertex(iterator, &x2, &y2);
            get_vertex(iterator, &x3, &y3);
            CGContextAddCurveToPoint(cr, x1, y1, x2, y2, x3, y3);
            n+=3;
        }
    }
    return n;
}

static void _draw_hatch(void *info, CGContextRef cr)
{
    PyObject* hatchpath = (PyObject*)info;
    PyObject* transform;
    int nd = 2;
    npy_intp dims[2] = {3, 3};
    int typenum = NPY_DOUBLE;
    double data[9] = {HATCH_SIZE, 0, 0, 0, HATCH_SIZE, 0, 0, 0, 1};
    double rect[4] = { 0.0, 0.0, HATCH_SIZE, HATCH_SIZE};
    int n;
    transform = PyArray_SimpleNewFromData(nd, dims, typenum, data);
    if (!transform)
    {
        PyGILState_STATE gstate = PyGILState_Ensure();
        PyErr_Print();
        PyGILState_Release(gstate);
        return;
    }
    void* iterator  = get_path_iterator(hatchpath,
                                        transform,
                                        0,
                                        0,
                                        rect,
                                        QUANTIZE_FALSE,
                                        0);
    Py_DECREF(transform);
    if (!iterator)
    {
        PyGILState_STATE gstate = PyGILState_Ensure();
        PyErr_SetString(PyExc_RuntimeError, "failed to obtain path iterator for hatching");
        PyErr_Print();
        PyGILState_Release(gstate);
        return;
    }
    n = _draw_path(cr, iterator);
    free_path_iterator(iterator);
    if (n==0) return;
    CGContextSetLineWidth(cr, 1.0);
    CGContextSetLineCap(cr, kCGLineCapSquare);
    CGContextDrawPath(cr, kCGPathFillStroke);
}

static void _release_hatch(void* info)
{
    PyObject* hatchpath = (PyObject*)info;
    Py_DECREF(hatchpath);
}

/* ---------------------------- Cocoa classes ---------------------------- */


@interface Window : NSWindow
{   PyObject* manager;
}
- (Window*)initWithContentRect:(NSRect)rect styleMask:(unsigned int)mask backing:(NSBackingStoreType)bufferingType defer:(BOOL)deferCreation withManager: (PyObject*)theManager;
- (BOOL)closeButtonPressed;
- (void)close;
- (void)dealloc;
@end

@interface ToolWindow : NSWindow
{
}
- (ToolWindow*)initWithContentRect:(NSRect)rect master:(NSWindow*)window;
- (void)masterCloses:(NSNotification*)notification;
- (void)close;
@end

@interface View : NSView
{   PyObject* canvas;
    NSRect rubberband;
}
- (void)dealloc;
- (void)drawRect:(NSRect)rect;
- (void)windowDidResize:(NSNotification*)notification;
- (View*)initWithFrame:(NSRect)rect canvas:(PyObject*)fc;
- (BOOL)windowShouldClose:(NSNotification*)notification;
- (BOOL)isFlipped;
- (void)mouseDown:(NSEvent*)event;
- (void)mouseUp:(NSEvent*)event;
- (void)mouseDragged:(NSEvent*)event;
- (void)mouseMoved:(NSEvent*)event;
- (void)rightMouseDown:(NSEvent*)event;
- (void)rightMouseUp:(NSEvent*)event;
- (void)otherMouseDown:(NSEvent*)event;
- (void)otherMouseUp:(NSEvent*)event;
- (void)setRubberband:(NSRect)rect;
- (void)removeRubberband;
- (const char*)convertKeyEvent:(NSEvent*)event;
- (void)keyDown:(NSEvent*)event;
- (void)keyUp:(NSEvent*)event;
- (void)scrollWheel:(NSEvent *)event;
- (void)flagsChanged:(NSEvent*)event;
@end

@interface ScrollableButton : NSButton
{
    SEL scrollWheelUpAction;
    SEL scrollWheelDownAction;
}
- (void)setScrollWheelUpAction:(SEL)action;
- (void)setScrollWheelDownAction:(SEL)action;
- (void)scrollWheel:(NSEvent *)event;
@end

@interface MenuItem: NSMenuItem
{   int index;
}
+ (MenuItem*)menuItemWithTitle:(NSString*)title;
+ (MenuItem*)menuItemSelectAll;
+ (MenuItem*)menuItemInvertAll;
+ (MenuItem*)menuItemForAxis:(int)i;
- (void)toggle:(id)sender;
- (void)selectAll:(id)sender;
- (void)invertAll:(id)sender;
- (int)index;
@end

/* ---------------------------- Python classes ---------------------------- */

typedef struct {
    PyObject_HEAD
    CGContextRef cr;
    NSSize size;
    int level;
    CGFloat color[4];
} GraphicsContext;

static CGMutablePathRef _create_path(void* iterator)
{
    unsigned code;
    CGMutablePathRef p;
    double x1, y1, x2, y2, x3, y3;

    p = CGPathCreateMutable();
    if (!p) return NULL;

    while (true)
    {
        code = get_vertex(iterator, &x1, &y1);
        if (code == CLOSEPOLY)
        {
            CGPathCloseSubpath(p);
        }
        else if (code == STOP)
        {
            break;
        }
        else if (code == MOVETO)
        {
            CGPathMoveToPoint(p, NULL, x1, y1);
        }
        else if (code==LINETO)
        {
            CGPathAddLineToPoint(p, NULL, x1, y1);
        }
        else if (code==CURVE3)
        {
            get_vertex(iterator, &x2, &y2);
            CGPathAddQuadCurveToPoint(p, NULL, x1, y1, x2, y2);
        }
        else if (code==CURVE4)
        {
            get_vertex(iterator, &x2, &y2);
            get_vertex(iterator, &x3, &y3);
            CGPathAddCurveToPoint(p, NULL, x1, y1, x2, y2, x3, y3);
        }
    }

    return p;
}

static int _get_snap(GraphicsContext* self, enum e_quantize_mode* mode)
{
    PyObject* snap = PyObject_CallMethod((PyObject*)self, "get_snap", "");
    if(!snap) return 0;
    if(snap==Py_None) *mode = QUANTIZE_AUTO;
    else if (PyBool_Check(snap)) *mode = QUANTIZE_TRUE;
    else *mode = QUANTIZE_FALSE;
    Py_DECREF(snap);
    return 1;
}

static PyObject*
GraphicsContext_new(PyTypeObject* type, PyObject *args, PyObject *kwds)
{
    GraphicsContext* self = (GraphicsContext*)type->tp_alloc(type, 0);
    if (!self) return NULL;
    self->cr = NULL;
    self->level = 0;

#ifndef COMPILING_FOR_10_5
    if (ngc==0)
    {
        int ok = _init_atsui();
        if (!ok)
        {
            return NULL;
        }
    }
    ngc++;
#endif

    return (PyObject*) self;
}

#ifndef COMPILING_FOR_10_5
static void
GraphicsContext_dealloc(GraphicsContext *self)
{
    ngc--;
    if (ngc==0) _dealloc_atsui();

    self->ob_type->tp_free((PyObject*)self);
}
#endif

static PyObject*
GraphicsContext_repr(GraphicsContext* self)
{
    return PyString_FromFormat("GraphicsContext object %p wrapping the Quartz 2D graphics context %p", (void*)self, (void*)(self->cr));
}

static PyObject*
GraphicsContext_save (GraphicsContext* self)
{
    CGContextRef cr = self->cr;
    if (!cr)
    {
        PyErr_SetString(PyExc_RuntimeError, "CGContextRef is NULL");
        return NULL;
    }
    CGContextSaveGState(cr);
    self->level++;
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
GraphicsContext_restore (GraphicsContext* self)
{
    CGContextRef cr = self->cr;
    if (!cr)
    {
        PyErr_SetString(PyExc_RuntimeError, "CGContextRef is NULL");
        return NULL;
    }
    if (self->level==0)
    {
        PyErr_SetString(PyExc_RuntimeError,
            "Attempting to execute CGContextRestoreGState on an empty stack");
        return NULL;
    }
    CGContextRestoreGState(cr);
    self->level--;
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
GraphicsContext_set_alpha (GraphicsContext* self, PyObject* args)
{
    float alpha;
    if (!PyArg_ParseTuple(args, "f", &alpha)) return NULL;
    CGContextRef cr = self->cr;
    if (!cr)
    {
        PyErr_SetString(PyExc_RuntimeError, "CGContextRef is NULL");
        return NULL;
    }
    CGContextSetAlpha(cr, alpha);
 
    self->color[3] = alpha;

    Py_INCREF(Py_None);
    return Py_None;
}

static BOOL
_set_antialiased(CGContextRef cr, PyObject* antialiased)
{
    const int shouldAntialias = PyObject_IsTrue(antialiased);
    if (shouldAntialias < 0)
    {
        PyErr_SetString(PyExc_ValueError,
                        "Failed to read antialiaseds variable");
        return false;
    }
    CGContextSetShouldAntialias(cr, shouldAntialias);
    return true;
}

static PyObject*
GraphicsContext_set_antialiased (GraphicsContext* self, PyObject* args)
{
    CGContextRef cr = self->cr;
    if (!cr)
    {
        PyErr_SetString(PyExc_RuntimeError, "CGContextRef is NULL");
        return NULL;
    }
    if (!_set_antialiased(cr, args)) return NULL;
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
GraphicsContext_set_capstyle (GraphicsContext* self, PyObject* args)
{
    char* string;
    CGLineCap cap;

    if (!PyArg_ParseTuple(args, "s", &string)) return NULL;

    if (!strcmp(string, "butt")) cap = kCGLineCapButt;
    else if (!strcmp(string, "round")) cap = kCGLineCapRound;
    else if (!strcmp(string, "projecting")) cap = kCGLineCapSquare;
    else
    {
        PyErr_SetString(PyExc_ValueError,
                        "capstyle should be 'butt', 'round', or 'projecting'");
        return NULL;
    }
    CGContextRef cr = self->cr;
    if (!cr)
    {
        PyErr_SetString(PyExc_RuntimeError, "CGContextRef is NULL");
        return NULL;
    }
    CGContextSetLineCap(cr, cap);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
GraphicsContext_set_clip_rectangle (GraphicsContext* self, PyObject* args)
{
    CGRect rect;
    float x, y, width, height;
    if (!PyArg_ParseTuple(args, "(ffff)", &x, &y, &width, &height)) return NULL;

    rect.origin.x = x;
    rect.origin.y = y;
    rect.size.width = width;
    rect.size.height = height;

    CGContextRef cr = self->cr;
    if (!cr)
    {
        PyErr_SetString(PyExc_RuntimeError, "CGContextRef is NULL");
        return NULL;
    }

    CGContextClipToRect(cr, rect);
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
GraphicsContext_set_clip_path (GraphicsContext* self, PyObject* args)
{
    int n;
    CGContextRef cr = self->cr;

    PyObject* path;
    int nd = 2;
    npy_intp dims[2] = {3, 3};
    int typenum = NPY_DOUBLE;
    double data[] = {1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0};

    if (!cr)
    {
        PyErr_SetString(PyExc_RuntimeError, "CGContextRef is NULL");
        return NULL;
    }

    if(!PyArg_ParseTuple(args, "O", &path)) return NULL;

    PyObject* transform = PyArray_SimpleNewFromData(nd, dims, typenum, data);
    if (!transform) return NULL;

    double rect[4] = {0.0, 0.0, self->size.width, self->size.height};
    void* iterator  = get_path_iterator(path,
                                        transform,
                                        0,
                                        0,
                                        rect,
                                        QUANTIZE_AUTO,
                                        0);
    Py_DECREF(transform);
    if (!iterator)
    {
        PyErr_SetString(PyExc_RuntimeError,
            "set_clip_path: failed to obtain path iterator for clipping");
        return NULL;
    }
    n = _draw_path(cr, iterator);
    free_path_iterator(iterator);

    if (n > 0) CGContextClip(cr);

    Py_INCREF(Py_None);
    return Py_None;
}

static BOOL
_set_dashes(CGContextRef cr, PyObject* linestyle)
{
    CGFloat phase = 0.0;
    PyObject* offset;
    PyObject* dashes;

    if (!PyArg_ParseTuple(linestyle, "OO", &offset, &dashes))
    {
        PyErr_SetString(PyExc_TypeError,
            "failed to obtain the offset and dashes from the linestyle");
        return false;
    }

    if (offset!=Py_None)
    {
        if (PyFloat_Check(offset)) phase = PyFloat_AsDouble(offset);
        else if (PyInt_Check(offset)) phase = PyInt_AsLong(offset);
        else
        {
            PyErr_SetString(PyExc_TypeError,
                            "offset should be a floating point value");
            return false;
        }
    }

    if (dashes!=Py_None)
    {
        if (PyList_Check(dashes)) dashes = PyList_AsTuple(dashes);
        else if (PyTuple_Check(dashes)) Py_INCREF(dashes);
        else
        {
            PyErr_SetString(PyExc_TypeError,
                            "dashes should be a tuple or a list");
            return false;
        }
        int n = PyTuple_GET_SIZE(dashes);
        int i;
        CGFloat* lengths = malloc(n*sizeof(CGFloat));
        if(!lengths)
        {
            PyErr_SetString(PyExc_MemoryError, "Failed to store dashes");
            Py_DECREF(dashes);
            return false;
        }
        for (i = 0; i < n; i++)
        {
            PyObject* value = PyTuple_GET_ITEM(dashes, i);
            if (PyFloat_Check(value))
                lengths[i] = (CGFloat) PyFloat_AS_DOUBLE(value);
            else if (PyInt_Check(value))
                lengths[i] = (CGFloat) PyInt_AS_LONG(value);
            else break;
        }
        Py_DECREF(dashes);
        if (i < n) /* break encountered */
        {
            free(lengths);
            PyErr_SetString(PyExc_TypeError, "Failed to read dashes");
            return false;
        }
        CGContextSetLineDash(cr, phase, lengths, n);
        free(lengths);
    }
    else
        CGContextSetLineDash(cr, phase, NULL, 0);

    return true;
}

static PyObject*
GraphicsContext_set_dashes (GraphicsContext* self, PyObject* args)
{
    CGContextRef cr = self->cr;
    if (!cr)
    {
        PyErr_SetString(PyExc_RuntimeError, "CGContextRef is NULL");
        return NULL;
    }

    if (!_set_dashes(cr, args))
        return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
GraphicsContext_set_foreground(GraphicsContext* self, PyObject* args)
{
    float r, g, b;
    if(!PyArg_ParseTuple(args, "(fff)", &r, &g, &b)) return NULL;

    CGContextRef cr = self->cr;
    if (!cr)
    {
        PyErr_SetString(PyExc_RuntimeError, "CGContextRef is NULL");
        return NULL;
    }

    CGContextSetRGBStrokeColor(cr, r, g, b, 1.0);
    CGContextSetRGBFillColor(cr, r, g, b, 1.0);

    self->color[0] = r;
    self->color[1] = g;
    self->color[2] = b;

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
GraphicsContext_set_graylevel(GraphicsContext* self, PyObject* args)
{   float gray;
    if(!PyArg_ParseTuple(args, "f", &gray)) return NULL;

    CGContextRef cr = self->cr;
    if (!cr)
    {
        PyErr_SetString(PyExc_RuntimeError, "CGContextRef is NULL");
        return NULL;
    }

    CGContextSetGrayStrokeColor(cr, gray, 1.0);
    CGContextSetGrayFillColor(cr, gray, 1.0);
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
GraphicsContext_set_linewidth (GraphicsContext* self, PyObject* args)
{
    float width;
    if (!PyArg_ParseTuple(args, "f", &width)) return NULL;

    CGContextRef cr = self->cr;
    if (!cr)
    {
        PyErr_SetString(PyExc_RuntimeError, "CGContextRef is NULL");
        return NULL;
    }

    CGContextSetLineWidth(cr, width);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
GraphicsContext_set_joinstyle(GraphicsContext* self, PyObject* args)
{   char* string;
    CGLineJoin join;

    if (!PyArg_ParseTuple(args, "s", &string)) return NULL;

    if (!strcmp(string, "miter")) join = kCGLineJoinMiter;
    else if (!strcmp(string, "round")) join = kCGLineJoinRound;
    else if (!strcmp(string, "bevel")) join = kCGLineJoinBevel;
    else
    {
        PyErr_SetString(PyExc_ValueError,
                        "joinstyle should be 'miter', 'round', or 'bevel'");
        return NULL;
    }

    CGContextRef cr = self->cr;
    if (!cr)
    {
        PyErr_SetString(PyExc_RuntimeError, "CGContextRef is NULL");
        return NULL;
    }
    CGContextSetLineJoin(cr, join);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
GraphicsContext_draw_path (GraphicsContext* self, PyObject* args)
{
    PyObject* path;
    PyObject* transform;
    PyObject* rgbFace;

    int n;

    void* iterator;

    CGContextRef cr = self->cr;
    double rect[4] = { 0.0, 0.0, self->size.width, self->size.height};

    if (!cr)
    {
        PyErr_SetString(PyExc_RuntimeError, "CGContextRef is NULL");
        return NULL;
    }

    if(!PyArg_ParseTuple(args, "OO|O",
                               &path,
                               &transform,
                               &rgbFace)) return NULL;

    if(rgbFace==Py_None) rgbFace = NULL;

    iterator  = get_path_iterator(path,
                                  transform,
                                  1,
                                  0,
                                  rect,
                                  QUANTIZE_AUTO,
                                  1);
    if (!iterator)
    {
        PyErr_SetString(PyExc_RuntimeError,
                        "draw_path: failed to obtain path iterator");
        return NULL;
    }
    n = _draw_path(cr, iterator);
    free_path_iterator(iterator);

    if (n > 0)
    {
        PyObject* hatchpath;
        if(rgbFace)
        {
            float r, g, b;
            if (!PyArg_ParseTuple(rgbFace, "fff", &r, &g, &b))
                return NULL;
            CGContextSaveGState(cr);
            CGContextSetRGBFillColor(cr, r, g, b, 1.0);
            CGContextDrawPath(cr, kCGPathFillStroke);
            CGContextRestoreGState(cr);
        }
        else CGContextStrokePath(cr);

        hatchpath = PyObject_CallMethod((PyObject*)self, "get_hatch_path", "");
        if (!hatchpath)
        {
            return NULL;
        }
        else if (hatchpath==Py_None)
        {
            Py_DECREF(hatchpath);
        }
        else
        {
            CGPatternRef pattern;
            CGColorSpaceRef baseSpace;
            CGColorSpaceRef patternSpace;
            static const CGPatternCallbacks callbacks = {0,
                                                         &_draw_hatch,
                                                         &_release_hatch};
            baseSpace = CGColorSpaceCreateWithName(kCGColorSpaceGenericRGB);
            if (!baseSpace)
            {
                Py_DECREF(hatchpath);
                PyErr_SetString(PyExc_RuntimeError,
                    "draw_path: CGColorSpaceCreateWithName failed");
                return NULL;
            }
            patternSpace = CGColorSpaceCreatePattern(baseSpace);
            CGColorSpaceRelease(baseSpace);
            if (!patternSpace)
            {
                Py_DECREF(hatchpath);
                PyErr_SetString(PyExc_RuntimeError,
                    "draw_path: CGColorSpaceCreatePattern failed");
                return NULL;
            }
            CGContextSetFillColorSpace(cr, patternSpace);
            CGColorSpaceRelease(patternSpace);

            pattern = CGPatternCreate((void*)hatchpath,
                                      CGRectMake(0, 0, HATCH_SIZE, HATCH_SIZE),
                                      CGAffineTransformIdentity,
                                      HATCH_SIZE, HATCH_SIZE,
                                      kCGPatternTilingNoDistortion,
                                      false,
                                      &callbacks);
            CGContextSetFillPattern(cr, pattern, self->color);
            CGPatternRelease(pattern);
            iterator  = get_path_iterator(path,
                                          transform,
                                          1,
                                          0,
                                          rect,
                                          QUANTIZE_AUTO,
                                          1);
            if (!iterator)
            {
                Py_DECREF(hatchpath);
                PyErr_SetString(PyExc_RuntimeError,
                    "draw_path: failed to obtain path iterator for hatching");
                return NULL;
            }
            n = _draw_path(cr, iterator);
            free_path_iterator(iterator);
            CGContextFillPath(cr);
        }
    }

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
GraphicsContext_draw_markers (GraphicsContext* self, PyObject* args)
{
    PyObject* marker_path;
    PyObject* marker_transform;
    PyObject* path;
    PyObject* transform;
    PyObject* rgbFace;

    int ok;
    float r, g, b;

    CGMutablePathRef marker;
    void* iterator;
    double rect[4] = {0.0, 0.0, self->size.width, self->size.height};
    enum e_quantize_mode mode;
    double xc, yc;
    unsigned code;

    CGContextRef cr = self->cr;

    if (!cr)
    {
        PyErr_SetString(PyExc_RuntimeError, "CGContextRef is NULL");
        return NULL;
    }

    if(!PyArg_ParseTuple(args, "OOOO|O",
                               &marker_path,
                               &marker_transform,
                               &path,
                               &transform,
                               &rgbFace)) return NULL;

    if(rgbFace==Py_None) rgbFace = NULL;

    if (rgbFace)
    {
        ok = PyArg_ParseTuple(rgbFace, "fff", &r, &g, &b);
        if (!ok)
        {
            return NULL;
        }
        CGContextSetRGBFillColor(cr, r, g, b, 1.0);
    }

    ok = _get_snap(self, &mode);
    if (!ok)
    {
        return NULL;
    }

    iterator = get_path_iterator(marker_path,
                                 marker_transform,
                                 0,
                                 0,
                                 rect,
                                 mode,
                                 0);
    if (!iterator)
    {
        PyErr_SetString(PyExc_RuntimeError,
            "draw_markers: failed to obtain path iterator for marker");
        return NULL;
    }
    marker = _create_path(iterator);
    free_path_iterator(iterator);
    if (!marker)
    {
        PyErr_SetString(PyExc_RuntimeError,
            "draw_markers: failed to draw marker path");
        return NULL;
    }
    iterator = get_path_iterator(path,
                                 transform,
                                 1,
                                 1,
                                 rect,
                                 QUANTIZE_TRUE,
                                 0);
    if (!iterator)
    {
        CGPathRelease(marker);
        PyErr_SetString(PyExc_RuntimeError,
            "draw_markers: failed to obtain path iterator");
        return NULL;
    }

    while (true)
    {
        code = get_vertex(iterator, &xc, &yc);
        if (code == STOP)
        {
            break;
        }
        else if (code == MOVETO || code == LINETO || code == CURVE3 || code ==CURVE4)
        {
            CGContextSaveGState(cr);
            CGContextTranslateCTM(cr, xc, yc);
            CGContextAddPath(cr, marker);
            CGContextRestoreGState(cr);
        }
        if(rgbFace) CGContextDrawPath(cr, kCGPathFillStroke);
        else CGContextStrokePath(cr);
    }
    free_path_iterator(iterator);
    CGPathRelease(marker);

    Py_INCREF(Py_None);
    return Py_None;
}

static BOOL _clip(CGContextRef cr, PyObject* object)
{
    if (object == Py_None) return true;

    PyArrayObject* array = NULL;
    array = (PyArrayObject*) PyArray_FromObject(object, PyArray_DOUBLE, 2, 2);
    if (!array)
    {
        PyErr_SetString(PyExc_ValueError, "failed to read clipping bounding box");
        return false;
    }

    if (PyArray_NDIM(array)!=2 || PyArray_DIM(array, 0)!=2 || PyArray_DIM(array, 1)!=2)
    {
        Py_DECREF(array);
        PyErr_SetString(PyExc_ValueError, "clipping bounding box should be a 2x2 array");
        return false;
    }

    const double l = *(double*)PyArray_GETPTR2(array, 0, 0);
    const double b = *(double*)PyArray_GETPTR2(array, 0, 1);
    const double r = *(double*)PyArray_GETPTR2(array, 1, 0);
    const double t = *(double*)PyArray_GETPTR2(array, 1, 1);

    Py_DECREF(array);

    CGRect rect;
    rect.origin.x = (CGFloat) l;
    rect.origin.y = (CGFloat) b;
    rect.size.width = (CGFloat) (r-l);
    rect.size.height = (CGFloat) (t-b);

    CGContextClipToRect(cr, rect);

    return true;
}

static BOOL
_set_offset(CGContextRef cr, PyObject* offsets, int index, PyObject* transform)
{
    CGFloat tx;
    CGFloat ty;
    double x = *(double*)PyArray_GETPTR2(offsets, index, 0);
    double y = *(double*)PyArray_GETPTR2(offsets, index, 1);
    PyObject* translation = PyObject_CallMethod(transform, "transform_point",
                                                           "((ff))", x, y);
    if (!translation)
    {
        return false;
    }
    if (!PyArray_Check(translation))
    {
        Py_DECREF(translation);
        PyErr_SetString(PyExc_ValueError,
            "transform_point did not return a NumPy array");
        return false; 
    }
    if (PyArray_NDIM(translation)!=1 || PyArray_DIM(translation, 0)!=2)
    {
        Py_DECREF(translation);
        PyErr_SetString(PyExc_ValueError,
            "transform_point did not return an approriate array");
        return false; 
    }
    tx = (CGFloat)(*(double*)PyArray_GETPTR1(translation, 0));
    ty = (CGFloat)(*(double*)PyArray_GETPTR1(translation, 1));
    Py_DECREF(translation);
    CGContextTranslateCTM(cr, tx, ty);
    return true;
}

static PyObject*
GraphicsContext_draw_path_collection (GraphicsContext* self, PyObject* args)
{
    PyObject* master_transform;
    PyObject* cliprect;
    PyObject* clippath;
    PyObject* clippath_transform;
    PyObject* paths;
    PyObject* transforms;
    PyObject* offsets;
    PyObject* offset_transform;
    PyObject* facecolors;
    PyObject* edgecolors;
    PyObject* linewidths;
    PyObject* linestyles;
    PyObject* antialiaseds;

    CGContextRef cr = self->cr;

    if (!cr)
    {
        PyErr_SetString(PyExc_RuntimeError, "CGContextRef is NULL");
        return NULL;
    }

    if(!PyArg_ParseTuple(args, "OOOOOOOOOOOOO", &master_transform,
                                                &cliprect,
                                                &clippath,
                                                &clippath_transform,
                                                &paths,
                                                &transforms,
                                                &offsets,
                                                &offset_transform,
                                                &facecolors,
                                                &edgecolors,
                                                &linewidths,
                                                &linestyles,
                                                &antialiaseds))
        return NULL;

    int ok = 1;
    Py_ssize_t i;
    Py_ssize_t Np = 0;
    Py_ssize_t N = 0;

    CGMutablePathRef* p = NULL;

    /* --------- Prepare some variables for the path iterator ------------- */
    void* iterator;
    double rect[4] = {0.0, 0.0, self->size.width, self->size.height};
    enum e_quantize_mode mode;
    ok = _get_snap(self, &mode);
    if (!ok)
    {
        return NULL;
    }

    /* ------------------- Check paths ------------------------------------ */

    if (!PySequence_Check(paths))
    {
        PyErr_SetString(PyExc_ValueError, "paths must be a sequence object");
        return NULL;
    }
    const Py_ssize_t Npaths = PySequence_Size(paths);

    /* ------------------- Check transforms ------------------------------- */

    if (!PySequence_Check(transforms))
    {
        PyErr_SetString(PyExc_ValueError, "transforms must be a sequence object");
        return NULL;
    }
    Py_ssize_t Ntransforms = PySequence_Size(transforms);

    CGContextSaveGState(cr);
    /* ------------------- Set master transform --------------------------- */

    if (Ntransforms)
    {
        CGAffineTransform master;
        double a, b, c, d, tx, ty;
        PyObject* values = PyObject_CallMethod(master_transform, "to_values", "");
        if (!values)
        {
            ok = 0;
            goto exit;
        }
        if (!PyTuple_Check(values))
        {
            Py_DECREF(values);
            ok = 0;
            goto exit;
        }
        /* CGAffineTransform contains CGFloat; cannot use master directly */
        ok = PyArg_ParseTuple(values, "dddddd", &a, &b, &c, &d, &tx, &ty);
        Py_DECREF(values);
        master.a = a;
        master.b = b;
        master.c = c;
        master.d = d;
        master.tx = tx;
	master.ty = ty;
        if (!ok) goto exit;
        CGContextConcatCTM(cr, master);
    }

    /* ------------------- Check offsets array ---------------------------- */

    offsets = PyArray_FromObject(offsets, NPY_DOUBLE, 0, 2);
    if (!offsets ||
        (PyArray_NDIM(offsets)==2 && PyArray_DIM(offsets, 1)!=2) ||
        (PyArray_NDIM(offsets)==1 && PyArray_DIM(offsets, 0)!=0))
    {
        PyErr_SetString(PyExc_ValueError, "Offsets array must be Nx2");
        ok = 0;
        goto exit;
    }
    const Py_ssize_t Noffsets = PyArray_DIM(offsets, 0);

    /* -------------------------------------------------------------------- */

    Np = Npaths > Ntransforms ? Npaths : Ntransforms;
    N = Np > Noffsets ? Np : Noffsets;
    if (N < Ntransforms) Ntransforms = N;

    p = malloc(Np*sizeof(CGMutablePathRef));
    if (!p)
    {
        ok = 0;
        goto exit;
    }
    for (i = 0; i < Np; i++)
    {
        PyObject* path;
        PyObject* transform;
        p[i] = NULL;
        path = PySequence_ITEM(paths, i % Npaths);
        if (!path)
        {
            ok = 0;
            goto exit;
        }
        if (Ntransforms)
        {
            transform = PySequence_ITEM(transforms, i % Ntransforms);
            if (!transform)
            {
                PyErr_SetString(PyExc_RuntimeError,
                                "failed to obtain transform");
                ok = 0;
                goto exit;
            }
            iterator = get_path_iterator(path,
                                         transform,
                                         1,
                                         0,
                                         rect,
                                         mode,
                                         0);
            Py_DECREF(transform);
        }
        else
        {
            iterator = get_path_iterator(path,
                                         master_transform,
                                         1,
                                         0,
                                         rect,
                                         mode,
                                         0);
        }
        Py_DECREF(path);
        if (!iterator)
        {
            PyErr_SetString(PyExc_RuntimeError,
                            "failed to obtain path iterator");
            ok = 0;
            goto exit;
        }
        p[i] = _create_path(iterator);
        free_path_iterator(iterator);
        if (!p[i])
        {
            PyErr_SetString(PyExc_RuntimeError, "failed to create path");
            ok = 0;
            goto exit;
        }
    }

    /* ------------------- Set clipping path ------------------------------ */

    if (!_clip(cr, cliprect))
    {
        ok = 0;
        goto exit;
    }
    if (clippath!=Py_None)
    {
        int n;
        iterator  = get_path_iterator(clippath,
                                      clippath_transform,
                                      0,
                                      0,
                                      rect,
                                      QUANTIZE_AUTO,
                                      0);
        if (!iterator)
        {
            PyErr_SetString(PyExc_RuntimeError,
                "draw_path_collection: failed to obtain path iterator for clipping");
            ok = 0;
            goto exit;
        }
        n = _draw_path(cr, iterator);
        free_path_iterator(iterator);
        if (n > 0) CGContextClip(cr);
    }

    /* ------------------- Check facecolors array ------------------------- */

    facecolors = PyArray_FromObject(facecolors, NPY_DOUBLE, 1, 2);
    if (!facecolors ||
        (PyArray_NDIM(facecolors)==1 && PyArray_DIM(facecolors, 0)!=0) ||
        (PyArray_NDIM(facecolors)==2 && PyArray_DIM(facecolors, 1)!=4))
    {
        PyErr_SetString(PyExc_ValueError, "Facecolors must by a Nx4 numpy array or empty");
        ok = 0;
        goto exit;
    }

    /* ------------------- Check edgecolors array ------------------------- */

    edgecolors = PyArray_FromObject(edgecolors, NPY_DOUBLE, 1, 2);
    if (!edgecolors ||
        (PyArray_NDIM(edgecolors)==1 && PyArray_DIM(edgecolors, 0)!=0) ||
        (PyArray_NDIM(edgecolors)==2 && PyArray_DIM(edgecolors, 1)!=4))
    {
        PyErr_SetString(PyExc_ValueError, "Edgecolors must by a Nx4 numpy array or empty");
        ok = 0;
        goto exit;
    }

    /* ------------------- Check the other arguments ---------------------- */

    if (!PySequence_Check(linewidths))
    {
        PyErr_SetString(PyExc_ValueError, "linewidths must be a sequence object");
        ok = 0;
        goto exit;
    }
    if (!PySequence_Check(linestyles))
    {
        PyErr_SetString(PyExc_ValueError, "linestyles must be a sequence object");
        ok = 0;
        goto exit;
    }
    if (!PySequence_Check(antialiaseds))
    {
        PyErr_SetString(PyExc_ValueError, "antialiaseds must be a sequence object");
        ok = 0;
        goto exit;
    }

    Py_ssize_t Nfacecolors = PyArray_DIM(facecolors, 0);
    Py_ssize_t Nedgecolors = PyArray_DIM(edgecolors, 0);
    Py_ssize_t Nlinewidths = PySequence_Size(linewidths);
    Py_ssize_t Nlinestyles = PySequence_Size(linestyles);
    Py_ssize_t Naa         = PySequence_Size(antialiaseds);
    if (N < Nlinestyles) Nlinestyles = N;
    if ((Nfacecolors == 0 && Nedgecolors == 0) || Np == 0) goto exit; 

    /* Preset graphics context properties if possible */
    if (Naa==1)
    {
        PyObject* antialiased = PySequence_ITEM(antialiaseds, 0);
        if (antialiased)
        {
            ok = _set_antialiased(cr, antialiased);
            Py_DECREF(antialiased);
        }
        else
        {
            PyErr_SetString(PyExc_SystemError,
                            "Failed to read element from antialiaseds array");
            ok = 0;
        }
        if (!ok) goto exit;
    }

    if (Nlinewidths==1)
    {
        PyObject* linewidth = PySequence_ITEM(linewidths, 0);
        if (!linewidth)
        {
            PyErr_SetString(PyExc_SystemError,
                            "Failed to read element from linewidths array");
            ok = 0;
            goto exit;
        }
        CGContextSetLineWidth(cr, (CGFloat)PyFloat_AsDouble(linewidth));
        Py_DECREF(linewidth);
    }
    else if (Nlinewidths==0)
        CGContextSetLineWidth(cr, 0.0);

    if (Nlinestyles==1)
    {
        PyObject* linestyle = PySequence_ITEM(linestyles, 0);
        if (!linestyle)
        {
            PyErr_SetString(PyExc_SystemError,
                            "Failed to read element from linestyles array");
            ok = 0;
            goto exit;
        }
        ok = _set_dashes(cr, linestyle);
        Py_DECREF(linestyle);
        if (!ok) goto exit;
    }

    if (Nedgecolors==1)
    {
        const double r = *(double*)PyArray_GETPTR2(edgecolors, 0, 0);
        const double g = *(double*)PyArray_GETPTR2(edgecolors, 0, 1);
        const double b = *(double*)PyArray_GETPTR2(edgecolors, 0, 2);
        const double a = *(double*)PyArray_GETPTR2(edgecolors, 0, 3);
        CGContextSetRGBStrokeColor(cr, r, g, b, a);
    }

    if (Nfacecolors==1)
    {
        const double r = *(double*)PyArray_GETPTR2(facecolors, 0, 0);
        const double g = *(double*)PyArray_GETPTR2(facecolors, 0, 1);
        const double b = *(double*)PyArray_GETPTR2(facecolors, 0, 2);
        const double a = *(double*)PyArray_GETPTR2(facecolors, 0, 3);
        CGContextSetRGBFillColor(cr, r, g, b, a);
    }

    for (i = 0; i < N; i++)
    {
        if (CGPathIsEmpty(p[i % Np])) continue;

        CGContextSaveGState(cr);
        if (Noffsets)
        {
            ok = _set_offset(cr, offsets, i % Noffsets, offset_transform);
            if (!ok)
            {
                CGContextRestoreGState(cr);
                goto exit;
            }
        }

        if (Naa > 1)
        {
            PyObject* antialiased = PySequence_ITEM(antialiaseds, i % Naa);
            if (antialiased)
            {
                ok = _set_antialiased(cr, antialiased);
                Py_DECREF(antialiased);
            }
            else
            {
                PyErr_SetString(PyExc_SystemError,
                    "Failed to read element from antialiaseds array");
                ok = 0;
            }
            if (!ok) goto exit;
        }

        if (Nlinewidths > 1)
        {
            PyObject* linewidth = PySequence_ITEM(linewidths, i % Nlinewidths);
            if (!linewidth)
            {
                PyErr_SetString(PyExc_SystemError,
                                "Failed to read element from linewidths array");
                ok = 0;
                goto exit;
            }
            CGContextSetLineWidth(cr, (CGFloat)PyFloat_AsDouble(linewidth));
            Py_DECREF(linewidth);
        }

        if (Nlinestyles > 1)
        {
            PyObject* linestyle = PySequence_ITEM(linestyles, i % Nlinestyles);
            if (!linestyle)
            {
                PyErr_SetString(PyExc_SystemError,
                                "Failed to read element from linestyles array");
                ok = 0;
                goto exit;
            }
            ok = _set_dashes(cr, linestyle);
            Py_DECREF(linestyle);
            if (!ok) goto exit;
        }

        if (Nedgecolors > 1)
        {
            npy_intp fi = i % Nedgecolors;
            const double r = *(double*)PyArray_GETPTR2(edgecolors, fi, 0);
            const double g = *(double*)PyArray_GETPTR2(edgecolors, fi, 1);
            const double b = *(double*)PyArray_GETPTR2(edgecolors, fi, 2);
            const double a = *(double*)PyArray_GETPTR2(edgecolors, fi, 3);
            CGContextSetRGBStrokeColor(cr, r, g, b, a);
        }

        CGContextAddPath(cr, p[i % Np]);

        if (Nfacecolors > 1)
        {
            npy_intp fi = i % Nfacecolors;
            const double r = *(double*)PyArray_GETPTR2(facecolors, fi, 0);
            const double g = *(double*)PyArray_GETPTR2(facecolors, fi, 1);
            const double b = *(double*)PyArray_GETPTR2(facecolors, fi, 2);
            const double a = *(double*)PyArray_GETPTR2(facecolors, fi, 3);
            CGContextSetRGBFillColor(cr, r, g, b, a);
            if (Nedgecolors > 0) CGContextDrawPath(cr, kCGPathFillStroke);
            else CGContextFillPath(cr);
        }
        else if (Nfacecolors==1)
        {
            if (Nedgecolors > 0) CGContextDrawPath(cr, kCGPathFillStroke);
            else CGContextFillPath(cr);
        }
        else /* We checked Nedgecolors != 0 above */
            CGContextStrokePath(cr);
        CGContextRestoreGState(cr);
    }

exit:
    CGContextRestoreGState(cr);
    Py_XDECREF(offsets);
    Py_XDECREF(facecolors);
    Py_XDECREF(edgecolors);
    if (p)
    {
        for (i = 0; i < Np; i++)
        {
            if (!p[i]) break;
            CGPathRelease(p[i]);
        }
        free(p);
    }
    if (!ok) return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
GraphicsContext_draw_quad_mesh (GraphicsContext* self, PyObject* args)
{
    PyObject* master_transform;
    PyObject* cliprect;
    PyObject* clippath;
    PyObject* clippath_transform;
    int meshWidth;
    int meshHeight;
    PyObject* coordinates;
    PyObject* offsets;
    PyObject* offset_transform;
    PyObject* facecolors;
    int antialiased;
    int showedges;

    CGContextRef cr = self->cr;

    if (!cr)
    {
        PyErr_SetString(PyExc_RuntimeError, "CGContextRef is NULL");
        return NULL;
    }

    if(!PyArg_ParseTuple(args, "OOOOiiOOOOii",
                               &master_transform,
                               &cliprect,
                               &clippath,
                               &clippath_transform,
                               &meshWidth,
                               &meshHeight,
                               &coordinates,
                               &offsets,
                               &offset_transform,
                               &facecolors,
                               &antialiased,
                               &showedges)) return NULL;

    int ok = 1;
    CGContextSaveGState(cr);

    CGAffineTransform master;
    double rect[4] = {0.0, 0.0, self->size.width, self->size.height};

    /* ------------------- Set master transform --------------------------- */

    PyObject* values = PyObject_CallMethod(master_transform, "to_values", "");
    if (!values)
    {
        ok = 0;
        goto exit;
    }
    if (PyTuple_Check(values))
    {
        double a, b, c, d, tx, ty;
        /* CGAffineTransform contains CGFloat; cannot use master directly */
        ok = PyArg_ParseTuple(values, "dddddd", &a, &b, &c, &d, &tx, &ty);
        master.a = a;
        master.b = b;
        master.c = c;
        master.d = d;
        master.tx = tx;
	master.ty = ty;
    }
    else
    {
        ok = 0;
    }
    Py_DECREF(values);
    if (!ok) goto exit;
    CGContextConcatCTM(cr, master);

    /* ------------------- Set clipping path ------------------------------ */

    ok = _clip(cr, cliprect);
    if (!ok) goto exit;
    if (clippath!=Py_None)
    {
        int n;
        void* iterator  = get_path_iterator(clippath,
                                            clippath_transform,
                                            0,
                                            0,
                                            rect,
                                            QUANTIZE_AUTO,
                                            0);
        if (iterator)
        {
            PyErr_SetString(PyExc_RuntimeError,
                "draw_quad_mesh: failed to obtain path iterator");
            ok = 0;
            goto exit;
        }
        n = _draw_path(cr, iterator);
        free_path_iterator(iterator);
        if (n > 0) CGContextClip(cr);
    }

    /* ------------------- Check coordinates array ------------------------ */

    coordinates = PyArray_FromObject(coordinates, NPY_DOUBLE, 3, 3);
    if (!coordinates ||
        PyArray_NDIM(coordinates) != 3 || PyArray_DIM(coordinates, 2) != 2)
    {
        PyErr_SetString(PyExc_ValueError, "Invalid coordinates array");
        ok = 0;
        goto exit;
    }

    /* ------------------- Check offsets array ---------------------------- */

    offsets = PyArray_FromObject(offsets, NPY_DOUBLE, 0, 2);
    if (!offsets ||
        (PyArray_NDIM(offsets)==2 && PyArray_DIM(offsets, 1)!=2) ||
        (PyArray_NDIM(offsets)==1 && PyArray_DIM(offsets, 0)!=0))
    {
        PyErr_SetString(PyExc_ValueError, "Offsets array must be Nx2");
        ok = 0;
        goto exit;
    }
    const Py_ssize_t Noffsets = PyArray_DIM(offsets, 0);

    /* ------------------- Check facecolors array ------------------------- */

    facecolors = PyArray_FromObject(facecolors, NPY_DOUBLE, 1, 2);
    if (!facecolors ||
        (PyArray_NDIM(facecolors)==1 && PyArray_DIM(facecolors, 0)!=0) ||
        (PyArray_NDIM(facecolors)==2 && PyArray_DIM(facecolors, 1)!=4))
    {
        PyErr_SetString(PyExc_ValueError, "Facecolors must by a Nx4 numpy array or empty");
        ok = 0;
        goto exit;
    }

    /* ------------------- Check the other arguments ---------------------- */

    size_t Npaths      = meshWidth * meshHeight;
    size_t Nfacecolors = (size_t) PyArray_DIM(facecolors, 0);
    if ((Nfacecolors == 0 && !showedges) || Npaths == 0)
    {
        /* Nothing to do here */
        goto exit;
    }

    size_t i = 0;
    size_t iw = 0;
    size_t ih = 0;

    /* Preset graphics context properties if possible */
    CGContextSetShouldAntialias(cr, antialiased);

    CGContextSetLineWidth(cr, 0.0);

    if (Nfacecolors==1)
    {
        const double r = *(double*)PyArray_GETPTR2(facecolors, 0, 0);
        const double g = *(double*)PyArray_GETPTR2(facecolors, 0, 1);
        const double b = *(double*)PyArray_GETPTR2(facecolors, 0, 2);
        const double a = *(double*)PyArray_GETPTR2(facecolors, 0, 3);
        CGContextSetRGBFillColor(cr, r, g, b, a);
        if (antialiased && !showedges)
        {
            CGContextSetRGBStrokeColor(cr, r, g, b, a);
        }
    }

    if (showedges)
    {
        CGContextSetRGBStrokeColor(cr, 0, 0, 0, 1);
    }

    double x, y;
    for (ih = 0; ih < meshHeight; ih++)
    {
        for (iw = 0; iw < meshWidth; iw++, i++)
        {
            CGContextSaveGState(cr);
            if (Noffsets)
            {
                ok = _set_offset(cr, offsets, i % Noffsets, offset_transform);
                if (!ok)
                {
                    CGContextRestoreGState(cr);
                    goto exit;
                }
            }

            CGPoint points[4];

            x = *(double*)PyArray_GETPTR3(coordinates, ih, iw, 0);
            y = *(double*)PyArray_GETPTR3(coordinates, ih, iw, 1);
            if (isnan(x) || isnan(y)) continue;
            points[0].x = (CGFloat)x;
            points[0].y = (CGFloat)y;

            x = *(double*)PyArray_GETPTR3(coordinates, ih, iw+1, 0);
            y = *(double*)PyArray_GETPTR3(coordinates, ih, iw+1, 1);
            if (isnan(x) || isnan(y)) continue;
            points[1].x = (CGFloat)x;
            points[1].y = (CGFloat)y;

            x = *(double*)PyArray_GETPTR3(coordinates, ih+1, iw+1, 0);
            y = *(double*)PyArray_GETPTR3(coordinates, ih+1, iw+1, 1);
            if (isnan(x) || isnan(y)) continue;
            points[2].x = (CGFloat)x;
            points[2].y = (CGFloat)y;

            x = *(double*)PyArray_GETPTR3(coordinates, ih+1, iw, 0);
            y = *(double*)PyArray_GETPTR3(coordinates, ih+1, iw, 1);
            if (isnan(x) || isnan(y)) continue;
            points[3].x = (CGFloat)x;
            points[3].y = (CGFloat)y;

            CGContextMoveToPoint(cr, points[3].x, points[3].y);
            CGContextAddLines(cr, points, 4);

            if (Nfacecolors > 1)
            {
                npy_intp fi = i % Nfacecolors;
                const double r = *(double*)PyArray_GETPTR2(facecolors, fi, 0);
                const double g = *(double*)PyArray_GETPTR2(facecolors, fi, 1);
                const double b = *(double*)PyArray_GETPTR2(facecolors, fi, 2);
                const double a = *(double*)PyArray_GETPTR2(facecolors, fi, 3);
                CGContextSetRGBFillColor(cr, r, g, b, a);
                if (showedges)
                {
                    CGContextDrawPath(cr, kCGPathFillStroke);
                }
                else if (antialiased)
                {
                    CGContextSetRGBStrokeColor(cr, r, g, b, a);
                    CGContextDrawPath(cr, kCGPathFillStroke);
                }
                else
                {
                    CGContextFillPath(cr);
                }
            }
            else if (Nfacecolors==1)
            {
                if (showedges || antialiased)
                {
                    CGContextDrawPath(cr, kCGPathFillStroke);
                }
                else
                {
                    CGContextFillPath(cr);
                }
            }
            else if (showedges)
            {
                CGContextStrokePath(cr);
            }
            CGContextRestoreGState(cr);
        }
    }

exit:
    CGContextRestoreGState(cr);
    Py_XDECREF(offsets);
    Py_XDECREF(facecolors);
    Py_XDECREF(coordinates);

    if (!ok) return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}


#ifdef COMPILING_FOR_10_5
static CTFontRef
#else
static ATSFontRef
#endif
setfont(CGContextRef cr, PyObject* family, float size, const char weight[],
        const char italic[])
{
#define NMAP 40
#define NFONT 31
    int i, j, n;
    const char* temp;
    const char* name = "Times-Roman";
    CFStringRef string;
#ifdef COMPILING_FOR_10_5
    CTFontRef font = 0;
#else
    ATSFontRef font = 0;
#endif

    const int k = (strcmp(italic, "italic") ? 0 : 2)
                + (strcmp(weight, "bold") ? 0 : 1);

    struct {char* name; int index;} map[NMAP] = {
        {"New Century Schoolbook", 0},
        {"Century Schoolbook L", 0},
        {"Utopia", 1},
        {"ITC Bookman", 2},
        {"Bookman", 2},
        {"Bitstream Vera Serif", 3},
        {"Nimbus Roman No9 L", 4},
        {"Times New Roman", 5},
        {"Times", 6},
        {"Palatino", 7},
        {"Charter", 8},
        {"serif", 0},
        {"Lucida Grande", 9},
        {"Verdana", 10},
        {"Geneva", 11},
        {"Lucida", 12},
        {"Bitstream Vera Sans", 13},
        {"Arial", 14},
        {"Helvetica", 15},
        {"Avant Garde", 16},
        {"sans-serif", 10},
        {"Apple Chancery", 17},
        {"Textile", 18},
        {"Zapf Chancery", 19},
        {"Sand", 20},
        {"cursive", 17},
        {"Comic Sans MS", 21},
        {"Chicago", 22},
        {"Charcoal", 23},
        {"Impact", 24},
        {"Western", 25},
        {"fantasy", 21},
        {"Andale Mono", 26},
        {"Bitstream Vera Sans Mono", 27},
        {"Nimbus Mono L", 28},
        {"Courier", 29},
        {"Courier New", 30},
        {"Fixed", 30},
        {"Terminal", 30},
        {"monospace", 30},
    };

    const char* psnames[NFONT][4] = {
      {"CenturySchoolbook",                   /* 0 */
       "CenturySchoolbook-Bold",
       "CenturySchoolbook-Italic",
       "CenturySchoolbook-BoldItalic"},
      {"Utopia",                              /* 1 */
       "Utopia-Bold",
       "Utopia-Italic",
       "Utopia-BoldItalic"},
      {"Bookman-Light",                       /* 2 */
       "Bookman-Bold",
       "Bookman-LightItalic",
       "Bookman-BoldItalic"},
      {"BitstreamVeraSerif-Roman",            /* 3 */
       "BitstreamVeraSerif-Bold",
       "",
       ""},
      {"NimbusRomNo9L-Reg",                   /* 4 */
       "NimbusRomNo9T-Bol",
       "NimbusRomNo9L-RegIta",
       "NimbusRomNo9T-BolIta"},
      {"TimesNewRomanPSMT",                   /* 5 */
       "TimesNewRomanPS-BoldMT",
       "TimesNewRomanPS-ItalicMT",
       "TimesNewRomanPS-BoldItalicMT"},
      {"Times-Roman",                         /* 6 */
       "Times-Bold",
       "Times-Italic",
       "Times-BoldItalic"},
      {"Palatino-Roman",                      /* 7 */
       "Palatino-Bold",
       "Palatino-Italic",
       "Palatino-BoldItalic"},
      {"CharterBT-Roman",                     /* 8 */
       "CharterBT-Bold",
       "CharterBT-Italic",
       "CharterBT-BoldItalic"},
      {"LucidaGrande",                        /* 9 */
       "LucidaGrande-Bold",
       "",
       ""},
      {"Verdana",                            /* 10 */
       "Verdana-Bold",
       "Verdana-Italic",
       "Verdana-BoldItalic"},
      {"Geneva",                             /* 11 */
       "",
       "",
       ""},
      {"LucidaSans",                         /* 12 */
       "LucidaSans-Demi",
       "LucidaSans-Italic",
       "LucidaSans-DemiItalic"},
      {"BitstreamVeraSans-Roman",            /* 13 */
       "BitstreamVeraSans-Bold",
       "BitstreamVeraSans-Oblique",
       "BitstreamVeraSans-BoldOblique"},
      {"ArialMT",                            /* 14 */
       "Arial-BoldMT",
       "Arial-ItalicMT",
       "Arial-BoldItalicMT"},
      {"Helvetica",                          /* 15 */
       "Helvetica-Bold",
       "",
       ""},
      {"AvantGardeITC-Book",                 /* 16 */
       "AvantGardeITC-Demi",
       "AvantGardeITC-BookOblique",
       "AvantGardeITC-DemiOblique"},
      {"Apple-Chancery",                     /* 17 */
       "",
       "",
       ""},
      {"TextileRegular",                     /* 18 */
       "",
       "",
       ""},
      {"ZapfChancery-Roman",                 /* 19 */
       "ZapfChancery-Bold",
       "ZapfChancery-Italic",
       "ZapfChancery-MediumItalic"},
      {"SandRegular",                        /* 20 */
       "",
       "",
       ""},
      {"ComicSansMS",                        /* 21 */
       "ComicSansMS-Bold",
       "",
       ""},
      {"Chicago",                            /* 22 */
       "",
       "",
       ""},
      {"Charcoal",                           /* 23 */
       "",
       "",
       ""},
      {"Impact",                             /* 24 */
       "",
       "",
       ""},
      {"Playbill",                           /* 25 */
       "",
       "",
       ""},
      {"AndaleMono",                         /* 26 */
       "",
       "",
       ""},
      {"BitstreamVeraSansMono-Roman",        /* 27 */
       "BitstreamVeraSansMono-Bold",
       "BitstreamVeraSansMono-Oblique",
       "BitstreamVeraSansMono-BoldOb"},
      {"NimbusMonL-Reg",                     /* 28 */
       "NimbusMonL-Bol",
       "NimbusMonL-RegObl",
       "NimbusMonL-BolObl"},
      {"Courier",                            /* 29 */
       "Courier-Bold",
       "",
       ""},
      {"CourierNewPS",                       /* 30 */
       "CourierNewPS-BoldMT",
       "CourierNewPS-ItalicMT",
       "CourierNewPS-Bold-ItalicMT"},
    };

    if(!PyList_Check(family)) return 0;
    n = PyList_GET_SIZE(family);

    for (i = 0; i < n; i++)
    {
        PyObject* item = PyList_GET_ITEM(family, i);
        if(!PyString_Check(item)) return 0;
        temp = PyString_AS_STRING(item);
        for (j = 0; j < NMAP; j++)
        {    if (!strcmp(map[j].name, temp))
             {    temp = psnames[map[j].index][k];
                  break;
             }
        }
        /* If the font name is not found in mapping, we assume */
        /* that the user specified the Postscript name directly */

        /* Check if this font can be found on the system */
        string = CFStringCreateWithCString(kCFAllocatorDefault,
                                           temp,
                                           kCFStringEncodingMacRoman);
#ifdef COMPILING_FOR_10_5
        font = CTFontCreateWithName(string, size, NULL);
#else
        font = ATSFontFindFromPostScriptName(string, kATSOptionFlagsDefault);
#endif

        CFRelease(string);

        if(font)
        {
            name = temp;
            break;
        }
    }
    if(!font)
    {   string = CFStringCreateWithCString(kCFAllocatorDefault,
                                           name,
                                           kCFStringEncodingMacRoman);
#ifdef COMPILING_FOR_10_5
        font = CTFontCreateWithName(string, size, NULL);
#else
        font = ATSFontFindFromPostScriptName(string, kATSOptionFlagsDefault);
#endif
        CFRelease(string);
    }
#ifndef COMPILING_FOR_10_5
    CGContextSelectFont(cr, name, size, kCGEncodingMacRoman);
#endif
    return font;
}

#ifdef COMPILING_FOR_10_5
static PyObject*
GraphicsContext_draw_text (GraphicsContext* self, PyObject* args)
{
    float x;
    float y;
    const UniChar* text;
    int n;
    PyObject* family;
    float size;
    const char* weight;
    const char* italic;
    float angle;
    CTFontRef font;
    CGColorRef color;
    CGFloat descent;

    CFStringRef keys[2];
    CFTypeRef values[2];

    CGContextRef cr = self->cr;
    if (!cr)
    {
        PyErr_SetString(PyExc_RuntimeError, "CGContextRef is NULL");
        return NULL;
    }

    if(!PyArg_ParseTuple(args, "ffu#Ofssf",
                                &x,
                                &y,
                                &text,
                                &n,
                                &family,
                                &size,
                                &weight,
                                &italic,
                                &angle)) return NULL;

    font = setfont(cr, family, size, weight, italic);

    color = CGColorCreateGenericRGB(self->color[0],
                                    self->color[1],
                                    self->color[2],
                                    self->color[3]);

    keys[0] = kCTFontAttributeName;
    keys[1] = kCTForegroundColorAttributeName;
    values[0] = font;
    values[1] = color;
    CFDictionaryRef attributes = CFDictionaryCreate(kCFAllocatorDefault,
                                        (const void**)&keys,
                                        (const void**)&values,
                                        2,
                                        &kCFTypeDictionaryKeyCallBacks,
                                        &kCFTypeDictionaryValueCallBacks);
    CGColorRelease(color);
    CFRelease(font);

    CFStringRef s = CFStringCreateWithCharacters(kCFAllocatorDefault, text, n);

    CFAttributedStringRef string = CFAttributedStringCreate(kCFAllocatorDefault,
                                                            s,
                                                            attributes);
    CFRelease(s);
    CFRelease(attributes);

    CTLineRef line = CTLineCreateWithAttributedString(string);
    CFRelease(string);

    CTLineGetTypographicBounds(line, NULL, &descent, NULL);

    if (!line)
    {
        PyErr_SetString(PyExc_RuntimeError,
                        "CTLineCreateWithAttributedString failed");
        return NULL;
    }

    CGContextSetTextMatrix(cr, CGAffineTransformIdentity);
    if (angle)
    {
        CGContextSaveGState(cr);
        CGContextTranslateCTM(cr, x, y);
        CGContextRotateCTM(cr, angle*M_PI/180);
        CTLineDraw(line, cr);
        CGContextRestoreGState(cr);
    }
    else
    {
        CGContextSetTextPosition(cr, x, y);
        CTLineDraw(line, cr);
    }
    CFRelease(line);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
GraphicsContext_get_text_width_height_descent(GraphicsContext* self, PyObject* args)
{
    const UniChar* text;
    int n;
    PyObject* family;
    float size;
    const char* weight;
    const char* italic;

    CGFloat ascent;
    CGFloat descent;
    double width;
    CGRect rect;

    CTFontRef font;

    CGContextRef cr = self->cr;
    if (!cr)
    {
        PyErr_SetString(PyExc_RuntimeError, "CGContextRef is NULL");
        return NULL;
    }

    if(!PyArg_ParseTuple(args, "u#Ofss",
                         &text, &n, &family, &size, &weight, &italic))
        return NULL;

    font = setfont(cr, family, size, weight, italic);

    CFStringRef keys[1];
    CFTypeRef values[1];

    keys[0] = kCTFontAttributeName;
    values[0] = font;
    CFDictionaryRef attributes = CFDictionaryCreate(kCFAllocatorDefault,
                                        (const void**)&keys,
                                        (const void**)&values,
                                        1,
                                        &kCFTypeDictionaryKeyCallBacks,
                                        &kCFTypeDictionaryValueCallBacks);
    CFRelease(font);

    CFStringRef s = CFStringCreateWithCharacters(kCFAllocatorDefault, text, n);

    CFAttributedStringRef string = CFAttributedStringCreate(kCFAllocatorDefault,
                                                            s,
                                                            attributes);
    CFRelease(s);
    CFRelease(attributes);

    CTLineRef line = CTLineCreateWithAttributedString(string);
    CFRelease(string);

    if (!line)
    {
        PyErr_SetString(PyExc_RuntimeError,
                        "CTLineCreateWithAttributedString failed");
        return NULL;
    }

    width = CTLineGetTypographicBounds(line, &ascent, &descent, NULL);
    rect = CTLineGetImageBounds(line, cr);
 
    CFRelease(line);

    return Py_BuildValue("fff", width, rect.size.height, descent);
}

#else

static PyObject*
GraphicsContext_draw_text (GraphicsContext* self, PyObject* args)
{
    float x;
    float y;
    const UniChar* text;
    int n;
    PyObject* family;
    float size;
    const char* weight;
    const char* italic;
    float angle;
    ATSFontRef atsfont;
    CGContextRef cr = self->cr;
    if (!cr)
    {
        PyErr_SetString(PyExc_RuntimeError, "CGContextRef is NULL");
        return NULL;
    }

    if(!PyArg_ParseTuple(args, "ffu#Ofssf",
                                &x,
                                &y,
                                &text,
                                &n,
                                &family,
                                &size,
                                &weight,
                                &italic,
                                &angle)) return NULL;

    atsfont = setfont(cr, family, size, weight, italic);

    OSStatus status;

    ATSUAttributeTag tags[] =  {kATSUFontTag, kATSUSizeTag, kATSUQDBoldfaceTag};
    ByteCount sizes[] = {sizeof(ATSUFontID), sizeof(Fixed), sizeof(Boolean)};
    Fixed atsuSize = Long2Fix(size);
    Boolean isBold = FALSE; /* setfont takes care of this */

    ATSUAttributeValuePtr values[] = {&atsfont, &atsuSize, &isBold};
    status = ATSUSetAttributes(style, 3, tags, sizes, values);
    if (status!=noErr)
    {
        PyErr_SetString(PyExc_RuntimeError, "ATSUSetAttributes failed");
        return NULL;
    }

    status = ATSUSetTextPointerLocation(layout,
                    text,
                    kATSUFromTextBeginning,  /* offset from beginning */
                    kATSUToTextEnd,          /* length of text range */
                    n);                      /* length of text buffer */
    if (status!=noErr)
    {
        PyErr_SetString(PyExc_RuntimeError,
                        "ATSUCreateTextLayoutWithTextPtr failed");
        return NULL;
    }

    status = ATSUSetRunStyle(layout,
                             style,
                             kATSUFromTextBeginning,
                             kATSUToTextEnd);
    if (status!=noErr)
    {
        PyErr_SetString(PyExc_RuntimeError, "ATSUSetRunStyle failed");
        return NULL;
    }

    Fixed atsuAngle = X2Fix(angle);
    ATSUAttributeTag tags2[] = {kATSUCGContextTag, kATSULineRotationTag};
    ByteCount sizes2[] = {sizeof (CGContextRef), sizeof(Fixed)};
    ATSUAttributeValuePtr values2[] = {&cr, &atsuAngle};
    status = ATSUSetLayoutControls(layout, 2, tags2, sizes2, values2);
    if (status!=noErr)
    {
        PyErr_SetString(PyExc_RuntimeError, "ATSUSetLayoutControls failed");
        return NULL;
    }

    status = ATSUDrawText(layout,
                          kATSUFromTextBeginning,
                          kATSUToTextEnd,
                          X2Fix(x),
                          X2Fix(y));
    if (status!=noErr)
    {
        PyErr_SetString(PyExc_RuntimeError, "ATSUDrawText failed");
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
GraphicsContext_get_text_width_height_descent(GraphicsContext* self, PyObject* args)
{
    const UniChar* text;
    int n;
    PyObject* family;
    float size;
    const char* weight;
    const char* italic;

    ATSFontRef atsfont;

    CGContextRef cr = self->cr;
    if (!cr)
    {
        PyErr_SetString(PyExc_RuntimeError, "CGContextRef is NULL");
        return NULL;
    }

    if(!PyArg_ParseTuple(args, "u#Ofss", &text, &n, &family, &size, &weight, &italic)) return NULL;

    atsfont = setfont(cr, family, size, weight, italic);

    OSStatus status = noErr;
    ATSUAttributeTag tags[] = {kATSUFontTag,
                               kATSUSizeTag,
                               kATSUQDBoldfaceTag,
                               kATSUQDItalicTag};
    ByteCount sizes[] = {sizeof(ATSUFontID),
                         sizeof(Fixed),
                         sizeof(Boolean),
                         sizeof(Boolean)};
    Fixed atsuSize = Long2Fix(size);
    Boolean isBold = FALSE; /* setfont takes care of this */
    Boolean isItalic = FALSE; /* setfont takes care of this */
    ATSUAttributeValuePtr values[] = {&atsfont, &atsuSize, &isBold, &isItalic};

    status = ATSUSetAttributes(style, 4, tags, sizes, values);
    if (status!=noErr)
    {
        PyErr_SetString(PyExc_RuntimeError, "ATSUSetAttributes failed");
        return NULL;
    }

    status = ATSUSetTextPointerLocation(layout,
                    text,
                    kATSUFromTextBeginning,  /* offset from beginning */
                    kATSUToTextEnd,          /* length of text range */
                    n);                      /* length of text buffer */
    if (status!=noErr)
    {
        PyErr_SetString(PyExc_RuntimeError,
                        "ATSUCreateTextLayoutWithTextPtr failed");
        return NULL;
    }

    status = ATSUSetRunStyle(layout,
                             style,
                             kATSUFromTextBeginning,
                             kATSUToTextEnd);
    if (status!=noErr)
    {
        PyErr_SetString(PyExc_RuntimeError, "ATSUSetRunStyle failed");
        return NULL;
    }

    ATSUAttributeTag tag = kATSUCGContextTag;
    ByteCount bc = sizeof (CGContextRef);
    ATSUAttributeValuePtr value = &cr;
    status = ATSUSetLayoutControls(layout, 1, &tag, &bc, &value);
    if (status!=noErr)
    {
        PyErr_SetString(PyExc_RuntimeError, "ATSUSetLayoutControls failed");
        return NULL;
    }

    ATSUTextMeasurement before;
    ATSUTextMeasurement after;
    ATSUTextMeasurement ascent;
    ATSUTextMeasurement descent;
    status = ATSUGetUnjustifiedBounds(layout,
                                      kATSUFromTextBeginning, kATSUToTextEnd,
                                      &before, &after, &ascent, &descent);
    if (status!=noErr)
    {
        PyErr_SetString(PyExc_RuntimeError, "ATSUGetUnjustifiedBounds failed");
        return NULL;
    }

    const float width = FixedToFloat(after-before);
    const float height = FixedToFloat(ascent-descent);

    return Py_BuildValue("fff", width, height, FixedToFloat(descent));
}
#endif

static void _data_provider_release(void* info, const void* data, size_t size)
{
    PyObject* image = (PyObject*)info;
    Py_DECREF(image);
}

static PyObject*
GraphicsContext_draw_mathtext(GraphicsContext* self, PyObject* args)
{
    float x, y, angle;
    npy_intp nrows, ncols;
    int n;

    PyObject* object;
    PyArrayObject* image;

    CGContextRef cr = self->cr;
    if (!cr)
    {
        PyErr_SetString(PyExc_RuntimeError, "CGContextRef is NULL");
        return NULL;
    }

    if(!PyArg_ParseTuple(args, "fffO", &x, &y, &angle, &object)) return NULL;

    /* ------------- Check the image ---------------------------- */
    if(!PyArray_Check (object))
    {
        PyErr_SetString(PyExc_TypeError, "image should be a NumPy array.");
        return NULL;
    }
    image = (PyArrayObject*) object;
    if(PyArray_NDIM(image) != 2)
    {
        PyErr_Format(PyExc_TypeError,
                         "image has incorrect rank (%d expected 2)",
                         PyArray_NDIM(image));
        return NULL;
    }
    if (PyArray_TYPE(image) != NPY_UBYTE)
    {
        PyErr_SetString(PyExc_TypeError,
                        "image has incorrect type (should be uint8)");
        return NULL;
    }
    if (!PyArray_ISCONTIGUOUS(image))
    {
        PyErr_SetString(PyExc_TypeError, "image array is not contiguous");
        return NULL;
    }

    nrows = PyArray_DIM(image, 0);
    ncols = PyArray_DIM(image, 1);
    if (nrows != (int) nrows || ncols != (int) ncols)
    {
        PyErr_SetString(PyExc_RuntimeError, "bitmap image too large");
        return NULL;
    }
    n = nrows * ncols;
    Py_INCREF(object);

    const size_t bytesPerComponent = 1;
    const size_t bitsPerComponent = 8 * bytesPerComponent;
    const size_t nComponents = 1; /* gray */
    const size_t bitsPerPixel = bitsPerComponent * nComponents;
    const size_t bytesPerRow = nComponents * bytesPerComponent * ncols;
    CGDataProviderRef provider = CGDataProviderCreateWithData(object,
                                                              PyArray_DATA(image),
                                                              n,
                                                              _data_provider_release);
    CGImageRef bitmap = CGImageMaskCreate ((int) ncols,
                                           (int) nrows,
                                           bitsPerComponent,
                                           bitsPerPixel,
                                           bytesPerRow,
                                           provider,
                                           NULL,
                                           false);
    CGDataProviderRelease(provider);

    if(!bitmap)
    {
        PyErr_SetString(PyExc_RuntimeError, "CGImageMaskCreate failed");
        return NULL;
    }

    if (angle==0.0)
    {
        CGContextDrawImage(cr, CGRectMake(x,y,ncols,nrows), bitmap);
    }
    else
    {
        CGContextSaveGState(cr);
        CGContextTranslateCTM(cr, x, y);
        CGContextRotateCTM(cr, angle*M_PI/180);
        CGContextDrawImage(cr, CGRectMake(0,0,ncols,nrows), bitmap);
        CGContextRestoreGState(cr);
    }
    CGImageRelease(bitmap);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
GraphicsContext_draw_image(GraphicsContext* self, PyObject* args)
{
    float x, y;
    int nrows, ncols;
    const char* data;
    int n;
    PyObject* image;
    PyObject* cliprect;
    PyObject* clippath;
    PyObject* clippath_transform;

    CGContextRef cr = self->cr;
    if (!cr)
    {
        PyErr_SetString(PyExc_RuntimeError, "CGContextRef is NULL");
        return NULL;
    }

    if(!PyArg_ParseTuple(args, "ffiiOOOO", &x,
                                           &y,
                                           &nrows,
                                           &ncols,
                                           &image,
                                           &cliprect,
                                           &clippath,
                                           &clippath_transform)) return NULL;

    CGColorSpaceRef colorspace;
    CGDataProviderRef provider;
    double rect[4] = {0.0, 0.0, self->size.width, self->size.height};

    if (!PyString_Check(image))
    {
        PyErr_SetString(PyExc_RuntimeError, "image is not a string");
        return NULL;
    }

    const size_t bytesPerComponent = 1;
    const size_t bitsPerComponent = 8 * bytesPerComponent;
    const size_t nComponents = 4; /* red, green, blue, alpha */
    const size_t bitsPerPixel = bitsPerComponent * nComponents;
    const size_t bytesPerRow = nComponents * bytesPerComponent * ncols;

    colorspace = CGColorSpaceCreateWithName(kCGColorSpaceGenericRGB);
    if (!colorspace)
    {
        PyErr_SetString(PyExc_RuntimeError, "failed to create a color space");
        return NULL;
    }

    Py_INCREF(image);
    n = PyString_GET_SIZE(image);
    data = PyString_AsString(image);

    provider = CGDataProviderCreateWithData(image,
                                            data,
                                            n,
                                            _data_provider_release);
    CGImageRef bitmap = CGImageCreate (ncols,
                                       nrows,
                                       bitsPerComponent,
                                       bitsPerPixel,
                                       bytesPerRow,
                                       colorspace,
                                       kCGImageAlphaLast,
                                       provider,
                                       NULL,
                                       false,
                                       kCGRenderingIntentDefault);
    CGColorSpaceRelease(colorspace);
    CGDataProviderRelease(provider);

    if(!bitmap)
    {
        PyErr_SetString(PyExc_RuntimeError, "CGImageMaskCreate failed");
        return NULL;
    }

    BOOL ok = true;
    CGContextSaveGState(cr);
    if (!_clip(cr, cliprect)) ok = false;
    else if (clippath!=Py_None)
    {
        int n;
        void* iterator  = get_path_iterator(clippath,
                                            clippath_transform,
                                            0,
                                            0,
                                            rect,
                                            QUANTIZE_AUTO,
                                            0);
        if (iterator)
        {
            n = _draw_path(cr, iterator);
            free_path_iterator(iterator);
            if (n > 0) CGContextClip(cr);
        }
        else
        {
            PyErr_SetString(PyExc_RuntimeError,
                "draw_image: failed to obtain path iterator for clipping");
            ok = false;
        }
    }

    if (ok) CGContextDrawImage(cr, CGRectMake(x,y,ncols,nrows), bitmap);

    CGImageRelease(bitmap);
    CGContextRestoreGState(cr);

    if (!ok) return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}


static PyMethodDef GraphicsContext_methods[] = {
    {"save",
     (PyCFunction)GraphicsContext_save,
     METH_NOARGS,
     "Saves the current graphics context onto the stack."
    },
    {"restore",
     (PyCFunction)GraphicsContext_restore,
     METH_NOARGS,
     "Restores the current graphics context from the stack."
    },
    {"get_text_width_height_descent",
     (PyCFunction)GraphicsContext_get_text_width_height_descent,
     METH_VARARGS,
     "Returns the width, height, and descent of the text."
    },
    {"set_alpha",
     (PyCFunction)GraphicsContext_set_alpha,
      METH_VARARGS,
     "Sets the opacitiy level for objects drawn in a graphics context"
    },
    {"set_antialiased",
     (PyCFunction)GraphicsContext_set_antialiased,
     METH_VARARGS,
     "Sets anti-aliasing on or off for a graphics context."
    },
    {"set_capstyle",
     (PyCFunction)GraphicsContext_set_capstyle,
     METH_VARARGS,
     "Sets the style for the endpoints of lines in a graphics context."
    },
    {"set_clip_rectangle",
     (PyCFunction)GraphicsContext_set_clip_rectangle,
     METH_VARARGS,
     "Sets the clipping path to the area defined by the specified rectangle."
    },
    {"set_clip_path",
     (PyCFunction)GraphicsContext_set_clip_path,
     METH_VARARGS,
     "Sets the clipping path."
    },
    {"set_dashes",
     (PyCFunction)GraphicsContext_set_dashes,
     METH_VARARGS,
     "Sets the pattern for dashed lines in a graphics context."
    },
    {"set_foreground",
     (PyCFunction)GraphicsContext_set_foreground,
     METH_VARARGS,
     "Sets the current stroke and fill color to a value in the DeviceRGB color space."
    },
    {"set_graylevel",
     (PyCFunction)GraphicsContext_set_graylevel,
     METH_VARARGS,
     "Sets the current stroke and fill color to a value in the DeviceGray color space."
    },
    {"set_linewidth",
     (PyCFunction)GraphicsContext_set_linewidth,
     METH_VARARGS,
     "Sets the line width for a graphics context."
    },
    {"set_joinstyle",
     (PyCFunction)GraphicsContext_set_joinstyle,
     METH_VARARGS,
     "Sets the style for the joins of connected lines in a graphics context."
    },
    {"draw_path",
     (PyCFunction)GraphicsContext_draw_path,
     METH_VARARGS,
     "Draw a path in the graphics context and strokes and (if rgbFace is not None) fills it."
    },
    {"draw_markers",
     (PyCFunction)GraphicsContext_draw_markers,
     METH_VARARGS,
     "Draws a marker in the graphics context at each of the vertices in path."
    },
    {"draw_path_collection",
     (PyCFunction)GraphicsContext_draw_path_collection,
     METH_VARARGS,
     "Draw a collection of paths in the graphics context."
    },
    {"draw_quad_mesh",
     (PyCFunction)GraphicsContext_draw_quad_mesh,
     METH_VARARGS,
     "Draws a mesh in the graphics context."
    },
    {"draw_text",
     (PyCFunction)GraphicsContext_draw_text,
     METH_VARARGS,
     "Draw a string at (x,y) with the given properties in the graphics context."
    },
    {"draw_mathtext",
     (PyCFunction)GraphicsContext_draw_mathtext,
     METH_VARARGS,
     "Draw a TeX string at (x,y) as a bitmap in the graphics context."
    },
    {"draw_image",
     (PyCFunction)GraphicsContext_draw_image,
     METH_VARARGS,
     "Draw an image at (x,y) in the graphics context."
    },
    {NULL}  /* Sentinel */
};

static char GraphicsContext_doc[] =
"A GraphicsContext object wraps a Quartz 2D graphics context\n"
"(CGContextRef). Most methods either draw into the graphics context\n"
"(moveto, lineto, etc.) or set the drawing properties (set_linewidth,\n"
"set_joinstyle, etc.).\n";

static PyTypeObject GraphicsContextType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "_macosx.GraphicsContext", /*tp_name*/
    sizeof(GraphicsContext),   /*tp_basicsize*/
    0,                         /*tp_itemsize*/
#ifdef COMPILING_FOR_10_5
    0,                         /*tp_dealloc*/
#else
    (destructor)GraphicsContext_dealloc,     /*tp_dealloc*/
#endif
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    (reprfunc)GraphicsContext_repr,     /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,        /*tp_flags*/
    GraphicsContext_doc,       /* tp_doc */
    0,                         /* tp_traverse */
    0,                         /* tp_clear */
    0,                         /* tp_richcompare */
    0,                         /* tp_weaklistoffset */
    0,                         /* tp_iter */
    0,                         /* tp_iternext */
    GraphicsContext_methods,   /* tp_methods */
    0,                         /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    0,                         /* tp_init */
    0,                         /* tp_alloc */
    GraphicsContext_new,       /* tp_new */
};

typedef struct {
    PyObject_HEAD
    View* view;
} FigureCanvas;

static PyObject*
FigureCanvas_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    FigureCanvas *self = (FigureCanvas*)type->tp_alloc(type, 0);
    if (!self) return NULL;
    self->view = [View alloc];
    return (PyObject*)self;
}

static int
FigureCanvas_init(FigureCanvas *self, PyObject *args, PyObject *kwds)
{
    int width;
    int height;
    if(!self->view)
    {
        PyErr_SetString(PyExc_RuntimeError, "NSView* is NULL");
        return -1;
    }

    if(!PyArg_ParseTuple(args, "ii", &width, &height)) return -1;

    NSRect rect = NSMakeRect(0.0, 0.0, width, height);
    self->view = [self->view initWithFrame: rect canvas: (PyObject*)self];
    return 0;
}

static PyObject*
FigureCanvas_repr(FigureCanvas* self)
{
    return PyString_FromFormat("FigureCanvas object %p wrapping NSView %p",
                               (void*)self, (void*)(self->view));
}

static PyObject*
FigureCanvas_draw(FigureCanvas* self)
{
    View* view = self->view;

    if(view) /* The figure may have been closed already */
    {
        /* Whereas drawRect creates its own autorelease pool, apparently
         * [view display] also needs one. Create and release it here. */
        NSAutoreleasePool* pool = [[NSAutoreleasePool alloc] init];
        [view display];
        [pool release];
    }

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
FigureCanvas_invalidate(FigureCanvas* self)
{
    View* view = self->view;
    if(!view)
    {
        PyErr_SetString(PyExc_RuntimeError, "NSView* is NULL");
        return NULL;
    }
    [view setNeedsDisplay: YES];
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
FigureCanvas_set_rubberband(FigureCanvas* self, PyObject *args)
{
    View* view = self->view;
    int x0, y0, x1, y1;
    NSRect rubberband;
    if(!view)
    {
        PyErr_SetString(PyExc_RuntimeError, "NSView* is NULL");
        return NULL;
    }
    if(!PyArg_ParseTuple(args, "iiii", &x0, &y0, &x1, &y1)) return NULL;
    if (x1 > x0)
    {
        rubberband.origin.x = x0;
        rubberband.size.width = x1 - x0;
    }
    else
    {
        rubberband.origin.x = x1;
        rubberband.size.width = x0 - x1;
    }
    if (y1 > y0)
    {
        rubberband.origin.y = y0;
        rubberband.size.height = y1 - y0;
    }
    else
    {
        rubberband.origin.y = y1;
        rubberband.size.height = y0 - y1;
    }
    [view setRubberband: rubberband];
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
FigureCanvas_remove_rubberband(FigureCanvas* self)
{
    View* view = self->view;
    if(!view)
    {
        PyErr_SetString(PyExc_RuntimeError, "NSView* is NULL");
        return NULL;
    }
    [view removeRubberband];
    Py_INCREF(Py_None);
    return Py_None;
}

static NSImage* _read_ppm_image(PyObject* obj)
{
    int width;
    int height;
    const char* data;
    int n;
    int i;
    NSBitmapImageRep* bitmap;
    unsigned char* bitmapdata;

    if (!obj) return NULL;
    if (!PyTuple_Check(obj)) return NULL;
    if (!PyArg_ParseTuple(obj, "iit#", &width, &height, &data, &n)) return NULL;
    if (width*height*3 != n) return NULL; /* RGB image uses 3 colors / pixel */

    bitmap = [[NSBitmapImageRep alloc]
                  initWithBitmapDataPlanes: NULL
                                pixelsWide: width
                                pixelsHigh: height
                             bitsPerSample: 8
                           samplesPerPixel: 3
                                  hasAlpha: NO
                                  isPlanar: NO
                            colorSpaceName: NSDeviceRGBColorSpace
                              bitmapFormat: 0
                               bytesPerRow: width*3
                               bitsPerPixel: 24];
    if (!bitmap) return NULL;
    bitmapdata = [bitmap bitmapData];
    for (i = 0; i < n; i++) bitmapdata[i] = data[i];

    NSSize size = NSMakeSize(width, height);
    NSImage* image = [[NSImage alloc] initWithSize: size];
    if (image) [image addRepresentation: bitmap];

    [bitmap release];

    return image;
}

static PyObject*
FigureCanvas_write_bitmap(FigureCanvas* self, PyObject* args)
{
    View* view = self->view;
    int n;
    const unichar* characters;
    NSSize size;
    double width, height;

    if(!view)
    {
        PyErr_SetString(PyExc_RuntimeError, "NSView* is NULL");
        return NULL;
    }
    /* NSSize contains CGFloat; cannot use size directly */
    if(!PyArg_ParseTuple(args, "u#dd",
				&characters, &n, &width, &height)) return NULL;
    size.width = width;
    size.height = height;

    /* This function may be called from inside the event loop, when an
     * autorelease pool is available, or from Python, when no autorelease
     * pool is available. To be able to handle the latter case, we need to
     * create an autorelease pool here. */

    NSAutoreleasePool* pool = [[NSAutoreleasePool alloc] init];

    NSRect rect = [view bounds];

    NSString* filename = [NSString stringWithCharacters: characters
						 length: (unsigned)n];
    NSString* extension = [filename pathExtension];

    /* Calling dataWithPDFInsideRect on the view causes its update status
     * to be cleared. Save the status here, and invalidate the view if not
     * up to date after calling dataWithPDFInsideRect. */
    const BOOL invalid = [view needsDisplay];
    NSData* data = [view dataWithPDFInsideRect: rect];
    if (invalid) [view setNeedsDisplay: YES];

    NSImage* image = [[NSImage alloc] initWithData: data];
    [image setScalesWhenResized: YES];
    [image setSize: size];
    data = [image TIFFRepresentation];
    [image release];

    if (! [extension isEqualToString: @"tiff"] &&
        ! [extension isEqualToString: @"tif"])
    {
	NSBitmapImageFileType filetype;
	NSBitmapImageRep* bitmapRep = [NSBitmapImageRep imageRepWithData: data];
	if ([extension isEqualToString: @"bmp"])
	    filetype = NSBMPFileType;
	else if ([extension isEqualToString: @"gif"])
	    filetype = NSGIFFileType;
	else if ([extension isEqualToString: @"jpg"] ||
	         [extension isEqualToString: @"jpeg"])
	    filetype = NSJPEGFileType;
	else if ([extension isEqualToString: @"png"])
	    filetype = NSPNGFileType;
	else
	{   PyErr_SetString(PyExc_ValueError, "Unknown file type");
	    return NULL;
	}

	data = [bitmapRep representationUsingType:filetype properties:nil];
    }

    [data writeToFile: filename atomically: YES];
    [pool release];

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
FigureCanvas_start_event_loop(FigureCanvas* self, PyObject* args, PyObject* keywords)
{
    float timeout = 0.0;

    static char* kwlist[] = {"timeout", NULL};
    if(!PyArg_ParseTupleAndKeywords(args, keywords, "f", kwlist, &timeout))
        return NULL;

    int error;
    int interrupted = 0;
    int channel[2];
    CFSocketRef sigint_socket = NULL;
    PyOS_sighandler_t py_sigint_handler = NULL;

    CFRunLoopRef runloop = CFRunLoopGetCurrent();

    error = pipe(channel);
    if (error==0)
    {
        CFSocketContext context = {0, NULL, NULL, NULL, NULL};
        fcntl(channel[1], F_SETFL, O_WRONLY | O_NONBLOCK);

        context.info = &interrupted;
        sigint_socket = CFSocketCreateWithNative(kCFAllocatorDefault,
                                                 channel[0],
                                                 kCFSocketReadCallBack,
                                                 _callback,
                                                 &context);
        if (sigint_socket)
        {
            CFRunLoopSourceRef source;
            source = CFSocketCreateRunLoopSource(kCFAllocatorDefault,
                                                 sigint_socket,
                                                 0);
            CFRelease(sigint_socket);
            if (source)
            {
                CFRunLoopAddSource(runloop, source, kCFRunLoopDefaultMode);
                CFRelease(source);
                sigint_fd = channel[1];
                py_sigint_handler = PyOS_setsig(SIGINT, _sigint_handler);
            }
        }
        else
            close(channel[0]);
    }

    NSAutoreleasePool* pool = [[NSAutoreleasePool alloc] init];
    NSDate* date =
        (timeout > 0.0) ? [NSDate dateWithTimeIntervalSinceNow: timeout]
                        : [NSDate distantFuture];
    while (true)
    {   NSEvent* event = [NSApp nextEventMatchingMask: NSAnyEventMask
                                            untilDate: date
                                               inMode: NSDefaultRunLoopMode
                                              dequeue: YES];
       if (!event || [event type]==NSApplicationDefined) break;
       [NSApp sendEvent: event];
    }
    [pool release];

    if (py_sigint_handler) PyOS_setsig(SIGINT, py_sigint_handler);

    if (sigint_socket) CFSocketInvalidate(sigint_socket);
    if (error==0) close(channel[1]);
    if (interrupted) raise(SIGINT);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
FigureCanvas_stop_event_loop(FigureCanvas* self)
{
    NSEvent* event = [NSEvent otherEventWithType: NSApplicationDefined
                                        location: NSZeroPoint
                                   modifierFlags: 0
                                       timestamp: 0.0
                                    windowNumber: 0
                                         context: nil
                                         subtype: STOP_EVENT_LOOP
                                           data1: 0
                                           data2: 0];
    [NSApp postEvent: event atStart: true];
    Py_INCREF(Py_None);
    return Py_None;
}

static PyMethodDef FigureCanvas_methods[] = {
    {"draw",
     (PyCFunction)FigureCanvas_draw,
     METH_NOARGS,
     "Draws the canvas."
    },
    {"invalidate",
     (PyCFunction)FigureCanvas_invalidate,
     METH_NOARGS,
     "Invalidates the canvas."
    },
    {"set_rubberband",
     (PyCFunction)FigureCanvas_set_rubberband,
     METH_VARARGS,
     "Specifies a new rubberband rectangle and invalidates it."
    },
    {"remove_rubberband",
     (PyCFunction)FigureCanvas_remove_rubberband,
     METH_NOARGS,
     "Removes the current rubberband rectangle."
    },
    {"write_bitmap",
     (PyCFunction)FigureCanvas_write_bitmap,
     METH_VARARGS,
     "Saves the figure to the specified file as a bitmap\n"
     "(bmp, gif, jpeg, or png).\n"
    },
    {"start_event_loop",
     (PyCFunction)FigureCanvas_start_event_loop,
     METH_KEYWORDS,
     "Runs the event loop until the timeout or until stop_event_loop is called.\n",
    },
    {"stop_event_loop",
     (PyCFunction)FigureCanvas_stop_event_loop,
     METH_KEYWORDS,
     "Stops the event loop that was started by start_event_loop.\n",
    },
    {NULL}  /* Sentinel */
};

static char FigureCanvas_doc[] =
"A FigureCanvas object wraps a Cocoa NSView object.\n";

static PyTypeObject FigureCanvasType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "_macosx.FigureCanvas",    /*tp_name*/
    sizeof(FigureCanvas),      /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    0,                         /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    (reprfunc)FigureCanvas_repr,     /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,        /*tp_flags*/
    FigureCanvas_doc,          /* tp_doc */
    0,                         /* tp_traverse */
    0,                         /* tp_clear */
    0,                         /* tp_richcompare */
    0,                         /* tp_weaklistoffset */
    0,                         /* tp_iter */
    0,                         /* tp_iternext */
    FigureCanvas_methods,      /* tp_methods */
    0,                         /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)FigureCanvas_init,      /* tp_init */
    0,                         /* tp_alloc */
    FigureCanvas_new,          /* tp_new */
};

typedef struct {
    PyObject_HEAD
    Window* window;
} FigureManager;

static PyObject*
FigureManager_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    Window* window = [Window alloc];
    if (!window) return NULL;
    FigureManager *self = (FigureManager*)type->tp_alloc(type, 0);
    if (!self)
    {
        [window release];
        return NULL;
    }
    self->window = window;
    return (PyObject*)self;
}

static int
FigureManager_init(FigureManager *self, PyObject *args, PyObject *kwds)
{
    NSRect rect;
    Window* window;
    View* view;
    const char* title;
    PyObject* size;
    int width, height;
    PyObject* obj;
    FigureCanvas* canvas;

    if(!self->window)
    {
        PyErr_SetString(PyExc_RuntimeError, "NSWindow* is NULL");
        return -1;
    }

    if(!PyArg_ParseTuple(args, "Os", &obj, &title)) return -1;

    canvas = (FigureCanvas*)obj;
    view = canvas->view;
    if (!view) /* Something really weird going on */
    {
        PyErr_SetString(PyExc_RuntimeError, "NSView* is NULL");
        return -1;
    }

    size = PyObject_CallMethod(obj, "get_width_height", "");
    if(!size) return -1;
    if(!PyArg_ParseTuple(size, "ii", &width, &height))
    {    Py_DECREF(size);
         return -1;
    }
    Py_DECREF(size);

    rect.origin.x = 100;
    rect.origin.y = 350;
    rect.size.height = height;
    rect.size.width = width;

    NSApp = [NSApplication sharedApplication];
    NSAutoreleasePool* pool = [[NSAutoreleasePool alloc] init];
    self->window = [self->window initWithContentRect: rect
                                         styleMask: NSTitledWindowMask
                                                  | NSClosableWindowMask
                                                  | NSResizableWindowMask
                                                  | NSMiniaturizableWindowMask
                                           backing: NSBackingStoreBuffered
                                             defer: YES
                                       withManager: (PyObject*)self];
    window = self->window;
    [window setTitle: [NSString stringWithCString: title
                                         encoding: NSASCIIStringEncoding]];

    [window setAcceptsMouseMovedEvents: YES];
    [window setDelegate: view];
    [window makeFirstResponder: view];
    [[window contentView] addSubview: view];
    [view release];
    [window makeKeyAndOrderFront: nil];

    nwin++;

    [pool release];
    return 0;
}

static PyObject*
FigureManager_repr(FigureManager* self)
{
    return PyString_FromFormat("FigureManager object %p wrapping NSWindow %p",
                               (void*) self, (void*)(self->window));
}

static void
FigureManager_dealloc(FigureManager* self)
{
    Window* window = self->window;
    if(window)
    {
        NSAutoreleasePool* pool = [[NSAutoreleasePool alloc] init];
        [window close];
        [pool release];
    }
    self->ob_type->tp_free((PyObject*)self);
}

static PyObject*
FigureManager_destroy(FigureManager* self)
{
    Window* window = self->window;
    if(window)
    {
        NSAutoreleasePool* pool = [[NSAutoreleasePool alloc] init];
        [window close];
        [pool release];
        self->window = NULL;
    }
    Py_INCREF(Py_None);
    return Py_None;
}

static PyMethodDef FigureManager_methods[] = {
    {"destroy",
     (PyCFunction)FigureManager_destroy,
     METH_NOARGS,
     "Closes the window associated with the figure manager."
    },
    {NULL}  /* Sentinel */
};

static char FigureManager_doc[] =
"A FigureManager object wraps a Cocoa NSWindow object.\n";

static PyTypeObject FigureManagerType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "_macosx.FigureManager",   /*tp_name*/
    sizeof(FigureManager),     /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)FigureManager_dealloc,     /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    (reprfunc)FigureManager_repr,     /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,        /*tp_flags*/
    FigureManager_doc,         /* tp_doc */
    0,                         /* tp_traverse */
    0,                         /* tp_clear */
    0,                         /* tp_richcompare */
    0,                         /* tp_weaklistoffset */
    0,                         /* tp_iter */
    0,                         /* tp_iternext */
    FigureManager_methods,     /* tp_methods */
    0,                         /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)FigureManager_init,      /* tp_init */
    0,                         /* tp_alloc */
    FigureManager_new,          /* tp_new */
};

@interface NavigationToolbarHandler : NSObject
{   PyObject* toolbar;
}
- (NavigationToolbarHandler*)initWithToolbar:(PyObject*)toolbar;
-(void)left:(id)sender;
-(void)right:(id)sender;
-(void)up:(id)sender;
-(void)down:(id)sender;
-(void)zoominx:(id)sender;
-(void)zoominy:(id)sender;
-(void)zoomoutx:(id)sender;
-(void)zoomouty:(id)sender;
@end

typedef struct {
    PyObject_HEAD
    NSPopUpButton* menu;
    NavigationToolbarHandler* handler;
} NavigationToolbar;

@implementation NavigationToolbarHandler
- (NavigationToolbarHandler*)initWithToolbar:(PyObject*)theToolbar
{   [self init];
    toolbar = theToolbar;
    return self;
}

-(void)left:(id)sender
{   PyObject* result;
    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    result = PyObject_CallMethod(toolbar, "panx", "i", -1);
    if(result)
        Py_DECREF(result);
    else
        PyErr_Print();
    PyGILState_Release(gstate);
}

-(void)right:(id)sender
{   PyObject* result;
    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    result = PyObject_CallMethod(toolbar, "panx", "i", 1);
    if(result)
        Py_DECREF(result);
    else
        PyErr_Print();
    PyGILState_Release(gstate);
}

-(void)up:(id)sender
{   PyObject* result;
    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    result = PyObject_CallMethod(toolbar, "pany", "i", 1);
    if(result)
        Py_DECREF(result);
    else
        PyErr_Print();
    PyGILState_Release(gstate);
}

-(void)down:(id)sender
{   PyObject* result;
    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    result = PyObject_CallMethod(toolbar, "pany", "i", -1);
    if(result)
        Py_DECREF(result);
    else
        PyErr_Print();
    PyGILState_Release(gstate);
}

-(void)zoominx:(id)sender
{   PyObject* result;
    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    result = PyObject_CallMethod(toolbar, "zoomx", "i", 1);
    if(result)
        Py_DECREF(result);
    else
        PyErr_Print();
    PyGILState_Release(gstate);
}

-(void)zoomoutx:(id)sender
{   PyObject* result;
    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    result = PyObject_CallMethod(toolbar, "zoomx", "i", -1);
    if(result)
        Py_DECREF(result);
    else
        PyErr_Print();
    PyGILState_Release(gstate);
}

-(void)zoominy:(id)sender
{   PyObject* result;
    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    result = PyObject_CallMethod(toolbar, "zoomy", "i", 1);
    if(result)
        Py_DECREF(result);
    else
        PyErr_Print();
    PyGILState_Release(gstate);
}

-(void)zoomouty:(id)sender
{   PyObject* result;
    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    result = PyObject_CallMethod(toolbar, "zoomy", "i", -1);
    if(result)
        Py_DECREF(result);
    else
        PyErr_Print();
    PyGILState_Release(gstate);
}

-(void)save_figure:(id)sender
{   PyObject* result;
    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    result = PyObject_CallMethod(toolbar, "save_figure", "");
    if(result)
        Py_DECREF(result);
    else
        PyErr_Print();
    PyGILState_Release(gstate);
}
@end

static PyObject*
NavigationToolbar_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    NavigationToolbarHandler* handler = [NavigationToolbarHandler alloc];
    if (!handler) return NULL;
    NavigationToolbar *self = (NavigationToolbar*)type->tp_alloc(type, 0);
    if (!self)
    {   [handler release];
        return NULL;
    }
    self->handler = handler;
    return (PyObject*)self;
}

static int
NavigationToolbar_init(NavigationToolbar *self, PyObject *args, PyObject *kwds)
{
    int i;
    NSRect rect;

    const float smallgap = 2;
    const float biggap = 10;
    const int height = 32;

    PyObject* images;
    PyObject* obj;

    FigureCanvas* canvas;
    View* view;

    obj = PyObject_GetAttrString((PyObject*)self, "canvas");
    if (obj==NULL)
    {
        PyErr_SetString(PyExc_AttributeError, "Attempt to install toolbar for NULL canvas");
        return -1;
    }
    Py_DECREF(obj); /* Don't increase the reference count */
    if (!PyObject_IsInstance(obj, (PyObject*) &FigureCanvasType))
    {
        PyErr_SetString(PyExc_TypeError, "Attempt to install toolbar for object that is not a FigureCanvas");
        return -1;
    }
    canvas = (FigureCanvas*)obj;
    view = canvas->view;
    if(!view)
    {
        PyErr_SetString(PyExc_RuntimeError, "NSView* is NULL");
        return -1;
    }

    if(!PyArg_ParseTuple(args, "O", &images)) return -1;
    if(!PyDict_Check(images)) return -1;

    NSAutoreleasePool* pool = [[NSAutoreleasePool alloc] init];
    NSRect bounds = [view bounds];
    NSWindow* window = [view window];

    bounds.origin.y += height;
    [view setFrame: bounds];

    bounds.size.height += height;
    [window setContentSize: bounds.size];

    char* imagenames[9] = {"stock_left",
                           "stock_right",
                           "stock_zoom-in",
                           "stock_zoom-out",
                           "stock_up",
                           "stock_down",
                           "stock_zoom-in",
                           "stock_zoom-out",
                           "stock_save_as"};

    NSString* tooltips[9] = {
        @"Pan left with click or wheel mouse (bidirectional)",
        @"Pan right with click or wheel mouse (bidirectional)",
        @"Zoom In X (shrink the x axis limits) with click or wheel mouse (bidirectional)",
        @"Zoom Out X (expand the x axis limits) with click or wheel mouse (bidirectional)",
        @"Pan up with click or wheel mouse (bidirectional)",
        @"Pan down with click or wheel mouse (bidirectional)",
        @"Zoom in Y (shrink the y axis limits) with click or wheel mouse (bidirectional)",
        @"Zoom Out Y (expand the y axis limits) with click or wheel mouse (bidirectional)",
        @"Save the figure"};

    SEL actions[9] = {@selector(left:),
                      @selector(right:),
                      @selector(zoominx:),
                      @selector(zoomoutx:),
                      @selector(up:),
                      @selector(down:),
                      @selector(zoominy:),
                      @selector(zoomouty:),
                      @selector(save_figure:)};

    SEL scroll_actions[9][2] = {{@selector(left:),    @selector(right:)},
                                {@selector(left:),    @selector(right:)},
                                {@selector(zoominx:), @selector(zoomoutx:)},
                                {@selector(zoominx:), @selector(zoomoutx:)},
                                {@selector(up:),      @selector(down:)},
                                {@selector(up:),      @selector(down:)},
                                {@selector(zoominy:), @selector(zoomouty:)},
                                {@selector(zoominy:), @selector(zoomouty:)},
                                {nil,nil},
                               };


    rect.size.width = 120;
    rect.size.height = 24;
    rect.origin.x = biggap;
    rect.origin.y = 0.5*(height - rect.size.height);
    self->menu = [[NSPopUpButton alloc] initWithFrame: rect
                                            pullsDown: YES];
    [self->menu setAutoenablesItems: NO];
    [[window contentView] addSubview: self->menu];
    [self->menu release];
    rect.origin.x += rect.size.width + biggap;
    rect.size.width = 24;

    self->handler = [self->handler initWithToolbar: (PyObject*)self];
    for (i = 0; i < 9; i++)
    {
        ScrollableButton* button;
        SEL scrollWheelUpAction = scroll_actions[i][0];
        SEL scrollWheelDownAction = scroll_actions[i][1];
        if (scrollWheelUpAction || scrollWheelDownAction)
            button = [ScrollableButton alloc];
        else
            button = [NSButton alloc];
        [button initWithFrame: rect];
        PyObject* imagedata = PyDict_GetItemString(images, imagenames[i]);
        NSImage* image = _read_ppm_image(imagedata);
        [button setBezelStyle: NSShadowlessSquareBezelStyle];
        [button setButtonType: NSMomentaryLightButton];
        if(image)
        {
            [button setImage: image];
            [image release];
        }
        [button setToolTip: tooltips[i]];
        [button setTarget: self->handler];
        [button setAction: actions[i]];
        if (scrollWheelUpAction)
            [button setScrollWheelUpAction: scrollWheelUpAction];
        if (scrollWheelDownAction)
            [button setScrollWheelDownAction: scrollWheelDownAction];
        [[window contentView] addSubview: button];
        [button release];
        rect.origin.x += rect.size.width + smallgap;
    }
    [[window contentView] display];
    [pool release];

    return 0;
}

static void
NavigationToolbar_dealloc(NavigationToolbar *self)
{
    [self->handler release];
    self->ob_type->tp_free((PyObject*)self);
}

static PyObject*
NavigationToolbar_repr(NavigationToolbar* self)
{
    return PyString_FromFormat("NavigationToolbar object %p", (void*)self);
}

static char NavigationToolbar_doc[] =
"NavigationToolbar\n";

static PyObject*
NavigationToolbar_update (NavigationToolbar* self)
{
    int n;
    NSPopUpButton* button = self->menu;
    if (!button)
    {
        PyErr_SetString(PyExc_RuntimeError, "Menu button is NULL");
        return NULL;
    }

    PyObject* canvas = PyObject_GetAttrString((PyObject*)self, "canvas");
    if (canvas==NULL)
    {
        PyErr_SetString(PyExc_AttributeError, "Failed to find canvas");
        return NULL;
    }
    Py_DECREF(canvas); /* Don't keep a reference here */
    PyObject* figure = PyObject_GetAttrString(canvas, "figure");
    if (figure==NULL)
    {
        PyErr_SetString(PyExc_AttributeError, "Failed to find figure");
        return NULL;
    }
    Py_DECREF(figure); /* Don't keep a reference here */
    PyObject* axes = PyObject_GetAttrString(figure, "axes");
    if (axes==NULL)
    {
        PyErr_SetString(PyExc_AttributeError, "Failed to find figure axes");
        return NULL;
    }
    Py_DECREF(axes); /* Don't keep a reference here */
    if (!PyList_Check(axes))
    {
        PyErr_SetString(PyExc_TypeError, "Figure axes is not a list");
        return NULL;
    }
    n = PyList_GET_SIZE(axes);

    NSAutoreleasePool* pool = [[NSAutoreleasePool alloc] init];
    [button removeAllItems];

    NSMenu* menu = [button menu];
    [menu addItem: [MenuItem menuItemWithTitle: @"Axes"]];

    if (n==0)
    {
        [button setEnabled: NO];
    }
    else
    {
        int i;
        [menu addItem: [MenuItem menuItemSelectAll]];
        [menu addItem: [MenuItem menuItemInvertAll]];
        [menu addItem: [NSMenuItem separatorItem]];
        for (i = 0; i < n; i++)
        {
            [menu addItem: [MenuItem menuItemForAxis: i]];
        }
        [button setEnabled: YES];
    }
    [pool release];
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
NavigationToolbar_get_active (NavigationToolbar* self)
{
    NSPopUpButton* button = self->menu;
    if (!button)
    {
        PyErr_SetString(PyExc_RuntimeError, "Menu button is NULL");
        return NULL;
    }
    NSMenu* menu = [button menu];
    NSArray* items = [menu itemArray];
    unsigned int n = [items count];
    int* states = malloc(n*sizeof(int));
    int i;
    unsigned int m = 0;
    NSEnumerator* enumerator = [items objectEnumerator];
    MenuItem* item;
    while ((item = [enumerator nextObject]))
    {
        if ([item isSeparatorItem]) continue;
        i = [item index];
        if (i < 0) continue;
        if ([item state]==NSOnState)
        {
            states[i] = 1;
            m++;
        }
        else states[i] = 0;
    }
    int j = 0;
    PyObject* list = PyList_New(m);
    for (i = 0; i < n; i++)
    {
        if(states[i]==1)
        {
            PyList_SET_ITEM(list, j, PyInt_FromLong(i));
            j++;
        }
    }
    free(states);
    return list;
}

static PyMethodDef NavigationToolbar_methods[] = {
    {"update",
     (PyCFunction)NavigationToolbar_update,
     METH_NOARGS,
     "Updates the toolbar menu."
    },
    {"get_active",
     (PyCFunction)NavigationToolbar_get_active,
     METH_NOARGS,
     "Returns a list of integers identifying which items in the menu are selected."
    },
    {NULL}  /* Sentinel */
};

static PyTypeObject NavigationToolbarType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "_macosx.NavigationToolbar", /*tp_name*/
    sizeof(NavigationToolbar), /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)NavigationToolbar_dealloc,     /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    (reprfunc)NavigationToolbar_repr,     /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,        /*tp_flags*/
    NavigationToolbar_doc,     /* tp_doc */
    0,                         /* tp_traverse */
    0,                         /* tp_clear */
    0,                         /* tp_richcompare */
    0,                         /* tp_weaklistoffset */
    0,                         /* tp_iter */
    0,                         /* tp_iternext */
    NavigationToolbar_methods, /* tp_methods */
    0,                         /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)NavigationToolbar_init,      /* tp_init */
    0,                         /* tp_alloc */
    NavigationToolbar_new,     /* tp_new */
};

@interface NavigationToolbar2Handler : NSObject
{   PyObject* toolbar;
    NSButton* panbutton;
    NSButton* zoombutton;
}
- (NavigationToolbar2Handler*)initWithToolbar:(PyObject*)toolbar;
- (void)installCallbacks:(SEL[7])actions forButtons: (NSButton*[7])buttons;
- (void)home:(id)sender;
- (void)back:(id)sender;
- (void)forward:(id)sender;
- (void)pan:(id)sender;
- (void)zoom:(id)sender;
- (void)configure_subplots:(id)sender;
- (void)save_figure:(id)sender;
@end

typedef struct {
    PyObject_HEAD
    NSPopUpButton* menu;
    NSText* messagebox;
    NavigationToolbar2Handler* handler;
} NavigationToolbar2;

@implementation NavigationToolbar2Handler
- (NavigationToolbar2Handler*)initWithToolbar:(PyObject*)theToolbar
{   [self init];
    toolbar = theToolbar;
    return self;
}

- (void)installCallbacks:(SEL[7])actions forButtons: (NSButton*[7])buttons
{
    int i;
    for (i = 0; i < 7; i++)
    {
        SEL action = actions[i];
        NSButton* button = buttons[i];
        [button setTarget: self];
        [button setAction: action];
        if (action==@selector(pan:)) panbutton = button;
        if (action==@selector(zoom:)) zoombutton = button;
    }
}

-(void)home:(id)sender
{   PyObject* result;
    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    result = PyObject_CallMethod(toolbar, "home", "");
    if(result)
        Py_DECREF(result);
    else
        PyErr_Print();
    PyGILState_Release(gstate);
}

-(void)back:(id)sender
{   PyObject* result;
    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    result = PyObject_CallMethod(toolbar, "back", "");
    if(result)
        Py_DECREF(result);
    else
        PyErr_Print();
    PyGILState_Release(gstate);
}

-(void)forward:(id)sender
{   PyObject* result;
    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    result = PyObject_CallMethod(toolbar, "forward", "");
    if(result)
        Py_DECREF(result);
    else
        PyErr_Print();
    PyGILState_Release(gstate);
}

-(void)pan:(id)sender
{   PyObject* result;
    PyGILState_STATE gstate;
    if ([sender state])
    {
        if (zoombutton) [zoombutton setState: NO];
    }
    gstate = PyGILState_Ensure();
    result = PyObject_CallMethod(toolbar, "pan", "");
    if(result)
        Py_DECREF(result);
    else
        PyErr_Print();
    PyGILState_Release(gstate);
}

-(void)zoom:(id)sender
{   PyObject* result;
    PyGILState_STATE gstate;
    if ([sender state])
    {
        if (panbutton) [panbutton setState: NO];
    }
    gstate = PyGILState_Ensure();
    result = PyObject_CallMethod(toolbar, "zoom", "");
    if(result)
        Py_DECREF(result);
    else
        PyErr_Print();
    PyGILState_Release(gstate);
}

-(void)configure_subplots:(id)sender
{   PyObject* canvas;
    View* view;
    PyObject* size;
    NSRect rect;
    int width, height;

    rect.origin.x = 100;
    rect.origin.y = 350;
    PyGILState_STATE gstate = PyGILState_Ensure();
    PyObject* master = PyObject_GetAttrString(toolbar, "canvas");
    if (master==nil)
    {
        PyErr_Print();
        PyGILState_Release(gstate);
        return;
    }
    canvas = PyObject_CallMethod(toolbar, "prepare_configure_subplots", "");
    if(!canvas)
    {
        PyErr_Print();
        Py_DECREF(master);
        PyGILState_Release(gstate);
        return;
    }

    view = ((FigureCanvas*)canvas)->view;
    if (!view) /* Something really weird going on */
    {
        PyErr_SetString(PyExc_RuntimeError, "NSView* is NULL");
        PyErr_Print();
        Py_DECREF(canvas);
        Py_DECREF(master);
        PyGILState_Release(gstate);
        return;
    }

    size = PyObject_CallMethod(canvas, "get_width_height", "");
    Py_DECREF(canvas);
    if(!size)
    {
        PyErr_Print();
        Py_DECREF(master);
        PyGILState_Release(gstate);
        return;
    }

    int ok = PyArg_ParseTuple(size, "ii", &width, &height);
    Py_DECREF(size);
    if (!ok)
    {
        PyErr_Print();
        Py_DECREF(master);
        PyGILState_Release(gstate);
        return;
    }

    NSWindow* mw = [((FigureCanvas*)master)->view window];
    Py_DECREF(master);
    PyGILState_Release(gstate);

    rect.size.width = width;
    rect.size.height = height;

    ToolWindow* window = [ [ToolWindow alloc] initWithContentRect: rect
                                                           master: mw];
    [window setContentView: view];
    [view release];
    [window makeKeyAndOrderFront: nil];
}

-(void)save_figure:(id)sender
{   PyObject* result;
    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    result = PyObject_CallMethod(toolbar, "save_figure", "");
    if(result)
        Py_DECREF(result);
    else
        PyErr_Print();
    PyGILState_Release(gstate);
}
@end

static PyObject*
NavigationToolbar2_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    NavigationToolbar2Handler* handler = [NavigationToolbar2Handler alloc];
    if (!handler) return NULL;
    NavigationToolbar2 *self = (NavigationToolbar2*)type->tp_alloc(type, 0);
    if (!self)
    {
        [handler release];
        return NULL;
    }
    self->handler = handler;
    return (PyObject*)self;
}

static int
NavigationToolbar2_init(NavigationToolbar2 *self, PyObject *args, PyObject *kwds)
{
    PyObject* obj;
    FigureCanvas* canvas;
    View* view;

    int i;
    NSRect rect;

    const float gap = 2;
    const int height = 36;

    const char* basedir;

    obj = PyObject_GetAttrString((PyObject*)self, "canvas");
    if (obj==NULL)
    {
        PyErr_SetString(PyExc_AttributeError, "Attempt to install toolbar for NULL canvas");
        return -1;
    }
    Py_DECREF(obj); /* Don't increase the reference count */
    if (!PyObject_IsInstance(obj, (PyObject*) &FigureCanvasType))
    {
        PyErr_SetString(PyExc_TypeError, "Attempt to install toolbar for object that is not a FigureCanvas");
        return -1;
    }
    canvas = (FigureCanvas*)obj;
    view = canvas->view;
    if(!view)
    {
        PyErr_SetString(PyExc_RuntimeError, "NSView* is NULL");
        return -1;
    }

    if(!PyArg_ParseTuple(args, "s", &basedir)) return -1;

    NSAutoreleasePool* pool = [[NSAutoreleasePool alloc] init];
    NSRect bounds = [view bounds];
    NSWindow* window = [view window];

    bounds.origin.y += height;
    [view setFrame: bounds];

    bounds.size.height += height;
    [window setContentSize: bounds.size];

    NSString* dir = [NSString stringWithCString: basedir
                                       encoding: NSASCIIStringEncoding];

    NSButton* buttons[7];

    NSString* images[7] = {@"home.png",
                           @"back.png",
                           @"forward.png",
                           @"move.png",
                           @"zoom_to_rect.png",
                           @"subplots.png",
                           @"filesave.png"};

    NSString* tooltips[7] = {@"Reset original view",
                             @"Back to  previous view",
                             @"Forward to next view",
                             @"Pan axes with left mouse, zoom with right",
                             @"Zoom to rectangle",
                             @"Configure subplots",
                             @"Save the figure"};

    SEL actions[7] = {@selector(home:),
                      @selector(back:),
                      @selector(forward:),
                      @selector(pan:),
                      @selector(zoom:),
                      @selector(configure_subplots:),
                      @selector(save_figure:)};

    NSButtonType buttontypes[7] = {NSMomentaryLightButton,
                                   NSMomentaryLightButton,
                                   NSMomentaryLightButton,
                                   NSPushOnPushOffButton,
                                   NSPushOnPushOffButton,
                                   NSMomentaryLightButton,
                                   NSMomentaryLightButton};

    rect.size.width = 32;
    rect.size.height = 32;
    rect.origin.x = gap;
    rect.origin.y = 0.5*(height - rect.size.height);
    for (i = 0; i < 7; i++)
    {
        const NSSize size = {24, 24};
        NSString* filename = [dir stringByAppendingPathComponent: images[i]];
        NSImage* image = [[NSImage alloc] initWithContentsOfFile: filename];
        buttons[i] = [[NSButton alloc] initWithFrame: rect];
        [image setSize: size];
        [buttons[i] setBezelStyle: NSShadowlessSquareBezelStyle];
        [buttons[i] setButtonType: buttontypes[i]];
        [buttons[i] setImage: image];
        [buttons[i] setImagePosition: NSImageOnly];
        [buttons[i] setToolTip: tooltips[i]];
        [[window contentView] addSubview: buttons[i]];
        [buttons[i] release];
        [image release];
        rect.origin.x += rect.size.width + gap;
    }

    self->handler = [self->handler initWithToolbar: (PyObject*)self];
    [self->handler installCallbacks: actions forButtons: buttons];

    NSFont* font = [NSFont systemFontOfSize: 0.0];
    rect.size.width = 300;
    rect.size.height = 0;
    rect.origin.x += 200;
    NSText* messagebox = [[NSText alloc] initWithFrame: rect];
    [messagebox setFont: font];
    [messagebox setDrawsBackground: NO];
    [messagebox setEditable: NO];
    rect = [messagebox frame];
    rect.origin.y = 0.5 * (height - rect.size.height);
    [messagebox setFrameOrigin: rect.origin];
    [[window contentView] addSubview: messagebox];
    [messagebox release];
    [[window contentView] display];

    [pool release];

    self->messagebox = messagebox;
    return 0;
}

static void
NavigationToolbar2_dealloc(NavigationToolbar2 *self)
{
    [self->handler release];
    self->ob_type->tp_free((PyObject*)self);
}

static PyObject*
NavigationToolbar2_repr(NavigationToolbar2* self)
{
    return PyString_FromFormat("NavigationToolbar2 object %p", (void*)self);
}

static char NavigationToolbar2_doc[] =
"NavigationToolbar2\n";

static PyObject*
NavigationToolbar2_set_message(NavigationToolbar2 *self, PyObject* args)
{
    const char* message;

    if(!PyArg_ParseTuple(args, "s", &message)) return NULL;
    NSText* messagebox = self->messagebox;

    if (messagebox)
    {   NSString* text = [NSString stringWithUTF8String: message];
        [messagebox setString: text];
    }

    Py_INCREF(Py_None);
    return Py_None;
}

static PyMethodDef NavigationToolbar2_methods[] = {
    {"set_message",
     (PyCFunction)NavigationToolbar2_set_message,
     METH_VARARGS,
     "Set the message to be displayed on the toolbar."
    },
    {NULL}  /* Sentinel */
};

static PyTypeObject NavigationToolbar2Type = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "_macosx.NavigationToolbar2", /*tp_name*/
    sizeof(NavigationToolbar2), /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)NavigationToolbar2_dealloc,     /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    (reprfunc)NavigationToolbar2_repr,     /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,        /*tp_flags*/
    NavigationToolbar2_doc,    /* tp_doc */
    0,                         /* tp_traverse */
    0,                         /* tp_clear */
    0,                         /* tp_richcompare */
    0,                         /* tp_weaklistoffset */
    0,                         /* tp_iter */
    0,                         /* tp_iternext */
    NavigationToolbar2_methods, /* tp_methods */
    0,                         /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)NavigationToolbar2_init,      /* tp_init */
    0,                         /* tp_alloc */
    NavigationToolbar2_new,    /* tp_new */
};

static PyObject*
choose_save_file(PyObject* unused, PyObject* args)
{
    int result;
    const char* title;
    if(!PyArg_ParseTuple(args, "s", &title)) return NULL;

    NSSavePanel* panel = [NSSavePanel savePanel];
    [panel setTitle: [NSString stringWithCString: title
                                        encoding: NSASCIIStringEncoding]];
    result = [panel runModal];
    if (result == NSOKButton)
    {
        NSString* filename = [panel filename];
        unsigned int n = [filename length];
        unichar* buffer = malloc(n*sizeof(unichar));
        [filename getCharacters: buffer];
        PyObject* string =  PyUnicode_FromUnicode(buffer, n);
        free(buffer);
        return string;
    }
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
set_cursor(PyObject* unused, PyObject* args)
{
    int i;
    if(!PyArg_ParseTuple(args, "i", &i)) return NULL;
    switch (i)
    { case 0: [[NSCursor pointingHandCursor] set]; break;
      case 1: [[NSCursor arrowCursor] set]; break;
      case 2: [[NSCursor crosshairCursor] set]; break;
      case 3: [[NSCursor openHandCursor] set]; break;
      default: return NULL;
    }
    Py_INCREF(Py_None);
    return Py_None;
}

static char show__doc__[] = "Show all the figures and enter the main loop.\nThis function does not return until all Matplotlib windows are closed,\nand is normally not needed in interactive sessions.";

static PyObject*
show(PyObject* self)
{
    if(nwin > 0) [NSApp run];
    Py_INCREF(Py_None);
    return Py_None;
}

@implementation Window
- (Window*)initWithContentRect:(NSRect)rect styleMask:(unsigned int)mask backing:(NSBackingStoreType)bufferingType defer:(BOOL)deferCreation withManager: (PyObject*)theManager
{
    self = [super initWithContentRect: rect
                            styleMask: mask
                              backing: bufferingType
                                defer: deferCreation];
    manager = theManager;
    Py_INCREF(manager);
    return self;
}

- (BOOL)closeButtonPressed
{
    PyObject* result;
    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    result = PyObject_CallMethod(manager, "close", "");
    if(result)
        Py_DECREF(result);
    else
        PyErr_Print();
    PyGILState_Release(gstate);
    return YES;
}

- (void)close
{
    [super close];
    nwin--;
    if(nwin==0) [NSApp stop: self];
}

- (void)dealloc
{
    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    Py_DECREF(manager);
    PyGILState_Release(gstate);
    [super dealloc];
}
@end

@implementation ToolWindow
- (ToolWindow*)initWithContentRect:(NSRect)rect master:(NSWindow*)window
{
    [self initWithContentRect: rect
                    styleMask: NSTitledWindowMask
                             | NSClosableWindowMask
                             | NSResizableWindowMask
                             | NSMiniaturizableWindowMask
                      backing: NSBackingStoreBuffered
                        defer: YES];
    [self setTitle: @"Subplot Configuration Tool"];
    [[NSNotificationCenter defaultCenter] addObserver: self
                                             selector: @selector(masterCloses:)
                                                 name: NSWindowWillCloseNotification
                                               object: window];
    return self;
}

- (void)masterCloses:(NSNotification*)notification
{
    [self close];
}

- (void)close
{
    [[NSNotificationCenter defaultCenter] removeObserver: self];
    [super close];
}
@end

@implementation View
- (BOOL)isFlipped
{
    return NO;
}

- (View*)initWithFrame:(NSRect)rect canvas: (PyObject*)fc
{
    self = [super initWithFrame: rect];
    rubberband = NSZeroRect;
    if (canvas)
    {
        Py_DECREF(canvas);
    }
    canvas = fc;
    Py_INCREF(canvas);
    return self;
}

- (void)dealloc
{
    FigureCanvas* fc = (FigureCanvas*)canvas;
    fc->view = NULL;
    Py_DECREF(canvas);
    [super dealloc];
}

-(void)drawRect:(NSRect)rect
{
    PyObject* result;
    PyGILState_STATE gstate = PyGILState_Ensure();

    PyObject* figure = PyObject_GetAttrString(canvas, "figure");
    if (!figure)
    {
        PyErr_Print();
        PyGILState_Release(gstate);
        return;
    }
    PyObject* renderer = PyObject_GetAttrString(canvas, "renderer");
    if (!renderer)
    {
        PyErr_Print();
        Py_DECREF(figure);
        PyGILState_Release(gstate);
        return;
    }
    GraphicsContext* gc = (GraphicsContext*) PyObject_GetAttrString(renderer, "gc");
    if (!gc)
    {
        PyErr_Print();
        Py_DECREF(figure);
        Py_DECREF(renderer);
        PyGILState_Release(gstate);
        return;
    }

    gc->size = [self frame].size;

    CGContextRef cr = (CGContextRef) [[NSGraphicsContext currentContext] graphicsPort];
    gc->cr = cr;
    gc->level = 0;

    result = PyObject_CallMethod(figure, "draw", "O", renderer);
    if(result)
        Py_DECREF(result);
    else
        PyErr_Print();

    gc->cr = nil;

    if (!NSIsEmptyRect(rubberband)) NSFrameRect(rubberband);

    Py_DECREF(gc);
    Py_DECREF(figure);
    Py_DECREF(renderer);

    PyGILState_Release(gstate);
}

- (void)windowDidResize: (NSNotification*)notification
{
    int width, height;
    Window* window = [notification object];
    NSSize size = [[window contentView] frame].size;
    NSRect rect = [self frame];

    size.height -= rect.origin.y;
    width = size.width;
    height = size.height;

    [self setFrameSize: size];

    PyGILState_STATE gstate = PyGILState_Ensure();
    PyObject* result = PyObject_CallMethod(canvas, "resize", "ii", width, height);
    if(result)
        Py_DECREF(result);
    else
        PyErr_Print();
    PyGILState_Release(gstate);
    [self setNeedsDisplay: YES];
}

- (BOOL)windowShouldClose:(NSNotification*)notification
{
    NSWindow* window = [self window];
    NSEvent* event = [NSEvent otherEventWithType: NSApplicationDefined
                                        location: NSZeroPoint
                                   modifierFlags: 0
                                       timestamp: 0.0
                                    windowNumber: 0
                                         context: nil
                                         subtype: WINDOW_CLOSING
                                           data1: 0
                                           data2: 0];
    [NSApp postEvent: event atStart: true];
    if ([window respondsToSelector: @selector(closeButtonPressed)])
    { BOOL closed = [((Window*) window) closeButtonPressed];
      /* If closed, the window has already been closed via the manager. */
      if (closed) return NO;
    }
    return YES;
}

- (void)mouseDown:(NSEvent *)event
{
    int x, y;
    int num;
    PyObject* result;
    PyGILState_STATE gstate;
    NSPoint location = [event locationInWindow];
    location = [self convertPoint: location fromView: nil];
    x = location.x;
    y = location.y;
    switch ([event type])
    {    case NSLeftMouseDown:
         {   unsigned int modifier = [event modifierFlags];
             if (modifier & NSControlKeyMask)
                 /* emulate a right-button click */
                 num = 3;
             else if (modifier & NSAlternateKeyMask)
                 /* emulate a middle-button click */
                 num = 2;
             else
             {
                 num = 1;
                 if ([NSCursor currentCursor]==[NSCursor openHandCursor])
                     [[NSCursor closedHandCursor] set];
             }
             break;
         }
         case NSOtherMouseDown: num = 2; break;
         case NSRightMouseDown: num = 3; break;
         default: return; /* Unknown mouse event */
    }
    gstate = PyGILState_Ensure();
    result = PyObject_CallMethod(canvas, "button_press_event", "iii", x, y, num);
    if(result)
        Py_DECREF(result);
    else
        PyErr_Print();

    PyGILState_Release(gstate);
}

- (void)mouseUp:(NSEvent *)event
{
    int num;
    int x, y;
    PyObject* result;
    PyGILState_STATE gstate;
    NSPoint location = [event locationInWindow];
    location = [self convertPoint: location fromView: nil];
    x = location.x;
    y = location.y;
    switch ([event type])
    {    case NSLeftMouseUp:
             num = 1;
             if ([NSCursor currentCursor]==[NSCursor closedHandCursor])
                 [[NSCursor openHandCursor] set];
             break;
         case NSOtherMouseUp: num = 2; break;
         case NSRightMouseUp: num = 3; break;
         default: return; /* Unknown mouse event */
    }
    gstate = PyGILState_Ensure();
    result = PyObject_CallMethod(canvas, "button_release_event", "iii", x, y, num);
    if(result)
        Py_DECREF(result);
    else
        PyErr_Print();

    PyGILState_Release(gstate);
}

- (void)mouseMoved:(NSEvent *)event
{
    int x, y;
    NSPoint location = [event locationInWindow];
    location = [self convertPoint: location fromView: nil];
    x = location.x;
    y = location.y;
    PyGILState_STATE gstate = PyGILState_Ensure();
    PyObject* result = PyObject_CallMethod(canvas, "motion_notify_event", "ii", x, y);
    if(result)
        Py_DECREF(result);
    else
        PyErr_Print();

    PyGILState_Release(gstate);
}

- (void)mouseDragged:(NSEvent *)event
{
    int x, y;
    NSPoint location = [event locationInWindow];
    location = [self convertPoint: location fromView: nil];
    x = location.x;
    y = location.y;
    PyGILState_STATE gstate = PyGILState_Ensure();
    PyObject* result = PyObject_CallMethod(canvas, "motion_notify_event", "ii", x, y);
    if(result)
        Py_DECREF(result);
    else
        PyErr_Print();

    PyGILState_Release(gstate);
}

- (void)rightMouseDown:(NSEvent *)event
{
    int x, y;
    int num = 3;
    PyObject* result;
    PyGILState_STATE gstate;
    NSPoint location = [event locationInWindow];
    location = [self convertPoint: location fromView: nil];
    x = location.x;
    y = location.y;
    gstate = PyGILState_Ensure();
    result = PyObject_CallMethod(canvas, "button_press_event", "iii", x, y, num);
    if(result)
        Py_DECREF(result);
    else
        PyErr_Print();

    PyGILState_Release(gstate);
}

- (void)rightMouseUp:(NSEvent *)event
{
    int x, y;
    int num = 3;
    PyObject* result;
    PyGILState_STATE gstate;
    NSPoint location = [event locationInWindow];
    location = [self convertPoint: location fromView: nil];
    x = location.x;
    y = location.y;
    gstate = PyGILState_Ensure();
    result = PyObject_CallMethod(canvas, "button_release_event", "iii", x, y, num);
    if(result)
        Py_DECREF(result);
    else
        PyErr_Print();

    PyGILState_Release(gstate);
}

- (void)otherMouseDown:(NSEvent *)event
{
    int x, y;
    int num = 2;
    PyObject* result;
    PyGILState_STATE gstate;
    NSPoint location = [event locationInWindow];
    location = [self convertPoint: location fromView: nil];
    x = location.x;
    y = location.y;
    gstate = PyGILState_Ensure();
    result = PyObject_CallMethod(canvas, "button_press_event", "iii", x, y, num);
    if(result)
        Py_DECREF(result);
    else
        PyErr_Print();

    PyGILState_Release(gstate);
}

- (void)otherMouseUp:(NSEvent *)event
{
    int x, y;
    int num = 2;
    PyObject* result;
    PyGILState_STATE gstate;
    NSPoint location = [event locationInWindow];
    location = [self convertPoint: location fromView: nil];
    x = location.x;
    y = location.y;
    gstate = PyGILState_Ensure();
    result = PyObject_CallMethod(canvas, "button_release_event", "iii", x, y, num);
    if(result)
        Py_DECREF(result);
    else
        PyErr_Print();

    PyGILState_Release(gstate);
}

- (void)setRubberband:(NSRect)rect
{
    if (!NSIsEmptyRect(rubberband)) [self setNeedsDisplayInRect: rubberband];
    rubberband = rect;
    [self setNeedsDisplayInRect: rubberband];
}

- (void)removeRubberband
{
    if (NSIsEmptyRect(rubberband)) return;
    [self setNeedsDisplayInRect: rubberband];
    rubberband = NSZeroRect;
}

- (const char*)convertKeyEvent:(NSEvent*)event
{
    NSString* text = [event charactersIgnoringModifiers];
    unichar uc = [text characterAtIndex:0];
    int i = (int)uc;
    if ([event modifierFlags] & NSNumericPadKeyMask)
    {
        if (i > 256)
        {
            if (uc==NSLeftArrowFunctionKey) return "left";
            else if (uc==NSUpArrowFunctionKey) return "up";
            else if (uc==NSRightArrowFunctionKey) return "right";
            else if (uc==NSDownArrowFunctionKey) return "down";
            else if (uc==NSF1FunctionKey) return "f1";
            else if (uc==NSF2FunctionKey) return "f2";
            else if (uc==NSF3FunctionKey) return "f3";
            else if (uc==NSF4FunctionKey) return "f4";
            else if (uc==NSF5FunctionKey) return "f5";
            else if (uc==NSF6FunctionKey) return "f6";
            else if (uc==NSF7FunctionKey) return "f7";
            else if (uc==NSF8FunctionKey) return "f8";
            else if (uc==NSF9FunctionKey) return "f9";
            else if (uc==NSF10FunctionKey) return "f10";
            else if (uc==NSF11FunctionKey) return "f11";
            else if (uc==NSF12FunctionKey) return "f12";
            else if (uc==NSScrollLockFunctionKey) return "scroll_lock";
            else if (uc==NSBreakFunctionKey) return "break";
            else if (uc==NSInsertFunctionKey) return "insert";
            else if (uc==NSDeleteFunctionKey) return "delete";
            else if (uc==NSHomeFunctionKey) return "home";
            else if (uc==NSEndFunctionKey) return "end";
            else if (uc==NSPageUpFunctionKey) return "pageup";
            else if (uc==NSPageDownFunctionKey) return "pagedown";
        }
        else if ((char)uc == '.') return "dec";
    }

    switch (i)
    {
        case 127: return "backspace";
        case 13: return "enter";
        case 3: return "enter";
        case 27: return "escape";
        default:
        {
            static char s[2];
            s[0] = (char)uc;
            s[1] = '\0';
            return (const char*)s;
        }
    }

    return NULL;
}

- (void)keyDown:(NSEvent*)event
{
    PyObject* result;
    const char* s = [self convertKeyEvent: event];
    PyGILState_STATE gstate = PyGILState_Ensure();
    if (s==NULL)
    {
        result = PyObject_CallMethod(canvas, "key_press_event", "O", Py_None);
    }
    else
    {
        result = PyObject_CallMethod(canvas, "key_press_event", "s", s);
    }
    if(result)
        Py_DECREF(result);
    else
        PyErr_Print();

    PyGILState_Release(gstate);
}

- (void)keyUp:(NSEvent*)event
{
    PyObject* result;
    const char* s = [self convertKeyEvent: event];
    PyGILState_STATE gstate = PyGILState_Ensure();
    if (s==NULL)
    {
        result = PyObject_CallMethod(canvas, "key_release_event", "O", Py_None);
    }
    else
    {
        result = PyObject_CallMethod(canvas, "key_release_event", "s", s);
    }
    if(result)
        Py_DECREF(result);
    else
        PyErr_Print();

    PyGILState_Release(gstate);
}

- (void)scrollWheel:(NSEvent*)event
{
    int step;
    float d = [event deltaY];
    if (d > 0) step = 1;
    else if (d < 0) step = -1;
    else return;
    NSPoint location = [event locationInWindow];
    NSPoint point = [self convertPoint: location fromView: nil];
    int x = (int)round(point.x);
    int y = (int)round(point.y - 1);

    PyObject* result;
    PyGILState_STATE gstate = PyGILState_Ensure();
    result = PyObject_CallMethod(canvas, "scroll_event", "iii", x, y, step);
    if(result)
        Py_DECREF(result);
    else
        PyErr_Print();

    PyGILState_Release(gstate);
}

- (void)flagsChanged:(NSEvent*)event
{
    const char *s = NULL;
    if (([event modifierFlags] & NSControlKeyMask) == NSControlKeyMask)
        s = "control";
    else if (([event modifierFlags] & NSShiftKeyMask) == NSShiftKeyMask)
        s = "shift";
    else if (([event modifierFlags] & NSAlternateKeyMask) == NSAlternateKeyMask)
        s = "alt";
    else return;
    PyGILState_STATE gstate = PyGILState_Ensure();
    PyObject* result = PyObject_CallMethod(canvas, "key_press_event", "s", &s);
    if(result)
        Py_DECREF(result);
    else
        PyErr_Print();

    PyGILState_Release(gstate);
}
@end

@implementation ScrollableButton
- (void)setScrollWheelUpAction:(SEL)action
{
    scrollWheelUpAction = action;
}

- (void)setScrollWheelDownAction:(SEL)action
{
    scrollWheelDownAction = action;
}

- (void)scrollWheel:(NSEvent*)event
{
    float d = [event deltaY];
    Window* target = [self target];
    if (d > 0)
        [NSApp sendAction: scrollWheelUpAction to: target from: self];
    else if (d < 0)
        [NSApp sendAction: scrollWheelDownAction to: target from: self];
}
@end

@implementation MenuItem
+ (MenuItem*)menuItemWithTitle: (NSString*)title
{
    MenuItem* item = [[MenuItem alloc] initWithTitle: title
                                              action: nil
                                       keyEquivalent: @""];
    item->index = -1;
    return [item autorelease];
}

+ (MenuItem*)menuItemForAxis: (int)i
{
    NSString* title = [NSString stringWithFormat: @"Axis %d", i+1];
    MenuItem* item = [[MenuItem alloc] initWithTitle: title
                                              action: @selector(toggle:)
                                       keyEquivalent: @""];
    [item setTarget: item];
    [item setState: NSOnState];
    item->index = i;
    return [item autorelease];
}

+ (MenuItem*)menuItemSelectAll
{
    MenuItem* item = [[MenuItem alloc] initWithTitle: @"Select All"
                                              action: @selector(selectAll:)
                                       keyEquivalent: @""];
    [item setTarget: item];
    item->index = -1;
    return [item autorelease];
}

+ (MenuItem*)menuItemInvertAll
{
    MenuItem* item = [[MenuItem alloc] initWithTitle: @"Invert All"
                                              action: @selector(invertAll:)
                                       keyEquivalent: @""];
    [item setTarget: item];
    item->index = -1;
    return [item autorelease];
}

- (void)toggle:(id)sender
{
    if ([self state]) [self setState: NSOffState];
    else [self setState: NSOnState];
}

- (void)selectAll:(id)sender
{
    NSMenu* menu = [sender menu];
    if(!menu) return; /* Weird */
    NSArray* items = [menu itemArray];
    NSEnumerator* enumerator = [items objectEnumerator];
    MenuItem* item;
    while ((item = [enumerator nextObject]))
    {
        if (item->index >= 0) [item setState: NSOnState];
    }
}

- (void)invertAll:(id)sender
{
    NSMenu* menu = [sender menu];
    if(!menu) return; /* Weird */
    NSArray* items = [menu itemArray];
    NSEnumerator* enumerator = [items objectEnumerator];
    MenuItem* item;
    while ((item = [enumerator nextObject]))
    {
        if (item->index < 0) continue;
        if ([item state]==NSOffState) [item setState: NSOnState];
        else [item setState: NSOffState];
    }
}

- (int)index
{
    return self->index;
}
@end

static struct PyMethodDef methods[] = {
   {"show",
    (PyCFunction)show,
    METH_NOARGS,
    show__doc__
   },
   {"choose_save_file",
    (PyCFunction)choose_save_file,
    METH_VARARGS,
    "Closes the window."
   },
   {"set_cursor",
    (PyCFunction)set_cursor,
    METH_VARARGS,
    "Sets the active cursor."
   },
   {NULL,          NULL, 0, NULL}/* sentinel */
};

void init_macosx(void)
{   PyObject *m;
    import_array();

    if (PyType_Ready(&GraphicsContextType) < 0) return;
    if (PyType_Ready(&FigureCanvasType) < 0) return;
    if (PyType_Ready(&FigureManagerType) < 0) return;
    if (PyType_Ready(&NavigationToolbarType) < 0) return;
    if (PyType_Ready(&NavigationToolbar2Type) < 0) return;

    m = Py_InitModule4("_macosx",
                       methods,
                       "Mac OS X native backend",
                       NULL,
                       PYTHON_API_VERSION);

    Py_INCREF(&GraphicsContextType);
    Py_INCREF(&FigureCanvasType);
    Py_INCREF(&FigureManagerType);
    Py_INCREF(&NavigationToolbarType);
    Py_INCREF(&NavigationToolbar2Type);
    PyModule_AddObject(m, "GraphicsContext", (PyObject*) &GraphicsContextType);
    PyModule_AddObject(m, "FigureCanvas", (PyObject*) &FigureCanvasType);
    PyModule_AddObject(m, "FigureManager", (PyObject*) &FigureManagerType);
    PyModule_AddObject(m, "NavigationToolbar", (PyObject*) &NavigationToolbarType);
    PyModule_AddObject(m, "NavigationToolbar2", (PyObject*) &NavigationToolbar2Type);

    PyOS_InputHook = wait_for_stdin;
}
