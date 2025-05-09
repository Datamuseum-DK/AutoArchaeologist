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

from ....base import bitview as bv
from . import common as cm

class NativeSegHead(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            mgr_=cm.MgrHead,
            hd_sh_=bv.Pointer(NativeSegSubHead),
            hd_001_p_=bv.Pointer(),
            hd_th_=bv.Pointer(NativeSegTerHead),
            hd_003_p_=-32,
            hd_004_p_=-32,
        )

class NativeSegSubHead(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            f00_=-32,
            f01_=-32,
            f02_=-32,
            f03_=-32,
            f04_=1,
        )

class NativeSegTerHead(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            f00_=27,
            f01_=32,
            f02_=32,
        )

class EtWas(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            f00_=-14,
            f01_=-10,
            f02_=-24,
            nxt_=bv.Pointer(EtWas),
        )

class V1017T89(cm.ManagerSegment):

    VPID = 1017
    TAG = 0x89
    TOPIC = "Native_Segment_Map"

    def spelunk_manager(self):
        self.ns00 = NativeSegHead(self, self.seg_head.hi).insert()
        y = cm.PointerArray(
            self,
            self.ns00.hd_th.dst().hi,
            cls=EtWas,
            dimension=10007,
            elide=(0,)
        ).insert()

        if False:
            for n in range(100):
                Huh(self, n * 80 + 0x80aec).insert()

        if False:
            y = cm.PointerArray(
                self,
                self.ns00.hd_002_p.val,
                dimension=100,
            ).insert()

        #bv.Array(6009, EtWas, vertical=True)(self, 0x4e59a).insert()

        #for i in self.find_all(0x4e59a):
        #    print("I", i)

