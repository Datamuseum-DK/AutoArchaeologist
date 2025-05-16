#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   VPID 1011 - TAG 0x83 - Code_Segment
   ===================================

   FE_HANDBOOK.PDF 187p: Note: […] The D2 mapping is:

	[…]
	CODE_SEGMENT	1011
	[…]

'''

from ....base import bitview as bv
from . import common as cm

class CS54(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            cs54_000_n_=-31,
            cs54_001_n_=bv.Pointer.to(CS54),
        )

class CS55(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            cs55_bitmap_n__=-16384,
            cs55_040_n_=-20,
            cs55_045_n_=-8,
            cs55_049_n_=-31,
        )

class CodeSegHead(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            mgr_=cm.MgrHead,
            hd_sh_=bv.Pointer.to(CodeSegSubHead),
            hd_001_n_=-32,
            hd_002_n_=bv.Pointer.to(CS62),
            hd_003_n_=-32,
            hd_004_n_=bv.Pointer.to(cm.BTree),
        )

class CodeSegSubHead(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            sh_001_n_=-32,
            sh_002_n_=bv.Pointer.to(CS58),
            sh_003_n_=-1,
            sh_004_n_=-32,
            sh_005_n_=bv.Pointer.to(CS59),
        )


class CS58(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            cs58_000_n_=bv.Array(1009, bv.Pointer.to(CS59), vertical=True),
        )

class CS59(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            cs59_000_n_=-32,
            cs59_001_n_=-32,
            cs59_002_n_=bv.Pointer.to(CS60),
            cs59_003_n_=bv.Pointer.to(CS59),
            cs59_004_n_=bv.Pointer.to(CS59),
            cs59_005_n_=-1,
        )

class CS60(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            cs60_000_n_=-24,
            cs60_010_n_=-24,
            cs60_020_n_=cm.SegId,
            cs60_021_n_=-32,
            cs60_060_n_=-3,

            cs60_066_n_=cm.ObjRef,
            cs60_067_n_=cm.ObjRef,
            cs60_078_n_=-32,
            cs60_079_n_=-32,
            cs60_080_n_=cm.TimedProperty,
            cs60_081_n_=cm.TimedProperty,
            cs60_082_n_=cm.TimedProperty,
            cs60_083_n_=cm.TimedProperty,
            #cs60_090_n_=-73,
            cs60_097_n_=-16,
            cs60_098_n_=-19,
            cs60_099_n_=-32,
        )

class CS62(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            cs62_000_n_=bv.Array(0x2ff, CS55, vertical=True),
            cs62_001_n_=bv.Pointer.to(CS54),
        )

class V1011T83(cm.ManagerSegment):

    VPID = 1011
    TAG = 0x83
    TOPIC = "Code_Segment"

    def spelunk_manager(self):
       '''...'''

       CodeSegHead(self, 0xa1).insert()
       
       if False:
           b = 0x0c07326
           n = 0x2fd
           t = b - n * 16443
           t=0x1560d1d
           for a in range(t, t + 1):
           #for a in range(0x000429c, t):
               for n in self.find_all(a):
                   print("NN", hex(a), hex(n))
