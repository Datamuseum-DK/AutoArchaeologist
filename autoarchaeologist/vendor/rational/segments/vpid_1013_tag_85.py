#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   VPID 1013 - TAG 0x85
   =========================================

   FE_HANDBOOK.PDf 187p

    Note: […] The D2 mapping is:

        […]
        NULL      1013
        […]


'''
    
from ....base import bitview as bv
from .common import ManagerSegment, PointerArray, StringArray

class V1013T85(ManagerSegment):

    VPID = 1013
    TAG = 0x85
    TOPIC = "Null_Device"

    def spelunk_manager(self):
        return
