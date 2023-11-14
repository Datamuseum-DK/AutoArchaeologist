#!/usr/bin/env python3

'''
   CP/M filesystems
   ~~~~~~~~~~~~~~~~

   With big hat-tip to CPMTOOLS

'''

from ..base import octetview as ov
from ..base import namespace
from ..base import type_case
from ..generic import floppy

class DirEntFlags():
    def __init__(self, flags):
        self.flags = flags

    def __getitem__(self, idx):
        return self.flags[idx]

    def __str__(self):
        return " ".join(self.render())

    def render(self):
        yield "[" + ",".join(str(x) for x in self.flags) + "]"

class DirEnt(ov.Struct):

    def __init__(self, tree, lo, width):
        super().__init__(
            tree,
            lo,
            status_=ov.Octet,
            name_=ov.Text(11),
            xl_=ov.Octet,
            bc_=ov.Octet,
            xh_=ov.Octet,
            rc_=ov.Octet,
            more=True,
        )
        if width == 8:
            self.add_field("al", ov.Array(16, ov.Octet))
        else:
            self.add_field("al", ov.Array(8, ov.Le16))
        self.done()
        flags = []
        name = bytearray()
        for i in self.name:
            flags.append(i >> 7)
            name.append(i & 0x7f)
        self.flags = DirEntFlags(flags)
        self.fields.append(("flags", self.flags))
        self.name.valid, self.name.txt = self.tree.FILENAME_TYPECASE.is_valid(name)

        self.filename = self.name.txt[:8].rstrip()
        i = self.name.txt[8:].rstrip()
        if i:
            self.filename += "." + i
        self.extent = ((self.xh.val & 0x3f) << 4) | (self.xl.val & 0x0f)

    def looks_sane(self, probable_blocks=0):
        if self.status.val >= 0x10:
            return False
        if probable_blocks > 0 and max(x.val for x in self.al) > probable_blocks:
            return False
        if self.xl.val & 0xe0:
            return False
        if self.xh.val & 0xc0:
            return False

        i = [x.val for x in self.al]
        while i and i[-1] == 0:
            i.pop(-1)
        if 0 in i:
            return False

        if self.name.txt[:1] == ' ':
            return False

        if not self.name.valid:
            return False
        return True

class UnusedDirEnt(ov.Opaque):
    ''' Unused Dirent '''
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            width=0x20,
            rendered="UnusedDirEnt {status=0xe5}"
        )

class DataBlock(ov.Opaque):
    ''' Data Block'''
    def __init__(self, tree, lo, width, dirent, offset):
        super().__init__(
            tree,
            lo,
            width=width,
            #rendered="DataBlock {»%s« @0x%x}" % (dirent.filename, offset)
            rendered="DataBlock {»%s«}" % dirent.filename
        )

class CpmNameSpace(namespace.NameSpace):
    ''' ... '''

    def ns_render(self):
        if self.ns_this:
             l = [len(self.ns_this)]
        else:
             l = ['-']
        return l + super().ns_render()

    TABLE = [
        ["r", "bytes"],
        ["l", "name"],
        ["l", "artifact"],
    ]

class SectorData(ov.Octets):
    ''' ... '''

    def render(self):
        octets = self.this[self.lo:self.hi]
        tcase = self.this.type_case.decode(octets)
        yield "SectorData   ┆" + tcase + "┆"

class CpmFileNameTypeCase(type_case.TypeCase):
    def __init__(self):
        super().__init__("CP/M Filenames")
        for n, slug in type_case.ascii:
            if 0x20 <= n <= 0x7e and "%c" % n not in "<>.;:=?*_":
                self.slugs[n] = slug

cpm_filename_typecase = CpmFileNameTypeCase()

