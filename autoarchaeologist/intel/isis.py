#!/usr/bin/env python3

'''
   Intel ISIS-II floppies

   See: http://bitsavers.org/pdf/intel/ISIS_II/ISIS_internals.pdf

'''

from ..base import octetview as ov
from ..generic import disk
from ..base import namespace

class LinkageBlock(disk.Sector):
    ''' 64 pairs of (track, sector), first two are prev+next '''

    ident = "LinkageBlock"

    def __iter__(self):
        for i in range(64):
            yield self[i]

    def __getitem__(self, idx):
        return self.tree.this[self.lo + idx * 2 + 1], self.tree.this[self.lo + idx * 2]

    def render(self):
        ''' render as list of "track,sect" '''
        yield self.ident + " {" + " ".join("%d,%d" % x for x in self) + "}"

class Linkage():
    ''' A list of LinkageBlocks '''

    def __init__(self, tree, cyl, sect, name):
        self.tree = tree
        self.cyl = cyl
        self.sect = sect
        self.lbs = []
        self.name = name
        while cyl != 0 or sect != 0:
            lblock = LinkageBlock(tree, cyl=cyl, head=0, sect=sect)
            self.tree.picture[(cyl, 0, sect)] = "L"
            if lblock[0] != (0,0) and len(self.lbs) == 0:
                break
            lblock.ident = "LinkageBlock[»%s«,%d]" % (name, len(self.lbs))
            lblock.insert()
            self.lbs.append(lblock)
            cyl, sect = lblock[1]
        self.sectors = []
        for lblock in self.lbs:
            for i in range(2, 64):
                if lblock[i] == (0,0):
                    return
                self.sectors.append(
                    disk.DataSector(self.tree, cyl=lblock[i][0], head=0, sect=lblock[i][1])
                )

    def __iter__(self):
        yield from self.sectors

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
        self.linkage = Linkage(self.tree, *self.linkadr, self.name)
        that = []
        unread = False
        for idx, sec in enumerate(self.linkage):
            sec.insert()
            sec.terse = True
            if sec.is_unread:
                unread = True
                self.tree.picture[(sec.cyl, 0, sec.sect)] = "▒"
            else:
                self.tree.picture[(sec.cyl, 0, sec.sect)] = "·"
            sec.ident = "DataSector[»%s«]" % (self.name,)
            that.append(sec.octets())
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
        for sec in linkage:
            self.tree.picture[(sec.cyl, 0, sec.sect)] = "D"
            for off in range(0, 128, 16):
                i = DirEnt(tree, sec.lo + off, width = 16, namespace=self.namespace)
                i.insert()
                self.dirents.append(i)

    def __iter__(self):
        yield from self.dirents

class IntelIsis(disk.Disk):
    ''' Intel ISIS-II floppy disks '''

    def __init__(self, this):
        if len(this) not in (77*52*128,):
            return

        this.add_note("Intel_ISIS_II")
        super().__init__(
            this,
            [
                [77, 1, 52, 128],
            ],
        )
        this.add_description("Intel_ISIS_II")

        dirlink = Linkage(self, 1, 1, "ISIS.DIR")
        self.dir = Directory(self, dirlink)
        for dirent in self.dir:
            if not dirent.activity and dirent.name != "ISIS.DIR":
                dirent.commit()

        this.add_interpretation(self, self.dir.namespace.ns_html_plain)

        self.picture_legend['D'] = "Directory Sector"
        self.picture_legend['▒'] = "Unread Data Sector"
        self.picture_legend['L'] = "Linkage Sector"
        this.add_interpretation(self, self.disk_picture)

        self.fill_gaps()
        self.add_interpretation(more=True)
