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

   The component name strings are stored uniquely, hashed through
   the ``D03`` array, each bucket being a singly-linked list of
   ``NameList``.
   XXX: hash-algo has not been figured out yet.

   The managed objects are hashed through DM04 and each bucket roots
   a binary ``DMTree``.  The hash is (DM object number + 6302 mod
   0x2717) where 0x2717 seems to be a compile time constant.

   All DM objects can have children, and many do, for instance a
   (ADA.MAIN_PROCEDURE_BODY) object often have two children named
   "*ATTR_1156" and "*ATTR_1157" of class CODE_SEGMENT.

   The children are recorded in a binary ``ChildTree`` hung of the
   DM object, where the leaves contain DM object numbers (rather
   than direct pointers).

   The actual DM object is represented by the following tree:

       DM07 -----> DM08 --+--> DM05 --+--> (VersionTree)
                          |           |
                          |           +--> (ChildTree)
                          |           |
                          +--> DM05   +--> (DM06)

   DM07 seems to be the 'stable' object and it only contains the
   DM08 pointer and a ``locking`` field which correlates with the
   R1000 ``show_directory_information()`` complaining about locking.

   DM08 only contains pointers to two DM05, where the second one
   in many cases is clearly unused.  (Used for
   update-protocol/snapshots/recovery ?)

   DM05 comes in two variants, one that has a DM06 pointer and one
   which instead holds the "Directory Control Point", (aka: "nearest
   world"?)

   DM06 looks like "Ok, we need more space for this one" and it
   comes in two variants, one with and one without ``AclSet`` and
   Target information.

   Open ends
   ---------

   There is complex non-directed graph of DM12 nodes, some kind of
   world-interdependency graph maybe ?


   Some of the Acls on our disk image contains group numbers which
   do not have [GROUP,,] entries, yet on the R1000 
   show_directory_information() reports their name.

   For instance 18=OPERATOR.

   Which btw, aligns with the messy situation described on pdf page
   365 of the FE_HANDBOOK.


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
from ....base import namespace
from . import common as cm

DM04_OFFSET = 6302
DM04_SIZE = 10007


class NameSpace(namespace.NameSpace):
    ''' ... '''

    KIND = "Environment filesystem"

    TABLE = (
        ("r", "dir_nbr"),
        ("l", "class"),
        ("l", "subclass"),
        ("r", "obj_nbr"),
        ("r", "version"),
        ("l", "name"),
        ("l", "artifact"),
    )

    def ns_render(self):
        meta = self.ns_priv
        return meta + super().ns_render()
            

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
        return ""

    def dot_node(self, dot):
        return "→ %s" % self.text(), ["shape=plaintext"]

    def render(self):
        dst = self.dst()
        if not hasattr(dst, "txt"):
            yield from super().render()
        else:
            retval = list(super().render())
            yield retval[0] + "(»" + dst.txt + "«)"

class DM00(bv.Struct):

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            #hd_000_n_=-32,
            hd_001_n_=-31,
            hd_002_n_=-32,
            hd_003_n_=-32,
            hd_004_n_=-32,
            hd_005_n_=-32,
            hd_006_n_=-32,
            d01_=bv.Pointer(DM01),
            hd_008_n_=-32,
            dm12_=bv.Pointer(DM12),
            hd_010_n_=-32,
            dm04_=bv.Pointer(DM04),
            hd_012_n_=-32,
            hd_013_n_=-32,
            hd_014_n_=-1,
        )

class DM01(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            hs_000_p_=-32,
            hs_010_p_=bv.Pointer(DM02),
        )

class DM02(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            hs_000_p_=-32,
            hs_010_p_=bv.Pointer(DM03),
            hs_020_n_=-32,
            hs_030_n_=-32,
        )

class DM03(cm.PointerArray):

    def __init__(self, bvtree, lo):
        super().__init__(bvtree, lo, cls=NameList, elide={0,})

class DM04(cm.PointerArray):

    def __init__(self, bvtree, lo):
        super().__init__(bvtree, lo, cls=DMTree, dimension=DM04_SIZE, elide={0,})

class DM07(bv.Struct):

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            b3_000_=bv.Pointer(DM08),
            b3_locked_=-3,
            b3_002_n_=-32,	# too big to be snapshot
        )

    def show_directory_information(self, out, prefix, path):
        ''' Just passing through '''
        dm04 = self.b3_000.dst()
        dm04.show_directory_information(out, prefix, path)

class DM08(bv.Struct):

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            b4_000_=bv.Pointer(DM05),
            b4_001_=bv.Pointer(DM05),
        )

    def show_directory_information(self, out, prefix, path):
        ''' Just passing through '''
        dm05 = self.b4_000.dst()
        dm05.show_directory_information(out, prefix, path)

