##############################################################################
# nrrd: nearly raw raster data, part of teem
##############################################################################
#
# Part of the python bindings for teem, by Carlos Scheidegger
#
# teem is developed by Gordon Kindlmann, and available at
# http://teem.sourceforge.net
#
# This is GPLv2, see /LICENSE
#

##############################################################################

import capi
import capi.numpy
import util
import ctypes

class NrrdEnum(object): pass

Type = NrrdEnum()

##############################################################################
# FIXME: nrrdTypeIsIntegral, nrrdTypeIsUnsigned are not accessible
# because array has no bounds declared

Measure = NrrdEnum()
Boundary = NrrdEnum()
Format = NrrdEnum()
Encoding = NrrdEnum()
Kernel = NrrdEnum()
Center = NrrdEnum()
BasicInfo = NrrdEnum()
UnaryOp = NrrdEnum()
BinaryOp = NrrdEnum()
TernaryOp = NrrdEnum()

##############################################################################
# FIXME: refactor this - it's just too ugly

for name in dir(capi):
    if name.startswith('nrrdType'):
        v = getattr(capi, name)
        if not isinstance(v, ctypes._CFuncPtr):
            setattr(Type, name[len('nrrdType'):], v)
    elif name.startswith('nrrdMeasure'):
        v = getattr(capi, name)
        if not isinstance(v, ctypes._CFuncPtr):
            setattr(Measure, name[len('nrrdMeasure'):], v)
    elif name.startswith('nrrdBoundary'):
        v = getattr(capi, name)
        if not isinstance(v, ctypes._CFuncPtr):
            setattr(Boundary, name[len('nrrdBoundary'):], v)
    elif name.startswith('nrrdFormat'):
        v = getattr(capi, name)
        if not isinstance(v, ctypes._CFuncPtr):
            setattr(Format, name[len('nrrdFormat'):], v)
    elif name.startswith('nrrdEncoding'):
        v = getattr(capi, name)
        if not isinstance(v, ctypes._CFuncPtr):
            setattr(Encoding, name[len('nrrdEncoding'):], v)
    elif name.startswith('nrrdKernel'):
        v = getattr(capi, name)
        if not isinstance(v, ctypes._CFuncPtr):
            setattr(Kernel, name[len('nrrdKernel'):], v)
    elif name.startswith('nrrdCenter'):
        v = getattr(capi, name)
        if not isinstance(v, ctypes._CFuncPtr):
            setattr(Center, name[len('nrrdCenter'):], v)
    elif name.startswith('nrrdBasicInfo'):
        v = getattr(capi, name)
        if not isinstance(v, ctypes._CFuncPtr):
            setattr(BasicInfo, name[len('nrrdBasicInfo'):], v)
    elif name.startswith('nrrdBinaryOp'):
        v = getattr(capi, name)
        if not isinstance(v, ctypes._CFuncPtr):
            setattr(BinaryOp, name[len('nrrdBinaryOp'):], v)
    elif name.startswith('nrrdTernaryOp'):
        v = getattr(capi, name)
        if not isinstance(v, ctypes._CFuncPtr):
            setattr(TernaryOp, name[len('nrrdTernaryOp'):], v)
    elif name.startswith('nrrdUnaryOp'):
        v = getattr(capi, name)
        if not isinstance(v, ctypes._CFuncPtr):
            setattr(UnaryOp, name[len('nrrdUnaryOp'):], v)

##############################################################################
# Utility

def nrrd_fun_make_new_nrrd(nrrd_fun):
    def do_it(*args):
        # make new nrrd
        r = Nrrd(True)
        new_args = []
        for arg in args:
            # if object exposes a _ctype accessor, use it
            try:
                new_args.append(arg._ctype)
            except AttributeError:
                new_args.append(arg)
        nrrd_fun(r._ctypesobj, *new_args)
        return r
    return do_it

##############################################################################
# NrrdRange

NrrdRangeBase = util.new_simple_class('NrrdRange', skip_methods='NewSet')

