##############################################################################
# ten: Diffusion tensor utilities
##############################################################################
# 
# Part of the python bindings for teem, by Carlos Scheidegger
#
# teem is developed by Gordon Kindlmann, and available at
# http://teem.sourceforge.net
#
# This is GPLv2, see /LICENSE
#

import capi
import util
import ctypes

class TenEnum(object): pass

Aniso = TenEnum()

for name in dir(capi):
    if name.startswith('tenAniso'):
        v = getattr(capi, name)
        if not isinstance(v, ctypes._CFuncPtr):
            shortname = name[len('tenAniso'):]
            if shortname.startswith('_'):
                # remove naming wrinkle from tenAniso enums
                shortname = shortname[1:]
            setattr(Aniso, shortname, v)

##############################################################################