class DM05(bv.Struct):

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
            self.add_field("b5_010_p", bv.Pointer(DM06))
        else:
            self.add_field("b5_dir_ctrl_point", DirNo)
            self.add_field("b5_011_b_", bv.Constant(1,0))
        self.done()

    def collect_users_and_groups(self):
        cname = self.b5_class.class_name
        if cname in ("USER", "GROUP"):
            if self.b5_version_tree.val == 0:
                return
            ver, nbr = self.b5_version_tree.dst().current_version()
            if cname == "USER":
                self.tree.users[nbr] = self.b5_name.text()
            elif cname == "GROUP":
                self.tree.groups[nbr] = self.b5_name.text()

    def dot_node(self, dot):
        return "[,%d,]\\n%s" % (self.b5_dir.val, self.b5_name.text()), []

    def show_directory_information(self, out, prefix, path):
        #out.write(prefix + "((0x%x))\n" % dm05.lo)
        out.write(prefix +
            '[DIRECTORY,%d,1] Information:\n' % self.b5_dir.val
        )
        name = self.b5_name.dst().txt
        path = path + [ name ]
        out.write(prefix +
            'Path    : ' + '/'.join(path) + '\n'
        )
        if self.b5_var.val == 2:
            dm06 = self.b5_010_p.dst()
        else:
            dm06 = None

        out.write(prefix +
            'Name    : [DIRECTORY,%d,1] (%s in [DIRECTORY,%d,1])\n' %
                (self.b5_dir.val, name, self.b5_world.val)
        )
        if self.b5_ctrl_point_is_dir.val:
            cp = "DIRECTORY_CONTROL_POINT"
        else:
            cp = "LIBRARY_CONTROL_POINT"
        if self.b5_var.val == 1:
            out.write(prefix +
                'Library : %s [DIRECTORY,%d,1] on Vpid %d\n' %
                    (cp, self.b5_dir_ctrl_point.val, self.b5_vpid.val)
            )
        elif self.b5_var.val == 2:
            out.write(prefix +
                'Library : %s [DIRECTORY,%d,1] on Vpid %d\n' %
                    (cp, dm06.b55_control_point.val, self.b5_vpid.val)
            )

        out.write(prefix + 'Class   : %d (%s)' %
            (self.b5_class.rclass.val, self.b5_class.class_name)
        )
        out.write('; Subclass: %d (%s)' %
            (self.b5_class.subclass.val, self.b5_class.subclass_name)
        )
        out.write('; State: %d (%s)' %
            (self.b5_state.val, [
                    "0",
                    "Archived",
                    "Source",
                    "Installed",
                    "Coded",
                    "5",
                    "6",
                    "N/A"
                ][self.b5_state.val])
        )
        if self.b5_frozen.val:
            out.write('; Frozen')
        if self.b5_control_point.val:
            out.write('; Control_Point')
        if self.b5_controlled.val:
            out.write('; Controlled')
        if self.b5_slushy.val:
            out.write('; Slushy')

        out.write('\n')

        if self.b5_var.val == 2:
            dm06.show_directory_information(out, prefix)

        if self.b5_version_tree.val:
            self.b5_version_tree.dst().show_directory_information(out, self, prefix)

        if self.b5_child_tree.val:
            out.write(prefix + "Children:\n")
            for child in self.b5_child_tree.dst().recurse_childtree():
                self.tree.find_dir(child.de_nbr.val).show_directory_information(
                    out,
                    prefix + "  ",
                    path,
                )
        else:
            out.write(prefix + "No children.\n")
        out.write('\n')

        # We cannot pass self as priv, it prevents releasing memory

        if self.b5_version_tree.val:
            for ver, nbr in self.b5_version_tree.dst().recurse_version_tree():
                NameSpace(
                    name = '/'.join(path),
                    parent = self.tree.namespace,
                    priv = [
                         str(self.b5_dir.val),
                         self.b5_class.class_name,
                         self.b5_class.subclass_name,
                         nbr,
                         ver,
                    ],
                )
        else:
            ver, nbr = ("", "")
            NameSpace(
                name = '/'.join(path),
                parent = self.tree.namespace,
                priv = [
                     str(self.b5_dir.val),
                     self.b5_class.class_name,
                     self.b5_class.subclass_name,
                     nbr,
                     ver,
                ],
            )

class DM06(bv.Struct):

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
            self.add_field("acls", AclSet)
            self.add_field("b55_11_n", -46)
            self.add_field("b55_target", -28)
            self.add_field("b55_13_n", -1)
        self.done()

    def show_directory_information(self, out, prefix):
        out.write(prefix + 'Switches: [DIRECTORY,%d,1]\n' % self.b55_switches_n.val)

        if self.b55_000_n.val == 0x202:

            for ln in self.acls.show_directory_information():
                out.write(prefix + ln + '\n')

            # NB: show_directory_information() on R1000 does not indent this line
            out.write(prefix + 'Target  : ' + {
                    0x111111: "111111 = R1000",
                }.get(self.b55_target.val, "<<Unknown>>")
            )
            out.write('\n')


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
            dir_02_=bv.Pointer(DM07),
            dir_03_=bv.Pointer(DMTree),
            dir_04_=bv.Pointer(DMTree),
            dir_05_n_=-1,
        )

    def dot_node(self, dot):
        return "0x%x\\n?0x%x" % (self.dir_nbr.val, self.dir_05_n.val), ["shape=triangle"]

    def find_dir(self, nbr):
        mydir = self.dir_nbr.dirno.val
        print("FD", nbr, mydir)
        if nbr < mydir and self.dir_03.val:
            yield from self.dir_03.dst().find_dir(nbr)
        elif mydir == nbr:
            yield self
        elif nbr > mydir and  self.dir_04.val:
            yield from self.dir_04.dst().find_dir(nbr)

