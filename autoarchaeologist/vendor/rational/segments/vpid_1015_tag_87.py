#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   VPID 1015 - TAG 0x87
   =========================================

   FE_HANDBOOK.PDF 187p

    Note: […] The D2 mapping is:

        […]
        ARCHIVED_CODE      1015
        […]


'''

from ....base import bitview as bv
from . import common as cm

class ArchCodeHead(bv.Struct):

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            mgr_=cm.MgrHead,
            hd_sh_=bv.Pointer.to(ArchCodeSubHead),
            hd_001_n_=-32,
            hd_002_n_=bv.Pointer.to(cm.BTree),
        )

class ArchCodeSubHead(bv.Struct):

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            sh_000_c_=-32,
            sh_001_b_=bv.Pointer,
            sh_002_b_=-32,
            sh_003_b_=-32,
            sh_004_b_=-1,
        )

class V1015T87(cm.ManagerSegment):

    VPID = 1015
    TAG = 0x87
    TOPIC = "Archived_Code"

    def spelunk_manager(self):
        self.head = ArchCodeHead(self, self.seg_head.hi).insert()
