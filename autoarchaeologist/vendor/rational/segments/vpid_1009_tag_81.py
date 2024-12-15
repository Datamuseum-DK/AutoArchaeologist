#!/usr/bin/env python3

# NB: This docstring is also used as interpretation

'''
   Directory Segments - VPID 1009 - TAG 0x81
   =========================================

   This is the Directory Manager's persistent segment.

   The Directory Manager is responsible for:

	* hierachical naming
	* versioning
	* access control lists.

   The objects managed by the DM are the nodes in a DAG rooted by
   DM object number one (aka: [DIRECTORY,1,1], aka "!") 

   DM objects reference managed objects such as [TERMINAL,2,1] or
   [ADA,15481,1], and DM additionally has a field for "subclass"

   Note that "World" and "Directory" are of class ADA.WORLD and
   ADA.DIRECTORY.

   The component name strings are stored uniquely, hashed through the
   ``D03`` array, each bucket being a singly-linked list of ``NameList``.
   XXX: hash-algo has not been figured out yet.

   The managed objects are hashed through DM04 and each bucket roots
   a binary ``DMTree``.  The hash is (DM object number + 6302 mod 0x2717)
   where 0x2717 seems to be a compile time constant.

   All DM objects can have children, and many do, for instance a
   (ADA.MAIN_PROCEDURE_BODY) object often have two children named
   "*ATTR_1156" and "*ATTR_1157" of class CODE_SEGMENT.

   The children are recorded in a binary ``ChildTree`` hung of the DM object,
   where the leaves contain DM object numbers (rather than direct pointers).

   The actual DM object is represented by the following tree:

       DM3 -----> DM4 --+--> DM5 --+--> (VersionTree)
                        |          |
                        |          +--> (ChildTree)
                        |          |
                        +--> DM5   +--> (DM6)

   DM3 seems to be the 'stable' object and it only contains the DM4 pointer
   and some fields which correspond to ``show_directory_information()`` complaining
   about locking.

   DM4 only contains pointers to two DM5, where the second one in many cases
   is clearly unused.  (Used for update-protocol/snapshots/recovery ?)

   DM5 comes in two variants, one that has a DM6 pointer and one which
   instead holds the "Directory Control Point", (aka: "nearest world"?)

   DM6 looks like "Ok, we need more space for this one" and it comes in two
   variants, one with and one without ACLs.

   Finally there is complex non-directed graph of DM12 nodes which is at present
   not understood at all.  Some kind of world-interdependency graph maybe ?
   

   Footnotes & References
   ----------------------
   According to FE_HANDBOOK pdf page 209, the "[manager,number,1]"
   format is called "internal names", and can be used as filenames
   when enclosed in <…>.

   FE_HANDBOOK.PDF 187p:

        Note: […] The D2 mapping is:
            […]
            DIRECTORY        1009
            […]


'''

from ....base import bitview as bv
from . import common as cm

DM04_OFFSET = 6302
DM04_SIZE = 10007

class DirNo(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            dirno_=-31,
        )
        self.val = self.dirno.val

    def render(self):
        yield "[DIRECTORY,%d,1]" % self.val

class Vpid(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vpid_=-10,
        )
        self.val = self.vpid.val

    def render(self):
        yield "Vpid %d" % self.val

class ObjId(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            objid_=-31,
        )
        self.val = self.objid.val

    def render(self):
        yield "[,%d,]" % self.objid.val

class StringPointer(bv.Pointer(cm.StringArray)):
    ''' ... '''

    def text(self):
        if self.val:
             dst = self.dst()
             return '»' + dst.txt + '«'
        else:
             return ""

    def dot_node(self, dot):
        return "→ %s" % self.text(), ["shape=plaintext"]

    def render(self):
        if not self.val:
            yield from super().render()
            return
        dst = self.dst()
        retval = list(super().render())
        yield retval[0] + "(»" + dst.txt + "«)"

