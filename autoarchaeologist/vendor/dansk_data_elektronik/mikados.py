#!/usr/bin/env python3

'''
   DDE SPC/1 Mikados
   =================

   Doc: [30005441] & [30005443]
'''

from ...base import octetview as ov
from ...base import namespace

class MikadosTextFile():
    '''
       [30005441] section 5.4.1
       Lines in text-files have length-byte before and after
    '''

    def __init__(self, this):
        if not this.has_note("Mikados_K"):
            return
        txt = []
        i = 0
        while i < len(this) - 1 and this[i] != 0:
            l1 = this[i]
            if i + l1 + 2 > len(this):
                return
            i += 1
            txt.append(this.type_case.decode_long(this[i:i+l1]))
            i += l1
            l2 = this[i]
            i += 1
            if l1 != l2:
                return
        if not txt:
            return
        f = this.add_utf8_interpretation("Text")
        with open(f.filename, "w", encoding="utf8") as file:
            for l in txt:
                file.write(l + "\n")
        this.add_note("Mikados TextFile")

class DiskAdr(ov.Struct):
    ''' [30005441] section 5.1 '''

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            f00_=ov.Le16,
            f01_=ov.Octet,
            **kwargs,
        )
        self.lba = (self.f00.val * self.tree.mult) + self.f01.val

    def __lt__(self, other):
        if self.f00.val < other.f00.val:
            return True
        return self.f01.val < other.f01.val

    def render(self):
        yield "{DA %04x,%02x (0x%06x)}" % (self.f00.val, self.f01.val, self.lba*256)

class DiskLabel(ov.Struct):
    ''' [30005441] section 5.3.1 '''

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            plidn_=ov.Text(10),	# MIKADOS init prog ident 'PLADELAGER'
            ledig_=DiskAdr,	# track/sector of first unused sector on disk
            plart_=ov.Text(5),	# disk type
            pldto_=ov.Text(10),	# date last backup
            plbtg_=ov.Text(10),	# disc name
            pluda_=ov.Text(10),	# date last system startup
            more = True,
            **kwargs,
        )
        # self.add_field("f99", 256 - len(self))
        self.done()

class DirEnt(ov.Struct):
    ''' [30005441] section 5.3.2 '''

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            name_=ov.Text(8),
            typ_=ov.Text(1),
            seg_=ov.Text(1),
            seg0_=DiskAdr,
            **kwargs,
        )
        self.deleted = False
        self.bogus = False
        self.valid = False
        self.unused = False
        if sum(self.this[self.lo:self.hi]) == 0:
            self.unused = True
        elif self.seg.txt != 'A':
            self.bogus = True
        elif self.typ.txt not in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            self.bogus = True
        elif ' '  in self.name.txt.rstrip():
            self.bogus = True
        elif self.this[self.lo] == 0x01:
            self.deleted = True
        else:
            self.valid = True

        if self.deleted:
            self.pname = '░' + self.name.txt[1:].rstrip()
        else:
            self.pname = self.name.txt.rstrip()

    def render(self):
        if self.unused:
            return
        if self.valid:
            yield from super().render()
        elif self.deleted:
            yield "Deleted" + "".join(super().render())
        else:
            yield "Bogus" + "".join(super().render())

class DirSect(ov.Struct):
    ''' [30005441] section 5.3.2 '''

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            dent_=ov.Array(19, DirEnt, vertical=True),
            fill__=9,
            vertical=True,
            **kwargs,
        )
        self.nok = 0
        self.nused = 0
        for de in self.dent:
            if de.valid:
                self.nused += 1
                self.nok += 1
            elif de.unused:
                self.nok += 1

    def render(self):
        if self.nused > 0:
            yield from super().render()
        else:
            yield "EmptyDirSect"

    def iter(self):
        for i in self.dent:
            if i.valid or i.deleted:
                yield i

class ExtentHdr(ov.Struct):
    ''' [30005441] section 5.4 '''

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            name_=ov.Text(8),
            typ_=ov.Text(1),
            seg_=ov.Text(1),
            next_=ov.Octet,
            basis_=ov.Le16,
            nextext_=DiskAdr,
            prevext_=DiskAdr,
            nextfile_=DiskAdr,
            f04_=ov.Text(3),
            postl_=ov.Le16,
            f99_=ov.Text(5),
            **kwargs,
        )
        if self.this[self.lo] in (0x0, 0x1, 0x20):
            self.pname = '░' + self.name.txt[1:].rstrip()
        else:
            self.pname = self.name.txt.rstrip()

class Extent(ov.Opaque):
    ''' just for the name '''

class Mikados(ov.OctetView):
    ''' Hard disks can be partitioned '''

    def __init__(self, this):
        if not this.top in this.parents:
            return

        super().__init__(this)

        if len(this) == 20782080:

            for start, stop in (
                (0x2100, 0x4b2100,),
                (0x4b2100, 0x962100,),
                (0x962100, 0xe14200,),
                (0xe14200, len(this),),
            ):
                magic = ov.Text(10)(self, start)
                if magic.txt.lower() == "pladelager":
                    y = this.create(start=start, stop=stop)
                    y.add_note("Mikados_Logisk_Disk")

