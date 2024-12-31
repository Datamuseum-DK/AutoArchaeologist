#!/usr/bin/env python3

'''
'''
    
from ....base import bitview as bv

class UX00(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            ux00_010_n_=-32,
            ux00_020_n_=-32,
            ux00_030_n_=-32,
            ux00_040_n_=-32,
            ux00_050_n_=-32,
            ux00_060_n_=-32,
            ux00_070_n_=-32,
            ux00_080_n_=-32,
            ux00_090_n_=-32,
            vertical=True,
        )

class UX01(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            ux01_020_n__=-64,
            more = True,
        )
        self.add_field("text", bv.Text(self.ux01_020_n_.val))
        self.txt = self.text.txt
        self.done()

class UX02(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            ux01_007_n_=bv.Constant(64, 4),
            ux01_008_n_=-64,
            ux01_009_n_=-64,
            ux01_010_n_=UX01,
            ux01_019_n_=-64,
            ux01_020_n_=UX01,
            ux01_029_n_=-64,
            ux01_030_n_=UX01,
            ux01_039_n_=-64,
            ux01_040_n_=UX01,
            ux01_049_n_=-64,
            ux01_050_n_=UX01,
            ux01_060_n_=bv.Constant(64, 1),
            ux01_061_n_=bv.Constant(64, 1),
            ux01_062_n_=-64,
            ux01_063_n_=bv.Constant(64, 5),
            ux01_064_n_=-64,
            ux01_065_n_=bv.Constant(64, 1),
            ux01_066_n_=bv.Constant(64, 9),
            ux01_067_n_=-64,
            ux01_068_n_=bv.Constant(64, 1),
            ux01_069_n_=-64,
            ux01_070_n_=bv.Constant(64, 5),
            ux01_071_n_=bv.Constant(64, 2),
            ux01_072_n_=bv.Constant(64, 1),
            ux01_073_n_=bv.Constant(64, 5),
            ux01_074_n_=bv.Constant(64, 1),
            #ux01_075_n_=-64,
            #ux01_076_n_=-64,
            #ux01_077_n_=-64,
            #ux01_078_n_=-64,
            #ux01_079_n_=-64,
            #ux01_080_n_=-64,
            #ux01_081_n_=-64,
            #ux01_082_n_=-64,
            #vertical=True,
        )

class DiscreteComponent(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            dc_id__=UX01,
            dc_1_n_=-64,
            dc_2_n_=-64,
            dc_3_n_=-64,
        )

class ArrayComponent(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            ac_id__=UX01,
            ac_1_n_=-64,
            ac_2_n_=-64,
        )

class ArrayBoundsComponent(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            abc_id__=UX01,
            abc_1_n_=-64,
            abc_2_n_=-64,
            abc_3_n_=-64,
            abc_4_n_=-64,
            abc_5_n_=-64,
        )

class HeapAccessComponent(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            hac_id__=UX01,
            hac_1_n_=-64,
            hac_2_n_=-64,
            hac_3_n_=-64,
        )

class ClauseComponent(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            clc_id__=UX01,
            clc_1_n_=-64,
            clc_2_n_=-64,
            clc_3_n_=-64,
            clc_4_n_=-64,
        )

class RecordComponent(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            rc_id__=UX01,
            rc_1_n_=-64,
            rc_2_n_=-64,
            rc_3_n_=-64,
        )

class DiscriminatedRecordComponent(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            drc_id__=UX01,
            drc_1_n_=-64,
            drc_2_n_=-64,
            drc_3_n_=-64,
            drc_4_n_=-64,
        )

class DiscriminatedRecordHeaderComponent(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            drhc_id__=UX01,
            drhc_1_n_=-64,
            drhc_2_n_=-64,
            drhc_3_n_=-64,
            drhc_4_n_=-64,
        )

class PureTxt(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            ux01_020_n__=-64,
            more = True,
        )
        self.add_field("text", bv.Text(self.ux01_020_n_.val))
        self.txt = self.text.txt
        self.done()

class Pure():

    def __init__(self, tree):
        self.tree = tree

        self.spelunk()

        for i in self.tree.find_all(0x88581):
            print("FF", hex(i))

        for i in self.tree.find_all(0x885c1):
            print("FF", hex(i))

    def spelunk(self):
        bv.Array(1, -32)(self.tree, 0xa1).insert()
        #bv.Array((0x301-0xc1) // 64, -64)(self.tree, 0xc1).insert()
        for lo, hi in self.tree.gaps():
            for adr in range(lo, hi - 100):
                if self.try_text(adr):
                    y = PureTxt(self.tree, adr)
                    self.expand(y)
        for lo, hi in self.tree.gaps():
            if (hi - lo) & 0x3f == 0:
                bv.Array((hi - lo) // 64, -64)(self.tree, lo).insert()

    def expand(self, txt):
        if txt.txt == "DISCRETE_COMPONENT":
            DiscreteComponent(self.tree, txt.lo).insert()
        elif txt.txt == "ARRAY_COMPONENT":
            ArrayComponent(self.tree, txt.lo).insert()
        elif txt.txt == "ARRAY_BOUNDS_COMPONENT":
            ArrayBoundsComponent(self.tree, txt.lo).insert()
        elif txt.txt == "HEAP_ACCESS_COMPONENT":
            HeapAccessComponent(self.tree, txt.lo).insert()
        elif txt.txt == "CLAUSE_COMPONENT":
            ClauseComponent(self.tree, txt.lo).insert()
        elif txt.txt == "RECORD_COMPONENT":
            RecordComponent(self.tree, txt.lo).insert()
        elif txt.txt == "DISCRIMINATED_RECORD_COMPONENT":
            DiscriminatedRecordComponent(self.tree, txt.lo).insert()
        elif txt.txt == "DISCRIMINATED_RECORD_HEADER_COMPONENT":
            DiscriminatedRecordHeaderComponent(self.tree, txt.lo).insert()
        else:
            txt.insert()

    def try_text(self, adr):
        x = int(self.tree.bits[adr:adr+64], 2)
        if x < 2 or x > 1000:
            return False
        for i in range(x):
            y = int(self.tree.bits[adr+64+i*8:adr+72+i*8], 2)
            if y < 32 or y > 126:
                return False
        return True