class DM00(bv.Struct):

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
            d01_=bv.Pointer(D01),
            hd_008_n_=-32,
            dm12_=bv.Pointer(DM12),
            hd_010_n_=-32,
            dm04_=bv.Pointer(DM04),
            hd_012_n_=-32,
            hd_013_n_=-32,
            hd_014_n_=-1,
        )


class DM12(bv.Struct):

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
            bc_100_=bv.Pointer(DM12),
            bc_101_=bv.Pointer(DM12),
            bc_102_=bv.Pointer(DM12),
            bc_103_=bv.Pointer(DM12),
        )

class DMTree(bv.Struct):

    ''' DirTree node '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            dir_00__=bv.Constant(width=33, value=18),
            dir_nbr_=DirNo,
            dir_02_=bv.Pointer(DM3),
            dir_03_=bv.Pointer(DMTree),
            dir_04_=bv.Pointer(DMTree),
            dir_05_n_=-1,
        )

    def dot_node(self, dot):
        return "0x%x\\n?0x%x" % (self.dir_nbr.val, self.dir_05_n.val), ["shape=triangle"]

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

class DM3(bv.Struct):

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            b3_000_=bv.Pointer(DM4),
            b3_locked_=-3,
            b3_002_n_=-32,	# too big to be snapshot
        )

    def visit(self, *args):
        print("    B3", self)
        if self.b3_000.val:
            self.b3_000.dst().visit(*args)

class DM4(bv.Struct):

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            b4_000_=bv.Pointer(DM5),
            b4_001_=bv.Pointer(DM5),
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

class DM5(bv.Struct):

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            b5_dir_=DirNo,
            b5_name_=StringPointer,
            b5_002__=bv.Constant(32, 0),
            b5_version_tree_=bv.Pointer(VersionTree),
            b5_004__=bv.Constant(32, 0),
            b5_child_tree_=bv.Pointer(ChildTree),
            b5_objnbr_=ObjId,
            b5_var_=-9,
            b5_control_point_=-1,
            b5_world_=DirNo,
            b5_class_=ObjClass,
            b5_vpid_=Vpid,
            b5_ctrl_point_is_dir_=-1,
            b5_008_=8,
            b5_retention_count_=-3,
            b5_frozen_=-1,
            b5_controlled_=-1,
            b5_slushy_=-1,
            b5_state_=-3,
            more=True,
            vertical=True,
        )
        if self.b5_var.val == 2:
            self.add_field("b5_010_p", bv.Pointer(DM6))
        else:
            self.add_field("b5_dir_ctrl_point", DirNo)
            self.add_field("b5_011_b_", bv.Constant(1,0))
        self.done()

    def dot_node(self, dot):
        return "[,%d,]\\n%s" % (self.b5_dir.val, self.b5_name.text()), []

    def visit(self, *args):
        print("        B5", self)
        if self.b5_005.val:
            self.b5_005.dst().visit(*args)


class DM6(bv.Struct):

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
            self.add_field("acls", ACLs)
            self.add_field("b55_11_n", -46)
            self.add_field("b55_target", -28)
            self.add_field("b55_13_n", -1)
        self.done()


class ChildTree(bv.Struct):

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            b9_root_=bv.Pointer(ChildBranch),
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

class ChildBranch(bv.Struct):

    ''' A directory entry '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            de_nam_=StringPointer,
            de_nbr_=DirNo,
            de_l_=bv.Pointer(ChildBranch),
            de_r_=bv.Pointer(ChildBranch),
            de_04_n_=-1,
        )

    def dot_node(self, dot):
        return "0x%x\\n%s" % (self.de_nbr.val, self.de_nam.text()), ["shape=triangle"]

    def visit(self, *args):
        if self.de_l.val:
            self.de_l.dst().visit(*args)
        print("              DE", self)
        if self.de_r.val:
            self.de_r.dst().visit(*args)

