#
# See:
#    file:///critter/aa/r1k_dfs/34/344289524.html

from pympler import summary
from pympler import muppy

import autoarchaeologist.generic.bitview as bv

COLORS = [
   # https://iamkate.com/data/12-bit-rainbow/
   [ 0x00, 0x00, 0x00],
   [ 0x88, 0x11, 0x77],
   [ 0xaa, 0x33, 0x55],
   [ 0xcc, 0x66, 0x66],
   [ 0xee, 0x99, 0x44],
   [ 0xee, 0xdd, 0x00],
   [ 0x99, 0xdd, 0x55],
   [ 0x44, 0xdd, 0x88],
   [ 0x22, 0xcc, 0xbb],
   [ 0x00, 0xbb, 0xcc],
   [ 0x00, 0x99, 0xcc],
   [ 0x33, 0x66, 0xbb],
   [ 0x66, 0x33, 0x99],
]

COLOR_BAD_SECT = 1
COLOR_BAD_META = 2
COLOR_FREE_SECT = 3
COLOR_FREE_META = 4
COLOR_PART_1 = 5
COLOR_PART_2 = 6
COLOR_WORLD_META = 7
COLOR_SEGMENT_META = 8
COLOR_DATA = 9
COLOR_SUPER_BLOCK = 10
COLOR_METADATA = 11
COLOR_PROBE = 12

SECTSHIFT = 13
SECTBITS = (1<<SECTSHIFT)

try:
    magic_fd = open("/critter/R1K/DiskHack/_magic", "w")
except:
    magic_fd = open("/dev/null", "w")

class OurStruct(bv.Struct):
    def __init__(self, up, lo, **kwargs):
        assert lo != 0

        # Set these early for diags, .done() may happen much later
        self.lo = lo
        self.name = self.__class__.__name__

        super().__init__(up, lo, name=self.name, **kwargs)

    def used_array(self, name, what):
        lo = self.hi - self.lo
        for w in range(2,10):
            if self.up.this.bitint(self.hi + w, width=32) == 0x40:
                break
        fmt = name + '[0x%%0%dx]' % ((w+3) >> 2)
        used = self.addfield(name + "_used", w)
        self.addfield(name + "_mark", 32)
        sze = self.addfield(name + "_size", 32)
        dim1 = self.addfield(name + "_dim1", 32)
        if dim1.val != 1:
            print(self, "bad", name+ ".dim1", hex(dim1.val))
            return
        assert dim1.val == 1
        dim2 = self.addfield(name + "_dim2", 32)
        width = (sze.val - 64) / dim2.val
        lst = list()
        for i in range(used.val):
            before = self.hi
            if isinstance(what, int):
                if what > 0:
                    j = bv.Int(self.up, self.hi, width=what)
                else:
                    j = bv.Bits(self.up, self.hi, width=-what)
            else:
                j = what(self.up, self.hi)
            j.hidden = True
            assert j.hi == before + width
            self.hi = j.hi
            self.fields.append((fmt % i, j))
            lst.append(j)
        setattr(self, name, lst)
        self.hide_the_rest(lo + w + 64 + sze.val)

#################################################################################################

class Probe(OurStruct):
    def __init__(self, up, lo, **kwargs):
        super().__init__(
            up,
            lo=lo,
            pr_kind_=23,
            pr_word_=42,
            pr_vol_=5,
            pr_sect_=24,
            probe_=-128,
            **kwargs
        )
        up.claim_sector(lo >> SECTSHIFT, COLOR_PROBE)
        if not up.color[(lo >> SECTSHIFT) + 1]:
            # check for double storage
            a = up.this.bitint(lo, width=SECTBITS)
            b = up.this.bitint(lo + SECTBITS, width=SECTBITS)
            if a == b:
                print("Is Dup", hex(lo >> SECTSHIFT), self)

class ObjSect(OurStruct):
    def __init__(self, up, lo, color, **kwargs):
        assert lo != 0
        self.lo = lo
        up.claim_sector(lo >> SECTSHIFT, color)
        super().__init__(up, lo=lo, id_kind_=23, id_word_=42, id_vol_=5, id_sect_=24, **kwargs)
        magic_fd.write(self.name + " 0x%x" % (lo >> SECTSHIFT) + "\n")
        magic_fd.flush()
        lba = lo >> SECTSHIFT
        self.good = self.id_sect == lba
        if not self.good:
            print("ID_SECT mismatch", up.this, self, hex(lba), hex(self.id_sect))

