

'''
   CR80 Filesystem type 2

   See https://ta.ddhf.dk/wiki/Bits:30004479
'''

import autoarchaeologist
from autoarchaeologist.generic import disk
import autoarchaeologist.generic.octetview as ov

N_SECT = 26
N_TRACK = 77
SECTOR_LENGTH = 128

L_SECTOR_SHIFT = 9

class CR80_FS2Interleave():

    def __init__(self, this):
        if not this.top in this.parents:
            return
        if len(this) != N_SECT * N_TRACK * SECTOR_LENGTH:
            return
        if this[0x10] != 0xff or this[0x11] != 0xfd:
            return

        img = bytearray(len(this))

        ileave = [
                  0,  2,  4,  6,  8, 10, 12, 14, 16, 18, 20, 22, 24,
                  1,  3,  5,  7,  9, 11, 13, 15, 17, 19, 21, 23, 25,
        ]
        for cyl in range(N_TRACK):
            for sect in range(N_SECT):
                pcyl = cyl
                psect = ileave[(cyl * 0 + sect + N_SECT) % N_SECT]
                padr = pcyl * N_SECT * SECTOR_LENGTH + psect * SECTOR_LENGTH
                octets = this[padr:padr + SECTOR_LENGTH]
                lba = cyl * N_SECT * SECTOR_LENGTH + sect * SECTOR_LENGTH
                for n, i in enumerate(octets):
                    img[lba + n] = i ^ 0xff
        that = this.create(bits=img)
        that.add_type("ileave2")
        this.add_interpretation(self, this.html_interpretation_children)

class NameSpace(autoarchaeologist.NameSpace):
    ''' ... '''

    TABLE = (
        ("r", "bfd"),
        ("r", "ok"),
        ("r", "-"),
        ("r", "-"),
        ("r", "type"),
        ("r", "length"),
        ("r", "-"),
        ("r", "nsect"),
        ("r", "-"),
        ("r", "areasz"),
        ("r", "sector"),
        ("r", "-"),
        ("r", "-"),
        ("r", "flags"),
        ("l", "name"),
        ("l", "artifact"),
    )

    def ns_render(self):
        sfd = self.ns_priv
        bfd = sfd.bfd
        return [
            sfd.file.val,
            bfd.ok.val,
            bfd.bfd01.val,
            bfd.bfd02.val,
            hex(bfd.type.val),
            bfd.length.val,
            bfd.bfd05.val,
            bfd.nsect.val,
            bfd.bfd07.val,
            bfd.areasz.val,
            bfd.sector.val,
            bfd.bfd0a.val,
            bfd.bfd0b.val,
            bfd.flags.val,
        ] + super().ns_render()

class HomeBlock(ov.Struct):
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            vertical=False,
            label_=ov.Text(16),
            magic_=ov.Be16,
            f00_=ov.Be16,
            f01_=ov.Be16,
            f02_=ov.Be16,
            f03_=ov.Be16,
            f04_=ov.Be16,
            nsect_=ov.Be16,
            f06_=ov.Be16,
            f07_=ov.Be16,
            f08_=ov.Be16,
            more=False,
        )
        #self.done(pad=0x200)
        self.up.set_picture('H', lo=lo)

    def render(self):
        yield from super().render()

class IndexBlock(ov.Struct):
    def __init__(self, up, lo, bfd):
        super().__init__(
            up,
            lo,
            vertical=False,
            pad00_=ov.Be16,
            pad01_=ov.Be16,
            more=True,
        )
        self.bfd = bfd
        self.list = []
        if bfd:
            nsect = bfd.nsect.val
        else:
            nsect = 5
        for i in range(nsect):
            y = self.addfield(None, ov.Be16)
            self.list.append(y)
            y = self.addfield(None, ov.Be16)

        self.done(pad=0x200)
        self.up.set_picture('I', lo=lo)

    def __getitem__(self, idx):
        return self.list[idx].val

    def iter_sectors(self):
        for i in self.list:
            yield i.val

    def render(self):
        a = list(super().render())
        yield a[0]
        yield "  bfd = " + str(self.bfd)
        yield from a[1:]

class BasicFileDesc(ov.Struct):
    def __init__(self, up, nbr, lo):
        self.nbr = nbr
        super().__init__(
            up,
            lo,
            vertical=False,
            ok_=ov.Be16,
            bfd01_=ov.Be16,
            bfd02_=ov.Be16,
            type_=ov.Be16,
            length_=ov.Be16,
            bfd05_=ov.Be16,
            nsect_=ov.Be16,
            bfd07_=ov.Be16,
            areasz_=ov.Be16,
            sector_=ov.Be16,
            bfd0a_=ov.Be16,
            bfd0b_=ov.Be16,
            flags_=ov.Be16,
            bfd0d_=ov.Be16,
            min3_=ov.Be16,
            bfd0f_=ov.Be16,
            more=True,
        )
        self.done(pad=0x200)
        self.sfd = None
        self.that = None
        self.block_list = []
        self.bad_bl = False
        self.index_block = None
        self.committed = False
        if not self.valid():
            return
        self.up.set_picture('B', lo=lo)

        if self.ok.val == 0:
            pass
        elif self.areasz.val == 0:
            for i in range(self.nsect.val):
                self.block_list.append(self.sector.val + i)
        else:
            self.index_block = IndexBlock(up, self.sector.val << 9, self)
            for bn in self.index_block.iter_sectors():
                for mult in range(self.areasz.val):
                    self.block_list.append(bn + mult)

    def insert(self):
        super().insert()
        if self.index_block:
            self.index_block.insert()
        return self

    def valid(self):
        if self.type.val not in (0, 10, 12, 14):
            return False
        if self.bad_bl:
            return False
        return True

    def __str__(self):
        return " ".join(
            (
                 "{BFD" if self.valid() else "{bfd",
                 "#0x%x" % self.nbr,
                 "ok=" + hex(self.ok.val),
                 "type=" + hex(self.type.val),
                 "areasz=" + hex(self.areasz.val),
                 "length=" + hex(self.length.val),
                 "sector=" + hex(self.sector.val),
                 "nsect=" + hex(self.nsect.val),
                 "flags=" + hex(self.flags.val),
                 "min3=" + hex(self.min3.val),
                 "" if self.sfd is None else self.sfd.fname.txt,
                 "" if self.that is None else self.that.top.html_link_to(self.that),
                 "}",
            )
        )

    def render(self):
        a = list(super().render())
        yield a[0]
        yield "  nbr = #0x%x" % self.nbr
        yield from a[1:]

    def iter_sectors(self):
        yield from self.block_list

