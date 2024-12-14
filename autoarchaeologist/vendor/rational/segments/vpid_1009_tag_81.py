#!/usr/bin/env python3

'''
   Directory Segments - VPID 1009 - TAG 0x81
   =========================================

   This is the Directory Managers persistent segment.

   FE_HANDBOOK.PDf 187p

    Note: […] The D2 mapping is:

        […]
        DIRECTORY        1009
        […]

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

    def render(self):
        yield "[DIRECTORY,%d,1]" % self.dirno.val

class Vpid(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vpid_=-10,
        )

    def render(self):
        yield "Vpid %d" % self.vpid.val

class ObjId(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            objid_=-31,
        )

    def render(self):
        yield "[,%d,]" % self.objid.val

class StringPointer(bv.Pointer(cm.StringArray)):
    ''' ... '''

    def render(self):
        if not self.val:
            yield from super().render()
            return
        dst = self.dst()
        retval = list(super().render())
        yield retval[0] + "(»" + dst.txt + "«)"

class D00(bv.Struct):

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            hd_000_n_=-32,
            hd_001_n_=-32,
            hd_002_n_=-32,
            hd_003_n_=-32,
            hd_004_n_=-32,
            hd_005_n_=-32,
            hd_006_n_=-32,
            hd_007_p_=bv.Pointer(D01),
            hd_008_n_=-32,
            hd_009_p_=bv.Pointer(Bla12),
            hd_010_n_=-32,
            hd_011_p_=bv.Pointer(D04),
            hd_012_n_=-32,
            hd_013_n_=-32,
            hd_014_n_=-1,
        )


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
            b3_locked_=-3,
            b3_002_n_=32,	# too big to be snapshot
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
            rclass_=-6,
            subclass_=-10,
        )
        # See 5d3bfb73b, 00_class, 75_tag, seg_0ea8df
        x = {
            1: ("ADA", {
                    2: "WORLD",
                    3: "DIRECTORY",
                    4: "SUBSYSTEM",
                    5: "SPEC_VIEW",
                    6: "LOAD_VIEW",
                    8: "GENERIC_PROCEDURE",
                    9: "GENERIC_FUNCTION",
                    10: "GENERIC_PACKAGE",
                    12: "PACKAGE_INSTANTIATION",
                    13: "PACKAGE_SPEC",
                    16: "PROCEDURE_INSTANTIATION",
                    17: "PROCEDURE_SPEC",
                    20: "FUNCTION_INSTANTIATION",
                    21: "FUNCTION_SPEC",
                    28: "PROCEDURE_BODY",
                    29: "FUNCTION_BODY",
                    31: "TASK_BODY",
                    32: "PACKAGE_BODY",
                    33: "UNRECOGNIZABLE",
                    39: "COMPILATION_UNIT",
                    56: "MAIN_PROCEDURE_SPEC",
                    57: "MAIN_PROCEDURE_BODY",
                    59: "MAIN_FUNCTION_BODY",
                    62: "LOADED_PROCEDURE_SPEC",
                    63: "LOADED_FUNCTION_SPEC",
                    66: "COMBINED_VIEW",
                    77: "SYSTEM_SUBSYSTEM",
                }
            ),
            2: ("DDB", {}),
            3: ("FILE", {
                    0: "NIL",
                    42: "TEXT",
                    43: "BINARY",
                    47: "SWITCH",
                    46: "ACTIVITY",
                    48: "SEARCH_LIST",
                    49: "OBJECT_SET",
                    51: "POSTSCRIPT",
                    52: "SWITCH_DEFINITION",
                    61: "COMPATIBILITY_DATABASE",
                    70: "CMVC_DATABASE",
                    71: "DOCUMENT_DATABASE",
                    72: "CONFIGURATION",
                    73: "VENTURE",
                    74: "WORK_ORDER",
                    80: "CMVC_ACCESS",
                    83: "MARKUP",
                    555: "BINARY_GATEWAY",
                    597: "REMOTE_TEXT_GATEWAY",
                }
            ),
            4: ("USER", {}),
            5: ("GROUP", {}),
            6: ("SESSION", {}),
            7: ("TAPE", {}),
            8: ("TERMINAL", {}),
            9: ("DIRECTORY", {}),
            10: ("CONFIGURATION", {}),
            11: ("CODE_SEGMENT", {}),
            12: ("LINK", {}),
            13: ("NULL_DEVICE", {}),
            14: ("PIPE", {}),
            15: ("ARCHIVED_CODE", {}),
            16: ("PROGRAM_LIBRARY", {}),
            17: ("NATIVE_SEGMENT_MAP", {}),
        }.get(self.rclass.val)
        if x is None:
            self.class_name = None
            subclasses = {}
        else:
            self.class_name, subclasses = x
        if not self.class_name:
            self.class_name = "%d" % self.rclass.val
        self.subclass_name = subclasses.get(self.subclass.val)
        if not self.subclass_name and self.subclass.val == 0:
            self.subclass_name = "NIL"
        elif not self.subclass_name:
            self.subclass_name = "%d" % self.subclass.val

    def render(self):
        yield "%d.%d (%s.%s)" % (
            self.rclass.val,
            self.subclass.val,
            self.class_name,
            self.subclass_name,
        )

class Bla5(bv.Struct):

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            b5_dir_=DirNo,
            b5_name_=StringPointer,
            b5_002__=bv.Constant(32, 0),
            b5_version_tree_=bv.Pointer(VersionTree),
            b5_004__=bv.Constant(32, 0),
            b5_dir_tree_=bv.Pointer(DirTree),
            b5_objnbr_=ObjId,
            b5_var_=-9,
            b5_control_point_=-1,
            b5_world_=DirNo,
            b5_class_=ObjClass,
            b5_vpid_=Vpid,
            b5_008_=11,
            b5_009_=-1,
            b5_frozen_=-1,
            b5_controlled_=-1,
            b5_slushy_=-1,
            b5_state_=-3,
            more=True,
            vertical=True,
        )
        if self.b5_var.val == 2:
            self.add_field("b5_010_p", bv.Pointer(B55))
        else:
            self.add_field("b5_dir_ctrl_point", DirNo)
            self.add_field("b5_011_b_", bv.Constant(1,0))
        self.done()

    def visit(self, *args):
        print("        B5", self)
        if self.b5_005.val:
            self.b5_005.dst().visit(*args)

class B55(bv.Struct):

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            b55_000_n_=-10,
            b55_control_point_=DirNo,
            b55_switches_n_=DirNo,
            vertical=True,
            more=True,
        )
        if self.b55_000_n.val == 0x202:
            self.add_field("array", bv.Array(9, AclEntry))
            self.add_field("b55_11_n", -74)
            self.add_field("b55_target", -28)
            self.add_field("b55_13_n", -1)
        self.done()


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
            ve_obj_n_=ObjId,
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

class D01(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            hs_000_p_=-32,
            hs_010_p_=bv.Pointer(D02),
        )

class D02(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            hs_000_p_=-32,
            hs_010_p_=bv.Pointer(D03),
            hs_020_n_=-32,
            hs_030_n_=-32,
        )

class D03(cm.PointerArray):

    def __init__(self, bvtree, lo):
        super().__init__(bvtree, lo, cls=NameList, elide={0,})

class D04(cm.PointerArray):

    def __init__(self, bvtree, lo):
        super().__init__(bvtree, lo, cls=Directory, dimension=0x2717, elide={0,})

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

class NameList(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            zw_000_p__=bv.Constant(32, 0),
            text_=bv.Pointer(cm.StringArray),
            next_=bv.Pointer(NameList),
        )

class V1009T81(cm.Segment):

    VPID = 1009
    TAG = 0x81

    def spelunk(self):

        self.seg_heap = cm.SegHeap(self, 0).insert()
        self.d00 = D00(self, self.seg_heap.hi).insert()
        self.investigate_name_hash()

    def find_dir(self, nbr):
        print("FINDDIR", nbr)
        idx = (6302 + nbr) % 0x2717
        pdir = self.dirs[idx]
        print("PDIR", pdir)
        if pdir.val != 0:
            i = list(pdir.dst().find_dir(nbr))
            print("I", len(i), i[0])

    def investigate_name_hash(self):
        d01 = self.d00.hd_007_p.dst()
        d02 = d01.hs_010_p.dst()
        d03 = d02.hs_010_p.dst()
        fn = self.this.filename_for(suf=".namehash.txt")
        with open(fn.filename, "w") as out:
            for n, i in enumerate(d03):
                if i.val == 0:
                    continue
                d = i.dst()
                while True:
                    s = d.text.dst()
                    out.write(hex(n) + " ")
                    out.write(bytes(s.iter_glyphs()).hex())
                    out.write(" # " + s.txt + "\n")
                    if d.next.val == 0:
                        break
                    d = d.next.dst()

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
