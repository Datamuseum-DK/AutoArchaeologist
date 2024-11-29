#!/usr/bin/env python3

'''
   Directory Segments - VPID 1009 - TAG 0x81
   =========================================
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
            yield "∅"
            return
        i = list(self.tree.find(self.ptr.val, self.ptr.val+1))
        yield "→»" + i[0].txt + '«'

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
            nc_01_=StringPointer,
            nc_02_=bv.Pointer(NameChain),
        )

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

class Bla3(bv.Struct):

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            b3_000_=bv.Pointer(Bla4),
            b3_001_n_=-35,
        )

class Bla4(bv.Struct):

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            b4_000_=bv.Pointer(Bla5),
            b4_001_=bv.Pointer(Bla5),
        )

class ObjClass(bv.Struct):
    
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            cls_=-6,
        )

    def render(self):
        # See 5d3bfb73b, 00_class, 75_tag, seg_0ea8df
        retval = {
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
        if not retval:
            retval = "CLASS(0x%x)" % self.cls.val
        yield retval

class Bla5(bv.Struct):

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            b5_dir_=DirNo,
            b5_001_=StringPointer,
            b5_002__=bv.Constant(32, 0),
            b5_003_=bv.Pointer(Bla6),
            b5_004__=bv.Constant(32, 0),
            b5_005_=bv.Pointer(Bla9),
            b5_objnbr_=-31,
            b5_007_n_=-9,
            b5_007a_n_=-1,
            b5_world_=DirNo,
            b5_cls_=ObjClass,
            b5_subcls_=-10,
            b5_008z_n_=-12,
            b5_retn_cnt_n_=-10,
            b5_009_n_=-6,
            b5_010_p_=-32,
        )
        if self.b5_007_n.val == 2:
            bvtree.points_to(self.b5_010_p.val, Acl)

class Bla9(bv.Struct):

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            b9_000_=bv.Pointer(DirEnt),
            b9_001__=bv.Constant(31, 0),
            b9_002_n_=-32,
            b9_003__=bv.Constant(34, 0),
        )

class Bla6(bv.Struct):

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            b6_000_=bv.Pointer(VersionLeaf),
            b6_001__=bv.Constant(32, 0),
            b6_nver_n_=-31,
            b6_003_n_=-2,
            b6_004_=bv.Pointer(Bla11),
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

class DirEnt(bv.Struct):

    ''' A directory entry '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            de_nam_=StringPointer,
            de_nbr_=DirNo,
            de_l_=bv.Pointer(DirEnt),
            de_r_=bv.Pointer(DirEnt),
            de_04_n_=-1,
        )

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

class V1009T81(cm.Segment):

    VPID = 1009
    TAG = 0x81

    def spelunk(self):

        self.seg_heap = cm.SegHeap(self, 0).insert()
        self.std_head = cm.StdHead(self, self.seg_heap.hi).insert()

        self.b12_head = Bla12(self, self.std_head.hd_009_p.val).insert()

        self.b18 = cm.PointerArray(
            self,
            self.std_head.hd_018_p.val,
            bv.Pointer(NameChain),
        ).insert()

        cls = bv.Array(0x2717, bv.Pointer(Directory), vertical=True)
        self.dirs = cls(self, self.std_head.hd_011_p.val).insert()

        if False:
            DirEnt(self, 0x72ee9e).insert()
