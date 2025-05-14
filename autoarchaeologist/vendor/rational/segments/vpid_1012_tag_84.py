#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   VPID 1012 - TAG 0x84
   =========================================

   FE_HANDBOOK.PDF 187p

    Note: […] The D2 mapping is:

        […]
        LINK      1012
        […]


'''

from .common import ManagerSegment

class V1012T84(ManagerSegment):

    VPID = 1012
    TAG = 0x84
    TOPIC = "Link"

    def spelunk_manager(self):
        return
