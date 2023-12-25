'''
   DOMUS filesystem
   ----------------

   As described in RCSL-43-GL-7915
'''

from ..generic import disk
from ..base import namespace
from ..base import octetview as ov

# Size of sectors
SEC_SIZE = (1 << 9)

class Kit(ov.Struct):
    '''
        Unit description block (cf. RCSL-43-GL-7915 p.5)
        ------------------------------------------------

        Words 6 to 255 are documented as "not used", but
        the first two are conspicuously zero on all extant
        filesystems.
    '''
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            sys_slice_size_=ov.Be16,
            slice_size_=ov.Be16,
            sectors_on_unit_=ov.Be16,
            free_sectors_=ov.Be16,
            first_data_sector_=ov.Be16,
            top_data_sector_=ov.Be16,
            more=True,
        )
        self.done(SEC_SIZE)

class Slice(ov.Struct):
    '''
        Index block (cf. RCSL-43-GL-7915 p.5)
        -------------------------------------
    '''
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            count_=ov.Be16,
            sector_=ov.Be16,
        )

class Index(ov.Struct):
    '''
        Index block (cf. RCSL-43-GL-7915 p.5)
        -------------------------------------
    '''
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            count_=ov.Be16,
            more=True,
        )
        self.slices = []
        if self.count.val <= 127:
            for i in range(self.count.val):
                self.addfield("a%03d" % i, Slice)
                self.slices.append(getattr(self, "a%03d" % i))
        self.done(SEC_SIZE)
        self.tree.set_picture('I', lo=lo)

    def __iter__(self):
        for slice in self.slices:
            for i in range(slice.count.val):
                yield slice.sector.val + i

class NameSpace(namespace.NameSpace):
    ''' ... '''

    TABLE = (
        ("r", "w3"),
        ("r", "w4"),
        ("r", "w5"),
        ("r", "attrib"),
        ("r", "attrib"),
        ("r", "length"),
        ("r", "idxblk"),
        ("r", "alloc"),
        ("r", "w10"),
        ("r", "w11"),
        ("r", "w12"),
        ("r", "w13"),
        ("r", "w14"),
        ("r", "w15"),
        ("l", "name"),
        ("l", "artifact"),
    )

    def ns_render(self):
        cateng = self.ns_priv
        return [
            hex(cateng.w3.val),
            hex(cateng.w4.val),
            hex(cateng.w5.val),
            hex(cateng.attrib.val),
            cateng.attr_string(),
            cateng.length.val,
            cateng.idxblk.val,
            cateng.alloc.val,
            hex(cateng.w10.val),
            hex(cateng.w11.val),
            hex(cateng.w12.val),
            hex(cateng.w13.val),
            hex(cateng.w14.val),
            hex(cateng.w15.val),
        ] + super().ns_render()

class CatEnt(ov.Struct):
    '''
        Catalog Entry (cf. RCSL-43-GL-7915 p.11)
        ----------------------------------------
    '''
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            name_=ov.Text(6),
            w3_=ov.Be16,
            w4_=ov.Be16,
            w5_=ov.Be16,
            attrib_=ov.Be16,
            length_=ov.Be16,
            idxblk_=ov.Be16,
            alloc_=ov.Be16,
            w10_=ov.Be16,
            w11_=ov.Be16,
            w12_=ov.Be16,
            w13_=ov.Be16,
            w14_=ov.Be16,
            w15_=ov.Be16,
            more=True,
        )
        self.name.txt = self.name.txt.rstrip()
        self.done(32)
        self.namespace = None
        self.subcat = None
        self.is_cat = self.attr(0)
        self.is_subcat = self.attr(1)
        self.is_big = self.attr(9)
        self.is_permanent = self.attr(11)
        self.is_write_protect = self.attr(12)
        self.is_entry_only = self.attr(13)
        self.is_device = self.attr(14)
        self.is_extendable = self.attr(15)
        self.idx = None
        self.this = None

    def attr_string(self):
        b = ['.'] * 8
        if self.is_subcat:
            b[1] = 'S'
        if self.is_big:
            b[2] = 'B'
        if self.is_permanent:
            b[3] = 'P'
        if self.is_write_protect:
            b[4] = 'W'
        if self.is_entry_only:
            b[5] = 'E'
        if self.is_device:
            b[6] = 'D'
        if self.is_extendable:
            b[7] = 'V'
        elif not self.is_entry_only:
            b[7] = 'F'
        return ''.join(b)

    def attr(self, n):
        return (self.attrib.val >> (15-n)) & 1

    def commit(self, pnamespace):
        self.namespace = NameSpace(
            name = self.name.txt,
            parent = pnamespace,
            priv = self,
            separator = ".",
        )
        if not self.length.val:
            return
        if self.name.txt == "SYS":
            return
        if self.is_entry_only:
            return
        if self.is_device:
            return
        if self.is_cat:
            return
        if self.is_subcat:
            return
        self.idx = Index(
            self.tree,
            self.tree.offset + self.idxblk.val * SEC_SIZE
        ).insert()
        l = []
        for i in self.idx:
            off = self.tree.offset + i * SEC_SIZE
            d = disk.DataSector(
                self.tree,
                lo=off,
                hi=off+SEC_SIZE,
                namespace=self.namespace
            ).insert()
            if len(l) < self.length.val:
                l.append(self.tree.this[off:off + SEC_SIZE])
        if l:
            that = self.tree.this.create(bits = b''.join(l))
            self.namespace.ns_set_this(that)
        else:
            print(self.tree.this, "no that", self.namespace, self, l)

