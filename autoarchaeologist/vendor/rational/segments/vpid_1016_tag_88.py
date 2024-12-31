#!/usr/bin/env python3

'''
   VPID 1016 - TAG 0x88
   =========================================

   FE_HANDBOOK.PDf 187p

    Note: […] The D2 mapping is:

        […]
        PROGRAM_LIBRARY      1016
        […]


'''
    
from ....base import bitview as bv
from .common import ManagerSegment, PointerArray, StringArray

class V1016T88(ManagerSegment):

    VPID = 1016
    TAG = 0x88
    TOPIC = "Program_Library"

    def spelunk_manager(self):
        return
