#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

''' ... '''

from ...base import octetview as ov

class SecRef(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            sec_=ov.Octet,
            trk_=ov.Octet,
        )
        self.chs = (self.trk.val, 0, self.sec.val & 0x1f)
        self.frag = self.tree.this.get_frag(self.chs)
        if self.frag is not None:
            self.that = Txt(tree, self.frag.lo)
            ov.Opaque(tree, self.frag.lo, hi=self.frag.hi).insert()

    def render(self):
        if self.frag is not None:
            yield str(self.chs).ljust(12) + str(self.sec.val>>5) + " ┆" + self.that.txt.txt + "┆"
        else:
            yield from super().render()

class Chs(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            sec_=ov.Octet,
            cyl_=ov.Octet,
            head_=ov.Octet,
        )

    def render(self):
        yield "(%d, %d, %d, %d)".ljust(15) % (
            self.cyl.val,
            self.head.val,
            self.sec.val & 0x1f,
            self.sec.val >> 5,
        )

class Hdr(ov.Struct):

    def __init__(self, tree, lo):
        for p in range(64):
            pp = lo + 3 + p * 2
            if sum(tree.this[pp:pp+3]) == 0:
                break
            if tree.this[pp] & 0xe0:
                p += 1
                break
        super().__init__(
            tree,
            lo,
            hdr_=Chs,
            secs_=ov.Array(p, SecRef, vertical=True),
            vertical=True,
        )
        r = []
        for s in self.secs:
            if s.frag is None:
                return
            r.append(s.frag.frag[3:])
        if len(r):
            that = self.tree.this.create(records=r)
            if self.hdr.cyl.val == 20 and (self.hdr.sec.val & 0x1f) == 0:
                that.add_type("P5002-Catalog")

class Cat(ov.Struct):

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            hdr_=Chs,
            secs_=ov.Array(32, 2, vertical=True),
            vertical=True,
        )

class Txt(ov.Struct):

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            hdr_=3,
            txt_=ov.Text(128),
        )

class P5002(ov.OctetView):

    def __init__(self, this):
        if this.top not in this.parents:
            return

        super().__init__(this, line_length=131)

        for r in this.iter_rec():
            if sum(r[3:]) == 0:
                ov.Opaque(self, r.lo, hi=r.hi).insert()
            elif r.frag[0] >> 5 == 5:
                Hdr(self, r.lo).insert()
            elif r.frag[0] >> 5 == 1:
                Hdr(self, r.lo).insert()
            elif 0:
                Txt(self, r.lo).insert()

        this.add_interpretation(self, this.html_interpretation_children)
        self.add_interpretation(title="HexDump", more=False, elide=0)
