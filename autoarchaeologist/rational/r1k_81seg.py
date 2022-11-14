'''
   R1000 '97' segments
   ===================

   Diana-trees, at least that's the current working theory.

'''

import sys

import autoarchaeologist.rational.r1k_bittools as bittools

class Bla1(bittools.R1kSegBase):

    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, -1), **kwargs)
        self.compact = True
        self.get_fields(
            ("b1_000_z", 32),
            ("b1_001_p", 32),
            ("b1_002_p", 32),
        )
        self.finish()
        bittools.make_one(self, "b1_002_p", Bla1)
        y = bittools.make_one(self, "b1_001_p", bittools.ArrayString)
        if False:
            if y != False:
                self.bla2 = y.end
                bittools.make_one(self, "bla2", Bla2)
            else:
                print("YY", hex(self.begin))

class Bla2(bittools.R1kSegBase):

    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, -1), **kwargs)
        self.compact = True
        self.get_fields(
            ("b2_000_n", 32),
            ("b2_dobj_n", 32),
        )
        self.fields[-1].fmt = "<DIRECTORY,%d,1>"
        self.get_fields(
            ("b2_002_p", 32),
            ("b2_003_p", 32),
            ("b2_004_p", 32),
            ("b2_005_n", 1),
            #("b2_006_p", 32),
            #("b2_007_n", 32),
            #("b2_008_n", 3),
        )
        self.finish()
        bittools.make_one(self, "b2_002_p", Bla3)
        bittools.make_one(self, "b2_003_p", Bla2)
        bittools.make_one(self, "b2_004_p", Bla2)

class Bla3(bittools.R1kSegBase):

    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, -1), **kwargs)
        self.compact = True
        self.get_fields(
            ("b3_000_p", 32),
            ("b3_001_n", 35),
        )
        self.finish()
        bittools.make_one(self, "b3_000_p", Bla4)

class Bla4(bittools.R1kSegBase):

    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, -1), **kwargs)
        self.compact = True
        self.get_fields(
            ("b4_000_p", 32),
            ("b4_001_p", 32),
        )
        self.finish()
        bittools.make_one(self, "b4_000_p", Bla5)
        bittools.make_one(self, "b4_001_p", Bla5)

class Bla5(bittools.R1kSegBase):

    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, -1), **kwargs)
        self.compact = True
        self.get_fields(
            ("b5_dobj_n", 31),
        )
        self.fields[-1].fmt = "<DIRECTORY,%d,1>"
        self.get_fields(
            ("b5_001_p", 32),
            ("b5_002_z", 32),
            ("b5_003_p", 32),
            ("b5_004_z", 32),
            ("b5_005_p", 32),
            ("b5_006_n", 32),
            ("b5_007_n", 16),
            ("b5_008_n", 52),
            ("b5_009_n", 16),
            ("b5_010_n", 32),
        )
        self.finish()
        bittools.make_one(self, "b5_003_p", Bla6)
        bittools.make_one(self, "b5_005_p", Bla9)
        if self.b5_007_n == 0x280:
            bittools.make_one(self, "b5_010_n", Bla13)

class Bla6(bittools.R1kSegBase):

    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, -1), **kwargs)
        self.compact = True
        self.get_fields(
            ("b6_000_p", 32),
            ("b6_001_z", 32),
            ("b6_002_n", 32),
            ("b6_003_n", 1),
            ("b6_004_p", 32),
        )
        self.finish()
        bittools.make_one(self, "b6_000_p", Bla7)
        bittools.make_one(self, "b6_004_p", Bla11)

class Bla7(bittools.R1kSegBase):

    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, -1), **kwargs)
        self.compact = True
        self.get_fields(
            ("b7_000_n", 32),
            ("b7_001_n", 32),
            ("b7_002_p", 30),
            ("b7_003_p", 32),
            ("b7_004_n", 1),
        )
        self.finish()
        bittools.make_one(self, "b7_002_p", Bla7)
        bittools.make_one(self, "b7_003_p", Bla7)

class Bla8(bittools.R1kSegBase):

    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, -1), **kwargs)
        self.compact = True
        self.get_fields(
            ("b8_000_n", 62),
            ("b8_001_p", 32),
            ("b8_002_p", 32),
            ("b8_003_n", 1),
        )
        self.finish()

