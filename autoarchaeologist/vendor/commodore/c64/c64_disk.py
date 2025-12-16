#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

''' Commodore C=64 aka CBM1541/CBM4040 Filesystem '''

from ....base import octetview as ov
from ....base import namespace as ns

from ..  import petscii

class NameSpace(ns.NameSpace):
    ''' ... '''

    KIND = "C64Disk"

class C64TrackSect(ov.Struct):
    ''' Track+Sector coordinates '''

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            trk_=ov.Octet,
            sec_=ov.Octet,
        )

    def chs(self):
        ''' Return as (c,h,s) tuple '''
        return (self.trk.val, 0, self.sec.val)

    def render(self):
        yield "(%2d, 0, %2d)" % (self.trk.val, self.sec.val)

class C64DirEnt(ov.Struct):
    ''' Directory Entry '''

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            next_=C64TrackSect,
            ftype_=ov.Octet,
            data_=C64TrackSect,
            fname_=ov.Text(16),
            side_=C64TrackSect,
            reclen_=ov.Octet,
            unused_=6,
            fsize_=ov.Le16,
        )
        self.namespace = None

    def commit(self):
        ''' Commit and create child '''

        if not self.ftype.val & 0x80:
            return
        if self.fsize.val == 0:
            return
        data = []
        chs = self.data.chs()
        seen = set()
        while chs[0] != 0:
            try:
                rec = self.this.get_rec(chs)
            except KeyError:
                print(self.tree.this, self, "Sector not found", chs)
                break
            l = 256
            if rec[0] == 0:
                l = rec[1]

            if len(rec[2:l]) > 0:
                data.append(rec[2:l])
            else:
                break
            y = ov.Opaque(self.tree, rec.lo, hi=rec.hi).insert()
            y.rendered = "Data sector »" + self.fname.txt.rstrip() + "«"
            seen.add(chs)
            chs = (rec[0], 0, rec[1])
            if chs in seen:
                print(self.tree.this, "LOOP", chs, self)
                break

        if len(data) > 0:
            print("DR", list(len(x) for x in data))
            that = self.tree.this.create(records=data, define_records=False)
            that.add_type("C64-File")
            if self.fname.txt.rstrip():
                that.add_name(self.fname.txt.rstrip())
        else:
            that = None

        self.namespace = NameSpace(
            name = self.fname.txt.rstrip(),
            parent = self.tree.namespace,
            priv = self,
            this = that,
        )

class C64DirSect(ov.Struct):
    ''' Directory Sector '''

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            vertical=True,
            dirents_=ov.Array(8, C64DirEnt, vertical=True),
        )

class C64BAM(ov.Struct):
    ''' Block Allocation Map Sector (= superblock) '''

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            vertical=True,
            dir_=C64TrackSect,
            fmt_=ov.Octet,
            flt_=ov.Octet,
            map_=140,
            dname_=ov.Text(18),
            did_=ov.Text(2),
            dosv_=ov.Text(13),
            unused_=79,
        )

class C64Disk(ov.OctetView):
    ''' ... '''

    def __init__(self, this):
        if this.top not in this.parents:
            return
        print(this, self.__class__.__name__, len(this))

        chs = (18, 0, 0)
        try:
            ds = this.get_rec(chs)
        except KeyError:
            return

        if this[ds.lo + 0] != 0x12:
            return
        if this[ds.lo + 1] != 0x01:
            return

        super().__init__(this)
        this.type_case = petscii.PetScii()

        bam = C64BAM(self, ds.lo).insert()

        self.dirents = []

        chs = bam.dir.chs()
        while chs[0] != 0:
            ds = self.this.get_rec(chs)
            y = C64DirSect(self, ds.lo).insert()
            for de in y.dirents:
                self.dirents.append(de)
            chs = y.dirents[0].next.chs()

        self.namespace = NameSpace(name = '', root = this, separator = "")

        for i in self.dirents:
            i.commit()

        this.add_interpretation(self, self.namespace.ns_html_plain)
        self.add_interpretation(more=True, elide=0)
