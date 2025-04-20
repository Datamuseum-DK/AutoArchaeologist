#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   VPID 1008 - TAG 0x80
   =========================================

   FE_HANDBOOK.PDf 187p

    Note: […] The D2 mapping is:

        […]
        TERMINAL       1008
        […]

'''

from ....base import bitview as bv
from . import common as cm


class T97(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            t97_000_z_=-177,
            t97_006_z_=cm.StringArray,
            t97_007_z_=-357,
            t97_008_z_=cm.StringArray,
            t97_099_z_=-443,
        )

class T98(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            t98_000_z_=-32,
            t98_001_z_=-32,
            t98_002_z_=bv.Pointer(T97),
            t98_099_z_=-65,
        )

class T99(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            t99_049_z_=-205,
            t99_096_z_=bv.Pointer(T99),
            t99_097_z_=bv.Pointer(T99),
            t99_098_z_=bv.Pointer(T99),
            t99_099_z_=bv.Pointer(T99),
        )

class TerminalHead(bv.Struct):

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            mgr_=cm.MgrHead,
            hd_sh_=bv.Pointer(TerminalSubHead),
            hd_001_n_=-32,
            hd_002_n_=bv.Pointer(cm.BTree),
        )

class TerminalSubHead(bv.Struct):

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            sh_000_c_=-32,
            sh_001_p_=bv.Pointer(),
            sh_002_b_=-32,
            sh_003_b_=-32,
            sh_004_b_=-1,
        )


class V1008T80(cm.ManagerSegment):

    VPID = 1008
    TAG = 0x80
    TOPIC = "Terminal"

    def spelunk_manager(self):

        self.head = TerminalHead(self, self.seg_head.hi).insert()

        y = cm.PointerArray(
            self,
            self.head.hd_sh.dst().sh_001_p.val,
            dimension=257,
            cls=T98,
        ).insert()

        bv.Pointer(T99)(self, 0x34e).insert()
