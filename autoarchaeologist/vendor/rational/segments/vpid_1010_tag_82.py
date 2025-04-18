#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   VPID 1010 - TAG 0x82
   =========================================

   FE_HANDBOOK.PDf 187p

    Note: […] The D2 mapping is:

        […]
        CONFIGURATION      1010
        […]


'''

from .common import ManagerSegment

class V1010T82(ManagerSegment):

    VPID = 1010
    TAG = 0x82
    TOPIC = "Configuration"

    def spelunk_manager(self):
        return
