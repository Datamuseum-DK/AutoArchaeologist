#'''
#   R1000 '97' segments
#   ===================
#
#   To be totally honest, I'm not sure what these segments contain.
#   Initially I was pretty sure they were the Diana-Trees, but I have
#   come to doubt that somewhat after seeing more of them.
#
#   The overall structure is that there is a header which points into
#   the segment, where "chunks" are appended as needed
#
#   pointers are up to 32bit wide and point to the bit-offset into the segment.
#
#   The code is very brute-force:  We convert the artifact to a binary
#   (Unicode-)string, and operate on that, using `int(...., 2)` when we
#   want a value.
#
#   For a lot of type `97` segments, this code accounts for all bits,
#   save four extents, three in the header, and the end of the segment
#   which is belived to be unallocated.
#
#   There are also plenty of seqments where this code explodes, those
#   are "for further study"
#
#'''

import autoarchaeologist.rational.r1k_bittools as bittools

def make_one(self, attr, cls, **kwargs):
    a = getattr(self, attr)
    if not a:
        return
    self.seg.fdot.write("X_%x -> X_%x\n" % (self.begin, a))
    p = self.seg.mkcut(a)
    if isinstance(p.owner, cls):
        return
    if p.owner:
        print("COLL 0x%x" % a, self, attr, p.owner)
        return
    try:
        cls(self.seg, a, **kwargs)
    except bittools.MisFit as e:
        print("MISFIT 0x%x" % a, self, attr, e)

def what_is(self, attr):
    a = getattr(self, attr)
    if not a:
        return
    p = self.seg.starts.get(a)
    if not p:
        return
    self.seg.fdot.write("X_%x -> X_%x [color=red]\n" % (self.begin, p.begin))
    if p.owner:
        print("IS 0x%06x" % a, self, attr, p.owner)

class Thing13(bittools.R1kSegBase):
    def __init__(self, seg, address, **kwargs):
        p = seg.mkcut(address)
        c = seg.cut(address, 0x83)
        super().__init__(seg, c, title="THING13", **kwargs)
        self.compact = True
        offset = self.get_fields(
            ("t13_0", 32),
            ("t13_1", 32),
            ("t13_3",  3),
            ("t13_4", 32),
            ("t13_5", 32),
        )
        make_one(self, "t13_0", Thing9)
        make_one(self, "t13_4", Thing12)
        make_one(self, "t13_5", Thing7)

class Thing12(bittools.R1kSegBase):
    def __init__(self, seg, address, **kwargs):
        p = seg.mkcut(address)
        c = seg.cut(address, 0x7f)
        super().__init__(seg, c, title="THING12", **kwargs)
        self.compact = True
        offset = self.get_fields(
            ("t12_n", -1),
        )

class Thing10(bittools.R1kSegBase):
    def __init__(self, seg, address, **kwargs):
        p = seg.mkcut(address)
        c = seg.cut(address, 0x34)
        super().__init__(seg, c, title="THING10", **kwargs)
        self.compact = True
        offset = self.get_fields(
            ("t10_n", -1),
        )

class Thing9(bittools.R1kSegBase):
    def __init__(self, seg, address, **kwargs):
        c = seg.cut(address, 0xa0)
        super().__init__(seg, c, title="THING9", **kwargs)
        self.compact = True
        offset = self.get_fields(
            ("t9_0", 37),
            ("t9_1", 32),
            ("t9_2", 15),
            ("t9_3", 77),
        )
        make_one(self, "t9_1", Thing10)

class Thing8(bittools.R1kSegBase):
    def __init__(self, seg, address, **kwargs):
        p = seg.mkcut(address)
        i = int(p[0xc0:0xe0], 2)
        c = seg.cut(address, 0xe0 + i * 8)
        super().__init__(seg, c, title="THING8", **kwargs)
        # self.compact = True
        offset = self.get_fields(
            ("t8_0", 32),
            ("t8_1", 32),
            ("t8_2", 32),
            ("t8_3", 32),
            ("t8_4", 32),
            ("t8_5", 32),
            ("t8_6", 32),
        )
        _i, self.text = bittools.to_text(seg, self.chunk, offset, self.t8_6)
        make_one(self, "t8_1", Thing8)
        make_one(self, "t8_2", Thing9)

    def render(self, chunk, fo):
        fo.write(self.title)
        self.render_fields_compact(fo)
        fo.write(' "' + self.text + '"\n')
        