#################################################################################################
# Much of the metadata is redundantly stored in two consequtive sectors

def double_up(obj, up, lo, color):
    ''' Claim color for two sectors, supposedly identical '''
    a = up.this.bitint(lo, width=SECTBITS)
    b = up.this.bitint(lo + SECTBITS, width=SECTBITS)
    if a != b:
        print("Double Fault", hex(lo >> SECTSHIFT), type(obj), hex(a^b))
    up.claim_sector(lo >> SECTSHIFT, color)
    up.claim_sector((lo >> SECTSHIFT) + 1, color)

class DoubleObjSect(ObjSect):
    ''' Trivial wrapper for doubled objects '''
    def __init__(self, up, lo, color, **kwargs):
        double_up(self, up, lo, color)
        super().__init__(up, lo=lo, color=color, **kwargs)

#################################################################################################

class DataSect():
    def __init__(self, up, lo, **kwargs):
        assert lo != 0
        self.lo = lo
        up.claim_sector(lo >> SECTSHIFT, COLOR_DATA)

#################################################################################################

class ArrayHead(OurStruct):
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            mark_=32,
            bits_=32,
            dim1_=32,
            dim2_=32,
        )
        if self.mark != 0x40:
            print("BAD array.mark", hex(lo >> SECTSHIFT), up)
        if self.dim1 != 1:
            print("BAD array.dim1", hex(lo >> SECTSHIFT), up)

#################################################################################################

class DiskAddress(OurStruct):

    ''' A C/H/S 512B disk-address in the superblock '''

    def __init__(self, up, lo):
        super().__init__(up, lo, flg_=1, cyl_=15, hd_=8, sect_=8)
        self.lba_ = None

    def lba(self):
        ''' return 1K Logical Block Address, (depending on which field in SB) '''
        if self.lba_ is None:
            if self == self.up.sb.geometry:
                self.lba_ = self.cyl * self.hd * self.sect // 2
            else:
                geom = self.up.sb.geometry
                self.lba_ = ((self.cyl * geom.hd + self.hd) * geom.sect + self.sect) // 2
        return self.lba_

class Partition(OurStruct):
    def __init__(self, up, lo):
        super().__init__(up, lo, vertical=True, first_=DiskAddress, last_=DiskAddress)

    def lba(self):
        ''' Return first+last LBA '''
        return (self.first.lba(), self.last.lba())

class VolSerial(bv.String):
    def __init__(self, up, lo):
        super().__init__(up, lo)
        self.hi = self.lo + 10 * 8

class VolName(bv.String):
    def __init__(self, up, lo):
        super().__init__(up, lo, 32)

class FreeHead(OurStruct):
    def __init__(self, up, lo):
        super().__init__(up, lo, f0_=110, sector_=24)

class Etwas(OurStruct):
    def __init__(self, up, lo):
        super().__init__(up, lo, f0_=45, lba_=Lba)

class Etwas45(DoubleObjSect):
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            color=COLOR_METADATA,
            vertical=True,
            f0_=-20,
            more=True,
        )
        self.used_array("ew45", -45)
        self.hide_the_rest(SECTBITS)
        self.done()

class LogString(bv.String):
    def __init__(self, up, lo):
        super().__init__(up, lo, length = 80)

class LogEntry(OurStruct):
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            f0_=32,
            txt_=LogString,
        )

class LogSect(DoubleObjSect):
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            color=COLOR_METADATA,
            vertical=True,
            f0_=-15,
            more=True,
        )
        self.used_array("entry", LogEntry)
        self.hide_the_rest(SECTBITS)
        self.done()

class LogRec(OurStruct):
    def __init__(self, up, lo):
        super().__init__(up, lo, f0_=32, sector_=24)
        LogSect(up, self.sector << SECTSHIFT)

class SysLog(DoubleObjSect):
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            color=COLOR_METADATA,
            vertical=True,
            f0_=-21,
            more=True,
        )
        self.used_array("logrec", LogRec)
        self.hide_the_rest(SECTBITS)
        self.done()

class Etwas209rec(OurStruct):
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            f0_=13,
            snapshot_=28,
            more=True,
        )
        self.addfield(None, 209 + self.lo - self.hi)
        self.done()