class Cat():
    def __init__(self, tree, pnamespace, idxblk):
        self.tree = tree
        self.pnamespace = pnamespace
        self.idxblk = idxblk

        self.idx = Index(self.tree, self.tree.offset + idxblk * SEC_SIZE).insert()
        self.catents = []

        for i in self.idx:
            off = self.tree.offset + i * SEC_SIZE
            self.tree.set_picture('C', lo=off)
            for j in range(0, SEC_SIZE, 32):
                catent = CatEnt(self.tree, off + j).insert()
                if catent.attrib.val in (0, 0xe5e5):
                    continue
                if catent.attrib.val not in (
                    0x0001,
                    0x0006,
                    0x0010,
                    0x0011,
                    0x0016,
                    0x0018,
                    0x0019,
                    0x0041,
                    0x0051,
                    0x0058,
                    0x4010,
                    0x8010,
                ):
                    print(self.tree.this, "BOGUS", catent)
                    continue
                self.catents.append(catent)

    def commit(self):
        for catent in self.catents:
            if not catent.attrib.val:
                continue
            if not catent.name.txt:
                continue
            try:
                catent.commit(self.pnamespace)
            except:
                print("CEFAIL", catent)
        for catent in self.catents:
            if not catent.is_subcat:
                continue
            if not catent.name.txt:
                continue
            try:
                catent.subcat = Cat(self.tree, catent.namespace, catent.idxblk.val)
                catent.subcat.commit()
            except:
                print("SUBCAT FAIL", catent)

class Domus_Filesystem(disk.Disk):

    def __init__(self, this):

        if not this.top in this.parents:
            return

        for geom in (
            [  77, 1, 26, 128],
            [ 203, 2, 12, 512],
            [   0, 0,  0,   0],
        ):
            if len(this) == geom[0] * geom[1] * geom[2] * geom[3]:
                break

        if not sum(geom):
            return
        # print(this, len(this), geom)
        super().__init__(
            this,
            [ geom ]
        )

        self.kit = None
        for idx in range(0xc00, 128 * SEC_SIZE, SEC_SIZE):  # Largest seen: 76
            if this[idx:idx+6] not in (
                b'\x00\x01\x00\x02\x00\x08',
                b'\x00\x01\x00\x03\x00\x08',
            ):
                continue

            kit = Kit(self, idx + SEC_SIZE)
            if kit.top_data_sector.val < 100:
                continue
            if kit.top_data_sector.val <= kit.first_data_sector.val:
                continue
            if kit.sectors_on_unit.val > len(this) // SEC_SIZE:
                continue
            if kit.sectors_on_unit.val + (idx // SEC_SIZE) - 7 > len(this) // SEC_SIZE:
                continue
            if kit.sys_slice_size.val % kit.slice_size.val:
                continue

            self.kit = kit
            self.offset = idx - 7 * SEC_SIZE
            #self.offset = 0
            break

        if not self.kit:
            return
        self.this.add_type("DOMUS Filesystem")
        # print(this, "IDX", hex(idx), idx // SEC_SIZE, "OFS", self.offset, "Kit", kit)

        self.kit.insert()
        self.set_picture('K', lo=self.kit.lo)
        mapidx = Index(self, self.offset + 7 * SEC_SIZE).insert()

        self.namespace = NameSpace(
            name="",
            root=this,
        )
        self.sys = Cat(self, self.namespace, 6)
        self.sys.commit()

        this.add_interpretation(self, self.namespace.ns_html_plain)

        self.picture_legend['I'] = "Index"
        self.picture_legend['C'] = "Catalog"
        self.picture_legend['K'] = "Kit"
        this.add_interpretation(self, self.disk_picture, more=True)

        self.fill_gaps()

        self.add_interpretation(more=True)
