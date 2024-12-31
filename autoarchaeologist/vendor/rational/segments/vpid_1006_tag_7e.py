#!/usr/bin/env python3

'''
   VPID 1006 - TAG 0x7e
   =========================================

   FE_HANDBOOK.PDf 187p

    Note: […] The D2 mapping is:

        […]
        SESSION          1006
        […]


'''
    
from ....base import bitview as bv
from .common import ManagerSegment, PointerArray, StringArray, StdHead

class V1006T7E(ManagerSegment):

    VPID = 1006
    TAG = 0x7e
    TOPIC = "Session"

    def spelunk_manager(self):
        self.std_head = StdHead(self, self.seg_head.hi).insert()
