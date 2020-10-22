'''
   DOMUS filesystem
   ----------------

   As described in RCSL-43-GL-7915
'''

import struct
import itertools

import autoarchaeologist

# For convenience, we treat the first six sectors as a different artifact
SEC_OFF = 6

# Sectors before first slice
SLICE_OFF = 32

# Size of sectors
SEC_SIZE = (1 << 9)

class Invalid(Exception):
    ''' Something is not OK '''

def name(b):
    ''' Extract name from words '''
    t = ""
    for i in b:
        if 32 < i < 126:
            t += "%c" % i
        elif not i:
            break
        else:
            raise Invalid("Invalid char in name 0x%02x" % i)
    return t

def make_ranges(i):
    ''' Turn a list of numbers into a list of ranges '''
    for _a, b in itertools.groupby(enumerate(i), lambda pair: pair[1] - pair[0]):
        b = list(b)
        yield b[0][1], b[-1][1]

class IndexBlock():

    '''
        Index block (cf. RCSL-43-GL-7915 p.5)
        -------------------------------------
    '''

    def __init__(self, this, secno, what = ""):
        self.this = this
        self.secno = secno
        b = this[secno]
        if len(b) != 512:
            raise Invalid("Wrong length of Index Block")
        self.what = what
        n = struct.unpack(">H", b[:2])[0]
        if not n:
            raise Invalid("No declared entries in Index Block")
        if n > 127:
            raise Invalid("Too many declared entries in Index Block")
        j = 2
        self.slabs = []
        self.len = 0
        for _i in range(n):
            words = struct.unpack(">2H", b[j:j + 4])
            if not words[0]:
                raise Invalid("Zero count in Index Block")
            self.len += words[0]
            self.slabs.append(words)
            j += 4
        #if max(b[j:]):
        #    raise Invalid("Junk after first declared entries in Index Block")
        if what != "SYS" and self.slabs[0][1] != secno + 1:
            raise Invalid("First sector in IndexBlock does not follow right after")

    def __str__(self):
        return "<IB " + " ".join([str(x) for x in self.slabs]) + ">"

    def __iter__(self):
        for i, j in self.slabs:
            for _x in range(i):
                yield j
                j += 1

    def get_bytes(self, what=None):
        ''' Return the data '''
        b = bytearray()
        for n, i in enumerate(self):
            b += self.this[i]
            if what:
                self.this.set_what(i, n, what)
        return b

    def html_details(self):
        ''' Render for per-sector interpretation '''
        return "Index Block [" + self.what + "] " + " ".join([str(x) for x in self.slabs])

class Kit():
    '''
        Unit description block (cf. RCSL-43-GL-7915 p.5)
        ------------------------------------------------

        Words 6 to 255 are documented as "not used", but
        the first two are conspicuously zero on all extant
        filesystems.
    '''

    def __init__(self, b):
        i = struct.unpack(">6H", b[:12])
        self.sys_slice_size = i[0]
        self.slice_size = i[1]
        self.sectors_on_unit = i[2]
        self.free_sectors = i[3]
        self.first_data_sector = i[4]
        self.top_data_sector = i[5]

        self.n_slices = (self.top_data_sector - self.first_data_sector) // self.slice_size

    def __str__(self):
        return "<Kit " + self.desc() + ">"

    def desc(self):
        ''' internal helper function '''
        t = "s_sl=%2d" % self.sys_slice_size
        t += " slice_size=%d" % self.slice_size
        t += " sectors_on_unit=%4d" % self.sectors_on_unit
        t += " first_data_sector=%d" % self.first_data_sector
        t += " top_data_sector=%4d" % self.top_data_sector
        t += " n_slices=%4d" % self.n_slices
        t += " free_sectors=%4d" % self.free_sectors
        return t

    def html_details(self):
        ''' Render for per-sector interpretation '''
        return "Kit descriptor " + self.desc()


class Map():
    '''
        'MAP' index block (cf. RCSL-43-GL-7915 p.5)
        -------------------------------------------
    '''

    def __init__(self, this, idxblk):
        self.this = this
        self.bytes = idxblk.get_bytes()

    def __getitem__(self, n):
        n = (n - SLICE_OFF) // self.this.kit.slice_size
        return ((self.bytes[SEC_SIZE + (n >> 3)] << (n & 7)) & 0x80) >> 7

    def html_details(self):
        ''' Render for per-sector interpretation '''
        nsl = self.this.kit.n_slices
        nchr = int(nsl + 3) // 4
        s = self.bytes[SEC_SIZE:].hex()[:nchr]
        return "MAP block [" + s + "]"

