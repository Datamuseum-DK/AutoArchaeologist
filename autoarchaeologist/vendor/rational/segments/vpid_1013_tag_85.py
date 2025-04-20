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
from . import common as cm

class NullHead(bv.Struct):

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            mgr_=cm.MgrHead,
            hd_sh_=bv.Pointer(NullSubHead),
            hd_001_n_=-32,
            hd_002_n_=bv.Pointer(cm.BTree),
        )

class NullSubHead(bv.Struct):

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            sh_000_c_=-32,
            sh_001_b_=bv.Pointer(),
            sh_002_b_=-32,
            sh_003_b_=-32,
            sh_004_b_=-1,
        )

class V1013T85(cm.ManagerSegment):

    VPID = 1013
    TAG = 0x85
    TOPIC = "Null_Device"

    def spelunk_manager(self):
        self.head = NullHead(self, self.seg_head.hi).insert()
