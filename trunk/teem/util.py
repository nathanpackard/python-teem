##############################################################################
# base module with assorted ctypes utilities
##############################################################################
# 
# Part of the python bindings for teem, by Carlos Scheidegger
#
# teem is developed by Gordon Kindlmann, and available at
# http://teem.sourceforge.net
#
# This is GPLv2, see /LICENSE
#

from ctypes import *
import ctypes
import capi

##############################################################################

def from_file(f):
    return cast(pythonapi.PyFile_AsFile(py_object(f)), FILE_p)

def ctypes_new_fun(library, funName, retType, params):
    f = getattr(library, funName)
    f.argtypes = params
    f.restype = retType
    return f

def ctypes_new_fun_retnewstr(library, funName, params):
    f = getattr(library, funName)
    f.argtypes = params
    f.restype = c_void_p
    def _callable(*args):
        r = f(*args)
        s = string_at(r)
        libc.free(r)
        return s
    return _callable

def ctypesobj_simple_ro_property(vname):
    def _reader(self):
        return getattr(self._ctypesobj.contents, vname)
    return property(_reader)

def ctypesobj_simple_rw_property(vname):
    def _reader(self):
        return getattr(self._ctypesobj.contents, vname)
    def _writer(self, value):
        setattr(self._ctypesobj.contents, vname, value)
    return property(_reader, _writer)

##############################################################################

class TeemObjectBase(object):
    pass

##############################################################################

_verbose = False

def new_simple_class(struct_name,
                     make_ctor=False,
                     ctor=None,
                     prefix=None,
                     base_class=None,
                     dtor=None,
                     skip_prefixes=[],
                     skip_methods=[],
                     permute={}):
    if _verbose:
        print "class", struct_name
    if not base_class:
        base_class = TeemObjectBase
    new_class = type(struct_name, (base_class,), {})
    
    struct = getattr(capi, struct_name)
    if not prefix:
        basename = struct_name.lower()[0] + struct_name[1:]
    else:
        basename = prefix

    # "methods"
    for name in dir(capi):
        skip = False
        for skip_prefix in skip_prefixes:
            if name.startswith(skip_prefix):
                skip = True
                break
        if skip:
            # if _verbose:
            #     print "    Skipping", name
            continue
        if name.startswith(basename):
            funcname = name[len(basename):]
            apientry = getattr(capi, name)
            if (funcname in ['Nix', 'New', 'Nuke', 'Copy'] or
                funcname in skip_methods or
                not isinstance(apientry, ctypes._CFuncPtr)):
                # if _verbose:
                #     print "    Skipping method (?)", funcname
                continue
            def make_func(name,permutation=None):
                apientry = getattr(capi, name)
                def func(*args):
                    newargs = list(x if not isinstance(x, TeemObjectBase)
                                   else x._ctypesobj
                                   for x, reqtype in zip(args, apientry.argtypes))
                    if permutation:
                        newargs = list(newargs[i] for i in permutation)
                    try:
                        return apientry(*newargs)
                    except ArgumentError:
                        print "args passed", newargs
                        print "types passed", list(type(x) for x in newargs)
                        print "args required", apientry.argtypes
                        raise
                return func
            if _verbose:
                print "    New method:", funcname, apientry
            setattr(new_class, funcname, make_func(name, permute.get(funcname, None)))

    # "fields"
    for fieldname, typ in struct._fields_:
        if _verbose:
            print "    New field:",fieldname
        setattr(new_class, fieldname, ctypesobj_simple_rw_property(fieldname))
    
    # "copy"
    if hasattr(capi, basename + 'Copy'):
        def make_copy(self):
            new_ctypesobj = getattr(capi, basename + 'Copy')(self._ctypesobj)
            return new_class.from_c_handle(new_ctypesobj)
        if _verbose:
            print "    Added __copy__"
        new_class.__copy__ = make_copy

    # "dtor"
    if not dtor:
        dtor = basename + 'Nix'
    else:
        dtor = basename + dtor
    if hasattr(capi, dtor):
        def __del__(self):
            getattr(capi, dtor)(self._ctypesobj)
        if _verbose:
            print "    Added __del__"
        new_class.__del__ = __del__

    # "ctor"
    if make_ctor:
        if not ctor:
            ctor = basename + 'New'
        else:
            ctor = basename + ctor
        if not hasattr(capi, dtor):
            msg = ("You told me to create ctor %s for class %s, but\n" +
                   "function is not there.") % (struct_name, ctor)
            print >>sys.stderr, msg
        else:
            def __init__(self):
                self._ctypesobj = getattr(capi, ctor)()
            new_class.__init__ = __init__
            if _verbose:
                print "    Added __init__"
    return new_class

