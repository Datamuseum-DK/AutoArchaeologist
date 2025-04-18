#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   VPID 1001 - TAG 0x79
   =========================================

   FE_HANDBOOK.PDf 187p

    Note: […] The D2 mapping is:

        […]
        ADA            1001
        […]


'''

from ....base import bitview as bv
from . import common as cm

class Pointer31(bv.Pointer_Class):
    WIDTH = 31

class A00(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            hd_001_n_=-31,
            hd_002_n_=-32,
            hd_003_n_=-32,
            hd_004_n_=-32,
            hd_005_n_=-32,
            hd_006_n_=-32,
            hd_007_p_=bv.Pointer(A13),
            hd_008_n_=-32,
            #hd_009_p_=bv.Pointer(A07),
            hd_009_p_=bv.Pointer(cm.BTree),
            hd_010_n_=-32,
            hd_011_p_=bv.Pointer(),
            hd_012_n_=-32,
            hd_013_n_=-1,
            hd_014_n_=bv.Pointer(A12),
        )

class A02(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            a02_000_n_=-7,
            a02_001_n_=-31,
            a02_003_n_=bv.Constant(31, 1),
            a02_004_n_=-31,
            a02_005_n_=bv.Pointer(A02),
        )


class A03(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            a03_050_n_=-32,
            a03_051_n_=-32,
            a03_052_n_=bv.Pointer(A04),
            a03_053_n_=bv.Pointer(A03),
            a03_054_n_=bv.Pointer(A03),
            a03_055_n_=-1,
        )

    def dot_node(self, dot):
        return "0x%x\\n?0x%x\\n0x%x" % (self.a03_050_n.val, self.a03_051_n.val, self.a03_055_n.val), ["shape=triangle"]

class A04(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            a04_050_n_=bv.Pointer(A05),
            a04_051_n_=-35,
        )

    def dot_node(self, dot):
        return "?0x%x" % self.a04_051_n.val, None


class A05(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            more=True,
            a05_000_n_=cm.TimedProperty,
            a05_001_n_=cm.TimedProperty,
            a05_040_n_=-38,
            a05_041_n_=-32,
            a05_042_n_=-64,
            a05_043_n_=-32,
            a05_050_n_=A15,
            a05_051_n_=A15,
            a05_094_n_=-32,
        )
        d = (self.lo + 0x3ae) - self.hi
        if d > 0:
            print("D", d)
            self.add_field("end", -d)
        self.done()


class A06(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            a06_045_n_=-32,
            a06_046_n_=-32,
            a06_047_n_=-32,
        )

class A07(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            a07_049_n_=-205,
            a07_070_n_=bv.Pointer(A07),
            a07_090_n_=bv.Pointer(A07),
            a07_091_n_=bv.Pointer(A07),
            a07_092_n_=bv.Pointer(A07),
        )


class A08(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            a08_050_n_=-32,
            a08_051_n_=bv.Pointer(A06),
            a08_052_n_=-96,
        )

class A09(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            a09_050_n_=-32,
        )

class A10(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            a10_050_n_=-64,
            a10_051_n_=-64,
            a10_084_n_=-24,
            a10_085_n_=-64,
            a10_086_n_=-64,
            a10_087_n_=-32,
            a10_088_n_=-22,
            a10_089_n_=-64,
            a10_090_n_=-64,
            a10_091_n_=-32,
            a10_092_n_=-32,
            a10_093_n_=-64,
            a10_094_n_=-64,
            a10_095_n_=-64,
            a10_096_n_=-64,
            a10_097_n_=-64,
            a10_098_n_=-64,
            a10_099_n_=-32,
        )

class A11(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            a11_050_n_=bv.Pointer(A10),
            a11_099_n_=-35,
        )

class A12(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            a12_000_n_=-64,
            a12_002_n_=bv.Pointer(A11),
            a12_003_n_=bv.Pointer(A12),
            a12_004_n_=-33,
        )

class A13(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            a13_000_n_=-6,
            a13_001_n_=-32,
            a13_002_p_=-32,
            a13_003_n_=-32,
            a13_004_p_=bv.Pointer(A08),
            a13_005_n_=-32,
            a13_006_p_=bv.Pointer(),
            a13_007_n_=-32,
            a13_008_p_=bv.Pointer(A09),
            vertical=True,
        )

class A15(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            a15_001_n_=-35,
            a15_002_n_=-32,
            a15_003_n_=-64,
            a15_004_n_=cm.TimedProperty,
            a15_005_n_=cm.ObjRef,
	)

class V1001T79(cm.ManagerSegment):

    VPID = 1001
    TAG = 0x79
    TOPIC = "Ada"

    def spelunk_manager(self):

        self.a00 = A00(self, self.seg_head.hi).insert()

        y = cm.PointerArray(
            self,
            self.a00.hd_007_p.dst().a13_006_p.val,
            dimension=1009,
            cls=A02,
        ).insert()

        cm.PointerArray(
            self,
            self.a00.hd_011_p.val,
            dimension=1009,
            cls=A03,
        ).insert()

        print(self.this, "FF", list(self.find_all(0x18ffa9e)))
