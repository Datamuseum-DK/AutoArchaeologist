#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Ohio Scientific Inc - OS65U filesystem
   ======================================

   Ohio Scientific several different computers using several
   different CPUs running several different OSs.

   This examiner support for 8" floppies with "OS65U".

   The input format is compatible with the ``.65U`` files
   used by the various OSI emulators, which is just a
   concatenation of the async data in each of the 77 tracks,
   without the parity bits, padded to 0xf00 bytes per track.

   Usage
   -----

   .. code-block:: none

       from autoarchaeologist.vendor.ohio_scientific import os65u_fs
       …
       self.add_examiner(*os65u_fs.ALL)

   Notes
   -----

   Test input
   ----------

   * Bits:30009355

   Documentation
   -------------

   https://osi.marks-lab.com/index.php

'''

from ...base import octetview as ov
from ...base import namespace

class NameSpace(namespace.NameSpace):
    ''' ... '''

    KIND = "Ohio Scientific OS65U"

    TABLE = (
        ("r", "password"),
        ("r", "attr"),
        ("r", "file type"),
        ("r", "access"),
        ("r", "start"),
        ("r", "length"),
        ("l", "name"),
        ("l", "artifact"),
    )

class AddressMark(ov.Struct):
    ''' ... '''

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            f00_=1,
            f01_=1,
            cyl_=1,
            f03_=1,
        )

class DirEnt(ov.Struct):
    ''' ... '''

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            nam_=ov.Text(6),
            pwd_=ov.Be16,
            attr_=ov.Octet,
            start_=ov.Le24,
            length_=ov.Le24,
            f05_=ov.Octet,
            vertical=False,
        )
        self.filetype = (self.attr.val >> 2) & 7
        self.access = self.attr.val & 3

    def commit(self):
        ''' Commit this file '''
        recs = []
        for i in range(self.length.val):
            o = self.tree.sector(self.start.val + i)
            if len(recs) == 0:
                z = DirEnt(self.tree, o).insert()
                y = ov.Opaque(self.tree, z.hi, width=256 - len(z)).insert()
            else:
                y = ov.Opaque(self.tree, o, width=256).insert()
            recs.append(self.tree.this[y.lo:y.hi])
            y.rendered = "[Data sector for " + self.nam.txt + "]"
        that = self.tree.this.create(records=recs, define_records=False)
        that.add_note("OS65UFile", dirent=self)
        priv = [
            "0x%04x" % self.pwd.val,
            "0x%02x" % self.attr.val,
            "0x%01x" % self.filetype,
            "0x%01x" % self.access,
            "0x%06x" % self.start.val,
            "0x%06x" % self.length.val,
        ]
        NameSpace(name = self.nam.txt.rstrip(), parent=self.tree.ns, this=that, flds=priv)

class OhioScientificOs65u(ov.OctetView):
    ''' ... '''

    def __init__(self, this):
        if this.top not in this.parents:
            return
        if len(this) != 0xf00 * 77:
            return

        super().__init__(this)

        d = DirEnt(self, self.sector(0x62))

        if d.nam.txt != "DIREC*":
            print(this, hex(d.lo), "DDD", d)
            return
        directory = ov.Vector(
            self,
            self.sector(0x62),
            count=(d.length.val << 8) // 0x10,
            target=DirEnt,
            vertical=True
        ).insert()

        self.ns = NameSpace(name="", root=this, separator="")
        for de in directory:
            if de.nam[0] > 0x20:
                de.commit()

        for frag in self.this.iter_rec():
            if frag.key[0] >= 7:
                AddressMark(self, frag.lo).insert()
                y = ov.Opaque(self, lo=frag.lo + 0xe04, hi=frag.hi).insert()
                y.rendered = "[Padding]"

        this.add_interpretation(self, self.ns.ns_html_plain)
        self.add_interpretation(more=True, elide=0)

    def sector(self, n):
        ''' Calculate address of sector '''
        trk = n // 14
        sect = n % 14
        try:
            frag = self.this.get_rec((trk,0,0))
            return frag.lo + 4 + (sect << 8)
        except KeyError:
            pass
        return trk*0xf00 + 4 + (sect << 8)

    def extract_basic_tokens(self):
        ''' Extract the BASIC token list '''
        ptr = 0x3204
        n = 0x80
        l = []
        while ptr < 0x3303:
            c = self.this[ptr]
            d = c & 0x7f
            if d < 0x20:
                break
            l.append(d)
            if c & 0x80:
                print("    0x%02x:" % n, "'" + "".join("%c" % x for x in l) + "',")
                l = []
                n += 1
            ptr += 1


ALL = (
    OhioScientificOs65u,
)
