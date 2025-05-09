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

   Struct Layouts based on pure description in ⟦c05ddcbe7⟧
'''

from ....base import bitview as bv
from . import common as cm

class IndirectFieldRefComponent(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            offset_=-32,
            width_=-32,
        )

class T94(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            t94_000_n_=-1,
            t94_001_n_=-31,
            t94_002_n_=-31,
            t94_003_n_=-32,
        )

class T95(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            t95_000_n_=-1,
            t95_001_n_=-31,
            t95_002_n_=-31,
            # Not quite sure about the rest...
            t95_003_n_=IndirectFieldRefComponent,
            t95_004_n_=-32,
            t95_005_n_=-32,
            t95_006_n_=bv.Array(0x14, -8),
        )

class T96(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            t96_000_n_=-4,
            t96_001_n_=-1,
            t96_002_n_=-1,
            t96_003_n_=-1,
            t96_004_n_=-1,
            t96_005_n_=-1,
            t96_006_n_=-1,
            t96_007_n_=-4,
            t96_008_n_=-4,
            t96_009_n_=-2,
            t96_010_n_=-2,
            t96_011_n_=-2,
            t96_012_n_=-1,
            t96_013_n_=-8,
            t96_014_n_=-8,
            t96_015_s_=T95,
            t96_016_n_=-31,
            t96_017_n_=-31,
            t96_018_s_=T94,
            t96_019_s_=-32,
        )


class T97(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            t97_000_z_=-9,
            t97_001_s_=T96,
            t97_002_s_=T96,
            t97_003_s_=cm.TimedProperty,
            t97_004_s_=cm.TimedProperty,
            t97_005_s_=cm.TimedProperty,
            t97_006_s_=-3,
            t97_007_s_=-32,
        )

class T98(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            t98_000_z_=-64,
            t98_001_z_=bv.Pointer(T97),
            t98_002_z_=bv.Pointer(),
            t98_003_z_=bv.Pointer(),
            t98_004_z_=-1,
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

class T04(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            t04_000_c_=-2,
            t04_001_b_=bv.Pointer(),
        )

class TerminalSubHead(bv.Struct):
    ''' Based on pure spec ⟦c05ddcbe7⟧ '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            sh_000_c_=bv.Pointer(),
            sh_001_p_=bv.Pointer(),
            sh_002_b_=-31,
            sh_003_b_=T04,
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
