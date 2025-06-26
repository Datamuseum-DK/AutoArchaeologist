#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Q1 floppy filesystem
   ====================
'''

from ...base import artifact
from ...base import octetview as ov
from ...base import namespace

class NameSpace(namespace.NameSpace):
    ''' ... '''

    TABLE = (
        ("r", "flag"),
        ("r", "nrec"),
        ("r", "reclen"),
        ("r", "rec_trk"),
        ("r", "t0"),
        ("r", "tn"),
        ("l", "name"),
        ("l", "artifact"),
    )

    def ns_render(self):
        cat = self.ns_priv
        if cat is None:
            return [ "" ] * 5 + super().ns_render()
        return [
            cat.f0.val,
            cat.nrec.val,
            cat.reclen.val,
            cat.rectrack.val,
            cat.track0.val,
            cat.trackn.val,
        ] + super().ns_render()

class DataSector(ov.Opaque):
    ''' ... '''

class Catalog(ov.Struct):

    def __init__(self, tree, lo):

        super().__init__(
            tree,
            lo,
            f0_=ov.Le16,
            name_=ov.Text(8),
            nrec_=ov.Le16,
            reclen_=ov.Le16,
            rectrack_=ov.Le16,
            track0_=ov.Le16,
            trackn_=ov.Le16,
            more=True,
        )
        self.done(40)

        if self.f0.val or self.nrec.val == 0:
            return
        l = []
        c = self.track0.val
        h = 0
        s = 0
        if c >= 80:
            print(tree.this,hex(lo), "BAD Catalog", self)
            return
        badsect = False
        for n in range(self.nrec.val):
            chs = (c, h, s)
            try:
                rec = self.tree.this.get_rec(chs)
                octets = rec.frag
                if self.lo != 0:
                    DataSector(self.tree, lo=rec.lo, hi=rec.hi).insert()
            except KeyError:
                octets = None
            if octets is None:
                badsect = True
                print(self.tree.this, "Missing", chs)
                octets = b'_UNREAD_' * ((self.reclen.val + 7) // 8)
                octets = octets[:self.reclen.val]
            l.append(artifact.Record(0, frag=octets, key=(n,)))
            s += 1
            if s == self.rectrack.val:
                c += 1
                s = 0
        # print(self, len(l), l[0], l[-1])
        that = self.tree.this.create(records=l)
        that.add_note("q1file")
        if badsect:
            that.add_note("BadSectors")
        that.add_type("reclen=%d" % self.reclen.val)

        self.namespace = NameSpace(
            name = self.name.txt.rstrip(),
            parent = tree.namespace,
            priv = self,
            this = that,
        )


class Q1FileSystem(ov.OctetView):

    def __init__(self, this):
        if this.top not in this.parents:
            return

        print(this, "Q1FileSystem")
        super().__init__(this)

        self.namespace = NameSpace(
            name = '',
            root = this,
            separator = "",
        )

        try:
            rec = self.this.get_rec((0,0,0))
        except KeyError:
            rec = None
        if rec:
            self.index = Catalog(self, rec.lo).insert()
            for i in this.iter_rec():
                if sum(i.key) == 0:
                    pass
                elif i.key[0] == 0 and i.key[2] != 0 and i.key[2] < self.index.nrec.val:
                    y = Catalog(self, i.lo).insert()

        this.add_interpretation(self, self.namespace.ns_html_plain)
        self.add_interpretation(more=True)
