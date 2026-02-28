#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Zilog MCZ floppies
   ==================

   Floppy disks from Zilog MCZ systems.

   Usage
   -----

   .. code-block:: none

       from autoarchaeologist.vendor.zilog.mcz_floppy import MczFloppy
       …
       self.add_examiner(MczFloppy)

   Test input
   ----------

   * COMPANY/ZILOG

   Documentation
   -------------

   https://bitsavers.org/pdf/zilog/mcz-1/03-0072-01A_Z80-RIO_Operating_System_Users_Manual_upd_Nov79.pdf

   * Page 41 (pdf p53) - Representation of type and prop
   * Page 116 (pdf p134) - Descriptor Layout
   * Page 125 (pdf p144) - Type and Prop values
   * Appendix J (pdf p232):


'''

from ...base import octetview as ov
from ...base import namespace
from ...base import type_case

class Chs(ov.Struct):
    ''' ... '''

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            s_=ov.Octet,
            c_=ov.Octet,
        )
        self.chs = (self.c.val, 0, self.s.val & 0x1f)
        self.mark = self.s.val >> 5

    def __str__(self):
        if self.mark:
            return "CHS(%d, %d, %d, #%d)" % (self.chs[0], self.chs[1], self.chs[2], self.mark)
        return str(self.chs)

    def render(self):
        yield str(self)

class UnusedSector(ov.Opaque):
    ''' An unused sector '''

    def __init__(self, tree, lo):
        super().__init__(tree, lo, width=136)
        i = set(self.tree.this[self.lo:self.hi])
        if len(i) == 1:
            self.fill = " 0x%02x[%d]" % (self.tree.this[self.lo], self.hi - self.lo)
        else:
            self.fill = None

    def render(self):
        if self.fill is not None:
            yield self.__class__.__name__ + self.fill
        else:
            yield self.__class__.__name__ + ' ┆' + self.tree.this.type_case.decode(self) + '┆'

def repr_type(x):
    ''' Text representation of the type field '''

    l = []
    if x & 0x80:
        l.append('P') # Procedure
    if x & 0x40:
        l.append('D') # Directory
    if x & 0x20:
        l.append('A') # Ascii
    if x & 0x10:
        l.append('B') # Binary
    if x & 0xf:
        l.append("%x" % (x & 0xf))
    #return "0x%02x " % x + "".join(l)
    return "".join(l)

def repr_prop(x):
    ''' Text representation of the property field '''

    l = []
    for n, c in enumerate("WELSRF21"):
        if x & (0x80 >> n):
            l.append(c)
        else:
            l.append('-')
    return "".join(l)

class NameSpace(namespace.NameSpace):
    ''' ... '''

    TABLE = (
        ("r", "reserved"),
        ("r", "file_id"),
        ("l", "dirsect"),
        ("l", "firstsect"),
        ("l", "lastsect"),
        ("l", "type"),
        ("r", "rec.cnt"),
        ("r", "rec.len"),
        ("r", "blk.len"),
        ("l", "prop"),
        ("r", "address"),
        ("r", "lastbytes"),
        ("l", "created"),
        ("l", "modified"),
        ("l", "name"),
        ("l", "artifact"),
    )

    def ns_render(self):
        '''
           See:
              03-0072-01A-Z80_RIO Operating System Users Manual Sep78, pg 116
        '''
        desc = self.ns_priv
        return [
            desc.rsv0,
            desc.file_id,
            desc.dirsect,
            desc.firstsect,
            desc.lastsect,
            repr_type(desc.type.val),
            desc.reccnt.val,
            desc.reclen.val,
            desc.blklen.val,
            repr_prop(desc.prop.val),
            hex(desc.adr.val),
            desc.lastbytes.val,
            desc.created.txt,
            desc.modified.txt,
        ] + super().ns_render()


class DirEnt(ov.Struct):
    ''' NB: Directory entires are variable length '''

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            flag_=ov.Octet,
            more=True,
        )
        self.final = self.flag.val in (0x00, 0xff)
        if not self.final:
            i = self.flag.val & 0x1f
            self.addfield("name", ov.Text(i))
            self.addfield("where", Chs)
        self.done()
        self.namespace = None
        self.chain = None
        self.desc = None

    def commit(self):
        ''' ... '''

        if self.name.txt == "DIRECTORY":
            desc = self.tree.directory
            r = []
        else:
            desc = self.tree.get_descriptor(self.where.chs)
            r = []
            for x in desc.get_chain():
                y = ov.Opaque(self.tree, lo=x.lo, hi=x.hi).insert()
                y.rendered = "DataSector"
                r.append(self.tree.this[x.lo + 2: x.hi - 6])

        trim = desc.reclen.val - desc.lastbytes.val
        while trim and trim >= len(r[-1]):
            trim -= len(r[-1])
            r.pop(-1)
        if trim:
            r[-1] = r[-1][:-trim]
        if r and desc != self.tree.directory:
            that = self.tree.this.create(records=r, define_records=False)
            if desc.problem:
                that.add_note(desc.problem)
            that.add_type("MCZFile", desc=desc)
        else:
            that = None
        self.namespace = NameSpace(
            name = self.name.txt,
            parent = self.tree.namespace,
            priv = desc,
            separator = "",
            this = that,
        )

class DirSec(ov.Struct):
    ''' ... '''

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            am_=Chs,
            f01_=ov.Vector.how(target=DirEnt, terminate=lambda x: (x.final), vertical=True),
            more=True,
            vertical=True,
        )
        if len(self) < 130:
            self.add_field("pad_", 130 - len(self))
        self.add_field("prev", Chs)
        self.add_field("next", Chs)
        self.add_field("crc", 2)
        self.done()

    def commit(self):
        ''' ... '''
        for i in self.f01:
            if not i.final:
                i.commit()

class Descriptor(ov.Struct):
    ''' ... '''

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            am_=Chs,
            rsv0_=4,
            file_id_=2,
            dirsect_=Chs,
            firstsect_=Chs,
            lastsect_=Chs,
            type_=ov.Octet,
            reccnt_=ov.Le16,
            reclen_=ov.Le16,
            blklen_=ov.Le16,
            prop_=ov.Octet,
            adr_=ov.Le16,
            lastbytes_=ov.Le16,
            created_=ov.Text(8),
            modified_=ov.Text(8),
            avail_=88,
            vertical=True,
            more=True,
        )
        self.add_field("prev", Chs)
        self.add_field("next", Chs)
        self.add_field("crc", 2)
        self.done()
        self.problem = False

    def get_chain(self):
        ''' Record the fragments of the chain '''

        # Only to be called once
        assert self.problem is False
        self.problem = None

        sects = []
        chs = self.firstsect.chs
        while chs != (255, 0, 255):
            need = self.reclen.val
            while need:
                x = self.tree.this.get_rec(chs)
                if x is None:
                    self.truncated("sector not found", chs)
                    return sects
                if x[:8] == b'_UNREAD_':
                    u = bytes(x.frag).count(b'_UNREAD_')
                    if u == 17:
                        self.truncated("Unread sector", chs)
                        return sects
                if len(x) != 136:
                    self.truncated("Wrong sector length", len(x), "sector", chs)
                    return sects
                if x[0] & 0x1f != chs[2]:
                    self.truncated(
                        "Wrong address mark",
                        "(%d,0,%d)" % (x[1], x[0]),
                        "instead of",
                        chs,
                    )
                    return sects
                if x[1] != chs[0]:
                    self.truncated(
                        "Wrong address mark",
                        "(%d,0,%d)" % (x[1], x[0]),
                        "instead of",
                        chs,
                    )
                    return sects
                sects.append(x)
                need -= 128
                chs = (chs[0], chs[1], chs[2] + 1)
            chsn = (x[-3], 0, x[-4])
            chs = chsn
        return sects

    def truncated(self, *args):
        ''' Record reason for truncation '''

        self.problem = "Truncated: " + " ".join(str(x) for x in args)

    def __getitem__(self, x):
        return self.sects.__getitem__(x)

    def __iter__(self):
        yield from self.sects.__iter__()

class MCZAscii(type_case.Ascii):
    ''' ... '''

    def __init__(self):
        super().__init__()
        self.set_slug(0x01, ' ', '«soh»')
        self.set_slug(0x0d, ' ', '\n')
        self.set_slug(0x0e, ' ', '«so»')
        self.set_slug(0x0f, ' ', '«si»')
        self.set_slug(0xff, ' ', '«eof»', self.EOF)

class MczFloppy(ov.OctetView):
    ''' ... '''

    type_case = MCZAscii()

    def __init__(self, this):
        if len(this) not in (77*32*136, 78*32*136):
            return

        print(this, self.__class__.__name__)
        this.add_note("MCZ_Fs")
        super().__init__(this)

        this.type_case = self.type_case

        self.namespace = NameSpace(name = '', root = this, separator = "")

        self.directory = self.get_descriptor((22, 0, 0))

        dirsecs = []
        for frag in self.directory.get_chain():
            y = DirSec(self, frag.lo).insert()
            dirsecs.append(y)

        for i in dirsecs:
            i.commit()

        for i in this.iter_rec():
            l = list(self.find(i.lo, i.hi))
            if not l:
                UnusedSector(self, i.lo).insert()

        this.add_interpretation(self, self.namespace.ns_html_plain)
        self.add_interpretation(more=True, elide=0)

    def get_descriptor(self, chs):
        ''' Get chain starting at chs '''

        frag = self.this.get_rec(chs)
        if frag:
            return Descriptor(self, frag.lo).insert()
        return None
