#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   PTS Tape
   ========
'''

from ...base import artifact
from ...base import octetview as ov
from ...base import namespace as ns

class Chunk(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            cno_=ov.Be16,
        )
        self.val = self.cno.val

    def render(self):
        yield "C0x%04x.0x%x.%x" % (self.cno.val >> 5, (self.cno.val >> 3) & 3, self.cno.val & 7)

class DirEnt(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            nam_=ov.Text(6),
            typ_=ov.Text(2),
            f00_=ov.Be16,
            f01_=ov.Be16,
            f02_=ov.Be16,
            f03_=ov.Be16,
        )

class DirSect(ov.Struct):

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            f00_=ov.Be16,
            f01_=ov.Be16,
            dents_=ov.Array(400//16, DirEnt, vertical=True),
            vertical=True,
        )

class IdxSect(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            f00_=ov.Be16,
            f01_=ov.Be16,
            gno_=ov.Array(400 // 2, Chunk, elide=(0,), vertical=True),
            vertical=True,
        )
        self.dirent = None

    def render(self):
        yield "# " + str(self.dirent)
        yield from super().render()

class DirGranule(ov.Struct):

    def __init__(self, tree, frag):
        super().__init__(
            tree,
            frag.lo,
            sects_=ov.Array(8, DirSect, vertical=True),
            vertical=True,
        )
        self.key = frag.key
        self.f00s = set(i.f00.val for i in self.iter_dents())
        self.f01s = set(i.f01.val for i in self.iter_dents())
        self.f03s = set(i.f03.val for i in self.iter_dents())
        self.typs = set(i.typ.txt for i in self.iter_dents())

    def valid(self):
        return len(self.typs) < 8

    def iter_dents(self):
        for sect in self.sects:
            for dent in sect.dents:
                if dent[0] == 0x00 and dent[1] == 0x00:
                    continue
                if dent[0] == 0xff and dent[1] == 0xff:
                    return
                yield dent

    def commit(self):
        fno, rno = self.key
        rno += 1
        our_ns = None
        for dent in self.iter_dents():
            that = None
            if not our_ns:
                our_ns = ns.NameSpace(
                    name=(dent.nam.txt + dent.typ.txt).rstrip(),
                    parent=self.tree.ns,
                )
                continue
            if dent.typ.txt in ("SC", "LM", "OB", "UF"):
                recs = []
                frag = self.tree.this.get_frag((fno, rno))
                if frag is None:
                    print(self.tree.this, "FRAG", frag, fno, rno, dent)
                    return
                for n, ptr in enumerate(range(frag.lo, frag.hi, len(frag)//8)):
                    if n == 0:
                        ov.Opaque(self.tree, ptr, width=404).insert()
                    elif n == 1:
                        z = IdxSect(self.tree, ptr).insert()
                        z.dirent = dent
                    else:
                        y = Dummy(self.tree, ptr).insert()
                        w = y.f01.val & 0x1fff
                        recs.append(
                            artifact.Record(
                                low = y.lo + 4,
                                frag = self.tree.this[y.lo+4:y.lo+4+w],
                                key = (len(recs), y.f01.val >> 13, y.f01.val & 0x1fff)
                            )
                        )
                bno = list(z.gno.iter_elided())
                nsec = len(bno)
                if z.f01.val != 2 * nsec:
                    print(self.tree.this, "N NSEC", n, nsec, z.f01.val, fno, rno, dent)
                nsec = z.f01.val // 2
                rno += 1
                for o in range(1, nsec):
                    frag = self.tree.this.get_frag((fno, rno))
                    if frag is None:
                        print(self.tree.this, "FRAG2", frag, o, dent)
                        return

                    rno += 1
                    for p in range(0, len(frag), len(frag)//8):
                        y = Dummy(self.tree, frag.lo + p).insert()
                        w = y.f01.val & 0x1fff
                        recs.append(
                            artifact.Record(
                                low = y.lo + 4,
                                frag = self.tree.this[y.lo+4:y.lo+4+w],
                                key = (len(recs), y.f01.val >> 13, y.f01.val & 0x1fff)
                            )
                        )

                n = 0
                for n, r in enumerate(recs):
                    if len(r) == 0:
                        break

                if n > 0:
                    that = self.tree.this.create(records=recs[:n])
                    that.add_note("pts_type", args=dent.typ.txt.rstrip())

            ns.NameSpace(
                name=dent.nam.txt.rstrip() + "." + dent.typ.txt.rstrip(),
                #parent=self.tree.ns,
                parent=our_ns,
                this=that
            )

    def render(self):
        yield "DirGranule (%s) {" % str(self.key)
        for dent in self.iter_dents():
            yield from ("  " + x for x in dent.render())
        yield "}"

class Dummy(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            f00_=ov.Be16,
            f01_=ov.Be16,
            f02_=ov.Text(400),
        )

    def render(self):
        for x in super().render():
            yield x[:300]

class Pad(Dummy):
    ''' same, different name '''

class PtsTape(ov.OctetView):

    def __init__(self, this):
        if this.top not in this.parents:
            return
        super().__init__(this)

        self.ns = ns.NameSpace(name="", root=this, separator="")

        for i in this.iter_rec():
            if i.key[1] == 0:
                dg = DirGranule(self, i)
                dg.insert()
                if dg.valid():
                    dg.commit()

        if True:
            for lo, hi in self.gaps():
                if hi - lo < 404:
                    continue
                if False:
                    ov.Opaque(self, lo, hi=hi).insert()
                else:
                    y = ov.Array((hi-lo)//404, Pad, vertical=True)(self, lo)
                    y.insert()
                    print(this, "PAD", hex(lo), hex(hi))

        this.add_interpretation(self, self.ns.ns_html_plain)
        self.add_interpretation(title="HexDump", more=True)
