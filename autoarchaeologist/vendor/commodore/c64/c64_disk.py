#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

''' ... '''

from ....generic import disk
from ....base import octetview as ov
from ....base import namespace as ns

from ..  import petscii

class NameSpace(ns.NameSpace):
    ''' ... '''

class C64TrackSect(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            trk_=ov.Octet,
            sec_=ov.Octet,
        )

    def chs(self):
        return (self.trk.val, 0, self.sec.val)

    def render(self):
        yield "(%2d, 0, %2d)" % (self.trk.val, self.sec.val)

class C64DirEnt(ov.Struct):

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
        print("CC", self)
        if not self.ftype.val & 0x80:
            return
        if self.fsize.val == 0:
            return
        data = []
        chs = self.data.chs()
        while chs[0] != 0:
            print("  ", chs)
            try:
                rec = self.this.get_rec(chs)
            except KeyError:
                print("  Not found", chs)
                break
            l = 256
            if rec[0] == 0:
                l = rec[1]

            data.append(rec[2:l])
            #y = ov.Opaque(self.tree, rec.lo, hi=rec.hi).insert()
            #y.rendered = "Data sector " + self.fname.txt + " 0x%x" % len(data)
            #y.rendered = "Data sector " + self.fname.txt
            chs = (rec[0], 0, rec[1])
        print("LD", len(data), chs[1])
        if len(data) > 0:
            that = self.tree.this.create(records=data)
            #that.add_note(self.fname.txt)
        else:
            that = None

        self.namespace = NameSpace(
            name = self.fname.txt,
            parent = self.tree.namespace,
            priv = self,
            this = that,
        )

class C64DirSect(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            vertical=True,
            dirents_=ov.Array(8, C64DirEnt, vertical=True),
        )

class C64BAM(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            vertical=True,
            dir_=C64TrackSect,
            fmt_=ov.Text(1),
            flt_=ov.Octet,
            map_=140,
            dname_=ov.Text(18),
            did_=ov.Be16,
            dosv_=ov.Text(13),
            unused_=79,
        )

class C64Disk(disk.Disk):
    ''' ... '''

    def __init__(self, this):
        if this.top not in this.parents:
            return
        if len(this) not in (174848,):
            return
        print(this, self.__class__.__name__, len(this))
        super().__init__(
            this,
            [
                (18, 1, 21, 256),
                ( 7, 1, 19, 256),
                ( 6, 1, 18, 256),
                ( 5, 1, 17, 256),
            ]
        )
        this.type_case = petscii.PetScii()
        self.dirents = []
        chs = (18, 0, 0)
        ds = self.this.get_rec(chs)
        y = C64BAM(self, ds.lo).insert()
        chs = y.dir.chs()
        while chs[0] != 0:
            ds = self.this.get_rec(chs)
            y = C64DirSect(self, ds.lo).insert()
            for de in y.dirents:
                self.dirents.append(de)
            chs = y.dirents[0].next.chs()

        self.namespace = NameSpace(name = '', root = this, separator = "")

        for i in self.dirents:
            print(i)
            i.commit()

        this.add_interpretation(self, self.namespace.ns_html_plain)
        this.add_interpretation(self, self.disk_picture)
        this.add_interpretation(self, self.this.html_interpretation_children)
        self.add_interpretation(more=True)