class File():
    ''' A file associated with a catalog entry '''

    def __init__(self, this, catent, idxblk):
        self.this = this
        self.catent = catent
        self.catent.file = self
        self.bytes = idxblk.get_bytes(self)
        self.a = None

    def commit(self):
        ''' Create an artifact for this file '''
        self.a = autoarchaeologist.Artifact(self.this.this, self.bytes)
        self.a.add_note(self.catent.name)
        self.a.add_note("DOMUS File")

    def html_details(self):
        ''' Render for per-sector interpretation '''
        return "File " + self.catent.get_name()

class CatEnt():
    '''
        Catalog Entry (cf. RCSL-43-GL-7915 p.11)
        ----------------------------------------
    '''
    def __init__(self, this, cat, b):
        self.this = this
        self.cat = cat
        self.b = b
        self.words = struct.unpack(">16H", b)
        self.file = None
        self.drv = None

        self.name = name(b[:5])
        if not self.name.strip():
            raise Invalid("Empty name")

        self.attributes = self.words[6]
        self.length = self.words[7]
        self.idxblk = self.words[8]
        self.allocated = self.words[9]

        self.extra_attr = self.attributes
        def get_attr(n):
            b = 0x8000 >> n
            r = self.extra_attr & b
            self.extra_attr &= ~b
            return r != 0

        self.is_catalog = get_attr(0)
        self.is_sub_catalog = get_attr(1)
        self.is_big = get_attr(9)
        self.is_permanent = get_attr(11)
        self.is_write_protected = get_attr(12)
        self.is_entry_only = get_attr(13)
        self.is_device = get_attr(14)
        self.is_extendable = get_attr(15)

        if self.extra_attr:
            raise Invalid("Surplus attribute 0x%04x" % self.extra_attr)

        if self.is_device:
            if self.cat.parent:
                raise Invalid("Device in subcat")
            self.drv = name(self.b[20:25])
        else:
            for i in (3, 4, 5,):
                if self.words[i]:
                    raise Invalid(self.name + " Word %d is non-zero (0x%04x)" % (i, self.words[i]))
            if self.idxblk < SLICE_OFF:
                raise Invalid(self.name + " Indexblock before data sectors (%d)" % self.idxblk)
            if self.idxblk > self.this.kit.top_data_sector:
                raise Invalid(self.name + " Indexblock past end of unit (%d)" % self.idxblk)

        if self.is_device and self.cat.parent:
            raise Invalid("Device in subcat")

    def __lt__(self, other):
        return self.name < other.name

    def __str__(self):
        return "<CE " + self.catli() + ">"

    def get_file(self, only_perfect = True):
        ''' Get the corresponding file, if any '''

        if self.is_device or self.is_catalog or self.is_sub_catalog:
            return 0

        try:
            fib = IndexBlock(self.this, self.idxblk)
        except Invalid as error:
            #print("DOMUSFS", self.name + " Bad file allocation " + str(error))
            return 0

        for n, sector in enumerate(fib):
            if sector in self.this.what:
                #print("DOMUSFS", self.name + " sector %d (0x%x) already allocated" % (n, sector))
                if only_perfect:
                    return 0

        self.this.set_what(self.idxblk, 0, fib)
        self.file = File(self.this, self, fib)
        return 1

    def commit(self):
        ''' Commit the file, if any '''
        if self.file:
            self.file.commit()

    def get_name(self):
        ''' return name of entry '''
        return (self.cat.name + " " + self.name).strip()

    def catli(self):
        ''' Render entry in CATLI format '''
        t = ""
        t += "%-5s" % self.name
        t += " 0x%02x " % self.b[5]
        t += "C" if self.is_catalog else "."
        t += "S" if self.is_sub_catalog else "."
        t += "B" if self.is_big else "."
        t += "P" if self.is_permanent else "."
        t += "W" if self.is_write_protected else "."
        t += "E" if self.is_entry_only else "."
        t += "D" if self.is_device else "."
        if self.is_device:
            t += "."
            t += "%-5s" % self.drv
            t += " %03o" % self.b[30]
            t += " %03o" % self.b[31]
            t += " %05d" % self.words[14]
            t += " 2'%s" % bin(128 | self.words[13])[-5:]
            t += " 8'%06o" % self.words[7]
            surplus = (3, 4, 5, 8, 9, 12)
        else:
            t += "V" if self.is_extendable else "F"
            t += " %05d" % self.idxblk
            t += " %05d" % self.length
            t += " %05d" % (self.allocated + 1)
            surplus = (3, 4, 5, 10, 11, 12, 13, 14, 15)
        if self.extra_attr:
            t += " {Surplus Attribute: 0x%04x}" % self.extra_attr
        for i in surplus:
            if self.words[i]:
                t += " {%d:0x%04x}" % (i, self.words[i])
        if self.file and self.file.a:
            t += " // " + self.file.a.summary()
        return t

    def html_details(self):
        ''' Render for per-sector interpretation '''
        return self.catli()

