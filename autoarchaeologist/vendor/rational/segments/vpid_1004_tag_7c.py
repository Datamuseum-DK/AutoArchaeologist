#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   VPID 1004 - TAG 0x7c
   =========================================

   FE_HANDBOOK.PDf 187p

    Note: […] The D2 mapping is:

        […]
        USER            1004
        […]

   20240304 accounts for all bits in 20b035c69 from disk08
'''

from ....base import bitview as bv
from . import common as cm

class U00(bv.Struct):
    def __init__(self, bvtree, lo, **kwargs):
        super().__init__(
            bvtree,
            lo,
            u00_000_c__=-32,
            u00_001_b_=-32,
            u00_002_p_=bv.Pointer(U02),
            u00_003_z__=-32,
            u00_004_p_=bv.Pointer(U00),
            u00_005_n_=-1,
            **kwargs,
        )
        assert self.u00_000_c_.val == 4
        assert self.u00_003_z_.val == 0

class U01(bv.Struct):
    def __init__(self, bvtree, lo, **kwargs):
        super().__init__(
            bvtree,
            lo,
            u01_000_c__=-32,
            u01_001_p_=-32,
            u01_002_p_=bv.Pointer(U02),
            u01_003_z__=-32,
            u01_004_z__=-33,
            **kwargs,
        )
        assert self.u01_000_c_.val == 4
        assert self.u01_003_z_.val == 0
        assert self.u01_004_z_.val == 0

class U02(bv.Struct):
    def __init__(self, bvtree, lo, **kwargs):
        super().__init__(
            bvtree,
            lo,
            u02_000_p_=bv.Pointer(U03),
            u02_001_n_=-3,
            u02_002_n_=-32,
            **kwargs,
        )

    def dot_node(self, dot):
        return None, ["color=red"]

class U03(bv.Struct):
    def __init__(self, bvtree, lo, **kwargs):
        super().__init__(
            bvtree,
            lo,
            u03_000_b_=cm.TimedProperty,	# = {0x1, 0x4, 0x12, 0x23
            u03_001_b_=cm.TimedProperty,
            u03_002_b_=cm.TimedProperty,
            u03_003_b_=cm.TimedProperty,
            u03_004_c_=cm.ObjRef,
            u03_005_c_=cm.ObjRef,
            u03_006__=bv.Constant(32, 1),
            u03_007_=-32,
            u03_009_s_=U17,
            u03_020_s_=U17,
            u03_099_z__=-128,	# = 0x0
            vertical=True,
            **kwargs,
        )

    def dot_node(self, dot):
        return None, ["color=orange"]

class U07(bv.Struct):
    def __init__(self, bvtree, lo, **kwargs):
        super().__init__(
            bvtree,
            lo,
            u07_000_p_=bv.Pointer(U08),
            **kwargs,
        )

class U08(bv.Struct):
    def __init__(self, bvtree, lo, **kwargs):
        super().__init__(
            bvtree,
            lo,
            u08_000_p_=-32,
            u08_001_p_=-32,
            u08_002_c__=-31,
            u08_003_p_=bv.Pointer(U08),
            **kwargs,
        )
        assert self.u08_002_c_.val == 1


class ListHead(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            entry_=bv.Pointer(ListEntry),
        )

    def dot_node(self, dot):
        return None, ["shape=plaintext"]

class ListEntry(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            obj_=cm.ObjRef,
            next_=bv.Pointer(ListEntry),
        )

    def dot_node(self, dot):
        return None, ["color=cyan"]

class SessionList(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            u16_010_c_=cm.ObjRef,
            u16_040_n_=bv.Pointer(SessionList),
        )

class U17(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            u17_000_n_=-32,
            u17_010_=cm.ObjRef,
            u17_020_=cm.ObjRef,
            u17_070__=bv.Constant(32, 0),
            u17_groups_=bv.Pointer(ListHead),
            u17_090__=bv.Constant(32, 0),
            u17_sessions_=bv.Pointer(ListHead),
        )


class U26(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            u26_010_n_=-32,
            u26_020_n_=-32,
        )

class UserHead(bv.Struct):

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            mgr_=cm.MgrHead,
            hd_sh_=bv.Pointer(UserSubHead),
            hd_001_p_=bv.Pointer(),
            hd_002_n_=-32,
            hd_003_p_=bv.Pointer(cm.BTree),
        )

class UserSubHead(bv.Struct):

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            sh_001_n_=-32,
            sh_002_p_=bv.Pointer(),
            sh_003_n_=-32,
            sh_004_n_=-33,
        )


class V1004T7C(cm.ManagerSegment):

    VPID = 1004
    TAG = 0x7c
    TOPIC = "User"

    def find_ptr(self, adr, width=32):
        print("FF", hex(adr), hex(self.bits.find(bin((1<<width)|adr)[3:])))

    def spelunk_manager(self):

        self.head = UserHead(self, self.seg_head.hi).insert()

        #if True:
            # Possibly the array limits of hd_009_p
        #    U26(self, self.head.hd_007_p.val).insert()

        y = cm.PointerArray(
            self,
            self.head.hd_sh.dst().sh_002_p.val,
            dimension=101,
            cls=U00,
        ).insert()
