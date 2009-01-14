##############################################################################
# air: part of teem
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

##############################################################################

Enum = util.new_simple_class('airEnum')
  
class EnumC(Enum):
    def __init__(self, obj):
        self._ctypesobj = obj

##############################################################################

Bool = EnumC(capi.airBool)

##############################################################################

class _AirEnum(object): pass
