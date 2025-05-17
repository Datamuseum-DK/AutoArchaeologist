#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   VPID 1017 - TAG 0x89 - Native_Segment_Map
   =========================================

   Not mentioned in FE_HANDBOOK.PDF 187p
   Not mentioned in Guru Course 1 pg 133

   Layout based descriptions in pure segment ⟦f47e6ad1b⟧
'''

from ....base import bitview as bv
from . import common as cm

class NativeSegmentMapHead(bv.Struct):
    ''' ⟦f47e6ad1b⟧ @ 0x50d39 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_n_=-31,
            m001_n_=bv.Array(2, -32),
            m002_p_=bv.Array(2, bv.Pointer),		# NSM05
            m003_p_=bv.Array(2, bv.Pointer.to(NSM04)),
            m004_p_=bv.Array(2, bv.Pointer.to(NSM03)),
        )

class NSM03(bv.Struct):
    ''' ⟦f47e6ad1b⟧ @ 0x53e59 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m00_=-5,
            m01_=-22,
            m02_=bv.Array(2, bv.Pointer.to(NSM06)),
       )

class NSM04A(bv.Struct):
    ''' ⟦f47e6ad1b⟧ @ 0x54c01 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            m00_=-2,
            m01_=bv.Pointer.to(NSM07),		# NSM07
        )

class NSM04(bv.Struct):
    ''' ⟦f47e6ad1b⟧ @ 0x545e1 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m00_=bv.Pointer.to(NSM07),		# NSM07
            m01_=bv.Pointer,			# NSM08
            m02_=-31,
            m03_=NSM04A,
        )

class NSM06(bv.Struct):
    ''' ⟦f47e6ad1b⟧ @ 0x552f9 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m00_=bv.Array(0x2716 + 1, bv.Pointer.to(NSM09), vertical=True, elide=(0,)),
        )

class NSM07(bv.Struct):
    ''' ⟦f47e6ad1b⟧ @ 0x55949 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_=bv.Array(2, -32),
            m001_=bv.Pointer.to(NSM10),
            m002_=bv.Pointer.to(NSM07),
            m003_=bv.Pointer.to(NSM07),
            m004_=-1,
        )

class NSM09A(bv.Struct):
    ''' ⟦f47e6ad1b⟧ @ 0x56c31 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            m000_n_=-24,
            m001_n_=-24,
        )

class NSM09(bv.Struct):
    ''' ⟦f47e6ad1b⟧ @ 0x56af1 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            m000_s_=NSM09A,
            m001_p_=bv.Pointer.to(NSM09),
        )

class NSM10(bv.Struct):
    ''' ⟦f47e6ad1b⟧ @ 0x57439 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            # m001 is empty record
            m001_=-3,
            m002_=-32,
        )

class V1017T89(cm.ManagerSegment):
    ''' Native Segment Map Manager Segment - VPID 1017 - TAG 0x89 '''

    VPID = 1017
    TAG = 0x89
    TOPIC = "Native_Segment_Map"

    def spelunk_manager(self):
        head = NativeSegmentMapHead(self, self.seg_head.hi).insert()
        bv.Pointer(self, head.hi, target=cm.BTree).insert()
