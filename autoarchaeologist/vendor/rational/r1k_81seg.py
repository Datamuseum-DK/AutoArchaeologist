#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   R1000 '97' segments
   ===================

   Diana-trees, at least that's the current working theory.

'''

from . import r1k_bittools as bittools

class AclEntry(bittools.R1kSegField):

    def __init__(self, up, name):
        val = int(up.chunk[up.offset:up.offset+14], 2)
        super().__init__(up, up.offset, 14, name, val)
        up.offset += 14

    def render(self):
        if not self.val:
            return ""
        t = " " + self.name + " " + bin((1<<14)|self.val)[3:] + " "
        t = " "
        subj = self.val >> 4
        if subj == 0:
            subj = "PUBLIC"
        elif subj == 1:
            subj = "NETWORK_PUBLIC"
        else:
            subj = "[0x%x]" % subj
        t += subj + "=>"
        mode = self.val & 0xf
        if mode == 0x1:
            t += "R"
        elif mode == 0x3:
            t += "RW"
        elif mode == 0xf:
            t += "RCOD"
        else:
            if mode & 0x1:
                t += "R"
            if mode & 0x2:
                t += "W"
            if mode & 0x4:
                t += "C"
            if mode & 0x8:
                t += "O"
        return t

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
            ("b5_006_n", 31),
	)
        self.fields[-1].fmt = "[,%d,]"
        self.get_fields(
            ("b5_007_n", 9),
            ("b5_007a_n", 1),
            ("b5_008_n", 31),
	)
        self.fields[-1].fmt = "[DIRECTORY,%d,1]"
        self.get_fields(
            ("b5_cls_n", 6),
            ("b5_subcls_n", 10),
            ("b5_008z_n", 12),
            ("b5_retn_cnt_n", 10),
            ("b5_009_n", 6),
        )
        if self.b5_007_n == 0x2:
            self.get_fields(
                ("b5_012_p", 32),
            )
        else:
            self.get_fields(
                ("b5_013_n", 30),
                ("b5_014_n", 2),
            )
        self.finish()
        bittools.make_one(self, "b5_003_p", Bla6)
        self.b9 = bittools.make_one(self, "b5_005_p", Bla9)
        if self.b5_007_n == 0x2:
            bittools.make_one(self, "b5_012_p", Acl)

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
            ("b6_nver_n", 31),
            ("b6_003_n", 2),
            ("b6_004_p", 32),
        )
        self.finish()
        bittools.make_one(self, "b6_000_p", VerEnt)
        bittools.make_one(self, "b6_004_p", Bla11)

class VerEnt(bittools.R1kSegBase):

    ''' Version Entry '''

    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, -1), **kwargs)
        self.compact = True
        self.get_fields(
            ("ve_ver_n", 31),
            ("ve_obj_n", 31),
            ("ve_left_p", 32),
            ("ve_right_p", 32),
            ("ve_004_n", 1),
        )
        self.fields[0].fmt = "%d"
        self.fields[1].fmt = "[?,%d,?]"
        self.finish()
        bittools.make_one(self, "ve_left_p", VerEnt)
        bittools.make_one(self, "ve_right_p", VerEnt)

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


class Acl(bittools.R1kSegBase):

    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, -1), **kwargs)
        self.compact = True
        self.get_fields(
            ("bd_000_n", 10),
            ("bd_001_n", 31),
            ("bd_switches_n", 31),
        )
        self.fields[1].fmt = "[DIRECTORY,%d,1]"
        self.fields[2].fmt = "[DIRECTORY,%d,1]"
        if int(self.chunk[:8], 2) == 0x80:
            for i in range(9):
                self.fields.append(AclEntry(self, "acl%d" % i))
            self.get_fields(
                ("bd_012_n", 5),
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
