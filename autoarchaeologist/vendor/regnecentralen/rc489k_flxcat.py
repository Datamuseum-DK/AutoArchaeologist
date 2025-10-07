#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   RC4000/RC8000/RC9000 "flxcat"
   -----------------------------

'''

import html

from ...base import octetview as ov
from .rc489k_utils import DWord, ShortClock

#################################################
#
# A file can be a subdirectory if it has key=10

class Foo00(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            w000_=DWord,
            name_=ov.Text(6),
            w020_=ov.Text(12),
            nent_=ov.Be24,
            nrec_=ov.Be24,
            w022_=ShortClock,
            w024_=ov.Be24,
            w026_=ov.Be24,
            w028_=ov.Be24,
            w030_=ov.Text(6),
            w040_=ov.Be24,
            w045_=ov.Text(6),
            w050_=ov.Text(6),
            # vertical=True,
        )

class Foo01(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            w00_=DWord,
            w01_=Foo02,
            w02_=Foo02,
            vertical=True,
        )

class Foo02(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            name_=ov.Text(18),
            w02_=ov.Be24,
            w03_=ov.Be24,
            w04_=ov.Be24,
            w05_=ov.Be24,
            w6_=ov.Be24,
            w07_=ov.Text(12),
            #w08_=ov.Be24,
            #w09_=ov.Text(3),
            w10_=ov.Be24,
            w11_=ov.Be24,
            w12_=ov.Be24,
            w13_=ov.Be24,
            w14_=ov.Be24,
        )

class FlxCat(ov.OctetView):
    def __init__(self, this):
        if this[6:12] != b'flxcat':
            return

        vol = list(this.parents)[0]
        self.volhead = vol.has_note("GA21-9182")["volhead"]
        self.volid = self.volhead.volume_identifier.txt

        volset_dict = this.top.get_by_class_dict(self)
        if len(volset_dict) == 0:
            this.top.add_interpretation(self, self.topall)

        this.add_type("flxcat")
        super().__init__(this)
        recs = []
        for r in this.iter_rec():
            n = len(r) // 126
            for i in range(n):
                recs.append(r.lo + i * 126)
        self.entries = []
        for o in recs:
            y = DWord(self, o)
            if y.w0.val == 1:
                self.hdr = Foo00(self, o).insert()
            elif y.w0.val == 2:
                y = Foo01(self, o).insert()
                self.entries.append(y.w01)
                self.entries.append(y.w02)
            else:
                y.insert()

        self.group = self.hdr.w030.txt
        gl = volset_dict.get(self.group)
        if not gl:
            gl = []
            volset_dict[self.group] = gl
        gl.append(self)

        self.add_interpretation(more=False)

    def __lt__(self, other):
        if self.hdr.w022.val != other.hdr.w022.val:
            return self.hdr.w022.val < other.hdr.w022.val
        if self.hdr.w040.val != other.hdr.w040.val:
            return self.hdr.w040.val < other.hdr.w040.val
        return self.volid < other.volid

    def topall(self, file, this):
        volset_dict = this.top.get_by_class_dict(self)
        file.write("<H3>TOPALL</H3>\n")
        file.write("<PRE>\n")
        for i, j in sorted(volset_dict.items()):
            file.write(html.escape(str(i)) + "\n")
            for gm in sorted(j):
                file.write("  " + str(gm.this) + " " + gm.volid)
                file.write("  " + html.escape(" ".join(gm.hdr.render())))
                file.write("  " + str(gm.hdr.w022.val))
                file.write("  " + html.escape(str(list(gm.this.parents))))
                file.write("\n")
        file.write("</PRE>\n")
