#!/usr/bin/env python3

'''
   VPID 1017 - TAG 0x89
   =========================================

   Not mentioned in FE_HANDBOOK.PDf 187p

'''
    
from ....base import bitview as bv
from .common import ManagerSegment, PointerArray, StringArray

class V1017T89(ManagerSegment):

    VPID = 1017
    TAG = 0x89
    TOPIC = "Native_Segment_Map"

    def spelunk_manager(self):
        return
