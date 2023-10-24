#!/usr/bin/env python3

'''
   CR80 Filesystem type 2

   See https://ta.ddhf.dk/wiki/Bits:30004479
'''

from ..generic import disk
from ..base import type_case
from ..base import namespace
from ..base import octetview as ov

N_SECT = 26
N_TRACK = 77
SECTOR_LENGTH = 128

L_SECTOR_LENGTH = 512
L_SECTOR_SHIFT = 9

class HomeBlock(ov.Struct):
    '''
       The "home block" lives in the first sector and we use it
       to determine if there is an AMOS filesystem on an artifact.

       The classes for 16 and 32 bit fields are parameters because
       the CR80 floppy controller has "issues", which we solve with
       CR80_FS2Interleave.
    '''

    def __init__(self, tree, lo, fe16=ov.Le16, fe32=ov.Le32):
        super().__init__(
            tree,
            lo,
            vertical=False,
            label_=ov.Text(16),
            bfdadr_=fe32,
            free_ent_=fe32,
            first_free_=fe32,
            sectors_=fe32,
            bst_size_=fe16,
            asf_adr_=fe32,
            bst_=400,
            bstsz_=fe16,
            unused_=52,
            boot_entry_=fe32,
            created_=6,
            accessed_=6,
            format_=fe16,
            state_=fe16,
        )
        self.tree.set_picture('H', lo=lo)
        self.tree.picture_legend['H'] = 'Home Block'

    def is_sensible(self, xor=0x00, verbose=True):
        ''' Does this even make sense ?! '''

        # This field not in first 128 bytes, so we cannot check it
        # until the interleave has been sorted out.
        #if 0 and self.format.val > 10:
        #    if verbose:
        #        print(self.tree.this, "-Homeblock.format", hex(self.format.val))
        #    return False

        nlba = len(self.tree.this) // L_SECTOR_LENGTH

        if not 0 < self.bfdadr.val < nlba:
            if verbose:
                print(self.tree.this, "-Homeblock.bfdaddr", hex(self.bfdadr.val))
            return False

        if not 0 < self.sectors.val <= nlba:
            if verbose:
                print(self.tree.this, "-Homeblock.sectors", hex(self.sectors.val))
            return False

        b = bytearray(x ^ xor for x in self.label.iter_bytes())
        while b and b[-1] == 0:
            b.pop(-1)

        if len(b) == 0:
            if verbose:
                print(self.tree.this, "-Homeblock.label", [b])
            return False

        for i in b:
            if 0x30 <= i <= 0x39:
                pass
            elif 0x41 <= i <= 0x5A:
                pass
            elif i in (0x2e, 0x5f,):
                pass
            else:
                if verbose:
                    print(self.tree.this, "-Homeblock.label", [b], hex(i))
                return False

        return True

class IBe16(ov.Be16):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.val ^= 0xffff

class IRe32(ov.L2301):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.val ^= 0xffffffff

class CR80_FS2Interleave(ov.OctetView):

    VERBOSE = False

    def __init__(self, this):
        if not this.top in this.parents:
            return
        if len(this) != N_SECT * N_TRACK * SECTOR_LENGTH:
            return

        super().__init__(this)
        self.picture_legend = {}

        obo = this.byte_order
        this.byte_order = [1, 0]
        hb = HomeBlock(self, 0, fe16 = IBe16, fe32 = IRe32)
        good = hb.is_sensible(0xff, True)
        this.byte_order = obo
        if not good:
            print("NOT", this)
            return

        img = bytearray(len(this))

        ileave = [
                  0,  2,  4,  6,  8, 10, 12, 14, 16, 18, 20, 22, 24,
                  1,  3,  5,  7,  9, 11, 13, 15, 17, 19, 21, 23, 25,
        ]
        unread = b'_UNREAD_' * (SECTOR_LENGTH//8)
        for cyl in range(N_TRACK):
            for sect in range(N_SECT):
                pcyl = cyl
                psect = ileave[(cyl * 0 + sect + N_SECT) % N_SECT]
                padr = pcyl * N_SECT * SECTOR_LENGTH + psect * SECTOR_LENGTH
                octets = this[padr:padr + SECTOR_LENGTH]
                lba = cyl * N_SECT * SECTOR_LENGTH + sect * SECTOR_LENGTH
                if octets == unread:
                    img[lba:lba + SECTOR_LENGTH] = unread
                else:
                    for n in range(0, len(octets), 2):
                        x = octets[n] ^ 0xff
                        y = octets[n + 1] ^ 0xff
                        img[lba + n] = y
                        img[lba + n + 1] = x
        that = this.create(bits=img)
        that.add_type("ileave2")
        this.add_interpretation(self, this.html_interpretation_children)

    def set_picture(self, *args, **kwargs):
        return

    def fe16(self, _tree, off):
        a = off // 128
        b = off % 128
        a *= 2
        off = a * 128 + b
        retval = self.this[off + 0] << 8
        retval |= self.this[off + 1]
        retval ^= 0xffff
        return retval

    def fe32(self, _tree, off):
        a = off // 128
        b = off % 128
        a *= 2
        off = a * 128 + b
        retval = self.this[off + 2] << 24
        retval |= self.this[off + 3] << 16
        retval |= self.this[off + 0] << 8
        retval |= self.this[off + 1]
        retval ^= 0xffffffff
        return retval

class NameSpace(namespace.NameSpace):
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
            hex(bfd.flags.val),
        ] + super().ns_render()


