#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license text

'''
   Zilog MCZ floppies
   ~~~~~~~~~~~~~~~~~~
'''

from ...generic import disk
from ...base import octetview as ov
from ...base import namespace
from ...base import type_case

class Sector(disk.Sector):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prev_sector = self.tree.prev_sector(self.lo)
        self.next_sector = self.tree.next_sector(self.lo)

class DataSector(Sector):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.picture('·')
        self.terse = True

    ident = "DataSector"

class Chain():
    def __init__(self, tree, chs, stype=None, reclen=128):
        if stype is None:
            stype = Sector
        self.tree = tree
        self.first = chs
        self.sectors = []
        octets = []
        self.chs = []
        while chs != (255,0,255):
            if chs == (65, 0, 69):
                # __UNREAD__
                self.octets = b''
                return
            done = 0
            while True:
                try:
                    sect = stype(self.tree, *chs)
                except KeyError:
                    print(tree.this, "Could not find chs", chs, self)
                    break
                # print("  c", chs, reclen, sect, hex(sect.lo), sect.next_sector)
                self.sectors.append(sect)
                octets.append(sect.this[sect.lo+2:sect.lo+130])
                done += 128
                if done >= reclen:
                    break
                chs = list(chs)
                chs[2] += 1
            chs = sect.next_sector
        self.octets = b''.join(octets)
        # print("CL", self, len(octets), len(self.octets))

    def insert(self):
        for sect in self.sectors:
            sect.insert()
        return self

    def picture(self, what):
        for sect in self.sectors:
            sect.picture(what)

class Label(Sector):
    ''' ... '''

    ident = "LabelSector"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.picture('L')

class NameSpace(namespace.NameSpace):
    ''' ... '''

    TABLE = (
        ("r", "reserved"),
        ("r", "file_id"),
        ("r", "dirsect"),
        ("r", "firstsect"),
        ("r", "lastsect"),
        ("r", "type"),
        ("r", "rec.cnt"),
        ("r", "rec.len"),
        ("r", "blk.len"),
        ("r", "prop"),
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
        dent = self.ns_priv
        desc = dent.desc
        return [
            desc.rsv0,
            desc.file_id,
            desc.dirsect,
            desc.firstsect,
            desc.lastsect,
            desc.type.val,
            desc.reccnt.val,
            desc.reclen.val,
            desc.blklen.val,
            desc.prop.val,
            hex(desc.adr.val),
            desc.lastbytes.val,
            desc.created.txt,
            desc.modified.txt,
        ] + super().ns_render()

class TrackSect(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            sector_=ov.Octet,
            track_=ov.Octet,
        )

    def render(self):
        yield "%d,%d" % (self.track.val, self.sector.val)

class DescRec(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            rsv0_=4,
            file_id_=2,
            dirsect_=TrackSect,
            firstsect_=TrackSect,
            lastsect_=TrackSect,
            type_=ov.Octet,
            reccnt_=ov.Le16,
            reclen_=ov.Le16,
            blklen_=ov.Le16,
            prop_=ov.Octet,
            adr_=ov.Le16,
            lastbytes_=ov.Le16,
            created_=ov.Text(8),
            modified_=ov.Text(8),
        )

class DirEnt(ov.Struct):
    def __init__(self, tree, lo, pnamespace):
        super().__init__(
            tree,
            lo,
            flag_=ov.Octet,
            more=True,
        )
        if self.flag.val not in (0x00, 0xff):
            i = self.flag.val & 0x1f
            self.addfield("name", ov.Text(i))
            self.addfield("sector", ov.Octet)
            self.addfield("track", ov.Octet)
        self.done()
        self.pnamespace = pnamespace
        self.namespace = None
        self.chain = None
        self.desc = None

    def commit(self):
        self.namespace = NameSpace(
            name = self.name.txt,
            parent = self.pnamespace,
            priv = self,
            separator = "",
        )
        sect = Sector(self.tree, self.track.val, 0, self.sector.val)
        sect.picture('R')
        #print("DE", self.name.txt, sect)
        self.desc = DescRec(self.tree, lo = sect.lo + 2)
        self.desc.insert()

        self.chain = Chain(
            self.tree,
            sect.next_sector,
            stype=DataSector,
            reclen=self.desc.reclen.val
        )
        #print("L", len(self.chain.octets))
        self.chain.insert()
        self.chain.picture('·')
        if len(self.chain.octets) == 0:
            return
        i = self.desc.reclen.val - self.desc.lastbytes.val
        if i == len(self.chain.octets):
            return
        if i:
            that = self.tree.this.create(bits=self.chain.octets[:-i])
        else:
            that = self.tree.this.create(bits=self.chain.octets)
        self.namespace.ns_set_this(that)

class Directory(Chain):
    def __init__(self, tree, chs, pnamespace):
        super().__init__(tree, chs)
        self.picture("D")
        self.dirents = []
        for sect in self.sectors:
            offset = sect.lo + 2
            while True:
                dent = DirEnt(tree, offset, pnamespace)
                self.dirents.append(dent)
                if dent.flag.val in (0x00, 0xff):
                    break
                offset = dent.hi

    def insert(self):
        for dent in self.dirents:
            dent.insert()
        for dent in self.dirents:
            if dent.flag.val in (0x00, 0xff):
                continue
            if dent.name.txt == "DIRECTORY":
                continue
            dent.commit()

class MCZAscii(type_case.Ascii):

    def __init__(self):
        super().__init__()
        self.set_slug(0x01, ' ', '«soh»')
        self.set_slug(0x0d, ' ', '\n')
        self.set_slug(0x0e, ' ', '«so»')
        self.set_slug(0x0f, ' ', '«si»')
        self.set_slug(0xff, ' ', '«eof»', self.EOF)

class MCZRIO(disk.Disk):

    SECTOR_OFFSET = 0

    type_case = MCZAscii()

    def __init__(self, this):
        if len(this) not in (77*32*136, 78*32*136):
            return

        print(this, "MCZRIO")
        this.add_note("Zilog_MCZ_fs")
        super().__init__(
            this,
            [ [ len(this) // (32 * 136), 1, 32, 136 ] ],
        )

        self.picture_legend['L'] = "Label"
        self.picture_legend['R'] = "Descriptor"
        self.picture_legend['D'] = "Directory"

        this.type_case = self.type_case

        self.namespace = NameSpace(name = '', root = this, separator = "")
        self.label = Label(self, 22, 0, 0).insert()
        self.dir = Directory(self, self.label.next_sector, self.namespace)
        self.dir.insert()

        self.fill_gaps()
        this.add_interpretation(self, self.namespace.ns_html_plain)
        this.add_interpretation(self, self.disk_picture)
        self.add_interpretation(more=True)

    def next_sector(self, lo):
        assert (lo % 136) == 0
        return (self.this[lo + 133], 0, self.this[lo+132])

    def prev_sector(self, lo):
        assert (lo % 136) == 0
        return (self.this[lo + 131], 0, self.this[lo+130])