class Etwas209(DoubleObjSect):
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            color=COLOR_METADATA,
            vertical=True,
            f0_=-17,
            more=True,
        )
        self.used_array("ew209", Etwas209rec)
        self.hide_the_rest(SECTBITS)
        self.done()

class Etwas213(DoubleObjSect):
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            color=COLOR_METADATA,
            vertical=True,
            more=True,
        )
        while self.hi < lo + SECTBITS - 213:
            self.addfield(None, -213)
        self.done()

class Etwas383(DoubleObjSect):
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            color=COLOR_METADATA,
            vertical=True,
            f0_=-15,
            more=True,
        )
        self.used_array("ew383", -383)
        self.hide_the_rest(SECTBITS)
        self.done()

class SuperBlock(OurStruct):

    def __init__(self, up, lo):
        self.lo = lo
        self.name = self.__class__.__name__
        double_up(self, up, self.lo, COLOR_SUPER_BLOCK)
        super().__init__(
            up,
            lo,
            vertical=True,
            magic_=32,				# 0x00007fed
            at0020_const_=32,			# 0x00030000
            geometry_=DiskAddress,
            part0_=Partition,
            part1_=Partition,
            part2_=Partition,
            part3_=Partition,
            part4_=Partition,
            at01a0_=16,
            volserial_=VolSerial,
            at0200_const_=128,			# 0
            at0280_const_=120,			# 0x0000000000a4c70f07c00000000000
            at0300_=Lba,
            volname_=VolName,
            volnbr_=5,
            at042d_const_=10,			# 3
            at0437_part3_lba_first_=24,
            at044f_part3_lba_last_=24,
            freehead1_=FreeHead,
            freehead2_=FreeHead,
            at0573_=23,
            at058a_=Etwas,
            at05e7_=Etwas,
            at0644_=Etwas,
            at06a1_=Etwas,
            at06fe_=49,
            more=True,
        )
        for i in range(0x72f, 0x128f, 91):
            self.addfield("at%x" % i, -91)
        self.addfield(None, -69)
        self.addfield("worldidx", 24)		# stage2_ptr
        self.addfield(None, -69)
        self.addfield("at1331", 24)		# stage6_ptr
        self.addfield(None, -74)
        self.addfield("syslog", 24)
        self.addfield(None, -69)
        self.addfield(None, 24)
        self.addfield(None, -8)
        self.addfield("snapshot1", 24)
        self.addfield("reboots", 16)
        self.addfield(None, -20)
        self.addfield("snapshot2", 24)
        self.addfield(None, -305)
        self.addfield(None, -16)
        self.addfield(None, 48)			# Maybe: system-id
        self.addfield("sbmagic", -32)		# 11010011000111000011110000011111
        self.hide_the_rest(SECTBITS)
        self.done()

#################################################################################################
# Known bad sectors are stored in 512-byte CHS in partition 0

