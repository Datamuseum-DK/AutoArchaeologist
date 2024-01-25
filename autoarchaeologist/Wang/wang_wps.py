#!/usr/bin/env python3

'''
   Wang WPS floppies
   =================
'''

from ..generic import disk
from ..base import artifact
from ..base import octetview as ov
from ..base import namespace

from .wang_text import WangTypeCase

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
        '''
           See:
              03-0072-01A-Z80_RIO Operating System Users Manual Sep78, pg 116
        '''
        head = self.ns_priv
        if head is None:
            return [ "" ] * 23 + super().ns_render()
        return [
            head.f00.txt,
            head.f01.txt,
            head.f02.txt,
            head.f03.txt,
            head.f04.txt,
            head.f05.txt,
            head.f06.txt,
            head.f07.txt,
            head.f08.txt,
            head.f09.txt,
            head.f10.txt,
            head.f11.txt,
            head.f12.txt,
            head.f13.txt,
            head.f14.txt,
            head.f15.txt,
            head.f16.txt,
            head.f17.txt,
            head.f18.txt,
            head.f19.txt,
            head.f20.txt,
            head.f21.txt,
            head.f22.txt,
        ] + super().ns_render()


class WangPtr(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            cyl_=ov.Octet,
            sect_=ov.Octet,
        )
        self.chs = (self.cyl.val, 0, self.sect.val)

    def render(self):
        yield "(%2d,0,%2d)" % (self.cyl.val, self.sect.val)

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
            if sect is None:
                print(tree.this, "No sector", chs)
                break
            tree.set_picture('CH', lo=sect.lo, legend="Chunk")
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
        tree.set_picture('CL', lo=lo, legend="Chunk List")
        super().__init__(
            tree,
            lo,
            hdr_=WangSectHead,
            f0_=1,
            f1_=2,
            f2_=2,
            f3_=WangPtr,
            f4_=2,
            more=True,
        )
        self.chunks = []
        print("WCL", self.hdr, self.hdr.len.val)
        if self.hdr.len.val:
            self.add_field("chunks", ov.Array(min(self.hdr.len.val, 100), WangPtr))
        self.done(256)

class WangTimeStamp(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            parts_=ov.Array(5, ov.Text(3)),
        )
        self.txt = "%s-%s-%s %s:%s" % (
            self.parts[0].txt[:2],
            self.parts[1].txt[:2],
            self.parts[2].txt[:2],
            self.parts[3].txt[:2],
            self.parts[4].txt[:2],
        )

    def render(self):
        yield self.txt

class WangDocumentHead(ov.Struct):
    def __init__(self, tree, lo):
        tree.set_picture('DH', lo=lo, legend="Document Head")
        super().__init__(
            tree,
            lo,
            vertical=False,
            hdr_=WangSectHead,
            f00_=ov.Text(6),
            f01_=ov.Text(26),
            f02_=ov.Text(21),
            f03_=ov.Text(21),
            f04_=ov.Text(21),
            f05_=WangTimeStamp,
            f06_=ov.Text(5),
            f07_=ov.Text(3),
            f08_=ov.Text(7),
            f09_=WangTimeStamp,
            f10_=ov.Text(5),
            f11_=ov.Text(3),
            f12_=ov.Text(7),
            f13_=WangTimeStamp,
            f14_=WangTimeStamp,
            f15_=ov.Text(6),
            f16_=ov.Text(4),
            f17_=ov.Text(5),
            f18_=ov.Text(3),
            f19_=ov.Text(6),
            f20_=ov.Text(7),
            f21_=ov.Text(2),
            f22_=ov.Text(3),
            more=True,
        )
        if self.hi < self.lo + 256:
            self.add_field("f99", self.lo + 256 - self.hi)
        self.done(256)

