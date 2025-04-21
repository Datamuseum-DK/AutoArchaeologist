#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   VPID 1005 - TAG 0x7d
   =========================================

   FE_HANDBOOK.PDf 187p

    Note: […] The D2 mapping is:

        […]
        GROUP           1005
        […]

'''

from ....base import bitview as bv
from . import common as cm

class Bla99(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            b99_000_b_=512,
        )

class G00(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            g00_000_c_=-32,
            g00_001_b_=-32,
            g00_002_p_=bv.Pointer(G01),
            g00_003_z_=-32,
            g00_004_p_=bv.Pointer(G03),
            g00_005_n_=-1,
            #g00_004_p_=Pointer,
        )
        #assert self.g00_000_c_.val == 4
        #assert self.g00_003_z_.val == 0
        #self.points_to(bvtree, self.g00_002_p.val, G02)
        #self.points_to(bvtree, self.g00_004_p.val, G01)

class G01(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            g01_000_c_=bv.Pointer(G02),
            g01_001_b_=35,
        )

class G02(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            g02_000_p_=cm.TimedProperty,
            g02_010_p_=cm.TimedProperty,
            g02_020_p_=cm.TimedProperty,
            g02_030_p_=cm.TimedProperty,
            g02_obj_=bv.Array(2, cm.ObjRef),
            g02_valid_=bv.Array(2, -32),
            g02_nbr_n_=bv.Array(2, -10),
            vertical=True,
        )

class G03(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            g03_000_b_=-32,
            g03_001_b_=-32,
            g03_002_p_=bv.Pointer(G01),
            g03_004_b_=-32,
            g03_005_b_=-32,
            g03_006_b_=-1,
        )
        #assert self.u03_013_z_.val == 0

class GroupHead(bv.Struct):

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            mgr_=cm.MgrHead,
            hd_sh_=bv.Pointer(GroupSubHead),
            hd_001_p_=bv.Pointer(GroupBitMap),
            hd_002_n_=-32,
            hd_003_p_=bv.Pointer(cm.BTree),
        )

class GroupSubHead(bv.Struct):

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            sh_001_n_=-32,
            sh_002_p_=bv.Pointer(GroupHash),
            sh_003_n_=-32,
            sh_004_n_=-33,
        )

class GroupBitMap(bv.Struct):
   
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            gb_001_b_=-1024,
        )

class GroupHash(bv.Struct):
    def __init__(self, bvtree, lo, **kwargs):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            hash_=bv.Array(101, bv.Pointer(G00), vertical=True),
            **kwargs,
        )

class V1005T7D(cm.ManagerSegment):

    VPID = 1005
    TAG = 0x7d
    TOPIC = "Group"

    def spelunk_manager(self):

        self.head = GroupHead(self, self.seg_head.hi).insert()
