#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   VPID 1004 - TAG 0x7c
   =========================================

   FE_HANDBOOK.PDF 187p

    Note: […] The D2 mapping is:

        […]
        USER            1004
        […]

   Layout based descriptions in pure segment ⟦cde05a7c6⟧
'''

from ....base import bitview as bv
from . import common as cm

class UserHead(bv.Struct):
    ''' ⟦cde05a7c6⟧ @ 0x5eac1 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_n_=-31,
            m001_n_=bv.Array(2, -32),
            m002_p_=bv.Array(2, bv.Pointer),
            m003_p_=bv.Pointer.to(U04),
            m004_p_=bv.Array(2, bv.Pointer.to(U03)),
        )

class U03(bv.Struct):
    ''' ⟦cde05a7c6⟧ @ 0x61be1 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            m000_p_=bv.Array(2, bv.Pointer),
        )

class U04A(bv.Struct):
    ''' ⟦cde05a7c6⟧ @ 0x625e9 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_n_=2,
            m001_p_=bv.Pointer,
        )

class U04(bv.Struct):
    ''' ⟦cde05a7c6⟧ @ 0x61fc9 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_n_=bv.Pointer,
            m001_p_=bv.Pointer.to(U08),
            m002_n_=-31,
            m003_n_=U04A,
        )

class U07(bv.Struct):
    ''' ⟦cde05a7c6⟧ @ 0x62ef1 '''

    def __init__(self, bvtree, lo, **kwargs):
        super().__init__(
            bvtree,
            lo,
            m000_c_=bv.Array(2, -32),
            m001_p_=bv.Pointer.to(U09),
            m002_p_=bv.Pointer.to(U07),
            m003_p_=bv.Pointer.to(U07),
            m004_n_=-1,
            **kwargs,
        )

class U08(bv.Struct):
    ''' ⟦cde05a7c6⟧ @ 0x63a49 '''

    def __init__(self, bvtree, lo, **kwargs):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            hash_=bv.Array(101, bv.Pointer.to(U07), vertical=True),
            **kwargs,
        )

class U09(bv.Struct):
    ''' ⟦cde05a7c6⟧ @ 0x64099 '''

    def __init__(self, bvtree, lo, **kwargs):
        super().__init__(
            bvtree,
            lo,
            m000_p_=bv.Pointer.to(U10),
            m001_n_=-3,
            m002_n_=-32,
            **kwargs,
        )

class U10A(bv.Struct):
    ''' ⟦cde05a7c6⟧ @ 0x683d1 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_n_=-32,
            m001_s_=cm.ObjRef,
            m002_s_=cm.ObjRef,
            m003_p_=bv.Array(2, bv.Pointer.to(U12)),
            m004_p_=bv.Array(2, bv.Pointer.to(U11)),
        )

class U10(bv.Struct):
    ''' ⟦cde05a7c6⟧ @ 0x64821 '''

    def __init__(self, bvtree, lo, **kwargs):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_=cm.TimedProperty,
            m001_=cm.TimedProperty,
            m002_=cm.TimedProperty,
            m003_=cm.TimedProperty,
            m004_=cm.ObjRef,
            m005_=cm.ObjRef,
            m006_=-32,
            m007_=-32,
            m008_=U10A,
            m009_=U10A,

            # U10 consistently has a 128 byte tail not in the pure description
            x010_=-128,

            **kwargs,
        )

class U11(bv.Struct):
    ''' ⟦cde05a7c6⟧ @ 0x6bf71 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            entry_=bv.Pointer.to(U13),
        )

class U12(bv.Struct):
    ''' ⟦cde05a7c6⟧ @ 0x6c359 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            entry_=bv.Pointer.to(U14),
        )

class U13(bv.Struct):
    ''' ⟦cde05a7c6⟧ @ 0x6c741 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            obj_=cm.ObjRef,
            next_=bv.Pointer.to(U14),
        )

class U14(bv.Struct):
    ''' ⟦cde05a7c6⟧ @ 0x6d5b1 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            obj_=cm.ObjRef,
            next_=bv.Pointer.to(U14),
        )

class V1004T7C(cm.ManagerSegment):
    ''' User Manager Segment - VPID 1004 - TAG 0x7c '''

    VPID = 1004
    TAG = 0x7c
    TOPIC = "User"

    def spelunk_manager(self):
        head = UserHead(self, self.seg_head.hi).insert()
        bv.Pointer(self, head.hi, target=cm.BTree).insert()
