
from ..generic import disk
from ..base import octetview as ov

class WangPtr(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            cyl_=ov.Octet,
            sect_=ov.Octet,
        )

class WangSectHead(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            next_=WangPtr,
            len_=ov.Octet,
            h3_=4,
        )

class WangSector(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            hdr_=WangSectHead,
            more=True,
        )
        self.body = self.tree.this[self.lo + len(self):1 + self.lo + self.hdr.len.val]
        if self.hdr.len.val > len(self):
            self.add_field("txt", ov.Text(1 + self.hdr.len.val - len(self)))
        self.done(256)

    def render(self):
        yield from super().render()
        yield str([self.body.tobytes()])

class FillSector(disk.Sector):
    def render(self):
        ''' Render respecting byte ordering '''
        if self.terse:
            yield self.ident
            return
        if self.is_unread:
            octets = self.octets()
        else:
            octets = self.iter_bytes()
        yield self.ident + " " + self.this[self.lo:self.lo+7].hex() + " ┆" + self.this.type_case.decode(octets) + "┆"

class WangChunk():
    def __init__(self, tree, chs):
        self.sectors = []
        while True:
            sect = tree.sectors.get(chs)
            self.sectors.append(sect)
            sect.insert()
            if sect.hdr.len.val == 0:
                print("SHORT", sect)
            if sect.hdr.len.val < 0xff:
                break
            chs = sect.next

    def __iter__(self):
        yield from self.sectors

class WangChunkList(ov.Struct):

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            hdr_=WangSectHead,
            f0_=9,
            more=True,
        )
        print("WCL", self, self.hdr.len.val)
        if self.hdr.len.val:
            self.add_field("chunks", ov.Array(self.hdr.len.val, WangPtr))
        self.done(256)

class WangDesc(ov.Struct):

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            d00_=ov.Octet,
            d01_=ov.Octet,
            d02_=ov.Octet,
            c_=ov.Octet,
            s_=ov.Octet,
            d05_=ov.Octet,
        )
        self.ptr = (self.c.val, 0, self.s.val)
        self.chunks = []

    def commit(self):
        print('-' * 80)
        sect = self.tree.sectors[self.ptr]
        print("H", sect.chs, sect)
        sect = self.tree.sectors.get(sect.next)
        self.chunklist = WangChunkList(self.tree, sect.lo).insert()
        print("CL", sect.chs, hex(self.chunklist.lo), self.chunklist)
        for i in self.chunklist.chunks:
            chunk = WangChunk(self.tree, (i.cyl.val, 0, i.sect.val))
            self.chunks.append(chunk)
        cont = []
        for i in self.chunks:
            #print("--")
            for j in i:
                if len(j.body) > 0:
                    cont.append(j.body)
        if len(cont) > 0:
            y = self.tree.this.create(records=cont)
            y.add_type("wang_text")
        print(cont)

class WangWps(disk.Disk):

    SECTOR_OFFSET = 0

    def __init__(self, this):
        if len(this) not in (77*16*256,):
            return

        super().__init__(
            this,
            [ [ 77, 1, 16, 256 ], ],
            physsect = 256,
        )

        self.sectors = {}
        for chs,lo in self.seclo.items():
            ws = WangSector(self, lo)
            ws.chs = chs
            self.sectors[chs] = ws
            ws.prev = set()
            ncyl = self.this[lo]
            nsect = self.this[lo + 1]
            ws.next = (ncyl, 0, nsect)

        for sect in self.sectors.values():
            nxt = self.sectors.get(sect.next)
            if nxt:
                nxt.prev.add(sect.chs)

        descs = []
        adr = 0x300
        for i in range(13):
            y = WangDesc(self, adr).insert()
            adr = y.hi
            descs.append(y)

        for desc in descs:
            desc.commit()

        self.fill_gaps(FillSector)
        this.add_interpretation(self, this.html_interpretation_children)
        self.add_interpretation()

    def hunt_chains(self):

        chains = {}
        for sect in sectors.values():
            if len(sect.prev) > 0:
                continue
            if sum(sect.next) == 0:
                continue
            l = list()
            chains[sect.chs] = l
            l.append(sect)
            while sum(sect.next) > 0:
                sect = sectors.get(sect.next)
                if sect:
                    l.append(sect)
                else:
                    break

        print("=" * 80)
        for chs, chain in chains.items():
            print(chs, hex(chs[0]))
        for chs, chain in chains.items():
            print("=" * 80)
            for ln in chain:
                print("", ln.chs, "\t", ln.this[ln.lo:ln.lo+7].tobytes().hex())
            t = ""
            for ln in chain:
                txt = ln.this[ln.lo + 7:ln.hi].tobytes()
                for i in txt:
                    if 32 <= i <= 126:
                        t += "%c" % i
                    elif i == 3:
                        print('  ', t)
                        t = ''
                    else:
                        t += " "
            print('  ', t)