class Thing7(bittools.R1kSegBase):
    def __init__(self, seg, address, **kwargs):
        p = seg.mkcut(address)
        c = seg.cut(address, 0x83)
        super().__init__(seg, c, title="THING7", **kwargs)
        self.compact = True
        offset = self.get_fields(
            ("t7_0", 32),
            ("t7_1", 32),
            ("t7_2", 3),
            ("t7_3", 32),
            ("t7_4", 32),
        )
        make_one(self, "t7_0", Thing9)
        make_one(self, "t7_3", Thing12)
        make_one(self, "t7_4", Thing7)
        
class Thing6(bittools.R1kSegBase):
    def __init__(self, seg, address, **kwargs):
        p = seg.mkcut(address)
        c = seg.cut(address, 0x20 * 103)
        super().__init__(seg, c, title="THING6", **kwargs)
        # self.compact = True
        for n, i in enumerate(range(0, len(self.chunk), 0x20)):
            self.fields.append(
                (i, 32, "t6_%d" % n, int(self.chunk[i:i+0x20], 2))
            )
            setattr(self, self.fields[-1][2], self.fields[-1][3])

        for offset, width, name, val in self.fields:
            if val and 0:
                print("T6", self, offset, width, name, "0x%x" % val)
                p = seg.mkcut(val)
                if p[0] == '0':
                    make_one(self, name, Thing7)
                else:
                    make_one(self, name, Thing8)


class Thing5(bittools.R1kSegBase):
    def __init__(self, seg, address, **kwargs):
        seg.this.add_note("THING5_97")
        p = seg.mkcut(address)
        n = int(p[32:64], 2)
        if n <= address:
            print("T5?", seg.this, "N 0x%x" % n, "Address 0x%x" % address)
            return
        assert n >= address
        c = seg.cut(address, min(n - address, 0x80))
        super().__init__(seg, c, title="THING5", **kwargs)
        # self.compact = True
        for n, i in enumerate(range(0, len(self.chunk), 0x20)):
            self.fields.append(
                (i, 32, "t5_%d" % n, int(self.chunk[i:i+0x20], 2))
            )
            setattr(self, self.fields[-1][2], self.fields[-1][3])

        for offset, width, name, val in self.fields[2:]:
            if val:
                make_one(self, name, Thing6)

class Thing4(bittools.R1kSegBase):
    def __init__(self, seg, address, **kwargs):
        p = seg.mkcut(address)
        y = int(p[32:64], 2)
        c = seg.cut(address, 0x40 + y * 38)
        super().__init__(seg, c, title="THING4", **kwargs)
        self.compact = True
        offset = self.get_fields(
            ("x", 32),
            ("y", 32),
        )
        self.a = []
        for i in range(offset, len(c), 38):
            j = int(c[i:i+38], 2)
            self.a.append((j >> 15, j & 0x7fff))
            if not j & 0x7fff:
                break

    def render(self, chunk, fo):
        fo.write(self.title)
        self.render_fields_compact(fo)
        fo.write("\n")
        for n, i in enumerate(self.a):
            if i:
                fo.write("  [0x%x] = 0x%x, 0x%x\n" % (n, i[0], i[1]))


class Thing3(bittools.R1kSegBase):
    def __init__(self, seg, address, **kwargs):
        p = seg.mkcut(address)
        y = int(p[32:64], 2)
        # y = 0
        c = seg.cut(address, 0x40 + y * 8)
        super().__init__(seg, c, title="THING3", **kwargs)
        self.compact = True
        offset = self.get_fields(
            ("x", 32),
            ("y", 32),
        )
        self.pad = (14 - (self.begin + offset) % 8) % 8
        offset += self.pad
        self.a = []
        while offset < len(self.chunk) - 24:
            i = int(self.chunk.bits[offset:offset+16], 2)
            j = int(self.chunk.bits[offset+16:offset+24], 2)
            offset += 24
            try:
                text = bittools.to_text(seg, self.chunk, offset, j)
            except:
                text = "BOGUS"
            offset += 8 * j
            self.a.append((offset, i, j, text))

    def render(self, chunk, fo):
        fo.write(self.title)
        self.render_fields_compact(fo)
        fo.write("\n")
        for n, i in enumerate(self.a):
            fo.write("    [0x%x] = " % n + str(i) + "\n")

