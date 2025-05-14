#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

# NB: This docstring is also used as interpretation

'''
   EEDB "secret filesystem" - VPID 0256 - TAG 0x70
   ===============================================

   This is a very fundamental "filesystem" which is only mentioned
   one single place in all the documentation we have: the FE_HANDBOOK,
   pdf page 185.

   The directory is displayed with the ``VDIR *`` command at the
   ``EEDB:`` prompt.

   The "filesystem" is simply a mapping from filename to (vpid,
   segment).

   The various object managers state files live here, which is what
   that entry in the FE_HANDBOOK is about, but there also seems to
   be other "magic files" such as the product authentication codes,
   and some files which looks like crumbs from manual interventions at
   the ``EEDB:`` prompt.

   Some of the files are text files, which can be shown on the console
   with the ``TYPE_FILE`` command at the ``EEDB:`` prompt.

   Open ends
   ---------

   The discovered content is only a small fraction of the entire
   segment, and further discovery is warranted.

   Amongst the "debris" are StringArrays with the object managers'
   names with a ".pure" suffix.  These may be related to the
   ``Archive_On_Shutdown`` facility in ``package Operator`` documented
   on pdf page 6 of Guru_Course_3.

   Get the namespace to point to the actual segments.

   Does ``INSTRUCTIONS_SPEC`` and ``load_inst_spec.script_LOG`` reveal
   anything we did not already know ?

   This would also be a good place to stash the passwords.

'''

from ....base import bitview as bv
from ....base import namespace
# from .common import Segment, SegHeap, PointerArray, StringArray, StringPointer
from . import common as cm

class X00(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            x00_000_n_=-33,
            x00_001_n_=-32,
            more = True,
            vertical=True,
        )
        if self.x00_001_n.val == 1:
            self.add_field("x00_005_n", -32)
            self.add_field("x00_006_n", -32)
            self.add_field("x00_007_n", -32)
            self.add_field("x00_008_n", bv.Pointer.to(cm.BTree))
            self.add_field("x00_010_n", bv.Pointer)
            self.add_field("x00_011_n", bv.Pointer)
            self.add_field("x00_012_n", bv.Pointer)
            self.add_field("x00_013_n", bv.Pointer)
        self.done()

class X02(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            x02_000_n_=-32,
            x02_001_n_=-32,
            more=True,
            vertical=True,
        )
        self.add_field(
            "ptrs",
            bv.Array(
                self.x02_001_n.val,
                bv.Pointer.to(X03),
                vertical=True,
                #elide={0,},
            )
        )
        self.done()

class X03(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            x98_000_n__=bv.Constant(32, 0),
            x98_010_p_=bv.Pointer.to(cm.StringArray),
            x98_048_p_=bv.Pointer.to(X03),
        )

class SegId(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            x99_segkind_=-2,
            x99_segno_=-21,
            x99_vpid_=-10,
        )

class X04(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            #x99_000_n__=bv.Constant(32, 0),
            x99_000_n__=-32,
            x99_010_n_=cm.StringPointer,
            x99_seg_=SegId,
            #x99_049_n__=bv.Constant(32, 0x80),
            x99_049_n__=-32,
            x99_080_n_=bv.Pointer.to(X04),
        )
        if not self.x99_010_n.val:
            return
        that = None
        if self.x99_010_n.dst():
            self.name = name=self.x99_010_n.dst().txt
        else:
            self.name = "???"
        self.segment = "%03x:%06x" % (
            self.x99_seg.x99_vpid.val,
            (1 << 23) | self.x99_seg.x99_segno.val,
        )
        try:
            segidx = bvtree.this.top.by_class["r1k_segs"]
            segs = segidx.get(self.segment)
            if segs:
                print("EESEG", bvtree.this, name, segs)
                that = segs[max(segs.keys())]
        except KeyError:
            pass
        # print(self.x99_010_n.dst().txt)
        NameSpace(
            name=self.name,
            parent=bvtree.namespace,
            priv = self,
            this = that,
        )

class NameSpace(namespace.NameSpace):
    ''' ... '''

    KIND = "EEDB filesystem"

    TABLE = (
        ("r", "kind"),
        ("r", "vpid"),
        ("r", "segment"),
        ("l", "name"),
        ("l", "artifact"),
    )

    def ns_render(self):
        meta = self.ns_priv
        return [
            meta.x99_seg.x99_segkind.val,
            meta.x99_seg.x99_vpid.val,
            meta.segment,
        ] + super().ns_render()

class V0256T70_(cm.ManagerSegment):

    TOPIC = "EEDB filesystem"
    VPID = 256
    TAG = 0x70

class V0256T70(cm.Segment):

    VPID = 256
    TAG = 0x70

    def spelunk(self):

        self.namespace = NameSpace(
            name = "",
            separator = "",
        )

        self.seg_heap = cm.SegHeap(self, 0).insert()

        self.x00 = X00(self, self.seg_heap.hi).insert()

        if self.x00.x00_001_n.val != 1:
            return
        self.x02 = X02(self, self.x00.x00_011_n.val).insert()
        if False:
            for leaf in self:
                if not isinstance(leaf, X03):
                    continue
                sa = leaf.x98_010_p.dst()
                if isinstance(sa, cm.StringArray):
                    y = X04(self, sa.hi).insert()
                else:
                    print("NOSA", leaf)


        cm.PointerArray(
            self,
            self.x00.x00_013_n.val,
            dimension=101,
            cls=X04,
            elide={0,},
        ).insert()

        self.this.add_type("EEDB Filesystem")
        self.this.add_interpretation(self, self.namespace.ns_html_plain)
        self.this.top.add_interpretation(self, self.html_interpretation)
        with self.this.add_utf8_interpretation("What we have figured out") as file:
            file.write(__doc__)

    def html_interpretation(self, file, this):
        file.write("<H3>EEDB filesystem</H3>")
        file.write("<P>")
        file.link_to_that(self.this)
        file.write("</P>\n")
