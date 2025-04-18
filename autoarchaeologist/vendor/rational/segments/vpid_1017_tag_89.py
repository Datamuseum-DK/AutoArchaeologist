#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   VPID 1017 - TAG 0x89
   =========================================

   Not mentioned in FE_HANDBOOK.PDf 187p

'''

from .common import ManagerSegment

class V1017T89(ManagerSegment):

    VPID = 1017
    TAG = 0x89
    TOPIC = "Native_Segment_Map"

    def spelunk_manager(self):
        return