class Thing2(bittools.R1kSegBase):
    '''
        Simple, Singled list elements, one `next` pointer
        and one `payload` pointer
    '''
    def __init__(self, seg, address, payload_handler, **kwargs):
        super().__init__(seg, seg.cut(address, 0x40), title="THING2", **kwargs)
        self.compact = True
        self.get_fields(
            ("payload", 32),
            ("next", 32),
        )
        if self.payload:
            #payload_handler(seg, self.payload)
            make_one(self, "payload", payload_handler)

class Thing1(bittools.R1kSegBase):
    '''
        The `THING1` structure is pointed to from 0xdf,
        and contains the heads & tails of two linked lists.

        Chain1 contains 38 bit wide Arrays of unidentified content.

        Chain2 contains symbol-table-like chunks.
    '''
    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, 0x10c), title="THING1", **kwargs)
        self.get_fields(
            ("t1_unknown0", 0x20),
            ("t1_unknown1", 0x4c),
            ("t1_c1_head", 0x20),
            ("t1_c2_last", 0x20),
            ("t1_array1", 0x20),
            ("t1_c2_tail", 0x20),
            ("t1_c1_tail", 0x20),
        )

        i = self.t1_c1_tail
        seg.fdot.write("X_%x -> X_%x\n" % (self.chunk.begin, i))
        while i:
            follow = Thing2(seg, i, payload_handler=Thing4, ident="Chain1")
            seg.fdot.write("X_%x -> X_%x\n" % (i, follow.next))
            i = follow.next

        i = self.t1_c2_tail
        seg.fdot.write("X_%x -> X_%x\n" % (self.chunk.begin, i))
        while i:
            follow = Thing2(seg, i, payload_handler=Thing3, ident="Chain2")
            seg.fdot.write("X_%x -> X_%x\n" % (i, follow.next))
            i = follow.next

        if self.t1_c2_last:
            make_one(self, "t1_c2_last", Thing3)

        if self.t1_array1:
            make_one(self, "t1_array1", Thing4)



class Head(bittools.R1kSegBase):
    '''
        The start of the segment

    '''
    def __init__(self, seg, **kwargs):
        super().__init__(seg, seg.cut(0x80, 0x380), title="97HEAD", **kwargs)
        #self.compact = True
        self.get_fields(
            ("head_z_000", 32,),           # 0x80000001
            ("head_unknown_020", 32,),     # Unique except for two cases
            ("head_c_040", 31,),           # 0x1
            ("head_chains", 32,),          # 0x231a, one case 0x0
            ("head_z_07f", 1,),            # 0x0
            ("head_z_80", 31,),            # 0x0
            ("head_stuff1", 32,),          # bit-address
            ("head_c_bf", 33,),            # 0x12, one case 0x0
            ("head_unknown_e0", 32,),      # looks like addres, most invalid
            ("head_c_100", 32,),           # 0x4
            ("head_z_120", 32,),           # 0
            ("head_z_140", 32,),           # 0
            ("head_z_160", 32,),           # 0
            ("head_z_180", 32,),           # 0
            ("head_z_1a0", 32,),           # 0
            ("head_z_1c0", 32,),           # 0
            ("head_unknown_1e0", 42,),     # {0x1a00000000,0x800000000,0x1100000000}
            ("head_trees", 32,),           # valid address
            ("head_z_22a",  22,),          # looks like addres, most invalid
            ("head_unknown_240", 32,),     # Logs 0x0, rest random
            ("head_z_260", 32,),           # {0x0, 0x68400000}
            ("head_c_280", 32,),           # 0x400, one 0x0
            ("head_unknown_2a0", 32,),     # random
            ("head_unknown_2c0", 32,),     # random
            ("head_unknown_2e0", 32,),     # random
            ("head_z_300", 32,),           # random
            ("head_z_320", 32,),           # random
            ("head_z_340", 32,),           # random
            ("head_z_360", 32,),           # random
        )

        make_one(self, "head_chains", Thing1)
        make_one(self, "head_trees", Thing5)

class R1kSeg97():

    def __init__(self, seg):
        if len(seg.mkcut(0x80)) <= 0x400:
            return
        self.seg = seg
        seg.fdot = open("/tmp/_.dot", "w")
        seg.fdot.write("digraph {\n")
        self.head = Head(seg)
        seg.fdot.write("}\n")
        seg.fdot.close()
