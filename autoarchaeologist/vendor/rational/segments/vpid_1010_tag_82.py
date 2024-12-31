#!/usr/bin/env python3

'''
   VPID 1010 - TAG 0x82
   =========================================

   FE_HANDBOOK.PDf 187p

    Note: […] The D2 mapping is:

        […]
        CONFIGURATION      1010
        […]


'''
    
from ....base import bitview as bv
from .common import ManagerSegment, PointerArray, StringArray

class V1010T82(ManagerSegment):

    VPID = 1010
    TAG = 0x82
    TOPIC = "Configuration"

    def spelunk_manager(self):
        return
