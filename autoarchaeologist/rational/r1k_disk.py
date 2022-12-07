#
# See:
#    file:///critter/aa/r1k_dfs/34/344289524.html

import struct

import autoarchaeologist.generic.hexdump as hexdump
import autoarchaeologist.generic.bitview as bv

COLORS = [
   # https://iamkate.com/data/12-bit-rainbow/
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

SECTSHIFT = 13
SECTBITS = (1<<SECTSHIFT)

magic = open("/critter/R1K/DiskHack/_magic", "w")

class OurStruct(bv.Struct):
    def __init__(self, up, lo, **kwargs):
        self.lo = lo
        self.ident = self.__class__.__name__
        super().__init__(up, lo, **kwargs)
        self.bad = False

    def render(self):
        for n, i in enumerate(super().render()):
            if not n:
                yield i + " " + self.ident
            else:
                yield i

class ObjSect(OurStruct):
    def __init__(self, up, lo, **kwargs):
        self.lo = lo
        self.ident = self.__class__.__name__
        self.color = COLORS[2]
        if lo in up.sectors:
            print(up.this, "Sector Already Occupied", up.sectors[lo].ident, self)
        up.sectors[lo] = self
        super().__init__(up, lo=lo, id_kind_=23, id_word_=42, id_vol_=5, id_sect_=24, **kwargs)
        magic.write(self.ident + " 0x%x" % (lo >> SECTSHIFT) + "\n")
        magic.flush()
        lba = lo >> SECTSHIFT
        self.good = self.id_sect == lba
        if up.freemap:
            used = up.freemap[0][0][lba]
            if not used:
                self.ident += "_FREE"
                print("FREE Sector", up.this, kwargs.get("name"), hex(lba))
        if not self.good:
            self.ident += "_BADID"
            print("ID_SECT mismatch", up.this, kwargs.get("name"), hex(lba), hex(self.id_sect), hex(self.id_sect<<SECTSHIFT))

    def __str__(self):
        return "<%06x %s >" % (self.lo >> SECTSHIFT, self.ident)

#################################################################################################

def double_up(obj):
    a = obj.up.this.bitint(obj.lo, width=SECTBITS)
    b = obj.up.this.bitint(obj.lo + SECTBITS, width=SECTBITS)
    if a != b:
        print("Double Fault", type(obj), obj, hex(a^b))
    obj.up.sectors[obj.lo + SECTBITS] = obj

class DoubleObjSect(ObjSect):
    def __init__(self, up, lo, **kwargs):
        super().__init__(up, lo=lo, **kwargs)
        double_up(self)

#################################################################################################

class DataSect():
    def __init__(self, up, lo, **kwargs):
        self.lo = lo
        self.ident = "DataSect"
        t = up.sectors.get(lo)
        if t and not isinstance(t, DataSect):
            print("DATA already occupied", hex(lo >> SECTSHIFT), t.ident)
        else:
            up.sectors[lo] = self
        self.color = COLORS[11]

#################################################################################################

class ArrayHead(OurStruct):
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            name="ArrayHead",
            mark_=32,
            bits_=32,
            dim1_=32,
            dim2_=32,
        )
        if self.dim1 != 1:
            print("BAD array.dim1", hex(lo >> SECTSHIFT), up)

#################################################################################################

class DiskAddress(OurStruct):

    ''' A C/H/S 512B disk-address in the superblock '''

    def __init__(self, up, lo):
        super().__init__(up, lo, name="DiskAddress", flg_=1, cyl_=15, hd_=8, sect_=8)
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
        super().__init__(up, lo, name="Partition", vertical=True, first_=DiskAddress, last_=DiskAddress)

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
        super().__init__(up, lo, name="FreeHead", f0_=110, sector_=24)

class Etwas(OurStruct):
    def __init__(self, up, lo):
        super().__init__(up, lo, name="Etwas", f0_=45, lba_=Lba)

class Etwas45(ObjSect):
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            name="Etwas45",
            vertical=True,
            f0_=-20,
            used_=7,
            tbl_=ArrayHead,
            more=True,
        )
        for n in range(self.used):
            self.addfield("n%02x" % n, -45)
        self.hide_the_rest(SECTBITS)
        self.done()

class Etwas213(ObjSect):
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            name="Etwas213",
            vertical=True,
            more=True,
        )
        while self.hi < lo + SECTBITS - 213:
            self.addfield(None, -213)
        self.done()

class Etwas383(ObjSect):
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            name="Etwas383",
            vertical=True,
            f0_=-21,
            tbl_=ArrayHead,
            more=True,
        )
        while self.hi < lo + SECTBITS - 383:
            self.addfield(None, -383)
        self.done()

