#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   We think "bust" is a backup program written by RC, but this is
   not certain.  This module is based on just three samples, one
   from a RC900 system and two (almost identical) from a RC39 system.
'''

from ...base import octetview as ov
from ...base import namespace as ns

class NameSpace(ns.NameSpace):
    ''' ... '''


class Hdr(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            f00_=ov.Le16,
            f01_=ov.Le16,
            f02_=ov.Text(16),
            f03_=ov.Le16,
            f04_=ov.Le16,
            f05_=ov.Le16,
            f06_=ov.Le16,
            f07_=ov.Text(16),
            vertical=True,
        )

class Part61(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            f00_=6,
            f01_=ov.Text(14),
            f02_=4,
        )

class Part64(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            f00_=ov.Text(4),
            f01_=ov.Text(14),
            f02_=ov.Le16,
            f03_=ov.Array(6, ov.Le32),
        )

class Listx(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            f00_=ov.Le16,
            f01_=ov.Le16,
            f02_=ov.Le16,
            f03_=ov.Le16,
            more=True,
            vertical=False,
        )
        self.done()

class DirCatFile(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            f00_=ov.Le16,
            f01_=ov.Le16,
            f02_=ov.Le16,
            name_=ov.Text(14),
            f04_=ov.Le16,
            parent_=ov.Le16,
        )

class FilCatFile61(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            mode_=ov.Le16,
            links_=ov.Le16,
            uid_=ov.Le16,
            gid_=ov.Le16,
            size_=ov.Le32,
            dirno_=ov.Le16,
            blkno_=ov.Le32,
            mtime_=ov.Le32,
            f08_=1,
            name_=ov.Text(14),
            f09_=ov.Octet,
            hlink_=ov.Le16,
        )

class FilCatFile64(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            mode_=ov.Le16,
            links_=ov.Le16,
            uid_=ov.Le16,
            gid_=ov.Le16,
            size_=ov.Le32,
            blkno_=ov.Le16,
            f06_=ov.Le16,
            mtime_=ov.Le32,
            dirno_=ov.Le16,
            hlink_=ov.Le16,
            name_=ov.Text(14),
            f11_=ov.Le16,
        )

class Section(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            sec0_=ov.Le32,
            f01_=ov.Le32,
            nrec_=ov.Le32,
        )

class XenixBust(ov.OctetView):
    def __init__(self, this):
        if this.top not in this.parents:
            return
        super().__init__(this)

        print(this, self.__class__.__name__, bytes(this[:16]))

        hdr = Hdr(self, 0).insert()

        if this[0] == 0x64:
            nsec = ov.Le32(self, 0x44).insert()
            secs = ov.Array(nsec.val, Section, vertical=True)(self, 0x48).insert()
            sdir = secs[0]
            sfil = secs[1]
            self.base = (secs[4].sec0.val + secs[4].f01.val) << 10
            ov.Array(3, Part64, vertical=True)(self, 0x8c).insert()
            fcls = FilCatFile64

        elif this[0] == 0x61:
            nsec = ov.Le16(self, 0x76).insert()
            secs = ov.Array(nsec.val, Section, vertical=True)(self, 0x78).insert()
            sdir = secs[0]
            sfil = secs[1]
            ov.Array(2, Part61, vertical=True)(self, 0x90).insert()
            fcls = FilCatFile61
            secs2 = ov.Array(2, Section, vertical=True)(self, 0x2ae).insert()
            self.base = (secs2[1].sec0.val + secs2[1].f01.val) << 10
        else:
            return

        self.ns = NameSpace(name="", root=this, separator="/")
        nl = 0
        for ptr in range(0x400, 0x1800, 2):
            y = ov.Le16(self, ptr)
            if y.val == 0xffff:
                nl += 1
                y = Listx(self, ptr)
                if y.f01.val != 0xffff:
                    y.insert()

        print(this, "NL", nl, hex(nl))

        y = ov.Array(sdir.nrec.val + 1, DirCatFile, vertical=True)(self, sdir.sec0.val<<10).insert()
        self.dirs = {0: self.ns}
        for n, dcf in enumerate(y):
            if n == 0:
                continue
            print("DCF", dcf)
            if dcf.name[0] == 0:
                self.dirs[n] = self.dirs[0]
                continue
            self.dirs[n] = NameSpace(
                name = dcf.name.txt.rstrip(),
                parent = self.dirs[dcf.parent.val],
            )

        if True:
            y = ov.Array(sfil.nrec.val + 1, fcls, vertical=True)(self, sfil.sec0.val<<10).insert()
            for n, fcf in enumerate(y):
                b = self.base + (fcf.blkno.val<<10)
                if fcf.hlink.val == 0 and fcf.size.val > 0 and b + fcf.size.val <= len(this):
                    print("FCF", fcf, hex(b))
                    that = this.create(start = b, stop = b + fcf.size.val)
                else:
                    that = None
                NameSpace(
                    name = fcf.name.txt.rstrip(),
                    parent = self.dirs[fcf.dirno.val],
                    this=that,
                )

        this.add_interpretation(self, self.ns.ns_html_plain)
        self.add_interpretation(elide=1<<16, more=True)
