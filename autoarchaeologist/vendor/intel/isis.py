#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Intel ISIS-II floppies

   See: http://bitsavers.org/pdf/intel/ISIS_II/ISIS_internals.pdf

'''

from ...base import octetview as ov
from ...base import namespace

class Link(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            sector_=ov.Octet,
            track_=ov.Octet,
        )
        self.chs = (self.track.val, 0, self.sector.val)

    def render(self):
        yield str(self.chs)

class LinkageBlock(ov.Struct):
    ''' 64 pairs of (track, sector), first two are prev+next '''

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            ary_=ov.Array(64, Link, vertical=False),
            vertical=False,
        )

    def render(self):
        x = list(x.chs for x in self.ary)
        while x and x[-1] == (0,0,0):
            x.pop(-1)
        yield "LinkageBlock {" + " ".join(str(y) for y in x) + "}"

class Linkage():
    ''' A list of LinkageBlocks '''

    def __init__(self, tree, cs_adr, name):
        self.tree = tree
        self.cs_adr = cs_adr
        self.lbs = []
        self.chsl = []
        self.name = name
        chs = (cs_adr[0], 0, cs_adr[1])
        while sum(chs) != 0:
            try:
                frag = tree.this.get_rec(chs)
            except KeyError:
                break
            lblock = LinkageBlock(tree, frag.lo)
            prv = lblock.ary[0]
            nxt = lblock.ary[1]
            if prv.chs != (0,0,0) and len(self.lbs) == 0:
                return
            lblock.ident = "LinkageBlock[»%s«,%d]" % (name, len(self.lbs))
            lblock.insert()
            self.lbs.append(lblock)
            chs = nxt.chs
            for n, i in enumerate(lblock.ary):
                if n < 2:
                    continue
                if sum(i) == 0:
                    break
                self.chsl.append(i.chs)

    def __iter__(self):
        yield from self.chsl

class NameSpace(namespace.NameSpace):
    ''' customized namespace '''

    KIND = "Intel ISIS II file system"

    TABLE = (
        ("l", "activity"),
        ("l", "attribute"),
        ("r", "tail"),
        ("r", "blocks"),
        ("l", "linkadr"),
        ("l", "name"),
        ("l", "artifact"),
    )

    def __init__(self, dirent, *args, **kwargs):
        if dirent:
            super().__init__(dirent.name, *args, **kwargs)
        else:
            super().__init__("", *args, **kwargs)
        self.dirent = dirent

    def ns_render(self):
        ''' table data '''
        return [
            "0x%04x" % self.dirent.activity,
            "0x%04x" % self.dirent.attribute,
            "%d" % self.dirent.tail,
            "%d" % self.dirent.blocks,
            "%d,%d" % self.dirent.linkadr,
        ] + super().ns_render()

class DirEnt(ov.Octets):
    ''' Directory entry '''

    def __init__(self, *args, namespace=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.activity = self[0]
        self.attribute = self[0xa]
        self.tail = self[0xb]
        self.blocks = self[0xc] + self[0xd] * 256
        self.linkadr = (self[0xf], self[0xe])
        self.name = ""
        for i in range(1, 7):
            j = self[i]
            if 32 < j < 126:
                self.name += "%c" % j
            else:
                break
        self.name += "."
        for i in range(7, 10):
            j = self[i]
            if 32 < j < 126:
                self.name += "%c" % j
            else:
                break
        if self.name[-1] == ".":
            self.name = self.name[:-1]
        if not self.activity:
            self.namespace = NameSpace(
                self,
                parent=namespace,
            )
        else:
            self.namespace = None
        self.linkage = None

    def render(self):
        ''' render function '''
        yield " ".join(
            (
            ".DIRENT",
            self.name.ljust(10),
            "%02x" % self.activity,
            "%02x" % self.attribute,
            "%02x" % self.tail,
            "%02x" % self.blocks,
            "%d,%d" % self.linkadr
            )
        )

    def commit(self):
        ''' Commit to this directory entry '''
        self.linkage = Linkage(self.tree, self.linkadr, self.name)
        that = []
        unread = False
        for chs in self.linkage:
            try:
                frag = self.tree.this.get_rec(chs)
                that.append(frag.frag)
                y = ov.Opaque(self.tree, lo=frag.lo, hi=frag.hi).insert()
                y.rendered = "Filedata(%s)" % self.name
            except KeyError:
                unread = True
                that.append(b'_UNREAD_' * (128 // 8))
        if that:
            i = self.tree.this.create(b''.join(that)[:self.blocks * 128 + self.tail - 128])
            self.namespace.ns_set_this(i)
            if unread:
                i.add_note("UNREAD_DATA")

class Directory():
    ''' The directory sectors '''

    def __init__(self, tree, linkage):
        self.tree = tree
        self.linkage = linkage
        self.dirents = []
        self.namespace = NameSpace(None, separator="", root=tree.this)
        for chs in linkage:
            frag = self.tree.this.get_rec(chs)
            for off in range(0, 128, 16):
                i = DirEnt(tree, frag.lo + off, width = 16, namespace=self.namespace)
                i.insert()
                self.dirents.append(i)

    def __iter__(self):
        yield from self.dirents

class IntelIsis(ov.OctetView):
    ''' Intel ISIS-II floppy disks '''

    def __init__(self, this):
        if this.top not in this.parents:
            return

        super().__init__(this)

        de = None
        for frag in this.iter_rec():
            de = DirEnt(self, frag.lo, width=16)
            if de.name == 'ISIS.DIR':
                break
            if frag.key[0] > 1:
                return

        if not de:
            return


        this.add_description("Intel_ISIS_II")

        print(this, "ISIS.DIR", de)

        dirlink = Linkage(self, de.linkadr, "dir")
        print(this, "DIRLINK", dirlink)

        self.dir = Directory(self, dirlink)

        for dirent in self.dir:
            if not dirent.activity and dirent.name != "ISIS.DIR":
                dirent.commit()

        this.add_interpretation(self, self.dir.namespace.ns_html_plain)

        self.add_interpretation(more=True)