class SuperBlock(OurStruct):

    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            name="SuperBlock",
            vertical=True,
            magic_=32,
            at0020_const_=32,
            geometry_=DiskAddress,
            part0_=Partition,
            part1_=Partition,
            part2_=Partition,
            part3_=Partition,
            part4_=Partition,
            at01a0_=16,
            volserial_=VolSerial,
            at0200_const_=128,
            at0280_const_=120,
            at0300_=Lba,
            volname_=VolName,
            at0428_=-39,
            at044f_=-24,
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
        self.addfield(None, -195)
        self.addfield("snapshot1", 28)
        self.addfield(None, -32)
        self.addfield("snapshot2", 28)
        self.addfield(None, -369)
        self.addfield("at15d5_magic", -32)
        self.hide_the_rest(SECTBITS)
        self.done()
        self.up.sectors[lo] = self
        self.up.sectors[lo + SECTBITS] = self
        self.color = COLORS[2]

#################################################################################################

class BadSector():
    color = [ 0xff, 0xff, 0xff ]
    ident = "BadSect"

class BadSectList(OurStruct):
    def __init__(self, up, lo):
        super().__init__(up, lo, name="BadSectList", more=True)
        self.map = []
        for idx in range(SECTBITS // 32):
            if up.this.bitint(self.hi, width=32) == 1<<31:
                break
            self.map.append(
                self.addfield("n%x" % idx, DiskAddress)
            )
        self.hide_the_rest(SECTBITS)
        if len(self.map) > 1:
            self.vertical = True
        self.done()
        up.sectors[lo] = self
        double_up(self)
        self.color = COLORS[6]

class BadSect():
    def __init__(self, up):
        rng = up.sb.part0.lba()
        self.sectors = []
        n = 0
        self.map = {}
        for sect in range(rng[0], rng[1] + 1, 2):
            j = BadSectList(up, sect << SECTSHIFT)
            self.sectors.append(j)
            for i in j.map:
                self.map[i.lba()] = i

        for j in self.map:
            up.sectors[j << SECTSHIFT] = BadSector()

#################################################################################################

class Part1Sect(OurStruct):
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            name="Part1Sect",
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
        up.sectors[lo] = self
        self.color = COLORS[7]

class Part1():
    def __init__(self, up):
        rng = up.sb.part1.lba()
        self.sectors = []
        n = 0
        self.map = []
        for sect in range(rng[0], rng[1] + 1, 1):
            self.sectors.append(
                Part1Sect(up, sect << SECTSHIFT)
            )
            self.map += self.sectors[-1].map
            break


#################################################################################################

class BitMap(OurStruct):
    def __init__(self, up, lo):
        super().__init__(up, lo, name="BitMap", f0_=10, bits_=1024)

class BitMapSect(DoubleObjSect):
    def __init__(self, up, lo, **kwargs):
        super().__init__(
            up,
            lo,
            name="BitMap",
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

    def __getitem__(self, sect):
        i = sect // (1<<10)
        j = sect % (1<<10)
        a = self.map[i].lo + j + 10
        return self.up.this.bitint(a, width=1)


class FreeMapEntry(OurStruct):
    def __init__(self, up, lo):
        super().__init__(up, lo, name="FreeMapEntry", f0_=10, sector_=24)

class FreeMapSect(DoubleObjSect):
    def __init__(self, up, lo, **kwargs):
        super().__init__(
            up,
            lo,
            f44_=32,
            vertical=True,
            more=True,
            **kwargs,
        )
        self.map_sector = []
        n = 0
        while self.hi < lo + SECTBITS - 34:
            self.map_sector.append(
                self.addfield("n%x" % n, FreeMapEntry)
            )
            n += 1
            if not self.map_sector[-1].sector:
                break
        self.hide_the_rest(SECTBITS)
        self.done()
        self.map = []
        for i in self.map_sector:
            if i.sector:
                self.map.append(
                    BitMapSect(up, i.sector << SECTSHIFT)
                )

    def __getitem__(self, sect):
        i = sect // (7<<10)
        j = sect % (7<<10)
        return self.map[i][j]

#################################################################################################

class WorldIdxRec(OurStruct):
    ''' ... '''
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            name="WorldIdxRec",
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
            vertical=True,
            more=True,
            name="WorldIdx",
            s2f_=20,
            used_=5,
            f2_=19 + 45,
            f4_=32,
            f5_=32,
        )
        self.map = []
        for i in range(self.used):
            self.map.append(
                self.addfield("n%x" % i, WorldIdxRec)
            )
        self.hide_the_rest(SECTBITS)
        self.done()

#################################################################################################

class WorldListRec(OurStruct):
    ''' ... '''
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            name="WorldListRec",
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
            vertical=True,
            more=True,
            name="WorldList",
            f1_=18,
            used_=5,
            pad1_=32,
            pad2_=32,
            pad3_=32,
            alloc_=32
        )
        self.worlds = {}
        self.map = []
        for i in range(self.used):
            j = self.addfield("n%02x" % i, WorldListRec)
            self.map.append(j)
            self.worlds[j.world] = j
        self.hide_the_rest(SECTBITS)
        self.done()

