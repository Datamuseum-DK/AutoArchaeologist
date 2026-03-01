#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
    R1000 'E3' objects
    ==================
'''


import html
from ...generic import hexdump
from ...generic import bitdata

fof = open("/tmp/_fof", "w")


class R1kE3Objects(bitdata.BitRecord):
    def __init__(self, this):
        if not this.has_note("e3_tag"):
            return

        self.this = this
        self.verbose = False
        this.add_interpretation(self, self.render_text)
        this.add_interpretation(self, self.render_meta)
        this.add_interpretation(self, self.render_unclaimed)
        self.this.add_type("Ada Source")
        if len(self.this) > 1<<16:
            self.this.add_note("Long Ada Source")

        pb = bitdata.PackedBits(this[:0x400])
        super().__init__(
            (
                ("nblk1", 19, True),
                ("hdr0", 77, False),
                ("nblk2", 19, False),
                ("hdr1", 8, False),
                ("hdr2", 63, False),
                ("hdr3", 12, False),
                ("nid", 16, True),
                ("hdr5", 17, False),
                ("hdr6", 16, True),
            ),
            bits=pb,
        )
        assert self.hdr0 == 0x1f81ffffffff00000000
        assert self.hdr1 == 0xff
        assert self.hdr2 == 0x7c0511030fa00010
        assert self.hdr5 == 0x00002
        assert self.nblk1 == self.nblk2
        assert self.nblk1 + 1 == self.hdr3
        self.recs = []
        for i in range(100):
            j = bitdata.BitRecord(
                (
                    ("rec0", 8, True),
                    ("rec1", 8, True),
                    ("rec2", 8, True),
                    ("rec3", 11, True),
                ),
                bits=pb,
            )
            self.recs.append(j)
        self.tail0 = pb.get(82)
        assert not pb.get(3495)
        self.tail1 = pb.get(68)
        assert not pb.get(800)
        assert not len(pb)
        self.done = {}
        nested_scope = 0

        for i in self:
            j = i.split(maxsplit=1)
            if not len(j) or j[0] not in ("pragma", "package", "procedure", "function", "separate", "generic"):
                continue
            for j in "(),;":
                i = i.replace(j, " ")
            j = i.split(maxsplit=4)
            j[0] = j[0].lower()
            try:
                if len(j) == 2 and j[0] == "package":
                    self.this.add_note(" ".join(j[:2]))
                    nested_scope = 1
                elif j[0] == "pragma" and j[1] == "Cache_Register":
                    self.this.add_note(" ".join(j[:5]))
                elif j[0] == "pragma" and j[1] == "Segmented_Heap":
                    self.this.add_note(" ".join(j[:5]))
                elif j[0] == "pragma" and j[1] == "Module_Name":
                    self.this.add_note(" ".join(j[:4]))
                elif j[0] == "pragma" and j[1] == "Subsystem":
                    self.this.add_note(" ".join(j[:3]))
                elif nested_scope == 0 and j[0] == "package" and j[2].lower() == "is":
                    self.this.add_note(" ".join(j[:2]))
                    nested_scope = 1
                elif j[0] == "package" and j[1].lower() == "body" and j[3].lower() == "is":
                    self.this.add_note(" ".join(j[:3]))
                    nested_scope = 1
                elif nested_scope == 0 and j[0] == "procedure":
                    self.this.add_note(" ".join(j[:2]))
                    nested_scope = 1
                elif nested_scope == 0 and j[0] == "function":
                    self.this.add_note(" ".join(j[:2]))
                    nested_scope = 1
                elif j[0] == "separate":
                    self.this.add_note(" ".join(j))
                elif j[0] == "generic":
                    self.this.add_note(j[0])
            except Exception as e:
                print("R1KE3", self.this, j, e)

    def __iter__(self):
        buf = ""
        next = self.recs[0].rec2
        while next:
            self.done[next] = True
            adr = next << 10
            that = self.this[adr:adr+0x400].tobytes()
            next = (that[0] << 8) | that[1]
            end = 4 + (that[2] << 8) | that[3]
            ptr = 4
            while ptr < end:
                if not that[ptr]:
                    yield buf
                    buf = ""
                length = that[ptr + 1]
                length2 = that[ptr + length + 2]
                assert length == length2
                ptr += 2
                for a in that[ptr:ptr+length]:
                    if 0x20 <= a <= 0x7e:
                        buf += "%c" % a
                    else:
                        buf += "\\x%02x" % a
                ptr += length + 1
        yield buf

    def render_meta(self, fo, _this):
        fo.write("<H3>E3 Meta Data</H3>\n")
        fo.write("<pre>\n")
        fo.write(self.render(show_tag=True, one_per_line=True) + "\n")
        for i in range(min(100, self.nblk1)):
            fo.write("        [0x%02x] " % i)
            fo.write(self.recs[i].render(show_tag=True, fixed_width=True))
            fo.write("\n")
        fo.write("    tail 0x%x 0x%x" % (self.tail0, self.tail1))
        fo.write("\n")
        if self.nid:
            fo.write("Free Block Chain:\n")
            i = self.nid
            while i:
                self.done[i] = True
                fo.write("  0x%x: " % i)
                that = self.this[i<<10:(i<<10)+16]
                hexdump.hexdump_to_file(that, fo)
                i = (that[0] << 8) | that[1]

        fo.write("</pre>\n")

    def render_text(self, fo, _this):
        fo.write("<H3>E3 Source Code</H3>\n")
        fo.write("<pre>\n")
        for i in self:
            fo.write(html.escape(i) + "\n")
        fo.write("</pre>\n")

    def render_unclaimed(self, fo, _this):
        l = []
        for i in range(1, len(self.this) >> 10):
            if not i in self.done:
                print("UNCLAIMED BLOCK", self.this, "0x%x" % i)
                l.append(i)
        if not l:
            return
        fo.write("<H3>E3 Unclaimed Blocks</H3>\n")
        fo.write("<pre>\n")
        for i in l:
            fo.write("Unclaimed sector 0x%x\n" % i)
            hexdump.hexdump_to_file(self.this[i<<10:(i+1)<<10], fo)
        fo.write("</pre>\n")
