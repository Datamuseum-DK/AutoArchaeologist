#!/usr/bin/env python3

'''
   VPID 1007 - TAG 0x7f
   =========================================

   FE_HANDBOOK.PDf 187p

    Note: […] The D2 mapping is:

        […]
        TAPE            1007
        […]


'''
    
from ....base import bitview as bv
from .common import ManagerSegment, PointerArray

class V1007T7F(ManagerSegment):

    VPID = 1007
    TAG = 0x7F
    TOPIC = "Tape"

    def spelunk_manager(self):
        self.std_head = StdHead(self, self.seg_head.hi).insert()
