#!/usr/bin/env python3

'''
   DDE SPC/1 Mikados
   =================

   Doc: 30005441 & 30005443
'''

from ..generic import disk
from ..base import artifact
from ..base import octetview as ov
from ..base import namespace

class MikadosTextFile():

    def __init__(self, this):
        txt = []
        i = 0
        while i < len(this) - 1 and this[i] != 0:
            l1 = this[i]
            if i + l1 + 2 > len(this):
                print(this, self.__class__.__name__, "L1", l1)
                return
            i += 1
            txt.append(this.type_case.decode(this[i:i+l1]))
            i += l1
            l2 = this[i]
            i += 1
            if l1 != l2:
                print(this, self.__class__.__name__, "L1/L2", l1, l2)
                return
        f = this.add_utf8_interpretation("Text")
        with open(f.filename, "w") as file:
            for l in txt:
                file.write(l + "\n")
        this.add_type("Mikados TextFile")

class NameSpace(namespace.NameSpace):
    ''' ... '''

    XTABLE = (
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
        ''' ...  '''
        dent = self.ns_priv
        if dent is None:
            return [ "" ] * 1 + super().ns_render()
        return [
            dent.typ.txt,
        ] + super().ns_render()

class DiskAdr(ov.Struct):

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
        if sum(self.this[self.lo:self.hi]) == 0:
            self.valid = None
        elif self.this[self.lo] == 0x01:
            self.deleted = True
            self.valid = False
        else:
            self.valid = True

    def render(self):
        if self.valid is None:
            # yield 'DirEntUnused'
            return
        if self.valid:
            yield from super().render()
        elif self.deleted:
            yield "Deleted" + "".join(super().render())
        else:
            yield "Bogus" + "".join(super().render())

class Extent(ov.Struct):

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
            f04_=3,
            postl_=ov.Le16,
            more = True,
            **kwargs,
        )
        if len(self) != 32:
            self.add_field("f99", 32 - len(self))
        self.done()

class DirSect(ov.Struct):

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            dent_=ov.Array(19, DirEnt, vertical=True),
            fill__=9,
            vertical=True,
            **kwargs,
        )

    def iter(self):
        for i in self.dent:
            if i.valid or i.deleted:
                yield i

    def iter_valid(self):
        for i in self.dent:
            if i.valid:
                yield i

class Mikados(ov.OctetView):

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
                y = this.create(start=start, stop=stop)
                y.add_note("Mikados_Logisk_Disk")
        #else:
        #    this.add_note("Mikados_Logisk_Disk")

class MikadosDisk(ov.OctetView):

    def __init__(self, this):
        if this.top not in this.parents and not this.has_note("Mikados_Logisk_Disk"):
            return

        super().__init__(this)

        if not this.num_rec():
            self.mult = 32
        else:
            self.mult = len(set(x.key[-1] for x in this.iter_rec()))

        y = DiskLabel(self, 0x0)
        magic = y.plidn.txt.lower()
        if magic != "pladelager":
            print(this, "PL", [magic], magic == "pladelager")
            return

        print(this, "MikadosDisk", "mult:", self.mult, "len:", len(this), len(this) / self.mult, len(this) / (self.mult * 256))
        y.insert()

        self.namespace = NameSpace(
            name = '',
            root = this,
            separator = "",
        )

        adr = 0x100
        z = None
        low = len(this)
        self.dirents = {}
        self.deleted = {}
        while adr < low:
            y = DirSect(self, adr).insert()
            for de in y.iter():
                if de.valid:
                    self.dirents[(de.name.txt, de.typ.txt)] = de
                if de.deleted:
                    self.deleted[(de.name.txt, de.typ.txt)] = de
                if de.seg0.f01.val:
                     low = min(low, de.seg0.lba << 8)
            adr += 0x100

        print(this, "LOW", hex(adr), hex(low))

        self.commit_files()

        while self.spelunk():
            continue

        # self.fill_gaps(FillSector)
        this.add_interpretation(self, self.namespace.ns_html_plain)
        # this.add_interpretation(self, self.disk_picture)
        self.add_interpretation(more=False)

    def spelunk(self):
        for de in self.deleted.values():
            ptr = (de.seg0.lba << 8)
            what = list(self.find(lo=ptr))
            if not what and self.attempt_extents(ptr, de):
                print(self.this, "SP1", de)
                return True

        for lo, hi in list(self.gaps()):
            lo += 0x1ff
            lo &= ~0x1ff
            while lo < hi:
                if self.attempt_extents(lo):
                    print(self.this, "SP2", hex(lo))
                    return True
                lo += 100

        return False

    def attempt_extents(self, lo, dirent=None):
        hdrs = []
        bodies = []
        while True:
            if lo > len(self.this) - 256:
                return False
            hdrs.append(Extent(self, lo))
            if hdrs[0].seg.txt != 'A':
                return False
            if hdrs[-1].seg.txt != '%c' % (64 + len(hdrs)):
                return False
            if dirent and dirent.name.txt != hdrs[-1].name.txt:
                return False
            length = (hdrs[0].basis.val << 8) - 32
            if length < 0 or lo + length > len(self.this):
                return False
            bodies.append(ov.Opaque(self, lo + 32, width=length))
            if len(hdrs) == hdrs[0].next.val + 1:
                break
            lo = hdrs[-1].nextext.lba << 8
        for i, j in zip(hdrs, bodies):
            # print(self.this, "AE", i, j)
            i.insert()
            j.insert()
        z = self.this.create(records = [y.octets() for y in bodies])
        if dirent:
            z.add_note("Mikados_" + dirent.typ.txt)
            if dirent.deleted:
                pname = '░' + dirent.name.txt[1:]
            else:
                pname = dirent.name.txt
            ns = NameSpace(
                pname.rstrip() + "(" + dirent.typ.txt + ")" ,
                parent = self.namespace,
                this = z,
                priv = dirent,
            )
        else:
            pname = '░' + hdrs[0].name.txt[1:]
            ns = NameSpace(
                pname.rstrip() + "(" + hdrs[0].typ.txt + ")" ,
                parent = self.namespace,
                this = z,
                priv = None,
            )
        print(self.this, "Z", z, ns)
        return True

    def commit_files(self):
        for de in self.dirents.values():
            if de.seg.txt != "A":
                continue
            ptr = (de.seg0.lba << 8)
            if ptr:
                self.attempt_extents(ptr, de)
