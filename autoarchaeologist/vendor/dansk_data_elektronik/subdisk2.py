#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

from ...base import octetview as ov

SIGNATURE = bytes.fromhex('73 75 62 64 69 73 6b 32 20 70 72 65 73 65 6e 74')

class Entry(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            len_=ov.Be16,
            f01_=ov.Be16,
        )

class Hdr(ov.Struct):

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            vertical=True,
            pad000_=64,
            f040_=17,
            pad051_=47,
            pad080_=64,
            pad0c0_=32,
            pad0e0_=16,
            drive_=ov.Text(16),
            pad100_=64,
            pad140_=64,
            pad180_=64,
            pad1c0_=64,
            pad200_=64,
            pad240_=64,
            pad280_=64,
            pad2c0_=64,
            entire_=Entry,
            tbl_=ov.Array(31, Entry, vertical=True),
            pad380_=4,
            magic_=ov.Text(16),
            pad394_=12,
            pad3a0_=32,
            pad3c0_=28,
            f3cc_=ov.Be32,
            f3e0_=ov.Be32,
            pad3e4_=24,
            f3fc_=ov.Be32,
        )

class SubDisk2(ov.OctetView):

    def __init__(self, this):
        if not this.top in this.parents:
            return
        if this[900:900 + len(SIGNATURE)].tobytes() != SIGNATURE:
            return

        this.add_note("DDE:Subdisk2")
        super().__init__(this)

        offset = 8192
        hdr = Hdr(self, 0).insert()
        for n, fld in enumerate(hdr.tbl):
            if fld.len.val == 0:
                break
            length = fld.len.val << 16
            end = offset + length
            print(this, n, hex(offset), hex(length), hex(end), hex(len(this)))
            if end <= len(this):
                y = this.create(start=offset, stop=end)
                y.add_type("DDE:Subdisk2:0x%x" % n)
                self.helper(y)
            else:
                print(this, "Subdisk2 ran out of disk")
            offset = end
        if offset < len(this):
            y = this.create(start=offset, stop=len(this))
            y.add_type("DDE:Subdisk2:tail")

        ov.Opaque(self, 0x400, len(this)).insert()
        self.this.add_interpretation(self, this.html_interpretation_children)
        self.add_interpretation()

    def helper(self, that):
        if that[:5] == b'smos ':
            that.add_type("DDE:smos files")
        if that[:4] == b'@(#)':
            that.add_type("DDE:what-marker")