class ACLs(bv.Struct):

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            default_=bv.Array(7, AclEntry, vertical=True),
            library_=bv.Array(4, AclEntry, vertical=True),
            vertical=True,
        )

    def show_directory_information(self):
        l = [x.show_directory_information() for x in self.default]
        while l and l[-1] is None:
            l.pop(-1) 
        yield "Access  : Default: " + ",".join(l)

        l = [x.show_directory_information() for x in self.library]
        while l and l[-1] is None:
            l.pop(-1) 
        yield "          Library: " + ",".join(l)

        if False:
            for i in self.render():
                yield '||' + i

class AclEntry(bv.Struct):

    subjs = {
        0: "PUBLIC",
        1: "NETWORK_PUBLIC",
        5: "SPOOLER",
        6: "SYSTEM",
        18: "OPERATOR",
    }
    modes = {
        0x1: "R",
        0x3: "RW",
        0x5: "RC",
        0xd: "RCO",
        0xf: "RCOD",
    }

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            subj_=-10,
            mode_=-4,
        )

    def show_directory_information(self):
        if not self.mode.val:
            return None
        subj = self.subjs.get(self.subj.val, "%d" % self.subj.val)
        mode = self.modes.get(self.mode.val, "0x%x" % self.mode.val)
        return subj + "=>" + mode

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

class DM04(cm.PointerArray):

    def __init__(self, bvtree, lo):
        super().__init__(bvtree, lo, cls=DMTree, dimension=DM04_SIZE, elide={0,})

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
            text_=StringPointer,
            next_=bv.Pointer(NameList),
        )