#################################################################################################

class WorldPtr(OurStruct):
    ''' ... '''
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            name="WorldPtr",
            f1_=-34,
            f2_=31,
            sector_=24,
        )

class World(ObjSect):
    ''' ... '''
    def __init__(self, up, lo, nbr=-1, name="World"):
        super().__init__(
            up,
            lo,
            vertical=True,
            more=True,
            name=name,
        )
        self.world = nbr
        magic.write(name + " 0x%x" % (lo >> SECTSHIFT) + "\n")
        magic.flush()
        self.addfield("world_kind", 9)
        self.segments = []
        if self.world_kind == 0x1:
            self.addfield(None, 9)
            self.addfield("used", 7)
            self.addfield("obj_array", ArrayHead)
            self.map = []
            for n in range(self.used):
                j = self.addfield("n%02x" % n, WorldPtr)
                self.map.append(j)
            self.hide_the_rest(SECTBITS)
            for i in self.map:
                World(up, i.sector << SECTSHIFT, nbr=self.world, name=name)
        elif self.world_kind == 0x2:
            self.addfield(None, 3)
            self.addfield("used", 7)
            self.addfield("obj_array", ArrayHead)
            for n in range(self.used):
                j = self.addfield("n%02x" % n, Segment)
                self.segments.append(j)
            self.hide_the_rest(SECTBITS)
        else:
            print("TODO", up.this, "WORLD_KIND 0x%x" % self.world_kind, self)
            
        self.done()

        if self.world > 7:
            for i in self.segments:
                i.dive()

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
        self.dst = self.up.sectors.get(self.sector << SECTSHIFT)
        if self.dst:
            self.ident += "_Occupied"

    def render(self):
        i = list(super().render())
        if self.sector:
            t = self.up.sectors.get(self.sector << SECTSHIFT)
            if t:
                i.append(t.ident)
        yield " ".join(i)

class Segment(OurStruct):
    ''' ... '''
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            more=True,
            vertical=True,
            name="Segment",
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
        self.lba = []
        for i in range(10):
            self.lba.append(
                self.addfield("lba%d" % i, Lba)
            )
        self.addfield("tail", 915 + self.lo - self.hi)
        self.done()

    def dive(self):

        if self.col7 < 9 and self.multiplier > 1:
            self.ident += "_Bogus_blk_mult"
            self.bad = True
            print(hex(self.lo>>SECTSHIFT), self.ident, self.col7, self.multiplier)
        elif self.col7 > 10 and self.multiplier == 1:
            self.ident += "_Bogus_blk_mult"
            self.bad = True
            print(hex(self.lo>>SECTSHIFT), self.ident, self.col7, self.multiplier)
        elif self.col7 < 0xa2 and self.multiplier > 0xa2:
            self.ident += "_Bogus_blk_mult"
            self.bad = True
            print(hex(self.lo>>SECTSHIFT), self.ident, self.col7, self.multiplier)

        if self.lba_array.dim2 != 10:
            self.ident += "_Bogus_array"
            self.bad = True
            self.vertical = False
            print(hex(self.lo>>SECTSHIFT), self.ident, self.lba_array.dim2)

        self.map = []
        if self.multiplier != 1:
            j = []
            for i in self.lba:
                if i.flg and i.volume == 1:
                    j.append("%x %x" % (i.flg, i.sector))
                    indir = self.up.sectors.get(i.sector << SECTSHIFT)
                    if not indir:
                        indir = Indir(self.up, i.sector << SECTSHIFT, name="Indir_%x" % self.multiplier)
                    elif indir.name != "Indir_%x" % self.multiplier:
                        print("Indir mismatch", indir.name, hex(self.multiplier))
                    self.map.append(indir)
                else:
                    j.append("-")
            while j and j[-1] == "-":
                j.pop(-1)
            if 0 and "-" in j:
                print("JJ", self, ", ".join(j))
        else:
            j = []
            for i in self.lba:
                if i.flg and i.volume == 1:
                    j.append("%x %x" % (i.flg, i.sector))
                    DataSect(self.up, i.sector << SECTSHIFT)
            # assert len(j) == self.col7


