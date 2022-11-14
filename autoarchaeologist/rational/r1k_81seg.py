'''
   R1000 '97' segments
   ===================

   Diana-trees, at least that's the current working theory.

'''

import sys

import autoarchaeologist.rational.r1k_bittools as bittools

class NameChain(bittools.R1kSegBase):

    ''' Chains of names from the same hash-bucket '''

    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, -1), **kwargs)
        self.compact = True
        self.get_fields(
            ("nc_00_z", 32),
            ("nc_01_p", 32),
            ("nc_02_p", 32),
        )
        self.finish()
        bittools.make_one(self, "nc_02_p", NameChain)
        y = bittools.make_one(self, "nc_01_p", bittools.ArrayString)

class Directory(bittools.R1kSegBase):

    ''' Directory node '''

    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, -1), **kwargs)
        self.compact = True
        self.get_fields(
            ("dir_00_n", 32),
            ("dir_nbr_n", 32),
        )
        self.fields[-1].fmt = "[DIRECTORY,%d,1]"
        self.get_fields(
            ("dir_02_p", 32),
            ("dir_03_p", 32),
            ("dir_04_p", 32),
            ("dir_05_n", 1),
        )
        self.finish()
        seg.directories[self.dir_nbr_n] = self
        self.b3 = bittools.make_one(self, "dir_02_p", Bla3)
        bittools.make_one(self, "dir_03_p", Directory)
        bittools.make_one(self, "dir_04_p", Directory)

    def recurse(self, **kwargs):
        yield from self.b3.recurse(pfx="", **kwargs)

    def dump(self, pfx=""):
        dirents = {}
        for side, dirent in self.recurse():
            e = dirents.setdefault(dirent.name.text, [dirent, ""])
            e[1] += side
        for name, i in sorted(dirents.items()):
            dirent, side = i
            if "L" in side:
                side = " "
            else:
                side = "#"
            txt = (pfx + name).ljust(64) + " " + side
            if dirent.de_nbr_n:
                txt += " [DIRECTORY,%d,1]" % dirent.de_nbr_n
            txt += " " + str(dirent)
            yield txt
            if dirent.de_nbr_n:
                dir = self.seg.directories.get(dirent.de_nbr_n)
                if dir:
                    yield from dir.dump(pfx + "┆ ")
                else:
                    yield pfx + "┆ [DIRECTORY,%d,1] not found" % dirent.de_nbr_n

class Bla3(bittools.R1kSegBase):

    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, -1), **kwargs)
        self.compact = True
        self.get_fields(
            ("b3_000_p", 32),
            ("b3_001_n", 35),
        )
        self.finish()
        self.b4 = bittools.make_one(self, "b3_000_p", Bla4)

    def recurse(self, **kwargs):
        yield from self.b4.recurse(**kwargs)
        
class Bla4(bittools.R1kSegBase):

    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, -1), **kwargs)
        self.compact = True
        self.get_fields(
            ("b4_000_p", 32),
            ("b4_001_p", 32),
        )
        self.finish()
        self.b5_1 = bittools.make_one(self, "b4_000_p", Bla5)
        self.b5_2 = bittools.make_one(self, "b4_001_p", Bla5)

    def recurse(self, pfx, **kwargs):
        if self.b5_1:
            yield from self.b5_1.recurse(pfx=pfx + "L", **kwargs)
        if self.b5_2:
            yield from self.b5_2.recurse(pfx=pfx + "R", **kwargs)
        
class Bla5(bittools.R1kSegBase):

    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, -1), **kwargs)
        self.compact = True
        self.get_fields(
            ("b5_dobj_n", 31),
        )
        self.fields[-1].fmt = "[DIRECTORY,%d,1]"
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
        self.b9 = bittools.make_one(self, "b5_005_p", Bla9)
        if self.b5_007_n == 0x280:
            bittools.make_one(self, "b5_010_n", Bla13)

    def recurse(self, **kwargs):
        if self.b9:
            yield from self.b9.recurse(**kwargs)
        
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
        self.b10 = bittools.make_one(self, "b9_000_p", DirEnt)

    def recurse(self, **kwargs):
        yield from self.b10.recurse(**kwargs)

class DirEnt(bittools.R1kSegBase):

    ''' A directory entry '''

    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, -1), **kwargs)
        self.compact = True
        self.get_fields(
            ("de_nam_p", 32),
            ("de_nbr_n", 31),
        )
        self.fields[-1].fmt = "[DIRECTORY,%d,1]"
        self.get_fields(
            ("de_l_p", 32),
            ("de_r_p", 32),
            ("de_04_n", 1),
        )
        self.finish()
        self.name = bittools.make_one(self, "de_nam_p", bittools.ArrayString)
        self.left = bittools.make_one(self, "de_l_p", DirEnt)
        self.right = bittools.make_one(self, "de_r_p", DirEnt)

    def recurse(self, pfx, **kwargs):
        yield (pfx, self)
        if self.left:
            yield from self.left.recurse(pfx, **kwargs)
        if self.right:
            yield from self.right.recurse(pfx, **kwargs)


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
        self.seg = seg
        if False:
            for i in (
                0x378f6e0,
            ):
                print(hex(i))
                for j in seg.hunt(bin(i | (1<<32))[3:]):
                    print("  ", j, hex(j[1]), hex(j[2]))

        self.hd = Head(seg, 0x80)

        # Hash-table of names
        self.namehash = bittools.PointerArray(seg, self.hd.hd_017_p, target=NameChain)

        seg.directories = {}
        bittools.BitPointerArray(seg, self.hd.hd_011_p, 0x2717, target=Directory)

        self.seg.this.add_interpretation(self, self.render)

    def render(self, fo, this):
        fo.write("<H4>Directory Tree</H4>\n")
        fo.write("<pre>\n")
        fo.write("!\n")
        for i in self.seg.directories[1].dump("┆ "):
            fo.write(i + "\n")
        fo.write("</pre>\n")