class ObjClass(bv.Struct):

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            rclass_=-6,
            subclass_=-10,
        )
        # See 5d3bfb73b, 00_class, 75_tag, seg_0ea8df
        cm.OBJECTS.get(self.rclass.val)
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

    def recurse_childtree(self):
        yield from self.b9_root.dst().recurse_childbranch()

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

    def current_version(self):
        return list(self.recurse_version_tree())[-1]

    def recurse_version_tree(self):
        yield from self.b6_000.dst().recurse_version_leaf()

    def show_directory_information(self, out, dm05, prefix):
        versions = list(self.recurse_version_tree())
        out.write(prefix + 'Versions: %d' % len(versions))
        out.write('; Retention Count: %d' % dm05.b5_retention_count.val)
        out.write('; Default: [%s,%d,1]' % (dm05.b5_class.class_name, versions[-1][1]))
        out.write('\n')
        for ver, objno in versions:
            out.write(prefix + '  Version %d: [' % ver)
            out.write(dm05.b5_class.class_name + ",%d,1]" % objno)
            out.write('  ( %d in [DIRECTORY,%d,1])' % (ver, dm05.b5_dir.val))
            out.write('\n')

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

    def recurse_version_leaf(self):
        if self.ve_left.val:
            yield from self.ve_left.dst().recurse_version_leaf()
        yield (self.ve_ver_n.val, self.ve_obj_n.val)
        if self.ve_right.val:
            yield from self.ve_right.dst().recurse_version_leaf()


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

    def recurse_childbranch(self):
        if self.de_l.val:
            yield from self.de_l.dst().recurse_childbranch()
        yield self
        if self.de_r.val:
            yield from self.de_r.dst().recurse_childbranch()

class AclSet(bv.Struct):

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

class AclEntry(bv.Struct):

    # Not quite a bitmap...
    modes = {
        0x1: "R",
        0x3: "RW",
        0x5: "RC",
        0x6: "CD",
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
        subj = self.tree.groups.get(self.subj.val + 1, None)
        if subj is None:
            print(self.tree.this, "Missing ACL subject %d at" % self.subj.val, hex(self.lo))
            subj = "<unknown %d>" % self.subj.val
        mode = self.modes.get(self.mode.val, None)
        if mode is None:
            mode = "0x%x" % self.mode.val
            print(self.tree.this, "Missing ACL mode", mode, "at", hex(self.lo))
        return subj + "=>" + mode

class NameList(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            zw_000_p__=bv.Constant(32, 0),
            text_=StringPointer,
            next_=bv.Pointer(NameList),
        )

class V1009T81(cm.ManagerSegment):

    VPID = 1009
    TAG = 0x81
    TOPIC = "Directory"

    def spelunk_manager(self):

        self.namespace = NameSpace(
            name = "",
            separator = "",
        )

        self.groups = {}
        self.users = {}

        self.d00 = DM00(self, self.seg_head.hi).insert()
        self.dm04 = self.d00.dm04.dst()

        for leaf in self:
            if isinstance(leaf, DM05):
                leaf.collect_users_and_groups()

        for i in sorted(self.groups.items()):
            print("G", i)

        self.this.top.add_interpretation(self, self.html_interpretation)

        fn = self.build_show_dir_info()

        self.this.add_interpretation(self, self.namespace.ns_html_plain)

        with self.this.add_html_interpretation("Show_directory_information simulated") as file:
            file.write('<A href="' + fn.link + '">')
            file.write('Simulated output from show_directory_information.\n')
            file.write('</A>\n')
            file.write('''
<P>If comparing to actual show_directory_information() output, note that:</P>
<P>A) On the R1000 the 'Target =' lines are not indented properly.</P>
<P>B) This output has a "Path" line with the absolute path.</P>
''')
        with self.this.add_utf8_interpretation("What we have figured out") as file:
            file.write(__doc__)

        self.this.add_type("DirectoryManagerData")


    def find_dir(self, nbr):
        key = (DM04_OFFSET + nbr) % DM04_SIZE
        dmt = self.dm04[key].dst()
        while dmt.dir_nbr.val != nbr:
            if nbr < dmt.dir_nbr.val:
                dmt = dmt.dir_03.dst()
            else:
                dmt = dmt.dir_04.dst()
        return dmt.dir_02.dst()

    def build_show_dir_info(self):
        fn = self.this.filename_for(suf=".show_directory_information.txt")
        with open(fn.filename, "w", encoding="utf8") as out:
            self.find_dir(1).show_directory_information(out, "", [])
        return fn

    def html_interpretation(self, file, this):
        file.write("<H3>Environment filesystem</H3>")
        file.write("<P>")
        file.write(self.this.summary(link=True))
        file.write("</P>\n")

