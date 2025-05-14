#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   VPID 1017 - TAG 0x89
   =========================================

   Not mentioned in FE_HANDBOOK.PDF 187p

'''

from ....base import bitview as bv
from . import common as cm

class NativeSeg01(bv.Struct):
    def __init__(self, bvtree, lo):
        ''' ⟦f47e6ad1b⟧ @ 0x50d39 '''
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m001_n_=-31,
            m002_n_=bv.Array(2, -32),
            m003_p_=bv.Array(2, bv.Pointer),
            m004_p_=bv.Array(2, bv.Pointer.to(NativeSeg04)),
            m005_p_=bv.Array(2, bv.Pointer.to(NativeSeg03)),
        )

class NativeSeg03(bv.Struct):
    def __init__(self, bvtree, lo):
        ''' ⟦f47e6ad1b⟧ @ 0x53e59 '''
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m00_=-5,
            m01_=-22,
            m02_=bv.Array(2, bv.Pointer.to(NativeSeg05)),
       )

class NativeSeg04a(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            m00_=-2,
            m01_=bv.Pointer,
        )

class NativeSeg04(bv.Struct):
    def __init__(self, bvtree, lo):
        ''' ⟦f47e6ad1b⟧ @ 0x545e1 '''
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m00_=bv.Pointer.to(NativeSeg06),
            m01_=bv.Pointer,
            m02_=-31,
            m03_=NativeSeg04a,
        )

class NativeSeg05(bv.Struct):
    def __init__(self, bvtree, lo):
        ''' ⟦f47e6ad1b⟧ @ 0x552f9 '''
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m00_=bv.Array(0x2716 + 1, bv.Pointer.to(NativeSeg08), vertical=True),
        )

class NativeSeg06(bv.Struct):
    def __init__(self, bvtree, lo):
        ''' ⟦f47e6ad1b⟧ @ 0x55949 '''
        super().__init__(
            bvtree,
            lo,
            m00_=bv.Array(2, -32),
            m01_=bv.Pointer.to(NativeSeg09),
            m02_=bv.Pointer,
            m03_=bv.Pointer,
            m04_=-1,
        )

class NativeSeg07(bv.Struct):
    def __init__(self, bvtree, lo):
        ''' ⟦f47e6ad1b⟧ @ 0x564a1 '''
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m00_=bv.Array(0x3f0 + 1, -32, vertical=True),
        )

class NativeSeg08a(bv.Struct):
    def __init__(self, bvtree, lo):
        ''' ⟦f47e6ad1b⟧ @ 0x56af1 '''
        super().__init__(
            bvtree,
            lo,
            m00_=-24,
            m01_=-24,
        )
class NativeSeg08(bv.Struct):
    def __init__(self, bvtree, lo):
        ''' ⟦f47e6ad1b⟧ @ 0x56af1 '''
        super().__init__(
            bvtree,
            lo,
            m00_=NativeSeg08a,
            m01_=bv.Pointer.to(NativeSeg08),
        )

class NativeSeg09(bv.Struct):
    def __init__(self, bvtree, lo):
        ''' ⟦f47e6ad1b⟧ @ 0x57439 '''
        super().__init__(
            bvtree,
            lo,
            m00_=-3,
            m01_=-32,
        )

class V1017T89(cm.ManagerSegment):

    VPID = 1017
    TAG = 0x89
    TOPIC = "Native_Segment_Map"

    def spelunk_manager(self):

        self.ns00 = NativeSeg01(self, self.seg_head.hi).insert()
        bv.Pointer(self, self.ns00.hi, target=cm.BTree).insert()

        #bv.Array(2577, NativeSeg08, vertical=True)(self, 0x4e59c).insert()

        #cm.BTree(self, 0xb7a6e).insert()
        #cm.BTree(self, 0xbc6a4).insert()
        #cm.BTree(self, 0xc1216).insert()
        #cm.BTree(self, 0xc5d88).insert()
        #cm.BTree(self, 0xca8fa).insert()
        #cm.BTree(self, 0xcf46c).insert()
        #cm.BTree(self, 0xd3fde).insert()
        #cm.BTree(self, 0xd8b50).insert()
        #cm.BTree(self, 0xdd6c2).insert()
        #cm.BTree(self, 0xe2234).insert()
