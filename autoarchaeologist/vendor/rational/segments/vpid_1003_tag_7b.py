#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   VPID 1003 - TAG 0x7b - File
   ===========================

   FE_HANDBOOK.PDF 187p: Note: […] The D2 mapping is:

	[…]
	FILE		1003
	[…]

   hd_002_n is highest file number ?

   Layout based descriptions in pure segment ⟦8133374fe⟧
'''

from ....base import bitview as bv
from . import common as cm

class FileHead(bv.Struct):
    ''' ⟦8133374fe⟧ @ 0x470fbc1 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_n_=-31,
            m001_n_=bv.Array(2, -32),
            m002_p_=bv.Array(2, bv.Pointer),	# F05
            m003_p_=bv.Pointer.to(F04),
            m004_p_=bv.Array(2, bv.Pointer.to(F03)),
        )

class F03(bv.Struct):
    ''' ⟦8133374fe⟧ @ 0x4712ce1 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            # pure spec says length is zero
            x000_p_=-1,
        )

class F04A(bv.Struct):
    ''' ⟦8133374fe⟧ @ 0x47136d1 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            m000_p_=-2,
            m001_p_=bv.Pointer.to(F06),
        )

class F04(bv.Struct):
    ''' ⟦8133374fe⟧ @ 0x47130b1 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_n_=bv.Pointer.to(F06),
            m001_p_=bv.Pointer.to(F07),
            m002_n_=-31,
            m003_n_=F04A,
        )

class F06(bv.Struct):
    ''' ⟦8133374fe⟧ @ 0x4713dc9 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            m000_=bv.Array(2, -32),
            m001_=bv.Pointer.to(F08),
            m002_=bv.Pointer.to(F06),
            m003_=bv.Pointer.to(F06),
            m004_=-1,
        )

class F07(bv.Struct):
    ''' ⟦8133374fe⟧ @ 0x4714921 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_=bv.Array(0x3f1, bv.Pointer.to(F06), vertical=True),
        )

class F08(bv.Struct):
    ''' ⟦8133374fe⟧ @ 0x4714f71 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            m000_=bv.Pointer.to(F09),
            m001_=-3,
            m002_=-32,
        )

class F09B(bv.Struct):
    ''' ⟦8133374fe⟧ @ 0x4717861 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_=cm.Acl,
            m001_=bv.Array(2, -32),		# F11
            m002_=cm.TimedProperty,
            m003_=cm.ObjRef,
            m004_=-32,
        )

class F09A(bv.Struct):
    ''' ⟦8133374fe⟧ @ 0x47156f9 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            # pure defines these as:
            #   HeapAccessComponent {hac_loc=Location {0x0+0x40=0x40}, hac_3_n=CONST(0x0)}
            # The first element do not point into this heap and the second is 0x80
            m000_=bv.Array(2, -32),	# F10
            m001_=bv.Array(2, -32),	# F10
       )

class F09(bv.Struct):
    ''' ⟦8133374fe⟧ @ 0x47156f9 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_=cm.TimedProperty,
            m001_=cm.TimedProperty,
            m002_=-1,
            m003_=-2,
            m004_=-1,
            m005_=-1,
            m006_=-1,
            m007_=bv.Array(2, bv.Pointer),	# F07
            m008_=F09A,
            m009_=F09B,
            m010_=F09B,
        )

class V1003T7B(cm.ManagerSegment):
    ''' File Manager Segment - VPID 1003 - TAG 0x7b '''

    VPID = 1003
    TAG = 0x7b
    TOPIC = "File"

    def spelunk_manager(self):
        head = FileHead(self, self.seg_head.hi).insert()
        bv.Pointer(self, head.hi, target=cm.BTree).insert()
