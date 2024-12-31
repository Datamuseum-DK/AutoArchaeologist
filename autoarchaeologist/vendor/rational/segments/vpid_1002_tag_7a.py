#!/usr/bin/env python3

'''
   VPID 1002 - TAG 0x7a
   =========================================

   FE_HANDBOOK.PDf 187p

    Note: […] The D2 mapping is:

        […]
        DDB      1002
        […]


'''
    
from ....base import bitview as bv
from .common import ManagerSegment, PointerArray, StringArray

class V1002T7A(ManagerSegment):

    VPID = 1002
    TAG = 0x7a
    TOPIC = "DDB"

    def spelunk_manager(self):
        return
