##############################################################################
# main module for the interaction between teem and numpy
#
# Part of the python bindings for teem, by Carlos Scheidegger
# teem is developed by Gordon Kindlmann, and available at
# http://teem.sourceforge.net
# 

import numpy
import teem.capi
import ctypes

numpy_endianess_glyph = '<' if teem.capi.airMyEndian.value == 1234 else '>'

type_map = {numpy.dtype('byte'): teem.capi.nrrdTypeChar,
            numpy.dtype('ubyte'): teem.capi.nrrdTypeUChar,
            numpy.dtype('short'): teem.capi.nrrdTypeShort,
            numpy.dtype('ushort'): teem.capi.nrrdTypeUShort,
            numpy.dtype('int'): teem.capi.nrrdTypeInt,
            numpy.dtype('uint'): teem.capi.nrrdTypeUInt,
            numpy.dtype('int64'): teem.capi.nrrdTypeLLong,
            numpy.dtype('uint64'): teem.capi.nrrdTypeULLong,
            numpy.dtype('float32'): teem.capi.nrrdTypeFloat,
            numpy.dtype('float64'): teem.capi.nrrdTypeDouble}

numpy_type_map = {
    teem.capi.nrrdTypeChar: numpy_endianess_glyph + 'i1',
    teem.capi.nrrdTypeUChar: numpy_endianess_glyph + 'u1',
    teem.capi.nrrdTypeShort: numpy_endianess_glyph + 'i2',
    teem.capi.nrrdTypeUShort: numpy_endianess_glyph + 'u2',
    teem.capi.nrrdTypeInt: numpy_endianess_glyph + 'i4',
    teem.capi.nrrdTypeUInt: numpy_endianess_glyph + 'u4',
    teem.capi.nrrdTypeLLong: numpy_endianess_glyph + 'i8',
    teem.capi.nrrdTypeULLong: numpy_endianess_glyph + 'u8',
    teem.capi.nrrdTypeFloat: numpy_endianess_glyph + 'f4',
    teem.capi.nrrdTypeDouble: numpy_endianess_glyph + 'f8'
    }

def nrrd_from_array(array, nrrd=None):
    """nrrd_from_array(array, nrrd=None) -> Nrrd.

    if nrrd is not None, use that nrrd instead"""

    array = numpy.ascontiguousarray(array)
    
    ptr = array.ctypes.data
    dt = array.dtype

    if dt not in type_map:
        raise Exception("I do not understand dtype %s" % dt)

    tnrrd = teem.capi.nrrdNew()
    dims = list(reversed(array.shape))
    teem.capi.nrrdWrap_va(tnrrd, array.ctypes.data_as(ctypes.c_void_p),
                          type_map[dt], len(array.shape), *dims)

    if nrrd:
        nval = nrrd
    else:
        nval = teem.capi.nrrdNew()

    teem.capi.nrrdCopy(nval, tnrrd)
    teem.capi.nrrdNix(tnrrd)
    
    return nval

# def wrap_from_array(array, nrrd=None):
#     """wrap_from_array(array) -> Nrrd. Returns a wrapped nrrd around
#     the array. YOU HAVE TO MANAGE THE LIFETIME OF THESE OBJECTS - if the
#     array goes away (or is reallocated, etc), accessing the NRRD will
#     segfault! Also, array must be contiguous."""
#
# This is not finished because I don't know how to actually check that
# an array is contiguous. Without that, the code is of very limited
# use - x.transpose() is not contiguous in memory, for example.
# Flattening the array before the copy would make 3 copies of the array in
# memory every time, even when the array is in fact contiguous, which is
# just dumb.
    