class NameSpace(namespace.NameSpace):
    ''' ... '''

    TABLE = (
        ("l", "f04"),
        ("l", "f09"),
        ("r", "basis"),
        ("r", "postl"),
        ("r", "type"),
        ("l", "name"),
        ("l", "artifact"),
    )

    def ns_render(self):
        ''' ...  '''
        xhdr = self.ns_priv
        if isinstance(xhdr, ExtentHdr):
            return [
                xhdr.f04.txt,
                xhdr.f99.txt,
                xhdr.basis.val,
                xhdr.postl.val,
                xhdr.typ.txt,
            ] + super().ns_render()
        if isinstance(xhdr, DirEnt):
            return [
                "",
                "",
                "",
                "",
                "mangled",
            ] + super().ns_render()
        return [ "" ] * (len(self.TABLE) - 2) + super().ns_render()

class MikadosDisk(ov.OctetView):
    ''' One Mikados "plade" '''

    def __init__(self, this):
        if this.top not in this.parents and not this.has_note("Mikados_Logisk_Disk"):
            return

        super().__init__(this)

        magic = ov.Text(10)(self, 0x0)
        if magic.txt.lower() != "pladelager":
            return

        # We need to know the number of 256 byte sectors per "spor".
        # The geometry of the drive is available only in the memory table
        # described in [30005441] section 5.3.1 and not recorded on the media.
        # [30007261] page 8.1 contains a (partial?) list of formats.
        # We trust the imposed geometry if there is one, fall back to a lookup
        # or 32 if all else fails.
        if this.num_rec():
            self.mult = len(set(x.key[-1] for x in this.iter_rec()))
        else:
            self.mult = {
                77 * 2 * 26 * 256: 26,	# B - 8" 1Mb DDE format
            }.get(len(this), 32)

        y = DiskLabel(self, 0x0).insert()

        self.namespace = NameSpace(name = '', root = this, separator = "")

        self.extents = []
        adr = 0x100
        low = len(this)
        self.dirents = {}
        self.deleted = {}
        # This loop is based on the hypothesis that some dirent, active or deleted
        # will describe the first extent.
        while adr < low:
            y = DirSect(self, adr)
            if y.nok == 0:
                break
            y.insert()
            for de in y.iter():
                if de.unused:
                    continue
                if de.bogus:
                    break
                if de.valid:
                    self.dirents[(de.name.txt, de.typ.txt)] = de
                if de.deleted:
                    self.deleted[(de.name.txt, de.typ.txt)] = de
                if de.seg0.f01.val:
                    low = min(low, de.seg0.lba << 8)
            adr += 0x100
        if not self.dirents and not self.deleted:
            return

        print(this, "MikadosDisk", "mult:", self.mult)

        for de in self.dirents.values():
            ptr = de.seg0.lba << 8
            if ptr and not self.attempt_extents(ptr, de):
                print(self.this, "Mangled dirent", de)
                NameSpace(
                    de.pname,
                    parent = self.namespace,
                    priv = de,
                )

        self.spelunk()

        if not self.extents:
            print(this, "MikadosDisk", "Nothing found")
            return

        this.add_interpretation(self, self.namespace.ns_html_plain)
        self.add_interpretation(more=True)

    def spelunk(self):
        for de in self.deleted.values():
            ptr = de.seg0.lba << 8
            self.attempt_extents(ptr, de)

        for lo, hi in list(self.gaps()):
            lo += 0xff
            lo &= ~0xff
            while lo < hi:
                self.attempt_extents(lo)
                lo += 0x100

    def attempt_extents(self, lo, dirent=None):
        ''' Attempt to instantiate a chain of extents at ``lo`` '''
        hdrs = []
        bodies = []
        while True:
            if lo > len(self.this) - 256:
                return False
            what = list(self.find(lo=lo))
            if what:
                return False
            hdrs.append(ExtentHdr(self, lo))
            if hdrs[0].seg.txt != 'A':
                return False
            if hdrs[-1].seg.txt != '%c' % (64 + len(hdrs)):
                return False
            if dirent and dirent.name.txt != hdrs[-1].name.txt:
                return False
            length = (hdrs[0].basis.val << 8) - 32
            if length < 0 or lo + length > len(self.this):
                return False
            bodies.append(Extent(self, lo + 32, width=length))
            if len(hdrs) == hdrs[0].next.val + 1:
                break
            lo = hdrs[-1].nextext.lba << 8
        for i, j in zip(hdrs, bodies):
            i.insert()
            j.insert()
        z = self.this.create(records = [y.octets() for y in bodies])
        z.add_note("Mikados_" + hdrs[0].typ.txt)
        if dirent:
            pname = dirent.pname
        else:
            pname = hdrs[0].pname
        NameSpace(
            pname,
            parent = self.namespace,
            this = z,
            priv = hdrs[0],
        )
        self.extents.append(z)
        return True

examiners = (
    Mikados,
    MikadosDisk,
    MikadosTextFile,
)