#################################################################################################

class Indir(ObjSect):

    def __init__(self, up, lo, name="Indir"):
        self.color = COLORS[5]
        super().__init__(
            up,
            lo,
            name=name,
            more=True,
            vertical=True,
            f0_=32,
            f1_=32,
            f2_=32,
            multiplier_=30,
            indirhead_=ArrayHead,
        )
        self.bad = False
        self.map = []
        if self.good:
            if self.indirhead.dim2 > 0x289:
                print("INDIR", hex(lo>>SECTSHIFT), ", ".join(self.indirhead.render()))
            else:
                for n in range(self.indirhead.dim2):
                    j = self.addfield("n%02x" % n, Lba)
                    self.map.append(j)
                    if j.dst:
                        self.ident += "_Occupied"
        self.hide_the_rest(SECTBITS)
        self.done()
        if self.multiplier == 1:
            for i in self.map:
                if i.sector and i.volume == 1:
                    DataSect(up, i.sector << SECTSHIFT)
        elif self.multiplier == 0xa2:
            for i in self.map:
                if i.sector and i.volume == 1:
                    Indir(up, i.sector << SECTSHIFT)

#################################################################################################

class R1K_Disk(bv.BitView):

    def __init__(self, this):
        super().__init__(this)
        self.this = this
        self.sectors = {}
        self.freemap = []

        self.sb = SuperBlock(self, 2<<SECTSHIFT)

        self.freemap = [
            [
                FreeMapSect(self, (self.sb.freehead1.sector) << SECTSHIFT, name="FreeMap1"),
            ], [
                FreeMapSect(self, (self.sb.freehead2.sector) << SECTSHIFT, name="FreeMap2"),
            ],
        ]

        self.part0 = BadSect(self)
        self.part1 = Part1(self)

        if 1 and self.sb.worldidx:
            self.worldidx = WorldIdx(self, self.sb.worldidx << SECTSHIFT)
            self.worlds = {}
            for i in self.worldidx.map:
                j = WorldList(self, i.sector << SECTSHIFT)
                self.worlds |= j.worlds
            for i, j in self.worlds.items():
                if j.volume != 1:
                    continue
                World(self, j.sector << SECTSHIFT, nbr=i, name="World_%04d" % i)

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

        # self.brute_force()
        print(this, "render")
        super().render()
        self.make_image()

    def brute_force(self):
        rng = self.sb.part3.lba()
        for sect in range(rng[0], rng[1] + 1, 1):
            if sect<<SECTSHIFT in self.sectors:
                continue
            id_sect = self.this.bitint((sect << SECTSHIFT) + 70, width = 24)
            if id_sect == sect:
                y = ObjSect(self, sect << SECTSHIFT, name="Bruteforce", more=True, f0_=-128)
                y.hide_the_rest(SECTBITS)
                y.done()


    def pad(self, lo, hi):
        if lo & (SECTBITS-1):
            sect = lo >> SECTSHIFT
            hi = min(hi, (sect+1) << SECTSHIFT)
            yield from super().pad(lo, hi)

    def prefix(self, lo, hi):
        return "0x%06x" % (lo >> SECTSHIFT)

    def make_image(self):
        freemap = self.this.filename_for(suf=".map")
        cyl = self.sb.geometry.cyl
        hd = self.sb.geometry.hd
        sec = self.sb.geometry.sect >> 1

        colmap = [
            [self.sb.part0.lba(), COLORS[6]],
            [self.sb.part1.lba(), COLORS[7]],
            [self.sb.part2.lba(), COLORS[8]],
            [self.sb.part3.lba(), COLORS[9]],
            [self.sb.part4.lba(), COLORS[10]],
        ]

        # Make dimmed colors too
        for i in colmap:
            j = i.pop(-1)
            i.append([j, [x >> 1 for x in j]])

        with open(freemap.filename, "wb") as file:
            file.write(b'P6\n')
            file.write(b'%d %d\n' % (cyl, hd * sec))
            file.write(b'255\n')
            for j in range(hd * sec):
                for i in range(cyl):
                    lba = i * hd * sec + j
                    col = [0, 0, 0]
                    used = self.freemap[0][0][lba]
                    what = self.sectors.get(lba<<SECTSHIFT)
                    if what and not used:
                        col = COLORS[4]
                    elif what:
                        col = what.color
                    else:
                        for rng, c1 in colmap:
                            if rng[0] <= lba <= rng[1]:
                                col = c1[used]
                                break
                    file.write(bytes(col))