class Bla9(bittools.R1kSegBase):

    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, -1), **kwargs)
        self.compact = True
        self.get_fields(
            ("b9_000_p", 32),
            ("b9_001_z", 31),
            ("b9_002_n", 32),
            ("b9_003_z", 33),
            ("b9_004_z", 1),
        )
        self.finish()
        bittools.make_one(self, "b9_000_p", Bla10)

class Bla10(bittools.R1kSegBase):

    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, -1), **kwargs)
        self.compact = True
        self.get_fields(
            ("ba_000_p", 32),
            ("ba_dobj_n", 31),
        )
        self.fields[-1].fmt = "<DIRECTORY,%d,1>"
        self.get_fields(
            ("ba_002_p", 32),
            ("ba_003_p", 32),
            ("ba_004_n", 1),
        )
        self.finish()
        bittools.make_one(self, "ba_002_p", Bla10)
        bittools.make_one(self, "ba_003_p", Bla10)

class Bla11(bittools.R1kSegBase):

    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, -1), **kwargs)
        self.compact = True
        self.get_fields(
            ("bb_000_n", 127),
        )
        self.finish()

class Bla12(bittools.R1kSegBase):

    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, -1), **kwargs)
        self.compact = True
        self.get_fields(
            ("bc_000_n", 13),
            ("bc_050_n", 32),
            ("bc_051_n", 32),
            ("bc_052_n", 32),
            ("bc_053_n", 32),
            ("bc_054_n", 32),
            ("bc_055_n", 32),
            ("bc_100_p", 32),
            ("bc_101_p", 32),
            ("bc_102_p", 32),
            ("bc_103_p", 32),
        )
        self.finish()
        bittools.make_one(self, "bc_100_p", Bla12)
        bittools.make_one(self, "bc_101_p", Bla12)
        bittools.make_one(self, "bc_102_p", Bla12)
        bittools.make_one(self, "bc_103_p", Bla12)

class Bla13(bittools.R1kSegBase):

    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, -1), **kwargs)
        self.compact = True
        self.get_fields(
            ("bd_000_n", 0x8),
            ("bd_001_n", 0x20),
            ("bd_002_n", 0x20),
        )
        if int(self.chunk[:8], 2) == 0x80:
            self.get_fields(
                ("bd_003_n", 229),
            )
        self.finish()

class Head(bittools.R1kSegBase):

    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, -1), **kwargs)
        # self.compact = True
        self.get_fields(
            ("hd_000_n", 32),
            ("hd_001_n", 32),
            ("hd_002_n", 32),
            ("hd_003_n", 32),
            ("hd_004_n", 32),
            ("hd_005_n", 32),
            ("hd_006_n", 32),
            ("hd_007_n", 32),
            ("hd_008_n", 32),
            ("hd_009_p", 32),
            ("hd_010_n", 32),
            ("hd_011_p", 32),
            ("hd_012_n", 1),
            ("hd_013_n", 32),
            ("hd_014_n", 32),
            ("hd_015_n", 32),
            ("hd_015_n", 32),
            ("hd_016_n", 32),
            ("hd_017_p", 32),
            ("hd_018_n", 32),
            ("hd_019_n", 32),
        )
        self.finish()
        bittools.make_one(self, "hd_009_p", Bla12)

class R1kSeg81():
    ''' A Diana Tree Segmented Heap '''
    def __init__(self, seg):
        p = seg.mkcut(0x80)
        if False:
            p = seg.mkcut(0x1cc1fd4)
            p = seg.mkcut(0x1cc20d4)
            p = seg.mkcut(0x1cc1ff4)
            p = seg.mkcut(0x1cc21d4)
            p = seg.mkcut(0x1cc20f4)
            p = seg.mkcut(0x1cc21f4)
        self.seg = seg
        if True:
            for i in (
                0x378f6e0,
            ):
                print(hex(i))
                for j in seg.hunt(bin(i | (1<<32))[3:]):
                    print("  ", j, hex(j[1]), hex(j[2]))

        self.hd = Head(seg, 0x80)
        bittools.PointerArray(seg, self.hd.hd_017_p, target=Bla1)
        bittools.BitPointerArray(seg, self.hd.hd_011_p, 0x2717, target=Bla2)
