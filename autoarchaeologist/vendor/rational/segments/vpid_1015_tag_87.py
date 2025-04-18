#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   VPID 1015 - TAG 0x87
   =========================================

   FE_HANDBOOK.PDf 187p

    Note: […] The D2 mapping is:

        […]
        ARCHIVED_CODE      1015
        […]


'''

from .common import ManagerSegment

class V1015T87(ManagerSegment):

    VPID = 1015
    TAG = 0x87
    TOPIC = "Archived_Code"

    def spelunk_manager(self):
        return
