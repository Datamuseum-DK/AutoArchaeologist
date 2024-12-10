#!/usr/bin/env python3

'''
   Directory Segments - VPID 1009 - TAG 0x81
   =========================================

   This is the Directory Managers persistent segment.

'''

from ....base import bitview as bv
from . import common as cm

class DirNo(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            dirno_=-31,
        )

class StringPointer(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            ptr_=-32,
        )
        bvtree.points_to(self.ptr.val, cm.StringArray)

    def render(self):
        if self.ptr.val == 0:
            retval = "∅"
        else:
            i = list(self.tree.find(self.ptr.val, self.ptr.val+1))
            retval = "→»" + i[0].txt + '«'
        yield retval.ljust(50)

class Bla12(bv.Struct):

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            bc_000_n_=-13,
            bc_050_n_=-32,
            bc_051_n_=-32,
            bc_052_n_=-32,
            bc_053_n_=-32,
            bc_054_n_=-32,
            bc_055_n_=-32,
            bc_100_=bv.Pointer(Bla12),
            bc_101_=bv.Pointer(Bla12),
            bc_102_=bv.Pointer(Bla12),
            bc_103_=bv.Pointer(Bla12),
        )

class NameChain(bv.Struct):

    ''' Chains of names from the same hash-bucket '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            nc_00__=bv.Constant(32, 0),
            #nc_01_=StringPointer,
            nc_01_=bv.Pointer(cm.StringArray),
            nc_02_=bv.Pointer(NameChain),
        )

    def __iter__(self):
        yield self.nc_01.dst().txt
        if self.nc_02.val:
            yield from self.nc_02.dst()

class Directory(bv.Struct):

    ''' Directory node '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            dir_00__=bv.Constant(width=33, value=18),
            dir_nbr_=DirNo,
            dir_02_=bv.Pointer(Bla3),
            dir_03_=bv.Pointer(Directory),
            dir_04_=bv.Pointer(Directory),
            dir_05_n_=-1,
        )

    def visit(self, *args):
        print("  DIR", self)
        if self.dir_02.val:
            self.dir_02.dst().visit(*args)

    def find_dir(self, nbr):
        mydir = self.dir_nbr.dirno.val
        print("FD", nbr, mydir)
        if nbr < mydir and self.dir_03.val:
            yield from self.dir_03.dst().find_dir(nbr)
        elif mydir == nbr:
            yield self
        elif nbr > mydir and  self.dir_04.val:
            yield from self.dir_04.dst().find_dir(nbr)

class Bla3(bv.Struct):

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            b3_000_=bv.Pointer(Bla4),
            b3_001_n_=-35,
        )

    def visit(self, *args):
        print("    B3", self)
        if self.b3_000.val:
            self.b3_000.dst().visit(*args)

class Bla4(bv.Struct):

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            b4_000_=bv.Pointer(Bla5),
            b4_001_=bv.Pointer(Bla5),
        )

    def visit(self, *args):
        print("      B4", self)
        if self.b4_000.val:
            self.b4_000.dst().visit(*args)
        #if self.b4_001.val:
        #    self.b4_001.dst().visit(*args)

class ObjClass(bv.Struct):
    
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            cls_=-6,
        )
        # See 5d3bfb73b, 00_class, 75_tag, seg_0ea8df
        self.class_name = {
            1: "ADA",
            2: "DDB",
            3: "FILE",
            4: "USER",
            5: "GROUP",
            6: "SESSION",
            7: "TAPE",
            8: "TERMINAL",
            9: "DIRECTORY",
            10: "CONFIGURATION",
            11: "CODE_SEGMENT",
            12: "LINK",
            13: "NULL_DEVICE",
            14: "PIPE",
            15: "ARCHIVED_CODE",
            16: "PROGRAM_LIBRARY",
            17: "NATIVE_SEGMENT_MAP",
        }.get(self.cls.val)
        if not self.class_name:
            self.class_name = "CLASS(0x%x)" % self.cls.val

    def render(self):
        yield self.class_name

class Bla5(bv.Struct):

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            b5_dir_=DirNo,
            b5_001_=StringPointer,
            b5_002__=bv.Constant(32, 0),
            b5_003_=bv.Pointer(VersionTree),
            b5_004__=bv.Constant(32, 0),
            b5_005_=bv.Pointer(DirTree),
            b5_objnbr_=-31,
            b5_007_n_=-9,
            b5_007a_n_=-1,
            b5_world_=DirNo,
            b5_008z_n_=44,
            more=True,
        )
        if self.b5_007_n.val == 2:
            self.add_field("b5_010_p", bv.Pointer(Acl))
        else:
            self.add_field("b5_010_p", DirNo)
            self.add_field("b5_011_b", -1)
            b5_010_p_=-32,
        self.done()

    def visit(self, *args):
        print("        B5", self)
        if self.b5_005.val:
            self.b5_005.dst().visit(*args)