class CpmFileSystem(ov.OctetView):
    ''' Base class '''

    NAME = "IBM S/34, Interleave 2"
    ZONE = floppy.Zone(1, 76, 0, 0, 1, 26, 128)
    INTERLEAVE = ZONE.interleave(2)
    PROBE = None

    BLOCK_SIZE = 1024
    N_DIRENT = 64

    FILENAME_TYPECASE = cpm_filename_typecase

    def getsect(self, chs):
        c,h,s = chs
        s = self.INTERLEAVE[s + self.ZONE.first_sect]
        try:
            return self.this.get_rec((c, h, s))
        except KeyError:
            print(self.this, self.NAME, "Missing sector ?", (c, h, s))
            return None

    def __init__(self, this):
        super().__init__(this)
        #print(this, self.NAME)

        self.ns = CpmNameSpace(
            name = '',
            root = this,
            separator = '',
        )
        self.ns.KIND = "Namespace CP/M Filesystem - " + self.NAME
        this.add_type(self.__class__.__name__)

        nblock = self.ZONE.sectors * self.ZONE.sector_length // self.BLOCK_SIZE
        #print(this, "SZ", nblock, self.BLOCK_SIZE, self.ZONE)
        if nblock <= 256:
            al_width = 8
        else:
            al_width = 16

        dirsect = (self.N_DIRENT * 32) // self.ZONE.sector_length
        self.dirents = []
        n = 0
        for dirsec in range(0, dirsect):
            chs = self.sn2chs(dirsec)
            rec = self.getsect(chs)
            if rec is None:
                print(this, self.NAME, "Missing DIRSECT", chs)
                n += self.ZONE.sector_length // 32
                continue
            for adr in range(rec.lo, rec.lo + len(rec.frag), 32):
                assert n < self.N_DIRENT
                if self.this[adr] in (0x21, 0xe5):
                    UnusedDirEnt(self, adr).insert()
                else:
                    de = DirEnt(self, adr, al_width).insert()
                    de.idx = n
                    self.dirents.append(de)
                n += 1
        if al_width == 8:
            i = set()
            j = set()
            for dirent in self.dirents:
                if dirent.status.val > 0x0f:
                    continue
                for n, al in enumerate(dirent.al):
                    if n & 1:
                        j.add(al.val)
                    else:
                        i.add(al.val)
            j = sum(j) / len(j)
            i = sum(i) / len(i)
            if j * 10 < i:
               #print(this, self.NAME, "DAL8", i, j)
               return
        else:
            for dirent in self.dirents:
                if not dirent.looks_sane():
                    continue
                for al in dirent.al:
                    if al.val > 10 * nblock:
                        #print(this, self.NAME, "DAL16", al.val, nblock, dirent)
                        return
 

        this.add_type("CP/M Filesystem - " + self.NAME)
        this.add_interpretation(self, self.ns.ns_html_plain)

        filenames = {}
        for dirent in self.dirents:
            if dirent.status.val >= 0x10:
                continue
            if not dirent.name.valid:
                print(self.NAME, this, "Invalid filename", dirent.idx, hex(dirent.lo), dirent)
                continue
            if not dirent.looks_sane():
                print(self.NAME, this, "Improbable dirent", dirent.idx, hex(dirent.lo), dirent)
                continue
            if dirent.filename == '':
                print(self.NAME, this, "Empty filename ??", dirent.idx, hex(dirent.lo), dirent)
                continue
            i = filenames.setdefault(dirent.filename, [])
            i.append(dirent)

        for fn, dents in filenames.items():
            dents.sort(key=lambda x: x.extent)
            b = bytearray()
            for dirent in dents:
                off = len(b)
                for blkno in dirent.al:
                    if blkno.val == 0:
                        break
                    for i in self.getblock(blkno.val):
                        if not i:
                            break
                        y = DataBlock(
                            self,
                            i.lo,
                            len(i.frag),
                            dirent,
                            len(b)
                        ).insert()
                        b += i.frag
                l = dirent.rc.val * 128
                if dirent.bc.val:
                    l += dirent.bc.val - 128
                j = len(b) - off
                if j > 0:
                    l += 16384 * ((j-1) // 16384)
                l += off
            if len(b) == 0:
                continue
            if l > 0 and l <= len(b):
                y = this.create(bits = b[:l])
                ns = CpmNameSpace(
                     name = dirent.filename,
                     parent = self.ns,
                     this = y
                )
            else:
                print(self.this, self.NAME, "??  len", l, "of", len(b), dirent)

        self.add_interpretation(title="OctetView - " + self.NAME)

    def sn2chs(self, sn):
        sector = sn % self.ZONE.n_sect
        head = sn // self.ZONE.n_sect
        cyl = self.ZONE.first_cyl + head // self.ZONE.n_head
        head %= self.ZONE.n_head
        return (cyl, head, sector)

    def getblock(self, lbn):
        sn = lbn * (self.BLOCK_SIZE // self.ZONE.sector_length)
        for psect in range(self.BLOCK_SIZE // self.ZONE.sector_length):
            cyl, head, sector = self.sn2chs(sn)
            # print("SN", "lbl", lbn, "psect", psect, "sn", sn, "chs", cyl, head, sector)
            yield self.getsect((cyl, head, sector))
            sn += 1

class CpmFileSystemRc702a(CpmFileSystem):
    '''
       Det alm. 5.25 RC702 format:
        0/0 250 kbps SD  16x128
        0/1 250 kbps SD  16x256
        1/0 250 kbps DD  9x512
       72 tracks(36/36), 662 sectors
    '''

    NAME = 'RC702 5¼ DD(a)"'
    ZONE = floppy.Zone(2, 35, 0, 1, 1, 9, 512)
    INTERLEAVE = ZONE.interleave(2)
    BLOCK_SIZE = 2048
    N_DIRENT = 128

class CpmFileSystemRc702b(CpmFileSystemRc702a):
    ''' ... '''

    NAME = 'RC702 5¼ DD(b)"'
    ZONE = floppy.Zone(3, 35, 0, 1, 1, 9, 512)
    INTERLEAVE = ZONE.interleave(2)
    N_DIRENT = 128

class CpmFileSystemRc702c(CpmFileSystemRc702a):
    ''' ... '''

    NAME = 'RC702 5¼ DD(c)"'
    ZONE = floppy.Zone(4, 35, 0, 1, 1, 9, 512)
    INTERLEAVE = ZONE.interleave(2)
    N_DIRENT = 128

class CpmFileSystemRc703(CpmFileSystem):
    '''
       RC703 5.25 QD-drev:
        0/0 250 kbps SD  10x512
       160 tracks(80/80), 1600 sectors

       30003615  looks like more dirents than 128
    '''

    NAME = 'RC703 5¼" QD'
    ZONE = floppy.Zone(2, 79, 0, 1, 1, 10, 512)
    INTERLEAVE = ZONE.interleave(2)
    BLOCK_SIZE = 2048
    N_DIRENT = 240

class CpmFileSystemRc702_8ss(CpmFileSystem):
    '''
       RC702 8" single-sided:
        0/0 500 kbps SD  26x128
       77 tracks(77/0), 2002 sectors
    '''

    NAME = 'RC702 8" SS'
    ZONE = floppy.Zone(4, 76, 0, 0, 1, 26, 128)
    INTERLEAVE = ZONE.interleave(1)

class CpmFileSystemRc702_8ds(CpmFileSystem):
    '''
       RC702 8"-diskette
        0/0 500 kbps SD  26x128
       0/1 500 kbps SD  26x256
       1/0 500 kbps DD  15x512
       154 tracks(77/77), 2332 sectors
    '''

    NAME = 'RC702 8" DS'
    ZONE = floppy.Zone(2, 76, 0, 1, 1, 15, 512)
    INTERLEAVE = ZONE.interleave(4)
    BLOCK_SIZE = 2048
    N_DIRENT = 128

class CpmFileSystem_Jet80(CpmFileSystem):
    ''' JET80 '''

    NAME = "JET80"
    ZONE = floppy.Zone(1, 79, 0, 1, 1, 5, 1024)
    INTERLEAVE = ZONE.interleave(1)
    BLOCK_SIZE = 2048
    N_DIRENT = 128

class CpmFileSystem_James_2(CpmFileSystem):
    ''' James '''

    NAME = "James(2)"
    ZONE = floppy.Zone(1, 79, 0, 1, 1, 9, 512)
    INTERLEAVE = ZONE.interleave(1)
    BLOCK_SIZE = 2048
    N_DIRENT = 64

class CpmFileSystem_James_1(CpmFileSystem_James_2):
    ''' James '''
    # I think this format fills head=0 on all cyls, then head=1 on all cyls ?
    # See Bits:30003608
    N_HEAD = 1

class CpmFileSystem_Piccoline(CpmFileSystem):
    ''' Piccoline '''

    NAME = "Piccoline"
    ZONE = floppy.Zone(2, 76, 0, 1, 1, 8, 1024)
    INTERLEAVE = ZONE.interleave(1)
    BLOCK_SIZE = 2048
    N_DIRENT = 288

class CpmFileSystem_CR8(CpmFileSystem):
    ''' CR7/8 '''

    NAME = "CR7/8"
    ZONE = floppy.Zone(1, 77, 0, 1, 1, 16, 256)
    # See ⟦97d59898b⟧
    INTERLEAVE = [0, 1, 2, 5, 6, 9, 10, 13, 14, 3, 4, 7, 8, 11, 12, 15, 16]
    BLOCK_SIZE = 2048
    N_DIRENT = 128

class CpmFileSystem_CR16(CpmFileSystem):
    ''' CR16 '''

    NAME = "CR16"
    ZONE = floppy.Zone(1, 76, 0, 1, 1, 8, 512)
    # see ⟦f66f0fa9c⟧
    INTERLEAVE = ZONE.interleave(1)
    BLOCK_SIZE = 2048
    N_DIRENT = 64

    def sn2chs(self, sn):
        sector = sn % self.ZONE.n_sect
        track = sn // self.ZONE.n_sect
        cyl = self.ZONE.first_cyl + track
        head = 0
        if cyl > self.ZONE.last_cyl:
            # ... and back the other side
            head = 1
            cyl = 2 * self.ZONE.n_cyl - (cyl - 1)
        return (cyl, head, sector)


class CpmFileSystem_Comet1(CpmFileSystem):
    ''' ICL Comet '''

    NAME = "Comet (1)"
    ZONE = floppy.Zone(2, 39, 0, 0, 1, 10, 512)
    INTERLEAVE = ZONE.interleave(3)
    BLOCK_SIZE = 1024
    N_DIRENT = 64

class CpmFileSystem_Comet2(CpmFileSystem):
    ''' ICL Comet '''

    NAME = "Comet (2)"
    ZONE = floppy.Zone(1, 79, 0, 1, 1, 10, 512)
    INTERLEAVE = ZONE.interleave(3)
    BLOCK_SIZE = 4096
    N_DIRENT = 64

class CpmFileSystem_Mostek(CpmFileSystem):
    ''' Mostek '''

    NAME = "Mostek"
    ZONE = floppy.Zone(2, 76, 0, 0, 1, 26, 128)
    INTERLEAVE = ZONE.interleave(6)

    BLOCK_SIZE = 1024
    N_DIRENT = 64

def probe_butler(this, geom):
    if len(geom.c) < 100:
        return False
    return True

class CpmFileSystem_Butler1(CpmFileSystem):
    ''' ICL Comet '''

    NAME = "Butler (1)"
    ZONE = floppy.Zone(1, 79, 0, 1, 1, 10, 512)
    INTERLEAVE = ZONE.interleave(3)
    BLOCK_SIZE = 2048
    N_DIRENT = 64

class CpmFileSystem_Butler2(CpmFileSystem):
    ''' Butler '''

    NAME = "Butler (2)"
    PROBE = probe_butler
    ZONE = floppy.Zone(2, 179, 0, 1, 1, 10, 512)
    BLOCK_SIZE = 2048
    N_DIRENT = 128
    INTERLEAVE = ZONE.interleave(3)

    def sn2chs(self, sn):
        sector = sn % self.ZONE.n_sect
        track = sn // self.ZONE.n_sect
        cyl = self.ZONE.first_cyl + track
        head = track % 2
        return (cyl, head, sector)

def HasDirents(ovt, rec):
    for ptr in range(rec.lo, rec.lo + 128, 32):
        de = DirEnt(ovt, rec.lo, width=8)
        if de.looks_sane():
            return de
        de = DirEnt(ovt, rec.lo, width=16)
        if de.looks_sane():
            return de
    return None

class CpmFileSystem():

    FILENAME_TYPECASE = cpm_filename_typecase

    LAYOUTS = [
        CpmFileSystem,
        CpmFileSystem_Jet80,
        CpmFileSystem_James_2,
        CpmFileSystem_Piccoline,
        CpmFileSystemRc702a,
        CpmFileSystemRc702b,
        CpmFileSystemRc702c,
        CpmFileSystemRc703,
        CpmFileSystemRc702_8ss,
        CpmFileSystemRc702_8ds,
        CpmFileSystem_CR8,
        CpmFileSystem_CR16,
        CpmFileSystem_Comet1,
        CpmFileSystem_Comet2,
        CpmFileSystem_Butler1,
        CpmFileSystem_Butler2,
        CpmFileSystem_Mostek,
    ]

    def __init__(self, this):
        if this.top not in this.parents:
            return
        # print(self.__class__.__name__, this, "?")

        ovt = ov.OctetView(this)
        ovt.FILENAME_TYPECASE = self.FILENAME_TYPECASE

        de = None
        key = None
        for rec in this.iter_rec():
            if rec.key[2] > 5:
                continue
            if rec.key[0] > 5:
                return
            de = HasDirents(ovt, rec)
            if de:
                break

        if de is None:
            #print(this, self.__class__.__name__, "No Dirent", this.descriptions)
            return

        self.fdgeom = floppy.Geometry(this)
        candidates = []
        for cand in self.LAYOUTS:
            if cand.PROBE:
                if cand.PROBE(this, self.fdgeom):
                    candidates.append(cand)
                continue
            if cand.ZONE.sector_length != len(rec.frag):
                continue
            if cand.ZONE.first_cyl != rec.key[0]:
                continue
            if cand.ZONE.first_sect > rec.key[2]:
                continue
            if not self.fdgeom.fits(cand.ZONE):
                continue
            candidates.append(cand)
        #print()
        self.fdgeom.find_zones()
        if not candidates:
           print(this, "CP/M Desc", this.descriptions)
           print(this, "CP/M Type", this.types)
           print(this, "CP/M DE", rec.key, len(rec.frag), de)
           print(this, "CP/M Geom", self.fdgeom.zones)
        if not candidates:
           return

        for cand in candidates:
            cand(this)