class V1009T81(cm.Segment):

    VPID = 1009
    TAG = 0x81

    def spelunk(self):

        with self.this.add_utf8_interpretation("What we understand") as file:
             file.write(__doc__)

        self.seg_heap = cm.SegHeap(self, 0).insert()
        self.d00 = DM00(self, self.seg_heap.hi).insert()

        self.dm04 = self.d00.dm04.dst()

        self.build_show_dir_info()

    def find_dir(self, nbr):
        print("FINDDIR", nbr)
        hash = (DM04_OFFSET + nbr) % DM04_SIZE
        dmt = self.dm04[hash].dst()
        print("DMT", hex(dmt.lo), dmt)
        while dmt.dir_nbr.val != nbr:
            print("??", nbr, dmt)
            if nbr < dmt.dir_nbr.val:
                dmt = dmt.dir_03.dst()
            else:
                dmt = dmt.dir_04.dst()
            print("  dmt", hex(dmt.lo), dmt)
        return dmt.dir_02.dst()

    def recurse_childtree(self, out, chbr, prefix):
        assert isinstance(chbr, ChildBranch)
        print("CHBR", hex(chbr.lo), chbr)
        if chbr.de_l.val:
            self.recurse_childtree(out, chbr.de_l.dst(), prefix)
        self.show_dir_info(out, chbr.de_nbr.val, prefix)
        if chbr.de_r.val:
            self.recurse_childtree(out, chbr.de_r.dst(), prefix)

    def recurse_version_tree(self, vbr):
        print("VBR", type(vbr))
        print("  vbr", hex(vbr.lo))
        assert isinstance(vbr, VersionLeaf)
        if vbr.ve_left.val:
             yield from self.recurse_version_tree(vbr.ve_left.dst())
        yield (vbr.ve_ver_n.val, vbr.ve_obj_n.val)
        if vbr.ve_right.val:
             yield from self.recurse_version_tree(vbr.ve_right.dst())

    def show_dir_info(self, out, dmno, prefix):
        dm03 = self.find_dir(dmno)
        print("DM03", hex(dm03.lo), dm03)
        dm04 = dm03.b3_000.dst()
        print("DM04", hex(dm04.lo), dm04)
        dm05 = dm04.b4_000.dst()
        print("DM05", hex(dm05.lo), dm05)
        assert dm05.b5_dir.val == dmno
        name = dm05.b5_name.dst().txt

        if dm05.b5_var.val == 2:
            dm06 = dm05.b5_010_p.dst()
        else:
            dm06 = None
        
        #out.write(prefix + "((0x%x))\n" % dm05.lo)
        out.write(prefix +
            '[DIRECTORY,%d,1] Information:\n' % dmno
        )
        out.write(prefix +
            'Name    : [DIRECTORY,%d,1] (%s in [DIRECTORY,%d,1])\n' %
                (dmno, name, dm05.b5_world.val)
        )
        if dm05.b5_ctrl_point_is_dir.val:
            cp = "DIRECTORY_CONTROL_POINT"
        else:
            cp = "LIBRARY_CONTROL_POINT"
        if dm05.b5_var.val == 1:
            out.write(prefix +
                'Library : %s [DIRECTORY,%d,1] on Vpid %d\n' %
                    (cp, dm05.b5_dir_ctrl_point.val, dm05.b5_vpid.val)
            )
        elif dm05.b5_var.val == 2:
            out.write(prefix +
                'Library : %s [DIRECTORY,%d,1] on Vpid %d\n' %
                    (cp, dm06.b55_control_point.val, dm05.b5_vpid.val)
            )

        out.write(prefix + 'Class   : %d (%s)' %
            (dm05.b5_class.rclass.val, dm05.b5_class.class_name)
        )
        out.write('; Subclass: %d (%s)' %
            (dm05.b5_class.subclass.val, dm05.b5_class.subclass_name)
        )
        out.write('; State: %d (%s)' %
            (dm05.b5_state.val, [
                    "0",
                    "Archived",
                    "Source",
                    "Installed",
                    "Coded",
                    "5",
                    "6",
                    "N/A"
                ][dm05.b5_state.val])
        )
        if dm05.b5_frozen.val:
            out.write('; Frozen')
        if dm05.b5_control_point.val:
            out.write('; Control_Point')
        if dm05.b5_controlled.val:
            out.write('; Controlled')
        if dm05.b5_slushy.val:
            out.write('; Slushy')

        out.write('\n')

        if dm05.b5_var.val == 2:
            out.write(prefix + 'Switches: [DIRECTORY,%d,1]\n' % dm06.b55_switches_n.val)


        if dm05.b5_var.val == 2 and dm06.b55_000_n.val == 0x202:

            if True:
                for ln in dm06.acls.show_directory_information():
                    out.write(prefix + ln + '\n')

            # NB: no prefix is bug in show_directory_information()
            out.write('Target  : ' + {
                    0x111111: "111111 = R1000",
                }.get(dm06.b55_target.val, "<<Unknown>>")
            )
            out.write('\n')

        if dm05.b5_version_tree.val:
            versions = list(self.recurse_version_tree(dm05.b5_version_tree.dst().b6_000.dst()))
            out.write(prefix + 'Versions: %d' % len(versions))
            out.write('; Retention Count: %d' % dm05.b5_retention_count.val)
            out.write('; Default: [%s,%d,1]' % (dm05.b5_class.class_name, versions[-1][1]))
            out.write('\n')
            for ver, objno in versions:
                out.write(prefix + '  Version %d: [' % ver)
                out.write(dm05.b5_class.class_name + ",%d,1]" % objno)
                out.write('  ( %d in [DIRECTORY,%d,1])' % (ver, dmno))
                out.write('\n')

        if dm05.b5_child_tree.val:
            out.write(prefix + "Children:\n")
            chtr = dm05.b5_child_tree.dst()
            self.recurse_childtree(out, chtr.b9_root.dst(), prefix + "  ")
        else:
            out.write(prefix + "No children.\n")
        out.write('\n')

    def build_show_dir_info(self):
        fn = self.this.filename_for(suf=".show_dir_info.txt")
        with open(fn.filename, "w") as out:
            self.show_dir_info(out, 1, "")

    def investigate_name_hash(self):
        ''' out of date '''
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