class BadSectList(OurStruct):
    def __init__(self, up, lo):
        super().__init__(up, lo, more=True)
        double_up(self, up, lo, COLOR_BAD_META)
        last = None
        for idx in range(SECTBITS // 32):
            if up.this.bitint(self.hi, width=32) != 1<<31:
                j = self.addfield("i%02x" % idx, DiskAddress)
                sect = j.lba()
                if sect != last:
                    up.claim_sector(sect, COLOR_BAD_SECT)
                last = sect
        self.hide_the_rest(SECTBITS)
        self.vertical = last is not None
        self.done()

class BadSect():
    def __init__(self, up):
        rng = up.sb.part0.lba()
        for sect in range(rng[0], rng[1] + 1, 2):
            BadSectList(up, sect << SECTSHIFT)

#################################################################################################
# Unknown purpose

class Part1Sect(OurStruct):
    def __init__(self, up, lo):
        double_up(self, up, lo, COLOR_PART_1)
        super().__init__(
            up,
            lo,
            f0_=30,
            more=True,
        )
        self.map = []
        while self.hi < lo + SECTBITS - 64:
            self.map.append(
                self.addfield(None, -64)
            )
        # self.hide_the_rest(SECTBITS)
        if len(self.map) > 1:
            self.vertical = True
        self.done()

class Part1():
    def __init__(self, up):
        rng = up.sb.part1.lba()
        self.sectors = []
        n = 0
        self.map = []
        for sect in range(rng[0], rng[1] + 1, 2):
            self.sectors.append(
                Part1Sect(up, sect << SECTSHIFT)
            )
            self.map += self.sectors[-1].map

#################################################################################################
# DFS filesystem

class Part2():
    def __init__(self, up):
        rng = up.sb.part2.lba()
        n = 0
        self.map = []
        for sect in range(rng[0], rng[1] + 1):
            up.claim_sector(sect, COLOR_PART_2)
        up.claim_sector(1, COLOR_PART_2)

#################################################################################################

class BitMap(OurStruct):
    def __init__(self, up, lo):
        super().__init__(up, lo, f0_=10, bits_=-1024)

class BitMapSect(DoubleObjSect):
    def __init__(self, up, lo, **kwargs):
        super().__init__(
            up,
            lo,
            color=COLOR_FREE_META,
            flg_=1,
            vertical=True,
            more=True,
            **kwargs
        )
        self.map = []
        for i in range(7):
            self.map.append(
                self.addfield("bitmap%d" % i, BitMap)
            )
        self.hide_the_rest(SECTBITS)
        self.done()

    def claim(self, sect):
        for i in self.map:
            for j in self.up.this.bits(i.bits.lo, hi=i.bits.hi):
                if sect >= len(self.up.color):
                    return sect
                old = self.up.color[sect]
                if j == '0':
                    if old == COLOR_BAD_SECT:
                        print("Bad sector marked free (primary)", hex(sect))
                    else:
                        self.up.claim_sector(sect, COLOR_FREE_SECT)
                sect += 1
        return sect

class FreeMapEntry(OurStruct):
    def __init__(self, up, lo):
        super().__init__(up, lo, f0_=10, sector_=24)

class FreeMapSect(DoubleObjSect):
    def __init__(self, up, lo, primary, **kwargs):
        super().__init__(
            up,
            lo,
            color=COLOR_FREE_META,
            f44_=32,
            vertical=True,
            more=True,
            **kwargs,
        )
        self.map_sector = []
        n = 0
        while self.hi < lo + SECTBITS - 34 and up.this.bitint(self.hi + 10, width=24):
            j = self.addfield("n%02x" % n, FreeMapEntry)
            self.map_sector.append(j)
            n += 1
        self.hide_the_rest(SECTBITS)
        self.done()
        self.map = []
        sect = 0
        for i in self.map_sector:
            j = BitMapSect(up, i.sector << SECTSHIFT)
            self.map.append(j)
            if primary:
                sect = j.claim(sect)

#################################################################################################

class WorldIdxRec(OurStruct):
    ''' ... '''
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            world_=10,
            f2_=31,
            sector_=24,
        )

class WorldIdx(DoubleObjSect):
    ''' ... '''
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            color=COLOR_WORLD_META,
            vertical=True,
            s2f_=20,
            more=True,
        )
        self.used_array("worldidx", WorldIdxRec)
        self.hide_the_rest(SECTBITS)
        self.done()

#################################################################################################

class WorldListRec(OurStruct):
    ''' ... '''
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            world_=10,
            f2_=106,
            f6_=20,
            f5_=44,
            volume_=4,
            sector_=24,
            f4_=1,
        )

class WorldList(DoubleObjSect):
    ''' ... '''
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            color=COLOR_WORLD_META,
            vertical=True,
            f1_=18,
            more=True,
        )
        self.used_array("worldlist", WorldListRec)
        self.hide_the_rest(SECTBITS)
        self.done()
        self.worlds = {}
        for i in self.worldlist:
            self.worlds[i.world] = i

#################################################################################################

class WorldPtr(OurStruct):
    ''' ... '''
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            f1_=-34,
            snapshot_=31,
            sector_=24,
        )

class World(ObjSect):
    ''' ... '''
    def __init__(self, up, lo, nbr=-1):
        super().__init__(
            up,
            lo,
            color=COLOR_WORLD_META,
            vertical=True,
            more=True,
        )
        self.world = nbr
        magic_fd.write(self.name + " 0x%x" % (lo >> SECTSHIFT) + "\n")
        magic_fd.flush()
        self.addfield("world_kind", 9)
        self.segments = []
        if self.world_kind == 0x1:
            self.addfield(None, 9)
            self.used_array("worldptr", WorldPtr)
            self.hide_the_rest(SECTBITS)
            for i in self.worldptr:
                if i.snapshot and i.snapshot <= 0x0013a5a:
                    World(up, i.sector << SECTSHIFT, nbr=self.world)
        elif self.world_kind == 0x2:
            self.addfield(None, 3)
            self.used_array("segment", Segment)
            self.hide_the_rest(SECTBITS)
        else:
            print("TODO", up.this, "WORLD_KIND 0x%x" % self.world_kind, self)

        self.done()