class WangDocumentBody(ov.Struct):
    def __init__(self, tree, lo):
        tree.set_picture('DB', lo=lo, legend="Document Body")
        super().__init__(
            tree,
            lo,
            vertical=False,
            hdr_=WangSectHead,
            more=True,
        )
        i = 1 + self.hdr.len.val - (self.hi - self.lo)
        if i > 0:
            self.add_field("body", ov.Text(i))
            self.part = self.body.octets()
        else:
            self.part = None
        if self.hi < self.lo + 256:
            self.add_field("f99", self.lo + 256 - self.hi)
        self.done(256)

    def render(self):
        yield self.__class__.__name__

class WangDocument(ov.Struct):

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            d00_=ov.Octet,
            d01_=ov.Octet,
            d02_=ov.Octet,
            ptr_=WangPtr,
            d05_=ov.Octet,
        )
        self.head = None
        self.body = []
        self.namespace = None

    def commit(self):
        try:
            sect = self.tree.this.get_rec(self.ptr.chs)
        except KeyError:
            print(self.tree.this, "Invalid Document Head sector", self.ptr.chs)
            self.tree.this.add_note("Missing Document")
            return
        if sect.undefined:
            print(self.tree.this, "Unread Document Head sector", self.ptr.chs)
            self.tree.this.add_note("Missing Document")
            return
        self.head = WangDocumentHead(self.tree, sect.lo).insert()

        chs = self.head.hdr.next.chs
        parts = []
        all_present = True
        while chs != (0,0,0):
            sect2 = self.tree.this.get_rec(chs)
            if sect2.undefined:
                print(self.tree.this, "Unread Document Body sector", chs)
                all_present = False
                break
            body = WangDocumentBody(self.tree, sect2.lo).insert()
            if body.part is not None:
                parts.append(body.part)
            chs = body.hdr.next.chs
        if parts:
            that = self.tree.this.create(records=parts)
            that.add_type("Wang Wps File")
            if not all_present:
                that.add_note("Missing sectors")
        else:
            that = None
        self.namespace = NameSpace(
            name = self.head.f00.txt,
            parent = self.tree.namespace,
            priv = self.head,
            this = that,
        )

