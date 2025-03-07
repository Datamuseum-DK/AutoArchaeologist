#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   VPID 1014 - TAG 0x86
   =========================================

   FE_HANDBOOK.PDf 187p

    Note: […] The D2 mapping is:

        […]
        PIPE      1014
        […]


'''
    
from ....base import bitview as bv
from .common import ManagerSegment, PointerArray, StringArray

class V1014T86(ManagerSegment):

    VPID = 1014
    TAG = 0x86
    TOPIC = "Pipe"

    def spelunk_manager(self):
        return
