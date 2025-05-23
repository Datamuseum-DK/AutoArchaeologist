#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   VPID 1016 - TAG 0x88
   =========================================

   FE_HANDBOOK.PDF 187p

    Note: […] The D2 mapping is:

        […]
        PROGRAM_LIBRARY      1016
        […]


'''

from .common import ManagerSegment

class V1016T88(ManagerSegment):

    VPID = 1016
    TAG = 0x88
    TOPIC = "Program_Library"

    def spelunk_manager(self):
        return
