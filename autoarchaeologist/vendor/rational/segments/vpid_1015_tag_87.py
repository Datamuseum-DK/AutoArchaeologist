#!/usr/bin/env python3

'''
   VPID 1015 - TAG 0x87
   =========================================

   FE_HANDBOOK.PDf 187p

    Note: […] The D2 mapping is:

        […]
        ARCHIVED_CODE      1015
        […]


'''
    
from ....base import bitview as bv
from .common import ManagerSegment, PointerArray, StringArray

class V1015T87(ManagerSegment):

    VPID = 1015
    TAG = 0x87
    TOPIC = "Archived_Code"

    def spelunk_manager(self):
        return
