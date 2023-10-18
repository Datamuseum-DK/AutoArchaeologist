#!/usr/bin/env python3

'''
   MCZ floppies

'''

from ..generic import disk
from ..generic import octetview as ov
from .. import namespace
from .. import type_case

class Sector(disk.Sector):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prev_sector = self.up.prev_sector(self.lo)
        self.next_sector = self.up.next_sector(self.lo)

class DataSector(Sector):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.picture('·')
        self.terse = True

    ident = "DataSector"

class Chain():
    def __init__(self, up, chs, stype=None):
        if stype == None:
            stype = Sector
        self.up = up
        self.first = chs
        self.sectors = []
        octets = []
        self.chs = []
        while chs != (255,0,255):
            sect = stype(self.up, *chs)
            self.sectors.append(sect)
            octets.append(sect.this[sect.lo+2:sect.lo+130])
            chs = sect.next_sector
        self.octets = b''.join(octets)

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
            desc.adr.val,
            desc.lastbytes.val,
            desc.created.txt,
            desc.modified.txt,
        ] + super().ns_render()

class TrackSect(ov.Struct):
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            sector_=ov.Octet,
            track_=ov.Octet,
        )

    def render(self):
        yield "%d,%d" % (self.track.val, self.sector.val)

class DescRec(ov.Struct):
    def __init__(self, up, lo):
        super().__init__(
            up,
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
    def __init__(self, up, lo, pnamespace):
        super().__init__(
            up,
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
        sect = Sector(self.up, self.track.val, 0, self.sector.val)
        sect.picture('R')
        self.desc = DescRec(self.up, lo = sect.lo + 2)
        self.desc.insert()

        self.chain = Chain(self.up, sect.next_sector, stype=DataSector)
        self.chain.insert()
        self.chain.picture('·')
        i = 128 - self.desc.lastbytes.val
        if i:
            that = self.up.this.create(bits=self.chain.octets[:-i])
        else:
            that = self.up.this.create(bits=self.chain.octets)
        self.namespace.ns_set_this(that)

class Directory(Chain):
    def __init__(self, up, chs, pnamespace):
        super().__init__(up, chs)
        self.picture("D")
        self.dirents = []
        for sect in self.sectors:
            offset = sect.lo + 2
            while True:
                dent = DirEnt(up, offset, pnamespace)
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
        super().__init__(
            this,
            [ [ len(this) // (32 * 136), 1, 32, 136 ] ],
        )
        this.type_case = self.type_case
        this.add_note("Zilog_MCZ_fs")

        self.namespace = NameSpace(
            name = '',
            root = this,
            separator = "",
        )
        self.label = Label(self, 22, 0, 0).insert()
        self.dir = Directory(self, self.label.next_sector, self.namespace)
        self.dir.insert()
        #print(dir.octets)

        self.fill_gaps()
        this.add_interpretation(self, self.namespace.ns_html_plain)
        this.add_interpretation(self, self.disk_picture)
        self.render()

    def prefix(self, lo, hi):
        ''' Line prefix is hex off set + CHS '''
        i = super().prefix(lo, hi)
        if lo in self.losec:
            j = self.prev_sector(lo)
            prv = "%d,%d" % (j[0], j[2])
            j = self.next_sector(lo)
            nxt = "%d,%d" % (j[0], j[2])
            return i + prv.ljust(9) + nxt.ljust(9)
        return i + " " * 18

    def next_sector(self, lo):
        assert (lo % 136) == 0
        return (self.this[lo + 133], 0, self.this[lo+132])

    def prev_sector(self, lo):
        assert (lo % 136) == 0
        return (self.this[lo + 131], 0, self.this[lo+130])