class DataSector():
    def __init__(self, up, lo, bfdno):
        for i in range(4):
            y = disk.DataSector(
                up,
                lo=lo + i * SECTOR_LENGTH,
            ).insert()
            y.ident = "DataSector[bfd#%d]" % bfdno

class SymbolicFileDesc(ov.Struct):
    def __init__(self, up, lo, pnamespace):
        super().__init__(
            up,
            lo,
            vertical=False,
            valid_=ov.Be16,
            fname_=ov.Text(16),
            file_=ov.Be16,
            sfd3_=12,
        )
        self.dir = None
        self.bfd = None
        self.fname.txt = self.fname.txt.rstrip()
        if self.valid.val != 1:
            self.namespace = None
            self.bfd = None
        elif self.file.val in up.bfd:
            self.namespace = NameSpace(
                name = self.fname.txt,
                parent = pnamespace,
                priv = self,
                separator = "!"
            )
            self.bfd = up.bfd[self.file.val]
        else:
            print(self.up.this, "SFD has no BFD#", self.file.val)

    def commit(self):
        ''' ... '''
        bits = []
        for sect in self.bfd.iter_sectors():
            lo = sect << L_SECTOR_SHIFT
            hi = lo + (1 << L_SECTOR_SHIFT)
            if self.bfd.type.val != 0xa and self.file.val and not self.bfd.committed:
                DataSector(self.up, lo=lo, bfdno = self.file.val)
                self.bfd.committed = True
            bits.append(self.up.this[lo:hi])
        if self.file.val <= 2:
            return
        i = self.bfd.length.val
        if i == 0:
            return
        if not bits:
            return
        j = (i + 1) & ~1
        bits = b''.join(bits)[:j]
        if i & 1:
            # make sure the padding byte is legal ASCII
            bits = bits[:-2] + b' ' + bits[-1:]
        that = self.up.this.create(bits = bits)
        self.namespace.ns_set_this(that)

class Directory():
    def __init__(self, up, namespace, bfdno):
        self.sfds = []
        self.namespace = namespace
        for sect in up.bfd[bfdno].iter_sectors():
            lo = sect << L_SECTOR_SHIFT
            up.set_picture('S', lo=lo)
            for off in range(0, 1 << L_SECTOR_SHIFT, 32):
                y = SymbolicFileDesc(up, lo + off, namespace).insert()
                self.sfds.append(y)

        for sfd in self.sfds:
            if sfd.valid.val != 1:
                continue
            if sfd.bfd:
                continue
            if sfd.file.val == bfdno:
                continue
            if sfd.bfd.type.val == 0xa:
                print("SUBDIR", sfd, sfd.bfd)
                sfd.dir = Directory(up, sfd.namespace, sfd.file.val)

    def commit(self):
        for sfd in self.sfds:
            if sfd.valid.val != 1:
                continue
            if sfd.bfd.type.val == 0xa:
                continue
            sfd.commit()

class CR80_FS2(disk.Disk):

    def __init__(self, this):
        if not this.has_type("ileave2"):
            return
        if this[0x10] or this[0x11] != 0x2:
            return
        print("CRFS2", this)
        this.add_type("CR80_Amos_Fs")
        super().__init__(
            this,
            [ [ N_TRACK, 1, N_SECT, SECTOR_LENGTH ] ],
        )

        this.byte_order = [1, 0]

        self.sb = HomeBlock(self, 0x0).insert()

        tmpiblk = IndexBlock(self, 1 << L_SECTOR_SHIFT, None)
        tmpbfd = BasicFileDesc(self, 0, tmpiblk[0] << L_SECTOR_SHIFT)

        self.bfd = {}
        for n, secno in enumerate(tmpbfd.iter_sectors()):
            j = BasicFileDesc(self, n, secno << L_SECTOR_SHIFT)
            j.insert()
            self.bfd[n] = j

        self.namespace = NameSpace(
            name="",
            root=this,
            separator="",
        )

        assert self.bfd[1].type.val == 0x000a

        self.root = Directory(self, self.namespace, 1)
        self.root.commit()

        this.add_interpretation(self, self.namespace.ns_html_plain)

        this.add_interpretation(self, self.disk_picture)

        self.fill_gaps()

        self.render()

    def set_picture(self, what, lo):
        for i in range(4):
            super().set_picture(what, lo = lo + i * SECTOR_LENGTH)