class DirTree(bv.Struct):

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            b9_root_=bv.Pointer(DirBranch),
            b9_001__=bv.Constant(31, 0),
            b9_leaves_=-32,
            b9_003__=bv.Constant(34, 0),
        )

    def visit(self, *args):
        print("            B9", self)
        if self.b9_000.val:
            self.b9_000.dst().visit(*args)

class VersionTree(bv.Struct):

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            b6_000_=bv.Pointer(VersionLeaf),
            b6_001__=bv.Constant(32, 0),
            b6_nver_n_=-33,
            b6_003_=bv.Pointer(VersionLeaf),
        )

class Foo99(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            f99_000_=-94,
            f99_098_=bv.Pointer(),
            f99_099_=-1,
        )

class VersionLeaf(bv.Struct):

    ''' Version Entry '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            ve_ver_n_=-31,
            ve_obj_n_=-31,
            ve_left_=bv.Pointer(VersionLeaf),
            ve_right_=bv.Pointer(VersionLeaf),
            ve_004_n_=-1,
        )

class Bla11(bv.Struct):

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            b11_000_b_=127,
        )

class DirBranch(bv.Struct):

    ''' A directory entry '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            de_nam_=StringPointer,
            de_nbr_=DirNo,
            de_l_=bv.Pointer(DirBranch),
            de_r_=bv.Pointer(DirBranch),
            de_04_n_=-1,
        )

    def visit(self, *args):
        if self.de_l.val:
            self.de_l.dst().visit(*args)
        print("              DE", self)
        if self.de_r.val:
            self.de_r.dst().visit(*args)

class Acl(bv.Struct):

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            acl_000_n_=-10,
            acl_001_n_=-31,
            acl_switches_n_=-31,
            more=True,
        )
        if self.acl_000_n.val == 0x202:
            self.add_field("array", bv.Array(9, AclEntry))
            self.add_field("acl_12_n", -103)
        self.done()

class AclEntry(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            subj_=-10,
            mode_=-4,
        )

    def xrender(self):
        subj = "[GROUP=%d]" % self.subj.val
        if self.subj.val == 0:
            subj = "PUBLIC"
        elif self.subj.val == 1:
            subj = "NETWORK_PUBLIC"
        mode = []
        if self.mode.val & 0x1:
            mode.append("R")
        if self.mode.val & 0x2:
            mode.append("W")
        if self.mode.val & 0x4:
            mode.append("C")
        if self.mode.val & 0x8:
            mode.append("O")
        mode = "".join(mode)
        if self.mode.val == 0xf:
            mode = "RCOD"
        if self.mode.val:
            yield subj + "=>" + mode

class HeadSomething(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            hs_000_p_=-32,
            hs_010_p_=bv.Pointer(),
        )

class HeadSomething2(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            hs_000_p_=-32,
            hs_010_p_=bv.Pointer(),
            hs_020_n_=-32,
            hs_030_n_=-32,
        )

class Etwas(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            ew_000_p_=bv.Pointer(),
            ew_001_p_=-32,
            ew_002_p_=-32,
            ew_003_p_=-32,
        )


class V1009T81(cm.Segment):

    VPID = 1009
    TAG = 0x81

    def spelunk(self):

        self.seg_heap = cm.SegHeap(self, 0).insert()
        self.std_head = cm.StdHead(self, self.seg_heap.hi).insert()

        self.b12_head = Bla12(self, self.std_head.hd_009_p.val).insert()

        self.hs1 = HeadSomething(self,  self.std_head.hd_007_p.val).insert()
        self.hs2 = HeadSomething2(self,  self.hs1.hs_010_p.val).insert()

        self.b18 = cm.PointerArray(
            self,
            self.hs2.hs_010_p.val,
            bv.Pointer(NameChain, elide={0,}),
        ).insert()

        cls = bv.Array(0x2717, bv.Pointer(Directory), vertical=True)
        self.dirs = cls(self, self.std_head.hd_011_p.val).insert()

	# Maybe DirBranch from a GC ?
        # bv.Array(2062, Etwas)(self, 0x5a680b9, vertical=True).insert()

    def find_dir(self, nbr):
        print("FINDDIR", nbr)
        idx = (6302 + nbr) % 0x2717
        pdir = self.dirs[idx]
        print("PDIR", pdir)
        if pdir.val != 0:
            i = list(pdir.dst().find_dir(nbr))
            print("I", len(i), i[0])

    def wander(self):
        self.find_dir(1)
        self.find_dir(0x0000265c)
        for dirptr in self.dirs:
            if dirptr.val == 0:
                continue
            dir = dirptr.dst()
            print('-' * 40)
            print(dir.__class__.__name__, dir)
            dir.visit()