#################################################################################################

class Lba(OurStruct):
    ''' ... '''
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            flg_=20,
            volume_=4,
            sector_=24,
        )

class Extent(OurStruct):
    ''' ... '''
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            flg_=2,
            span_=22,
            sector_=24,
        )

class Segment(OurStruct):
    ''' ... '''
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            more=True,
            vertical=False,
            col2_=10,
            other1_=1,
            col4_=23,
            other2a_=30,
            other2b_=10,
            col9_=8,
            other3_=34,
            col5_=52,
            other5_=22,
            col7_=31,
            other6_=14,
            multiplier_=32,
            lba_array_=ArrayHead,
        )
        assert self.lba_array.dim2 == 10
        self.lba = []
        for i in range(self.lba_array.dim2):
            self.lba.append(
                self.addfield("lba%d" % i, Extent)
            )
        self.addfield("mgr", 8)
        self.addfield("mobj", 32)
        assert 915 + self.lo == self.hi
        self.done()
        t = up.segments.get(self.col5)
        if not t or t.other2a < self.other2a:
            up.segments[self.col5] = self

    def dive(self):

        self.map = []
        if self.multiplier == 1:
            for i in self.lba:
                if i.flg:
                    DataSect(self.up, i.sector << SECTSHIFT)

        elif self.multiplier > 1:
            for i in self.lba:
                if i.flg:
                    indir = Indir(self.up, i.sector << SECTSHIFT)
                    self.map.append(indir)

    def render(self):
        if self.up.segments[self.col5] != self:
            yield "Superseeded_Segment"
        else:
            yield from super().render()

#################################################################################################

class Indir(ObjSect):

    def __init__(self, up, lo):
        self.map = []
        super().__init__(
            up,
            lo,
            color=COLOR_SEGMENT_META,
            more=True,
            vertical=True,
            f0_=32,
            f1_=32,
            f2_=32,
            multiplier_=30,
            indirhead_=ArrayHead,
        )
        if not self.good or self.indirhead.dim2 != 0xa2:
            print(up.this, hex(self.lo >> SECTSHIFT), self, "Bad Indir", self.indirhead.dim2)
        elif self.good:
            for n in range(self.indirhead.dim2):
                j = self.addfield("ind%02x" % n, Extent)
                self.map.append(j)
            self.hide_the_rest(SECTBITS)
        self.done()

        if self.multiplier == 1:
            dowhat=DataSect
        elif self.multiplier == 0xa2:
            dowhat=Indir
        else:
            print(up.this, hex(self.lo >> SECTSHIFT), self, "Bad multiplier", self.multiplier)

        for j in self.map:
            if j.flg:
                assert j.sector
                dowhat(up, j.sector << SECTSHIFT)
            else:
                assert j.span == 0
                assert j.sector == 0

#################################################################################################