# NrrdRange is for things that are created on the Python side of the
# Python-C boundary
class NrrdRange(NrrdRangeBase):

    def __init__(self, *args):
        if type(args[0]) == float:
            # standard nrrdRangeNew construction
            min, max = args
            self._ctypesobj = capi.nrrdRangeNew(min, max)
        else:
            # nrrd construction
            try:
                nrrd, blind8BitRange = args
            except ValueError:
                nrrd = args[0]
                blind8BitRange = False
            self._ctypesobj = capi.nrrdRangeNewSet(nrrd._ctypesobj, blind8BitRange)

# NrrdRangeC is for things that are created on the C side of
# the Python-C boundary - we simply keep the reference
class NrrdRangeC(NrrdRangeBase):
    def __init__(self, ctype_obj):
        self._ctypesobj = ctype_obj

NrrdRangeBase.from_ctypesobj = NrrdRangeC
    
##############################################################################
# NrrdKernelSpec

NrrdKernelSpecBase = util.new_simple_class('NrrdKernelSpec',
                                           make_ctor=True)

class NrrdKernelSpecC(NrrdKernelSpecBase):
    def __init__(self, cobj):
        self._ctypesobj = cobj

NrrdKernelSpecBase.from_ctypesobj = NrrdKernelSpecC

##############################################################################
# NrrdResampleContext

NrrdResampleContext = util.new_simple_class('NrrdResampleContext',
                                            prefix='nrrdResample',
                                            make_ctor=True,
                                            ctor='ContextNew',
                                            dtor='ContextNix',
                                            skip_prefixes=['nrrdResampleInfo'],
                                            skip_methods=['ContextNew',
                                                          'ContextNix'])

##############################################################################
# NrrdIter

NrrdIter = util.new_simple_class('NrrdIter')

##############################################################################

class NrrdBase(util.TeemObjectBase):

    ##########################################################################
    # Numpy support
    
    # this allows us to say
    # >>> x = Nrrd.load('foo.nrrd')
    # >>> y = numpy.array(x)
    #
    # It creates a copy of the nrrd.
    #
    # see http://numpy.scipy.org/array_interface.shtml

    def __init__(self, will_own_data=False):
        self._ctypesobj = capi.nrrdNew()
        self._own_data = will_own_data

    def __del__(self):
        if self._own_data:
            capi.nrrdEmpty(self._ctypesobj)
        capi.nrrdNix(self._ctypesobj)
        
    def _get_array_interface(self):
        nrrd = self._ctypesobj.contents
        s = []
        for i in reversed(range(nrrd.dim)):
            s.append(nrrd.axis[i].size)
        r = {'shape': tuple(s),
             'typestr': capi.numpy.numpy_type_map[nrrd.type],
             'data': (nrrd.data, False),
             'version': 3}
        return r
    __array_interface__ = property(_get_array_interface)

    @staticmethod
    def from_array(array):
        r = Nrrd(True)
        capi.numpy.nrrd_from_array(array, r._ctypesobj)
        return r

Nrrd = util.new_simple_class('Nrrd',
                             base_class=NrrdBase,
                             skip_prefixes=['nrrdResampleContext',
                                            'nrrdKernel',
                                            'nrrdIter',
                                            'nrrdMeasure',
                                            'nrrdResample',
                                            'nrrdIoState',
                                            'nrrdAxisInfo',
                                            'nrrdRange'],
                             dtor='skip',
                             skip_methods=['PPM', 'PGM'],
                             permute={'Save': [1, 0, 2]})

##############################################################################
# FIXME: should be put these functions somewhere else?

for name, apientry in capi.__dict__.iteritems():
    if (name.startswith('ten') and
        isinstance(apientry, ctypes._CFuncPtr)):
        try:
            ok = (apientry.argtypes[0] == ctypes.POINTER(capi.Nrrd))
        except (AttributeError, ValueError, IndexError):
            ok = False
        if not ok:
            continue
        def make_func(name, apientry):
            def func(self, *args):
                newargs = list(x if not isinstance(x, util.TeemObjectBase) else x._ctypesobj
                               for x in args)
                return apientry(self._ctypesobj, *newargs)
            return func
        setattr(Nrrd, name, make_func(name, apientry))

class NrrdC(Nrrd):

    def __init__(self, ctypesobj, will_own_data=False):
        self._ctypesobj = ctypesobj
        self._own_data = will_own_data

##############################################################################


