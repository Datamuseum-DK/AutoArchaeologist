#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   VPID 1002 - TAG 0x7a
   =========================================

   FE_HANDBOOK.PDf 187p

    Note: […] The D2 mapping is:

        […]
        DDB      1002
        […]


'''

from .common import ManagerSegment

class V1002T7A(ManagerSegment):

    VPID = 1002
    TAG = 0x7a
    TOPIC = "DDB"

    def spelunk_manager(self):
        return