class Catalog():
    '''
        Catalog (cf. RCSL-43-GL-7915 p.8)
        ---------------------------------
    '''

    def __init__(self, this, idxblk, parent, catname, complain=True):
        self.this = this
        self.idxblk = idxblk
        self.parent = parent
        self.name = catname
        self.bytes = bytearray()
        self.entries = []
        self.bytes += idxblk.get_bytes(what=self)
        self.this.set_what(self.idxblk.secno, 0, self.idxblk)

        for i in range(0, len(self.bytes), 32):
            b = self.bytes[i:i+32]
            if not max(b):
                continue
            try:
                self.entries.append(CatEnt(this, self, b))
            except Invalid as error:
                if complain:
                    #print("DOMUSFS Bad catalog entry in %s offset 0x%x: " % (self.name, i), error)
                    #print("\t", b.hex())
                    pass

    def __lt__(self, other):
        return len(self.entries) < len(other.entries)

    def __iter__(self):
        yield from sorted(self.entries)

    def get_files(self, only_perfect=True):
        ''' Get the files in this catalog '''
        nsys = 0
        for dirent in self:
            nsys += dirent.get_file(only_perfect)
        return nsys

    def commit(self):
        ''' Commit the files in this catalog '''
        for dirent in self:
            dirent.commit()

    def html_details(self):
        ''' Render for per-sector interpretation '''
        return ("Catalog " + self.name).strip()

