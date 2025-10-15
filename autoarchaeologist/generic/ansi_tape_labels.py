#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   ANSI tape labels
   ----------------

   Implemented based on Ecma-13 as available her:

      http://bitsavers.org/pdf/ecma/ECMA-013.pdf

'''

from ..base import octetview as ov
from ..base import type_case
from ..base import namespace
from ..base import artifact

class AnsiTypeCase(type_case.Ascii):
    ''' ... '''
    # def __init__(self):

ansi_type_case = AnsiTypeCase()

class AnsiTapeLabel(ov.Struct):
    ''' One tape label record '''

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            vertical=True,
            hdr_=ov.Text(4),
            more=True
        )
        if self.hdr.txt == "VOL1":
            self.add_field("vol_id", ov.Text(6, True))
            self.add_field("vol_access", ov.Text(1, True))
            self.add_field("rsv12", ov.Text(13, True))
            self.add_field("impl_id", ov.Text(13, True))
            self.add_field("own_id", ov.Text(14, True))
            self.add_field("rsv52", ov.Text(28, True))
            self.add_field("version", ov.Text(1, True))
        elif self.hdr.txt in ("HDR1", "EOV1", "EOF1",):
            self.add_field("file_id", ov.Text(17, True))
            self.add_field("file_set", ov.Text(6, True))
            self.add_field("file_section", ov.Text(4, True))
            self.add_field("file_sequence", ov.Text(4, True))
            self.add_field("generation", ov.Text(4, True))
            self.add_field("generation_version", ov.Text(2, True))
            self.add_field("created", ov.Text(6, True))
            self.add_field("expiration", ov.Text(6, True))
            self.add_field("accessibility", ov.Text(1, True))
            self.add_field("block_count", ov.Text(6, True))
            self.add_field("impl_id", ov.Text(13, True))
            self.add_field("rsv74", ov.Text(7, True))
        elif self.hdr.txt in ("HDR2", "EOV2", "EOF2",):
            self.add_field("rec_fmt", ov.Text(1, True))
            self.add_field("block_len", ov.Text(5, True))
            self.add_field("rec_len", ov.Text(5, True))
            self.add_field("rsv16", ov.Text(35, True))
            self.add_field("offs_len", ov.Text(2, True))
            self.add_field("rsv53", ov.Text(28, True))
        if len(self) < 80:
            self.add_field("misc", ov.Text(80-len(self), True))
        self.done()

    def suffix(self, adr):
        return ""

class NameSpace(namespace.NameSpace):
    ''' ... '''

    TABLE = (
        ("r", "rec_fnt"),
        ("r", "block_len"),
        ("r", "block_count"),
        ("l", "name"),
        ("l", "artifact"),
    )

    def ns_render(self):
        file = self.ns_priv
        l = []
        if "HDR2" in file.hdrs:
            l.append(file.hdrs["HDR2"].rec_fmt.txt)
            l.append(file.hdrs["HDR2"].block_len.txt)
        else:
            l.append("-")
            l.append("-")
        if "EOF1" in file.tails:
            l.append(file.tails["EOF1"].block_count.txt)
        else:
            l.append("-")
        return l + super().ns_render()

class TapeFile():
    ''' One ANSI labeled tape file '''

    def __init__(self, tree):
        self.tree = tree
        self.hdrs = {}
        self.recs = []
        self.tails = {}
        self.that = None
        self.namespace = None

    def add_hdr(self, rec):
        ''' Add a header record '''
        hdr = AnsiTapeLabel(self.tree, rec.lo).insert()
        assert hdr.hdr.txt not in self.hdrs
        self.hdrs[hdr.hdr.txt] = hdr

    def add_rec(self, rec):
        ''' Add a body record '''
        self.recs.append(rec)

    def add_tail(self, rec):
        ''' Add a tail record '''
        hdr = AnsiTapeLabel(self.tree, rec.lo).insert()
        assert hdr.hdr.txt not in self.tails
        self.tails[hdr.hdr.txt] = hdr

    def segment(self):
        ''' Segment this file '''
        if "HDR2" not in self.hdrs:
            that = self.undefined()
        elif self.hdrs["HDR2"].rec_fmt.txt == "S":
            that = self.segmented()
        elif self.hdrs["HDR2"].rec_fmt.txt == "U":
            that = self.undefined()
        elif self.hdrs["HDR2"].rec_fmt.txt == "F":
            that = self.fixed()
        else:
            print(self.tree.this, "Unknown ANSI record format", self.hdrs["HDR2"].rec_fmt.txt)
            return
        if "HDR1" in self.hdrs:
            self.namespace = NameSpace(
                name = self.hdrs["HDR1"].file_id.txt.rstrip(),
                this = that,
                parent = self.tree.namespace,
                priv = self,
            )

    def fixed(self):
        ''' A tape with fixed blocking '''
        l = []
        w = int(self.hdrs["HDR2"].rec_len.txt)
        for r in self.recs:
            for p in range(0, len(r), w):
                l.append(self.tree.this[r.lo+p:r.lo+p+w])
        that = self.tree.this.create(records=l)
        that.add_note("Ansi-tape:Fixed")
        return that

    def undefined(self):
        ''' A tape with undefined blocking '''
        that = self.tree.this.create(
            records = (self.tree.this[x.lo:x.hi] for x in self.recs)
        )
        that.add_note("Ansi-tape:Undefined")
        return that

    def segmented(self):
        ''' A segmented tape '''
        segs = []
        frags = []
        offset = 0
        recno = 0
        for i in self.recs:
            pos = 0
            while pos < len(i):
                scw = i.frag[pos:pos+5].tobytes().decode('ascii')
                size = int(scw[1:])
                frag = self.tree.this[i.lo + pos + 5:i.lo + pos + size]
                frags.append(frag)
                if scw[0] == '0':
                    segs.append([recno, offset, len(frag), frag])
                    recno += 1
                elif scw[0] == '1':
                    segs.append([recno, offset, len(frag), None])
                    recno += 1
                elif scw[0] == '2':
                    segs[-1][2] += len(frag)
                elif scw[0] == '3':
                    segs[-1][2] += len(frag)
                else:
                    assert scw[0] in "0123"
                offset += len(frag)
                pos += size
        that = self.tree.this.create(records = frags, define_records=False)
        for recno, offs, size, frag in segs:
            that.define_rec(
                artifact.Record(
                    key = (recno,),
                    low=offs,
                    high=offs + size,
                    frag = frag,
                )
            )
        that.add_note("Ansi-tape:Segmented")
        return that

    def interpretation(self, file):
        ''' Emit html interpretation '''
        for i in self.hdrs.values():
            for j in i.render():
                file.write(j + "\n")
        for i in self.tails.values():
            for j in i.render():
                file.write(j + "\n")


class AnsiTapeLabels(ov.OctetView):
    ''' ANSI Tape Labels '''

    def __init__(self, this):
        if not this.has_type("SimhTapContainer"):
            return

        super().__init__(this)

        self.files = []
        curfile = None
        for rec in this.iter_rec():
            fno = rec.key[0] // 3
            if fno >= len(self.files):
                curfile = TapeFile(self)
                self.files.append(curfile)
            part = rec.key[0] % 3
            if part == 0:
                if len(rec) != 80:
                    return
                curfile.add_hdr(rec)
            elif part == 1:
                curfile.add_rec(rec)
                ov.Opaque(self, rec.lo, hi=rec.hi).insert()
            elif part == 2:
                if len(rec) != 80:
                    return
                curfile.add_tail(rec)
        print(self.__class__.__name__, this)
        self.namespace = NameSpace(
            name = "",
            separator = "",
            root = this,
        )
        self.this.add_interpretation(self, self.namespace.ns_html_plain)
        for tapefile in self.files:
            tapefile.segment()
        tfn = this.add_utf8_interpretation('ANSI labeled tape')
        with open(tfn.filename, "w", encoding="utf-8") as file:
            for tapefile in self.files:
                tapefile.interpretation(file)
        self.add_interpretation()