class R1K_Disk(bv.BitView):

    def __init__(self, this):
        super().__init__(this)
        self.r1ksys = None

        # Test superblock magic values
        if this.bitint(2<<SECTSHIFT, width=32) != 0x7fed:
            return
        if this.bits((2<<SECTSHIFT) + 0x15d5, width=32) != "11010011000111000011110000011111":
            return

        self.this = this
        self.color = bytearray(len(this)>>10)
        self.freemap = []
        self.segments = {}
        self.worlds = {}
        self.probe()

    def __repr__(self):
        return "<R1KDisk %s>" % str(self.this)

    def claim_sector(self, sect, color):
        # print("CS", sect, color)
        if self.color[sect] not in (0, color):
            print("Sector", hex(sect), "has color", self.color[sect], "but wanted", color)
        self.color[sect] = color

    def probe(self):
        self.sb = SuperBlock(self, 2<<SECTSHIFT)

        self.freemap = [
            FreeMapSect(self, (self.sb.freehead1.sector) << SECTSHIFT, True),
            FreeMapSect(self, (self.sb.freehead2.sector) << SECTSHIFT, False),
        ]

        self.part0 = BadSect(self)
        self.part1 = Part1(self)
        self.part2 = Part2(self)

        if self.sb.worldidx:
            self.worldidx = WorldIdx(self, self.sb.worldidx << SECTSHIFT)
            for i in self.worldidx.worldidx:
                j = WorldList(self, i.sector << SECTSHIFT)
                self.worlds |= j.worlds

        if self.sb.at0300.sector:
            Etwas213(self, self.sb.at0300.sector<<SECTSHIFT)

        if self.sb.at058a.lba.sector:
            Etwas213(self, self.sb.at058a.lba.sector<<SECTSHIFT)

        if self.sb.at05e7.lba.sector:
            Etwas213(self, self.sb.at05e7.lba.sector<<SECTSHIFT)

        if self.sb.at0644.lba.sector:
            Etwas213(self, self.sb.at0644.lba.sector<<SECTSHIFT)

        if self.sb.at06a1.lba.sector:
            Etwas45(self, self.sb.at06a1.lba.sector<<SECTSHIFT)

        if self.sb.at1331:
            Etwas383(self, self.sb.at1331<<SECTSHIFT)

        if self.sb.at13f0:
            Etwas209(self, self.sb.at13f0<<SECTSHIFT)

        if self.sb.syslog:
            SysLog(self, self.sb.syslog<<SECTSHIFT)

        found_disk(self)

    def need_volumes(self):
        vols = set()
        for j in self.worlds.values():
            vols.add(j.volume)
        return vols

    def brute_force(self):
        rng = self.sb.part3.lba()
        for sect in range(rng[0], rng[1] + 1, 1):
            if not self.color[sect]:
                id_sect = self.this.bitint((sect << SECTSHIFT) + 70, width = 24)
                if id_sect == sect:
                    Probe(self, sect << SECTSHIFT)

    def pad(self, lo, hi):
        if lo & (SECTBITS-1):
            sect = lo >> SECTSHIFT
            hi = min(hi, (sect+1) << SECTSHIFT)
            yield from super().pad(lo, hi)

    def prefix(self, lo, hi):
        return "0x%06x" % (lo >> SECTSHIFT)

    def picture(self):
        imgfile = self.this.filename_for(suf=".map")
        cyl = self.sb.geometry.cyl
        hd = self.sb.geometry.hd
        sec = self.sb.geometry.sect >> 1

        with open(imgfile.filename, "wb") as file:
            file.write(b'P6\n')
            file.write(b'%d %d\n' % (cyl, hd * sec))
            file.write(b'255\n')
            for j in range(hd * sec):
                lba = j
                for i in range(cyl):
                    what = self.color[lba]
                    col = COLORS[what]
                    file.write(bytes(col))
                    lba += hd * sec

#################################################################################################

class R1K_System():
    def __init__(self, ident):
        self.ident = ident
        self.disks = [None, None, None, None, None]

    def __str__(self):
        return "Sys_%x" % self.ident

    def __getitem__(self, idx):
        return self.disks[idx]

    def add_disk(self, disk):
        assert isinstance(disk, R1K_Disk)
        vol = disk.sb.volnbr
        assert not self.disks[vol]
        self.disks[vol] = disk
        disk.r1ksys = self
        print(disk, "Is vol", vol, "of", self)
        self.complete()

    def complete(self):
        if not self.disks[1]:
            print(self, "Waiting for Vol", 1)
            return
        vols = self[1].need_volumes()
        for i in vols:
            if not self[i]:
                print(self, "Waiting for Vol", i)
                return
        print(self, "Got all volumes")
        self.spelunk()

        for i in self.disks:
            if i:
                print(i, "Render")
                i.render()
                print(i, "Picture")
                i.picture()

    def spelunk(self):
        print(self, "Spelunking worlds")
        #sum = summary.summarize(muppy.get_objects())
        #summary.print_(sum)
        for i, j in self[1].worlds.items():
            # print("doing World", i, j.volume, hex(j.sector))
            World(self[j.volume], j.sector << SECTSHIFT, nbr=i)
        # return
        print(self, "Spelunking segments")
        #sum = summary.summarize(muppy.get_objects())
        #summary.print_(sum)
        for i in self.disks:
            if not i:
                continue
            print(i, len(i.segments), "Segments")
            for j in i.segments.values():
                j.dive()
            i.brute_force()
        print(self, "Spelunking done")
        #sum = summary.summarize(muppy.get_objects())
        #summary.print_(sum)

systems = {}

def found_disk(disk):
    ident = disk.sb.at15a5
    r1ksys = systems.setdefault(ident, R1K_System(ident))
    r1ksys.add_disk(disk)