class Domus_Filesystem_Class():
    ''' One instance of a DOMUS filesystem '''
    def __init__(self, this, offset, length):
        #print("DOMUSFS", this, offset, length)

        self.offset = offset
        self.length = length
        self.this = this.slice(offset + SEC_OFF * SEC_SIZE, length - SEC_OFF * SEC_SIZE)

        self.this.add_type("DOMUS Filesystem")

        self.what = {}
        self.subcats = []

        self.kit = Kit(self[8])
        self.set_what(8, 0, self.kit)

        mapib = IndexBlock(self, 7, "MAP")
        self.map = Map(self, mapib)
        self.set_what(9, 0, self.map)

        sysib = IndexBlock(self, 6, "SYS")
        self.sys = Catalog(self, sysib, None, "", False)

        nsys = self.sys.get_files()

        if not nsys:
            # Nothing at all in SYS, this is not credible
            self.this.add_comment("Bogus DOMUS filesystem: Nothing in SYS is valid")
            self.this.add_interpretation(self, self.html_as_interpretation_sectors)
            return

        self.this.add_interpretation(self, self.html_as_interpretation_catli)
        self.this.add_interpretation(self, self.html_as_interpretation_sectors)

        self.do_good_subcats()

        self.consistency_check()

        self.sys.commit()
        for subcat in self.subcats:
            subcat.commit()

        self.orphan_subcats()
        self.orphan_files()

    def __getitem__(self, n):
        assert n >= 0
        n -= SEC_OFF
        a = n * SEC_SIZE
        b = a + SEC_SIZE
        assert b <= len(self.this)
        return self.this[a:b]

    def set_what(self, secno, idx, what):
        ''' Account for one sector '''
        i = self.what.get(secno)
        if not i:
            i = []
        i.append((idx, what))
        self.what[secno] = i

    def sectors(self):
        ''' Yield all sector numbers '''
        yield from range(SEC_OFF, self.length // SEC_SIZE)

    def do_good_subcats(self):
        ''' Process subcatalogs found in SYS '''
        for dirent in self.sys:
            if not dirent.is_sub_catalog:
                continue
            idxblk = IndexBlock(self, dirent.idxblk, dirent.name)
            subcat = Catalog(self, idxblk, self.sys, dirent.name, False)
            if subcat.get_files():
                self.subcats.append(subcat)

    def consistency_check(self):
        ''' Check what we found in SYS+subcats against MAP '''
        alloc_orphan = []
        used_free = []
        for sector in range(SLICE_OFF, self.kit.n_slices * self.kit.slice_size):
            free = self.map[sector]
            used_by = self.what.get(sector)
            if free and used_by:
                used_free.append(sector)
            elif not free and not used_by:
                alloc_orphan.append(sector)

        if used_free:
            for i, j in make_ranges(used_free):
                s = set()
                for x in range(i, j + 1):
                    for _a, b in self.what[x]:
                        s.add(b.html_details())

                if i == j:
                    r = " 0x%04x" % i
                else:
                    r = "s 0x%04x-0x%04x" % (i, j)
                self.this.add_comment("Free sector" + r + " used by " + ",".join(sorted(s)))

        if alloc_orphan:
            for i, j in make_ranges(alloc_orphan):
                if i == j:
                    r = " 0x%04x" % i
                else:
                    r = "s 0x%04x-0x%04x" % (i, j)
                self.this.add_comment("Allocated sector" + r + " unaccounted for" )

    def orphan_subcats(self):
        ''' Look for orphan subcatalogs '''
        orphan_subcat = []
        for sector in self.sectors():
            if sector in self.what:
                continue
            idxblk = self.unused_index_block(sector)
            if not idxblk:
                continue
            subcat = Catalog(self, idxblk, self.sys, "ORPHAN_%d" % sector, False)
            #print("DOMUSFS ORPHAN IB", sector, subcat)
            ngood = 0
            for dirent in subcat:
                if dirent.is_catalog:
                    continue
                if dirent.is_sub_catalog:
                    continue
                if dirent.is_device:
                    continue
                gib = self.unused_index_block(dirent.idxblk)
                if gib:
                    ngood += 1
            if ngood:
                orphan_subcat.append([-ngood, subcat])
        for i, subcat in sorted(orphan_subcat):
            #print("DOMUSFS", -i, subcat)

            subcat.get_files(only_perfect=False)
            subcat.commit()
            self.this.add_note("Orphan_SubCat")

            self.subcats.append(subcat)

    def orphan_files(self):
        ''' XXX Incomplete '''
        for sector in self.sectors():
            if sector in self.what:
                continue
            idxblk = self.unused_index_block(sector)
            if not idxblk:
                continue
            #print("DOMUSFS ORPHAN FILE IB", sector)

    def unused_index_block(self, sector):
        ''' Check if this is an index block of unused sectors '''
        try:
            idxblk = IndexBlock(self, sector)
        except Invalid:
            return None
        for sector2 in idxblk:
            if sector2 in self.what:
                return None
        return idxblk

    def html_as_interpretation_sectors(self, fo, _this):
        ''' Sector by sector view '''
        fo.write("<H3>Domus Filesystem - Sectors</H3>\n")
        fo.write("<pre>")
        for sector in self.sectors():
            if sector >= SLICE_OFF and not (sector - SLICE_OFF) % self.kit.slice_size:
                fo.write("\n")
            used_by = self.what.get(sector)
            p = "    %05d 0x%04x" % (sector, sector) + " %d " % self.map[sector]
            if used_by is None:
                fo.write(p + " " + self[sector][:32].hex() + "\n")
            else:
                fo.write(p)
                sep = " "
                for idx, what in used_by:
                    fo.write(sep + what.html_details() + " Sector 0x%x" % idx)
                    sep = ", "
                fo.write("\n")
        fo.write("</pre>")

    def html_as_interpretation_catli(self, fo, _this):
        ''' CATLI-like listing '''
        fo.write("<H3>Domus Filesystem - CATLI</H3>\n")
        fo.write("<pre>\n")
        for dirent in self.sys:
            fo.write("    " + dirent.catli() + "\n")
        fo.write("</pre>\n")
        for subcat in self.subcats:
            fo.write("\n")
            fo.write("<H4>Subcat %s</H4>\n" % subcat.name)
            fo.write("<pre>\n")
            fo.write("\n")
            for dirent in subcat:
                fo.write("    " + dirent.catli() + "\n")
            fo.write("</pre>\n")

def Domus_Filesystem(this):
    ''' Probe for and instantiate DOMUS filesystems '''
    for idx in range(0, 128 * SEC_SIZE, SEC_SIZE):  # Largest seen: 76
        if this[idx:idx+6] not in (
            b'\x00\x01\x00\x02\x00\x08',
            b'\x00\x01\x00\x03\x00\x08',
        ):
            continue

        # Sanity check KIT description
        kit = Kit(this[idx + SEC_SIZE:idx + 2 * SEC_SIZE])
        if kit.sectors_on_unit > len(this) // SEC_SIZE:
            continue
        if kit.sectors_on_unit + (idx // SEC_SIZE) - 7 > len(this) // SEC_SIZE:
            continue
        if kit.sys_slice_size % kit.slice_size:
            continue

        # Sanity check SYS indexblock
        sysidxblk = struct.unpack(">3H", this[idx - SEC_SIZE:6 + idx - SEC_SIZE])
        if not 1 <= sysidxblk[0] <= 10:  # Largest seen: 7
            continue
        if sysidxblk[2] != SLICE_OFF:
            continue


        offset = idx - 7 * SEC_SIZE
        length = kit.sectors_on_unit * SEC_SIZE
        Domus_Filesystem_Class(this, offset, length)