class IndexBlock(ov.Struct):
    def __init__(self, tree, lo, bfd):
        super().__init__(
            tree,
            lo,
            vertical=False,
            pad00_=ov.Le16,
            pad01_=ov.Le16,
            more=True,
        )
        self.bfd = bfd
        self.list = []
        if bfd:
            nsect = bfd.nsect.val
        else:
            nsect = 5
        for i in range(nsect):
            y = self.addfield(None, ov.Le16)
            self.list.append(y)
            y = self.addfield(None, ov.Le16)

        self.done(pad=0x200)
        self.tree.set_picture('I', lo=lo)
        self.tree.picture_legend['I'] = 'Index Block'

    def __getitem__(self, idx):
        return self.list[idx].val

    def iter_sectors(self):
        #if self.lo == 0xfb400:
        #    yield 0x7db
        #    return
        for i in self.list:
            yield i.val

    def render(self):
        a = list(super().render())
        yield a[0]
        yield "  bfd = " + str(self.bfd)
        yield from a[1:]

class BasicFileDesc(ov.Struct):
    def __init__(self, tree, nbr, lo):
        self.nbr = nbr
        super().__init__(
            tree,
            lo,
            vertical=False,
            ok_=ov.Le16,
            bfd01_=ov.Le16,
            bfd02_=ov.Le16,
            type_=ov.Le16,
            length_=ov.Le16,
            bfd05_=ov.Le16,
            nsect_=ov.Le16,
            bfd07_=ov.Le16,
            areasz_=ov.Le16,
            sector_=ov.Le16,
            bfd0a_=ov.Le16,
            bfd0b_=ov.Le16,
            flags_=ov.Le16,
            bfd0d_=ov.Le16,
            min3_=ov.Le16,
            bfd0f_=ov.Le16,
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
        self.tree.set_picture('B', lo=lo)
        self.tree.picture_legend['B'] = 'Basic File Directory'
        self.taken = False

        if self.ok.val == 0:
            pass
        elif self.areasz.val == 0:
            for i in range(self.nsect.val):
                self.block_list.append(self.sector.val + i)
        else:
            self.index_block = IndexBlock(tree, self.sector.val << 9, self)
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
    def __init__(self, tree, lo, bfdno):
        self.is_unread = False
        for i in range(4):
            y = disk.DataSector(
                tree,
                lo=lo + i * SECTOR_LENGTH,
            ).insert()
            y.ident = "DataSector[bfd#%d]" % bfdno
            self.is_unread |= y.is_unread

class SymbolicFileDesc(ov.Struct):
    def __init__(self, tree, lo, pnamespace):
        super().__init__(
            tree,
            lo,
            vertical=False,
            valid_=ov.Le16,
            fname_=ov.Text(16),
            file_=ov.Le16,
            sfd3_=ov.Le32,
            sfd4_=ov.Le32,
            sfd5_=ov.Le32,
        )
        self.dir = None
        self.bfd = None
        self.fname.txt = self.fname.txt.rstrip()
        if self.valid.val != 1:
            self.namespace = None
            self.bfd = None
        elif self.file.val in tree.bfd:
            self.namespace = NameSpace(
                name = self.fname.txt,
                parent = pnamespace,
                priv = self,
                separator = "!"
            )
            self.bfd = tree.bfd[self.file.val]
        else:
            print(self.tree.this, "SFD has no BFD#", self.file.val)

    def commit(self):
        ''' ... '''
        bits = []
        is_unread = False
        for sect in self.bfd.iter_sectors():
            lo = sect << L_SECTOR_SHIFT
            hi = lo + (1 << L_SECTOR_SHIFT)
            if self.bfd.type.val != 0xa and self.file.val and not self.bfd.committed:
                y = DataSector(self.tree, lo=lo, bfdno = self.file.val)
                self.bfd.committed = True
                is_unread |= y.is_unread
            bits.append(self.tree.this[lo:hi])
        self.bfd.taken = True
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
        that = self.tree.this.create(bits = bits)
        if is_unread:
            that.add_note("UNREAD_DATA_SECTOR")
        self.namespace.ns_set_this(that)

class Directory():
    def __init__(self, tree, namespace, bfdno):
        self.tree = tree
        self.sfds = []
        self.namespace = namespace
        done = False
        for sect in tree.bfd[bfdno].iter_sectors():
            lo = sect << L_SECTOR_SHIFT
            tree.set_picture('S', lo=lo)
            tree.picture_legend['S'] = 'Symbolic File Directory'
            for off in range(0, 1 << L_SECTOR_SHIFT, 32):
                y = SymbolicFileDesc(tree, lo + off, namespace).insert()
                self.sfds.append(y)

        for sfd in self.sfds:
            if sfd.valid.val != 1:
                continue
            if sfd.file.val == bfdno:
                continue
            if sfd.file.val < 3:
                continue
            if not sfd.bfd:
                continue
            if sfd.bfd.type.val == 0xa:
                sfd.dir = Directory(tree, sfd.namespace, sfd.file.val)

    def commit(self):
        for sfd in self.sfds:
            if sfd.valid.val != 1:
                continue
            if not sfd.bfd:
                print(self.tree.this, "NOBFD", sfd)
                continue
            if sfd.dir:
                sfd.dir.commit()
            else:
                sfd.commit()

class CR80Amos_Ascii(type_case.Ascii):
    ''' ... '''
    def __init__(self):
        super().__init__()
        self.set_slug(0x00, ' ', '«nul»')
        self.set_slug(0x01, ' ', '«soh»')
        self.set_slug(0x02, ' ', '«stx»')
        self.set_slug(0x03, ' ', '«etx»')
        self.set_slug(0x04, ' ', '«eot»')
        self.set_slug(0x1c, ' ', '«fs»')
        self.set_slug(0x0c, ' ', '«ff»')


class CR80_FS2(disk.Disk):

    type_case = CR80Amos_Ascii()

    def __init__(self, this):
        if not ( this.has_type("ileave2") or len(this) == 67420160):
            return
        print("CRFS2", this)

        super().__init__(
            this,
            [ [ N_TRACK, 1, N_SECT, SECTOR_LENGTH ] ],
            # [ [ 823, 5, 32, 512 ] ],
            # physsect=512,
        )

        this.type_case = self.type_case

        # y = ov.Opaque(self, 0x00b4b7f0 + (1<<10), hi=len(this)).insert()

        self.homeblock = HomeBlock(self, 0x0).insert()
        if not self.homeblock.is_sensible(0x00, True):
            return

        this.add_note("CR80_Amos_Fs")

        self.bfd = {}
        self.namespace = NameSpace(
            name="",
            root=this,
            separator="",
        )

        tmpbfd = BasicFileDesc(self, 0, self.homeblock.bfdadr.val << L_SECTOR_SHIFT)

        for n, secno in enumerate(tmpbfd.iter_sectors()):
            j = BasicFileDesc(self, n, secno << L_SECTOR_SHIFT)
            j.insert()
            self.bfd[n] = j

        assert self.bfd[1].type.val == 0x000a

        self.root = Directory(self, self.namespace, 1)
        self.root.commit()

        this.add_interpretation(self, self.namespace.ns_html_plain)

        this.add_interpretation(self, self.disk_picture)

        self.fill_gaps()

        self.render()

    def set_picture(self, what, lo):
        for i in range(L_SECTOR_LENGTH//SECTOR_LENGTH):
            super().set_picture(what, lo = lo + i * SECTOR_LENGTH)
