
import autoarchaeologist.rational.r1k_bittools as BitTools

class MagicString(BitTools.R1kSegBase):

    def __init__(self, seg, address, **kwargs):
        super().__init__(
            seg,
            seg.cut(address, 0x14*8),
            title="MAGIC_STRING",
            **kwargs,
        )
        self.text = BitTools.to_text(self.chunk)

    def render(self, chunk, fo):
        fo.write(self.title + ' "' + self.text + '"\n')

class Header(BitTools.R1kSegBase):
    def __init__(self, seg, address, **kwargs):
        super().__init__(
            seg,
            seg.cut(address, 0xc1),
            title="HEADER",
            **kwargs,
        )
        self.compact = True
        self.get_fields(
            ("hdr_f0", 32),
            ("hdr_f1", 32),
            ("hdr_f2", 32),
            ("hdr_f3", 32),
            ("hdr_f4", 32),
            ("hdr_f5", 33),
        )

class Thing1(BitTools.R1kSegBase):
    def __init__(self, seg, up, address, **kwargs):
        super().__init__(
            seg,
            seg.cut(address, 0xe1),
            title="THING1",
            **kwargs,
        )
        self.compact = True
        self.get_fields(
            ("t1_str", 32),
            ("t1_t2", 32),
            ("t1_h2", 32),
            ("t1_h3", 32),
            ("t1_h4", 32),
            ("t1_h5", 32),
            ("t1_h6", 32),
            ("t1_tail", -1),
        )
        self.left = None
        self.right = None
        self.name = None
        self.t2 = None

    def dump(self, fo, pfx=""):
        text = pfx + self.name.text + " -> " + self.t2.text
        fo.write(text.ljust(100) + str(self).ljust(20))
        self.render_fields_compact(fo)
        fo.write('\n')
        if self.left:
            self.left.dump(fo, pfx + "    ")
        if self.right:
            self.right.dump(fo, pfx + "    ")

def mk_thing1(seg, up, address, **kwargs):
    y = Thing1(seg, up, address, **kwargs)
    if y.t1_str:
        Thing6(seg, y.t1_str - 0x34)
        y.name = BitTools.String(seg, y.t1_str)
    y.t2 = mk_thing2(seg, up, y.t1_t2)
    if y.t1_h5:
        try:
            y.left = mk_thing1(seg, up, y.t1_h5)
        except BitTools.MisFit as e:
            print("T1.H5", seg.this, "0x%x" % y.t1_h5, e)
    if y.t1_h6:
        y.right = mk_thing1(seg, up, y.t1_h6)
    return y

class Thing2(BitTools.R1kSegBase):
    def __init__(self, seg, address, **kwargs):
        p = seg.mkcut(address)
        i0 = int(p[32:64], 2)
        super().__init__(
            seg,
            seg.cut(address, 0x40 + i0 * 8),
            title="THING2",
            **kwargs,
        )
        offset = self.get_fields(
            ("t2_h0", 32),
            ("t2_h1", 32),
        )
        self.text = BitTools.to_text(self.chunk[offset:])

    def render(self, chunk, fo):
        fo.write(self.title + " ")
        self.render_fields_compact(fo)
        fo.write(' "' + self.text + '"\n')

def mk_thing2(seg, up, address, **kwargs):
    Thing6(seg, address - 0x34)
    y = Thing2(seg, address, **kwargs)
    return y

class Thing3(BitTools.R1kSegBase):
    def __init__(self, seg, address, **kwargs):
        super().__init__(
            seg,
            seg.cut(address, 0xc0),
            title="THING3",
            **kwargs,
        )
        self.compact = True
        offset = self.get_fields(
            ("t3_h0", 32),
            ("t3_h1", 32),
            ("t3_h2", 32),
            ("t3_h3", 32),
            ("t3_h4", 32),
            ("t3_h5", 32),
            # ("t3_tail", -1),
        )

def mk_thing3(seg, address, **kwargs):
    y = Thing3(seg, address, **kwargs)
    try:
        mk_thing4(seg, y.t3_h2)
    except BitTools.MisFit as e:
        print("T3->T4", seg.this, "0x%x" % y.t3_h2, "\n\t", e)

class Thing4(BitTools.R1kSegBase):
    def __init__(self, seg, address, **kwargs):
        super().__init__(
            seg,
            seg.cut(address, 0xb4),
            title="THING4",
            **kwargs,
        )
        self.compact = True
        offset = self.get_fields(
            ("t4_head", 0x74),
            ("t4_h0", 0x20),
            ("t4_h2", 0x20),
        )

def mk_thing4(seg, address, **kwargs):
    y = Thing4(seg, address, **kwargs)
    if y.t4_h0 != address:
        try:
            mk_thing5(seg, y.t4_h0)
        except BitTools.MisFit as e:
            print("T4->T5", seg.this, "0x%x" % y.t4_h0, "\n\t", e)
    return y

class Thing5(BitTools.R1kSegBase):
    def __init__(self, seg, address, **kwargs):
        super().__init__(
            seg,
            seg.cut(address, 0xb4),
            title="THING5",
            **kwargs,
        )
        self.compact = True
        offset = self.get_fields(
            ("t5_h0", 32),
            ("t5_h1", 32),
            ("t5_h2", 20),
            ("t5_h3", 32),

            ("t5_h4", 32),
            ("t5_h5", 32),
        )

def mk_thing5(seg, address, **kwargs):
    y = Thing5(seg, address, **kwargs)
    if 0 and y.t5_h2:
        try:
            seg.mkcut(y.t5_h2)
        except BitTools.MisFit as e:
            print("T5.h2", seg.this, "0x%x" % y.t5_h2, "\n\t", e)
    if y.t5_h3:
        try:
            seg.mkcut(y.t5_h3)
        except BitTools.MisFit as e:
            print("T5.h3", seg.this, "0x%x" % y.t5_h3, "\n\t", e)
    return y

class Thing6(BitTools.R1kSegBase):
    def __init__(self, seg, address, **kwargs):
        super().__init__(
            seg,
            seg.cut(address, 0x34),
            title="THING6",
            **kwargs,
        )
        self.compact = True
        offset = self.get_fields(
            ("t6_h0", 0x24),
            ("t6_h1", 0x10),
        )

class R1kSegLinkPack():

    def __init__(self, seg, chunk):
        #print("?R1KLP", seg.this, chunk)
        seg.this.add_note("R1K_Link_Pack")
        y = MagicString(seg, chunk.offset)
        self.hdr = Header(seg, y.end)
        a = self.hdr.end
        self.root = []
        n = 0
        while a < self.hdr.hdr_f5:
            y = BitTools.BitPointer(seg, a)
            if y.destination:
                z = mk_thing1(seg, self, y.destination)
                self.root.append((n, z))
            a += 32
            n += 1
        try:
            mk_thing3(seg, self.hdr.hdr_f5)
        except BitTools.MisFit as e:
            print("HDR.F5->T3", seg.this, "0x%x" % self.hdr.hdr_f5)

        if False:
            l = seg.hunt("100000000000000000000011010000001000000000")
            for ch, off, add in l:
                if off and not ch.owner:
                    print(">> 0x%x" % add)
                    seg.mkcut(add)
            seg.hunt_orphans()

        for n, i in self.root:
            seg.tfile.write("[0x%x]:\n" % n)
            i.dump(seg.tfile, "    ")
        seg.tfile.write("\n")