class SpelunkSector():
    ''' ... '''

    def __init__(self, tree, lo):
        self.tree = tree
        self.lo = lo
        self.prev = None
        self.next = None
        self.chs = None
        self.nchs = (tree.this[lo], 0, tree.this[lo + 1])
        self.key = tree.this[lo+4:lo+6]

    def __repr__(self):
        return "SPS " + str(self.chs) + " " + str(self.nchs)

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
        print(this, "WangWps")

        self.namespace = NameSpace(
            name = '',
            root = this,
            separator = "",
        )

        this.type_case = WangTypeCase("ascii")

        this._keys={}
        for cyl in range(77):
            for sect in range(0, 16):
                ptr = sect * 256 + cyl * 256 * 16
                frag = this[ptr:ptr + 256]
                rec = this.define_rec(
                    artifact.Record(low = ptr, frag = frag, key = (cyl, 0, sect))
                )
                if b'_UNREAD_' in frag.tobytes():
                    self.set_picture('U', lo=ptr)
                    rec.undefined = True

        self.free_list()

        self.set_picture('SB', lo=0x300, legend="Content List")
        documents = []
        for adr in range(0x300, 0x300 + this[0x3ff], 6):
            y = WangDocument(self, adr).insert()
            documents.append(y)

        for document in documents:
            document.commit()

        self.spelunk()
        self.fill_gaps(FillSector)
        this.add_interpretation(self, self.namespace.ns_html_plain)
        this.add_interpretation(self, self.disk_picture)
        self.add_interpretation(more=True)
        # self.make_bitstore_metadata()

    def spelunk(self):
        by_lo = {}
        for i, j in self.gaps():
            i = (i + 0xff) & ~0xff
            j = j & ~0xff
            for lo in range(i, j, 0x100):
                if lo < 0x1000:
                    continue
                if self.this[lo + 6] != 0x41:
                    continue
                spsect = SpelunkSector(self, lo)
                by_lo[lo] = spsect   
        by_chs = {}
        for i in self.this.iter_rec():
            j = by_lo.get(i.lo)
            if j is None:
                continue
            j.chs = i.key
            by_chs[j.chs] = j
        for j in by_chs.values():
            k = by_chs.get(j.nchs)
            if k is None or k.key != j.key:
                continue
            k.prev = j
            j.next = k
        done = set()
        for j in by_chs.values():
            if j.prev is not None:
                continue
            parts = []
            i = j
            key = i.key
            while i and i.key == key and i.chs not in done:
                last = self.this[i.lo+2]
                print(i, self.this[i.lo:i.lo+7].hex(), last)
                if last > 7:
                    parts.append(self.this[i.lo+7:i.lo+last])
                done.add(i.chs)
                i = i.next
            if not parts:
                continue
            if self.this[j.lo+3] == 0x41:
                head = WangDocumentHead(self, j.lo).insert()
                parts.pop(0)
            else:
                head = None
            print("JJ", j, parts, sum(len(x) for x in parts))
            that = self.this.create(records=parts)
            that.add_type("Wang Wps File")
            that.add_note("Spelunked")
            namespace = NameSpace(
                name = "~ORPHAN%02d.%02d" % (j.chs[0], j.chs[2]),
                parent = self.namespace,
                priv = head,
                this = that,
            )

        print("DD", len(done), len(by_chs), len(by_lo))
        for j in by_chs.values():
            if j.chs not in done:
                print("  d", j)

    def make_bitstore_metadata(self):

        date = "20240125"

        filename = self.this.descriptions[0]
        if "/critter/DDHF/2024/Wang" not in filename:
            return
        fnparts = filename.split('/')
        basename = fnparts[-1].replace(".flp","")
        book = fnparts[-2].lower()
        genstand = {
            "bog1": "11002393",
            "bog2": "11002394",
            "bog3": "11002398",
            "bog3b": "11002399",
            "bog4": "11002401",
            "bog5": "11002402",
        }[book]
        papers = {
            "bog1": "30005801",
            "bog2": "30005800",
            "bog3": "30005997",
            "bog3b": "30005998",
            "bog4": "30006033",
            "bog5": "30006050",
        }[book]
        diskid = set()
        for i in sorted(self.namespace):
            j = [x for x in i.ns_render()]
            did = j[15].strip()
            if did:
                diskid.add(did)
        print(diskid)
        assert len(diskid) == 1
        diskid = list(diskid)[0].strip()
        filename = "/tmp/" + book + "/" + basename + ".flp.meta"
        print("FN", filename, book, genstand, diskid)
        with open(filename, "w") as fo:
            fo.write("BitStore.Metadata_version:\n\t1.0\n\n")
            fo.write("BitStore.Access:\n\tpublic\n\n")
            fo.write("BitStore.Filename:\n\tCR_WCS_%s.bin\n\n" % diskid)
            fo.write("BitStore.Format:\n\tBINARY\n\n")
            fo.write("BitStore.Last_edit:\n\t%s phk\n\n" % date)
            fo.write("DDHF.Keyword:\n")
            fo.write("\tARTIFACTS\n")
            fo.write("\tCR/CR80/DOCS\n")
            fo.write("\n")
            fo.write("DDHF.Genstand:\n\t%s\n\n" % genstand)
            fo.write('Media.Summary:\n\t8" Wang WCS floppy, CR %s\n\n' % diskid)
            fo.write('Media.Geometry:\n\t77c 1h 16s 256b\n\n')
            fo.write('Media.Type:\n\t8" Floppy Disk\n\n')
            fo.write("Media.Description:\n")
            fo.write("\tIndhold:\n")
            for i in sorted(self.namespace):
                j = [x for x in i.ns_render()]
                txt = "".join(j[:4]).rstrip()
                if txt:
                    fo.write("\t\t" + txt + "\n")
            fo.write("\t\n")
            fo.write("\tSe også papirer fra samme ringbind: [[Bits:%s]]\n" % papers)
            fo.write("\n")
            fo.write("*END*\n")

    def free_list(self):
        bits = self.this.bits(0x200<<3, 77*16)
        for i, j in enumerate(bits):
            if j == '0':
                self.set_picture('F', lo=i << 8, legend='Marked Free')
