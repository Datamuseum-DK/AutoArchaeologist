'''
   R1000 '97' segments
   ===================

   To be totally honest, I'm not sure what these segments contain.
   Initially I was pretty sure they were the Diana-Trees, but I have
   come to doubt that somewhat after seeing more of them.

   The overall structure is that there is a header which points into
   the segment, where "chunks" are appended as needed

   pointers are 32bit wide and point to the bit-offset into the segment.

   The code is very brute-force:  We convert the artifact to a binary
   (Unicode-)string, and operate on that, using `int(...., 2)` when we
   want a value.

   For a lot of type `97` segments, this code accounts for all bits,
   save four extents, three in the header, and the end of the segment
   which is belived to be unallocated.

   It looks a lot like the first 32 bits is a pointer to the first free
   bit in the segment, but I can't quite make that work.

   There are also plenty of seqments where this code explodes, those
   are "for further study"

'''

class MisFit(Exception):
    ''' bla '''

class Chunk():

    '''
    A sequence of bits, represented as a python string "0101010101"
    '''

    def __init__(self, offset, bits):
        self.bits = bits
        self.offset = offset
        self.owner = None

    def __len__(self):
        return len(self.bits)

    def __str__(self):
        return "{Chunk 0x%x-0x%x/0x%x}" % (self.offset, self.offset + len(self.bits), len(self.bits))

    def __getitem__(self, idx):
        return self.bits[idx]

def render_chunk(fo, chunk):
    ''' Render the bits in a/our chunk '''
    for j in range(0, len(chunk), 128):
        i = chunk.bits[j:j+128]
        fo.write(("0x%x " % int(i, 2)).rjust(39) + i + "\n")

class Seg97Base():

    '''
    Base class for the bit-structures we find.
    '''

    def __init__(self, seg, chunk, title="", ident=""):
        self.seg = seg
        self.chunk = chunk
        self.title = title
        if ident:
            self.title += " " + ident
        chunk.owner = self
        self.begin = self.chunk.offset
        self.end = self.chunk.offset + len(self.chunk)
        self.fields = []
        self.compact = False

    def __str__(self):
        return "{@0x%x: " % self.begin + self.title + "}" 

    def get_fields(self, *fields):
        '''
        Create numerical fiels, starting at the first bit
        '''
        assert self.chunk
        offset = 0
        for name, width in fields:
            if width < 0:
                width = len(self.chunk[offset:])
            i = int(self.chunk[offset:offset+width], 2)
            setattr(self, name, i)
            self.fields.append((offset, width, name, i))
            offset += width
        return offset

    def render_fields_compact(self, fo):
        ''' Render the fields on a single line'''
        retval = 0
        for offset, width, name, value in self.fields:
            fo.write(" " + name)
            fo.write(" = 0x%x" % value)
            retval = offset + width
        return retval

    def render_fields(self, fo):
        ''' Render the fields '''
        retval = 0
        for offset, width, name, value in self.fields:
            if not self.compact:
                fo.write("    @0x%x:" % offset)
            fo.write(" " + name)
            fo.write(" = 0x%x" % value)
            if not self.compact:
                fo.write(" [%s]\n" % self.chunk[offset:offset+width])
            retval = offset + width
        if self.compact:
            fo.write("\n")
        return retval

    def render_bits(self, fo, chunk=None, offset=0):
        ''' Render the bits in a/our chunk '''
        if chunk is None:
            chunk = self.chunk
        for j in range(offset, len(chunk), 128):
            fo.write("    " + chunk.bits[j:j+128] + "\n")
        
    def render(self, chunk, fo):
        ''' Default render this bit-structure '''
        if self.title:
            fo.write(self.title)
        else:
            fo.write("=" * 40)
        if not self.compact:
            fo.write("\n")
        offset = self.render_fields(fo)
        self.render_bits(fo, chunk=chunk,offset=offset)

class Seg97Pointer(Seg97Base):
    '''
       This is simply a 32-pointer

       Use this a couple of places in the header, until
       we figure out more about the headers structure.
    '''
    def __init__(self, seg, address, ident=None):
        super().__init__(seg, seg.cut(address, 0x20))
        self.get_fields(("destination", 32))
        self.title = "POINTER"
        if ident:
            self.title += " " + ident

    def render(self, chunk, fo):
        fo.write(self.title)
        self.render_fields_compact(fo)
        fo.write("\n")

class Seg97Array(Seg97Base):
    '''
       This looks a lot like a native R1000 array layout
       Two 32 bit fields with 'first and 'last indices
       followed by that many array elments.
    '''
    def __init__(self, seg, address, width, ident=""):
        p = seg.cut(address)
        self.first = int(p[:32], 2)
        assert self.first == 1
        self.last = int(p[32:64], 2)
        p = seg.cut(address, 64 + (1 + self.last - self.first) * width)
        super().__init__(seg, p)
        self.compact = True
        self.width = width
        self.title = "ARRAY 0x%x[0x%x..0x%x]" % (width, self.first, self.last)
        if ident:
            self.title += " " + ident
        self.get_fields(
            ("first", 32),
            ("last", 32),
        )

    def render(self, chunk, fo):
        fo.write(self.title + "\n")
        offset = 64
        for i in range(self.first, self.last + 1):
            j = self.chunk[offset:offset+self.width]
            fo.write("\t[0x%x] " % i + j + "  0x%x" % int(j, 2) + "\n")
            offset += self.width

class Seg97Chain2(Seg97Array):
    '''
       Chain2 are laid out like arrays of 8-bit bytes,
       that is 32+32 'first and 'last, then that many bytes.

       The payload field consists or:
           [optional padding, 0-7 bits]
           N * ([a, 16 bit] [b, 8 bit] [c, b * 8 bits])

       The padding aligns the first `a` field on (X % 8 == 6)

       The `a` field looks like a symbol index number

       The `c` field is a symbol or character constant as 3 bytes "'X'"

       The payload field is often larger than the sane content and it
       is not obvious what the correct termination condition is.

       As the symbol table grows, Chain2 structures are appended, and
       a `LIST` header added, to put them all on a linked list.

       The `CHAIN` header contains pointers to the last `CHAIN2`
       structure and the head of the chain.

    '''
    def __init__(self, seg, address):
        super().__init__(seg, address, 8, "Chain2")
        self.title = "CHAIN2 [0x%x..0x%x]" % (self.first, self.last)

    def render(self, chunk, fo):
        fo.write(self.title + "\n")
        offset = 64
        i = self.chunk.offset % 8
        if i == 7:
            offset += 7
        else:
            offset += 6 - i
        while offset < len(self.chunk) - 24:
            j = self.chunk[offset:offset+16]
            x = int(j, 2)
            fo.write("\t[0x%04x]" % x)
            offset += 16

            j = self.chunk[offset:offset+8]
            y = int(j, 2)
            fo.write("  [0x%02x]" % y)
            offset += 8

            if not x or not y or len(self.chunk[offset:]) < y * 8:
                fo.write("\n")
                break

            text = "  "
            length = int(j, 2)
            for c in range(length):
                if len(self.chunk[offset:]) < 8:
                    break
                j = self.chunk[offset:offset+8]
                char = int(j, 2)
                if 32 < char < 126:
                    text += "%c" % char
                else:
                    text += "\\x%02x" % char
                offset += 8
            fo.write(text)
            fo.write("\n")
        if offset < len(self.chunk):
            fo.write("\t0x%x trailing bits\n" % (len(self.chunk) - offset))
            #self.render_bits(fo, offset=offset)

class Seg97List(Seg97Base):
    '''
        Simple, Singled list elements, one `next` pointer
        and one `payload` pointer
    '''
    def __init__(self, seg, address, ident=""):
        super().__init__(seg, seg.cut(address, 0x40))
        self.get_fields(
            ("payload", 32),
            ("next", 32),
        )
        self.title = "LIST" + ident

class Seg97Chains(Seg97Base):
    '''
        The `CHAINS` structure is pointed to from 0xdf,
        and contains the heads & tails of two linked lists.

        Chain1 contains 38 bit wide Arrays of unidentified content.

        Chain2 contains symbol-table-like chunks.
    '''
    def __init__(self, seg, address):
        self.address = address
        super().__init__(seg, seg.cut(self.address, 0x10c))
        self.title = "CHAINS"
        self.get_fields(
            ("chain_unknown0", 0x20),
            ("chain_unknown1", 0x4c),
            ("chain1_head", 0x20),
            ("chain2_last", 0x20),
            ("chain_array1", 0x20),
            ("chain2_tail", 0x20),
            ("chain1_tail", 0x20),
        )

        if self.chain2_last:
            Seg97Chain2(seg, self.chain2_last)

        i = self.chain2_tail
        while i:
            follow = Seg97List(seg, i, " Chain2")
            i = follow.next
            if follow.payload:
                Seg97Chain2(seg, follow.payload)

        if self.chain1_head:
            Seg97Array(seg, self.chain_array1, 38, "Chain1")

        i = self.chain1_tail
        while i:
            follow = Seg97List(seg, i, " Chain1")
            i = follow.next
            if follow.payload:
                Seg97Array(seg, follow.payload, 38, "Chain1")

class Seg97Thing0(Seg97Base):
    '''
        Unknown structure.
        Very likely a R1000 native descriptor.
    '''
    def __init__(self, seg, address, ident=""):
        super().__init__(seg, seg.cut(address, 0x34))
        self.title = "THING0"
        if ident:
            self.title += " "+ ident
        self.get_fields(
            ("unknown0", -1),
        )

def mk_thing0(seg, address, **kwargs):
    try:
        y = Seg97Thing0(seg, address, **kwargs)
    except MisFit as e:
        print("MISFIT THING0", seg.this, e)
        return None
    return y

class Seg97Thing1(Seg97Base):
    '''
        Unknown structure.
        Points to `THING0`
    '''
    def __init__(self, seg, address, ident=""):
        super().__init__(seg, seg.cut(address, 0xa0))
        self.title = "THING1"
        if ident:
            self.title += " "+ ident
        self.get_fields(
            ("unknown0", 50),
            ("thing0", 19),
            ("unknown2", 15),
            ("unknown3", -1),
        )

def mk_thing1(seg, address, **kwargs):
    try:
        y = Seg97Thing1(seg, address, **kwargs)
    except MisFit as e:
        print("MISFIT THING1", seg.this, e)
        return None
    if y.thing0:
        mk_thing0(seg, y.thing0)
    return y

class Seg97Thing2(Seg97Base):
    '''
        Unknown structure.
        Points to `THING4` and more `THING2`
    '''
    def __init__(self, seg, address, ident=""):
        super().__init__(seg, seg.cut(address, 0x83))
        self.title = "THING2"
        if ident:
            self.title += " "+ ident
        self.get_fields(
            ("unknown0", 32),
            ("unknown1", 32),
            ("thing4", 35),
            ("thing2", -1),
        )

def mk_thing2(seg, address, **kwargs):
    try:
        y = Seg97Thing2(seg, address, **kwargs)
    except MisFit as e:
        print("MISFIT THING2", seg.this, e)
        return None
    if y.thing2:
        mk_thing2(seg, y.thing2)
    if y.thing4:
        mk_thing4(seg, y.thing4)
    return y

#######################################################################

class Seg97Thing3(Seg97Base):
    '''
        `head->tree-header->table2->thing6->thing3`
    '''

    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, 0x7f), title="THING3", **kwargs)
        self.compact = True
        self.get_fields(
            ("t3_hdr", 31),
            ("t3_unknown1", 32),
            ("t3_unknown2", 32),
            ("t3_unknown3", 32),
        )

def mk_thing3(seg, address, **kwargs):
    t = seg.get(address)
    if t and isinstance(t.owner, Seg97Thing3):
        return t.owner
    try:
        x = Seg97Thing3(seg, address, **kwargs)
    except MisFit as e:
        print("MISFIT THING3", seg.this, e)
        return None
    if x.t3_unknown3:
        mk_thing3(seg, x.t3_unknown3, ident="t3_u3")
    p = seg.mkcut(x.end)
    if len(p) >= 0x7f:
        i = int(p[31:63], 2)
        if i == x.t3_unknown1:
            mk_thing3(seg, x.end)
    return x


#######################################################################

class Seg97Thing4(Seg97Base):
    '''
        `head->tree-header->table2->thing7->thing4`
    '''

    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, 0xa0), title="THING4", **kwargs)
        self.compact = True
        self.get_fields(
            ("t4_hdr", 13),
            ("t4_z1", 24),
            ("t4_unknown2", 32),
            ("t4_idx", 15),
            ("t4_z4", -1),
        )

def mk_thing4(seg, address, **kwargs):
    t = seg.get(address)
    if t and isinstance(t.owner, Seg97Thing4):
        return t.owner
    try:
        x = Seg97Thing4(seg, address, **kwargs)
    except MisFit as e:
        print("MISFIT THING4", seg.this, e)
        return None
    assert not x.t4_z1 
    assert not x.t4_z4 
    if x.t4_unknown2:
        Seg97Soak(seg, x.t4_unknown2, 0x34, ident="t4_u2")
    return x

#######################################################################

class Seg97Thing5(Seg97Base):
    '''
        `head->tree-header->table0->thing5`
    '''
    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, 71), title="THING5", **kwargs)
        self.compact = True
        self.get_fields(
            ("t5_unknown0", 39),
            ("t5_thing5", 32),
        )

def mk_thing5(seg, address, **kwargs):
    t = seg.get(address)
    if t and isinstance(t.owner, Seg97Thing5):
        return t.owner
    try:
        y = Seg97Thing5(seg, address, **kwargs)
    except MisFit as e:
        print("MISFIT THING5", seg.this, e)
        return None
    if y.t5_thing5:
        mk_thing5(seg, y.t5_thing5)
    return y

#######################################################################

class Seg97Thing6(Seg97Base):
    '''
        `head->tree-header->table1->thing6`
    '''
    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, 0x83), title="THING6", **kwargs)
        self.compact = True
        self.get_fields(
            ("t6_unknown0", 3),
            ("t6_unknown1", 32),
            ("t6_unknown2", 32),
            ("t6_t3", 32),
            ("t6_unknown4", 32),
        )

def mk_thing6(seg, address, **kwargs):
    t = seg.get(address)
    if t and isinstance(t.owner, Seg97Thing6):
        return t.owner
    try:
        x = Seg97Thing6(seg, address, **kwargs)
    except MisFit as e:
        print("MISFIT THING6", seg.this, e)
        return None
    if x.t6_t3:
        mk_thing3(seg, x.t6_t3, ident="t6_u3")
    if x.t6_unknown4:
        seg.mkcut(x.t6_unknown4)
    return x

#######################################################################

class Seg97Thing7(Seg97Base):
    '''
        `head->tree-header->table2->thing7`
    '''
    def __init__(self, seg, address, length, **kwargs):
        super().__init__(seg, seg.cut(address, 0xe0 + length * 8), title="THING7", **kwargs)
        self.compact = True
        offset = self.get_fields(
            ("t7_hdr", 32),
            ("t7_t7", 32),
            ("t7_t4", 32),
            ("t7_unknown3", 32),
            ("t7_unknown4", 32),
            ("t7_unknown5", 32),
            ("t7_unknown6", 24),
            ("t7_len", 8),
        )
        assert self.t7_len == length, "0x%x vs 0x%x" % (self.t7_len, length)
        self.text = ""
        for i in range(length):
            j = int(self.chunk[offset:offset+8], 2)
            if 32 < j <= 126:
                 self.text += "%c" % j 
            else:
                 self.text += "\\x%02x" % j 
            offset += 8
        self.title += " " + self.text
        
    def render(self, chunk, fo):
        ''' Default render this bit-structure '''
        if self.title:
            fo.write(self.title)
        else:
            fo.write("=" * 40)
        if not self.compact:
            fo.write("\n")
        offset = self.render_fields(fo)


def mk_thing7(seg, address, **kwargs):
    t = seg.get(address)
    if t and isinstance(t.owner, Seg97Thing7):
        return t.owner
    p = seg.mkcut(address)
    i = int(p[0xd8:0xe0], 2)
    try:
        x = Seg97Thing7(seg, address, i, **kwargs)
    except MisFit as e:
        print("MISFIT THING7", seg.this, e)
        return None
    if x.t7_t4:
        mk_thing4(seg, x.t7_t4, ident="t7_t4")
    if x.t7_t7:
        mk_thing7(seg, x.t7_t7, ident="t7_u1")
    return x

#######################################################################

class Seg97PointerArray(Seg97Base):
    '''
        Array of pointers, where the non-zero elements point to
        the same kind of thing.  See under `TREES` below
    '''
    def __init__(self, seg, address, length, ident=""):
        super().__init__(seg, seg.cut(address, length))
        self.title = "POINTER TABLE"
        if ident:
            self.title = " "+ ident
        self.fields = []
        for n, a in enumerate(range(0, len(self.chunk), 0x20)):
            i = self.chunk[a:a+0x20]
            j = int(i, 2)
            if j:
                self.fields.append((n, a, j))

    def __iter__(self):
        for n, a, j in self.fields:
            yield n, j

    def render(self, chunk, fo):
        fo.write(self.title + "\n")
        if not len(self.fields):
            fo.write("\t{empty}\n")
            return
        for n, a, j in self.fields:
            i = self.chunk[a:a+0x20]
            assert(j)
            fo.write("\t[0x%x] = 0x%x  [%s]\n" % (n, j, i))

class Seg97Trees(Seg97Base):
    '''
        This structure is not always present.

        It contains three pointers to starts of three pointer-arrays.

        First pointer-array points to 'THING5' which again points to THING6.

        Second pointer-array points to 'THING2' which again points to
        THING4 and more THING2s.

        Third pointer-array points to 'THING3' which again points to THING1,
        and from there to THING0, and also more THING3s.  All THING3s are
        followed by a STRING.
    '''

    def __init__(self, seg, address):

        # Assume that the table0 pointer points right past the Tree header
        p = seg.cut(address)
        size = int(p[32:64], 2) - address
        super().__init__(seg, seg.cut(address, size))
        self.title = "TREE HEADER"

        flds = ()
        for i, j in enumerate(range(0, size, 0x40)):
            flds += (("tree_unknown%d" % i, 0x20), ("tree_table%d" % i, 0x20), )
        self.get_fields(*flds)

        if size == 0x40:
            # Assume that the first table entry points right
            # past the single table (evidence: ⟦bba8365f⟧)
            p = seg.cut(self.end)
            i = int(p[:32], 2)
            assert i
            assert i > self.end
            n = (i - self.end) // 0x20
        elif size >= 0x80:
            # Assume the first table ends where the next starts
            n = (self.tree_table1 - self.tree_table0) // 0x20
        x = Seg97PointerArray(seg, self.tree_table0, 0x20 * n, ident="TREE_TABLE0")
        for index, addr in x:
            mk_thing5(seg, addr, ident="tree_table0[0x%x]" % index)

        if size == 0xc0:
            # Assume the second and third table are the same,
            # and that the third follows the second
            n = (self.tree_table2 - self.tree_table1) // 0x20
            x = Seg97PointerArray(seg, self.tree_table1, 0x20 * n, ident="TREE_TABLE1")
            for index, addr in x:
                mk_thing6(seg, addr, ident="tree_table1[0x%x]" % index)
            x = Seg97PointerArray(seg, self.tree_table2, 0x20 * n, ident="TREE_TABLE2")
            for index, addr in x:
                mk_thing7(seg, addr, ident="tree_table2[0x%x]" % index)

class Seg97Stuff1(Seg97Base):
    def __init__(self, seg, address):
        super().__init__(seg, seg.cut(address, 0xb3))
        self.title = "STUFF1 object"
        self.get_fields(
            ("stuff1_ident", 21),
            ("stuff1_unknown1", 42),
            ("stuff1_stuff5", 32),
            ("stuff1_unknown4", 20),
            ("stuff1_unknown5", 32),
            ("stuff1_unknown6", 32),
        )

def mk_stuff1(seg, address):

    t = seg.get(address)
    if t and isinstance(t.owner, Seg97Stuff1):
        return t.owner

    try:
        x = Seg97Stuff1(seg, address)
    except MisFit as e:
        print("MISFIT", seg.this, "S1 0x%x" % address, e)
        return None

    if x.stuff1_stuff5:
        try:
            mk_stuff5(seg, x.stuff1_stuff5)
        except MisFit as e:
            print("MISFIT", seg.this, "S1.stuff5 0x%x" % x.stuff1_stuff5)

    #seg.mkcut(x.stuff1_unknown5)
    #seg.mkcut(x.stuff1_unknown6)
    return x

class Seg97Stuff2(Seg97Base):
    def __init__(self, seg, address):
        super().__init__(seg, seg.cut(address, 0x35))
        self.title = "STUFF2 object"
        self.get_fields(
            ("s2_unknown0", 0x35 - 21),
            ("s2_stuff3", 21)
        )

    def render(self, chunk, fo):
        fo.write(self.title)
        self.render_fields_compact(fo)
        fo.write("\n")

def mk_stuff2(seg, address):
    t = seg.get(address)
    if t and isinstance(t.owner, Seg97Stuff2):
        return t.owner
    try:
        x = Seg97Stuff2(seg, address)
    except MisFit as e:
        print("MISFIT", seg.this, "S2 0x%x" % address, e)
        return None
    if x.s2_stuff3:
        try:
            mk_stuff3(seg, x.s2_stuff3)
        except MisFit as e:
            print("MISFIT", seg.this, "S3.stuff3 0x%x" % x.s2_stuff3)
    return x


class Seg97Stuff3(Seg97Base):
    def __init__(self, seg, address):
        super().__init__(seg, seg.cut(address, 0x77))
        self.title = "STUFF3 object"
        self.get_fields(
            ("unknown0", 21),
            ("stuff4", 22),
            ("unknown2", 41),
            ("zero", -1),
        )

    def render(self, chunk, fo):
        fo.write(self.title)
        self.render_fields_compact(fo)
        fo.write("\n")

def mk_stuff3(seg, address):
    t = seg.get(address)
    if t and isinstance(t.owner, Seg97Stuff3):
        return t.owner
    p = seg.mkcut(address)
    if int(p[:21], 2) != 0x13b170:
        return None
    try:
        y = Seg97Stuff3(seg, address)
    except MisFit as e:
        print("MISFIT", seg.this, "S3 0x%x" % address, e)
        return None
    if 0 and y.stuff4:
        try:
            mk_stuff4(seg, y.stuff4)
        except MisFit as e:
            print("MISFIT", seg.this, "S3 0x%x" % address, "-> S4 0x%x" % y.stuff4)
    return y

class Seg97Stuff4(Seg97Base):
    def __init__(self, seg, address):
        super().__init__(seg, seg.cut(address, 0x70))
        self.title = "STUFF4 object"
        self.get_fields(
            ("unknown0", 17),
            ("stuff5", 26),
            ("unknown2", 26),
            ("stuff2_3", 26),
            ("unknown4", -1),
        )

    def render(self, chunk, fo):
        fo.write(self.title)
        self.render_fields_compact(fo)
        fo.write("\n")

def mk_stuff4(seg, address):
    t = seg.get(address)
    if t and isinstance(t.owner, Seg97Stuff4):
        return t.owner
    try:
        x = Seg97Stuff4(seg, address)
    except MisFit as e:
        print("MISFIT", seg.this, "S4 0x%x" % address, e)
        return None
    if x.unknown0 and not seg.get(x.unknown0):
        try:
            y = seg.cut(x.unknown0)
        except MisFit as e:
            print("MISFIT", seg.this, "S4.unknown0 0x%x" % x.unknown0, e)
    print("X4 0x%x" % x.unknown0, "0x%x" % x.stuff5)
    if x.stuff5 in (0, 0x1016f, 0x10110,):
        pass
    elif x.stuff5:
        try:
            y = mk_stuff5(seg, x.stuff5)
        except MisFit as e:
            print("MISFIT", seg.this, "S4.stuff5 0x%x" % x.stuff5, e)
    return x
    if x.unknown2 and not seg.get(x.unknown2):
        try:
            y = seg.cut(x.unknown2)
        except MisFit as e:
            print("MISFIT", seg.this, "S4.2 0x%x" % x.unknown2, e)
    if x.unknown0 == 0x103a9 and x.stuff2_3:
        try:
            y = mk_stuff2(seg, x.stuff2_3)
        except MisFit as e:
            print("MISFIT", seg.this, "S4.stuff2_3(3) 0x%x" % x.stuff2_3, e)
    elif x.stuff2_3:
        try:
            y = mk_stuff3(seg, x.stuff2_3)
        except MisFit as e:
            print("MISFIT", seg.this, "S4.stuff2_3(2) 0x%x" % x.stuff2_3, e)
    return x

class Seg97Stuff5(Seg97Base):
    def __init__(self, seg, address):
        super().__init__(seg, seg.cut(address, 0x70))
        self.title = "STUFF5 object"
        self.get_fields(
            ("stuff5_ident", 21),
            ("stuff5_stuff1", 22),
            ("stuff5_unknown2", 28),
            ("stuff5_stuff6", 24),
            ("stuff5_tail", -1),
        )

def mk_stuff5(seg, address):
    t = seg.get(address)
    if t and isinstance(t.owner, Seg97Stuff5):
        return t.owner
    try:
        x = Seg97Stuff5(seg, address)
    except MisFit as e:
        print("MISFIT", seg.this, "S5 0x%x" % address, e)
        return None
    if x.stuff5_stuff1:
        mk_stuff1(seg, x.stuff5_stuff1)
    if x.stuff5_unknown2:
        seg.mkcut(x.stuff5_unknown2)
    if x.stuff5_stuff6:
        t = seg.mkcut(x.stuff5_stuff6)
        if 1 or t[:11] == "10000000000":
            mk_stuff6(seg, x.stuff5_stuff6)
    return x

class Seg97Stuff6(Seg97Base):
    def __init__(self, seg, address):
        super().__init__(seg, seg.cut(address, 0x8b))
        self.title = "STUFF6 object"
        self.get_fields(
            ("s6_unknown0", 1),
            ("s6_s6", 26),
            ("s6_u1", 32),
            ("s6_u2", 39),
            ("s6_s2", 24),
            ("s6_tail", -1),
        )

    def render(self, chunk, fo):
        fo.write(self.title)
        self.render_fields_compact(fo)
        fo.write("\n")

def mk_stuff6(seg, address):
    t = seg.get(address)
    if t and isinstance(t.owner, Seg97Stuff6):
        return t.owner
    try:
        x = Seg97Stuff6(seg, address)
    except MisFit as e:
        print("MISFIT", seg.this, "S6 0x%x" % address, e)
        return None
    if x.s6_s6:
        mk_stuff6(seg, x.s6_s6)
    if x.s6_s2:
        mk_stuff2(seg, x.s6_s2)
    return x


class Seg97Stuff7(Seg97Base):
    def __init__(self, seg, address):
        super().__init__(seg, seg.cut(address, 0x4a))
        self.title = "STUFF7 object"
        self.get_fields(
            ("unknown0", 32),
            ("unknown1", 5),
            ("unknown2", 4),
            ("unknown3", 28),
            ("unknown4", -1),
        )

    def render(self, chunk, fo):
        fo.write(self.title)
        self.render_fields_compact(fo)
        fo.write("\n")

class Seg97Tail(Seg97Base):
    def __init__(self, seg, address):
        super().__init__(seg, seg.cut(address, -1))
        self.title = "TAIL, unallocated bits"

    def render(self, chunk, fo):
        fo.write(" TAIL (unallocated)\n")

class Seg97Soak(Seg97Base):
    def __init__(self, seg, address, length, ident=None):
        super().__init__(seg, seg.cut(address, length))
        self.title = "SOAK object"
        if ident:
            self.title += " " + ident
        self.compact = True
        self.get_fields(
            #("soak_ident", 21),
            ("soak_tail", -1),
        )

class Seg97Head(Seg97Base):
    '''
        The start of the segment

    '''
    def __init__(self, seg):
        super().__init__(seg, seg.cut(0x0, 0x400))
        self.title = "HEAD"
        self.get_fields(
            ("head_free_ptr", 32,),
            ("head_c_020", 32,),
            ("head_z_040", 32,),
            ("head_unknown_060", 32,),
            ("head_z_080", 32,),
            ("head_unknown_0a0", 32,),
            ("head_c_0c0", 31,),
            ("head_chains", 32,),
            ("head_z_0ff", 1,),
            ("head_z_100", 31,),
            ("head_stuff1", 32,),
            ("head_c_13f", 33,),
            ("head_unknown_160", 32,),
            ("head_c_180", 32,),
            ("head_z_1a0", 32,),
            ("head_z_1c0", 32,),
            ("head_z_1e0", 32,),
            ("head_z_200", 32,),
            ("head_z_220", 32,),
            ("head_z_240", 32,),
            ("head_unknown_260", 42,),
            ("head_trees", 32,),
            ("head_z_2aa",  22,),
            ("head_unknown_2c0", 32,),
            ("head_z_2e0", 32,),
            ("head_c_300", 32,),
            ("head_unknown_320", 32,),
            ("head_unknown_340", 32,),
            ("head_unknown_360", 32,),
            ("head_z_380", 32,),
            ("head_z_3a0", 32,),
            ("head_z_3c0", 32,),
            ("head_z_3e0", 32,),
        )

        if self.head_free_ptr > len(seg.this) * 8:
            print(seg.this, "head.head_free_ptr past end of artifact")
            return

        if self.head_chains:
            try:
                Seg97Chains(seg, self.head_chains)
            except MisFit as e:
                print("MISFIT CHAINS", seg.this, "0x%x" % self.head_chains)

        if False: # ⟦bba8365f⟧
            i = Seg97PointerArray(
                seg,
                0x11971,
                0x125d1 - 0x11971,
                "Tree#3"
            )
            for index, addr in i:
                if not seg.get(addr):
                    seg.cut(addr)

            if False:
                seg.cut(0xae16)
                seg.cut(0xcf1d)
            if False:
                for chunk, offset, address in seg.hunt("100111011000101110000"):
                    if chunk.owner or address > 0x10000:
                        continue
                    mk_stuff3(seg, address)
    
        if self.head_stuff1:
            mk_stuff1(seg, self.head_stuff1)

        if self.head_trees:
            try:
                Seg97Trees(seg, self.head_trees)
            except MisFit as e:
                print("MISFIT TREES", seg.this, "0x%x" % self.head_trees, e)

        try:
            Seg97Tail(seg, self.head_free_ptr + 0x7f)
        except MisFit as e:
            print("MISFIT TAIL", seg.this, "0x%x" % (self.head_free_ptr + 0x7f), e)

        return

class R1k97Seg():

    ''' A '97' segment from the backup tape '''

    def __init__(self, this):
        if not this.has_note("97_tag"):
            return;
        print("?97:", this)
        self.this = this
        this.add_interpretation(self, self.render_chunks)
        b = bin(int.from_bytes(b'\xff' + this.tobytes(), 'big'))[10:]
        self.starts = {}
        self.chunks = [Chunk(0, b)]
        self.starts[0] = self.chunks[-1]
        try:
            Seg97Head(self)
        except Exception as e:
            print("DIED HORRIBLY in HEAD", this, e)
            raise

        # self.hunt_orphans()

    def hunt_orphans(self):
        for chunk in self.chunks:
            if chunk.offset < 0x1000:
                continue
            cuts = self.hunt(bin((1<<32) + chunk.offset)[3:])
            for chunk2, offset, address in cuts:
                if chunk2.owner is not None:
                    continue
                print(chunk, "    pointer at 0x%x in " % offset, chunk2)
                if chunk.owner:
                    print("OWNED", chunk, self.this)
                    Seg97Pointer(self, address, ident="orphan " + chunk.owner.title)
                else:
                    Seg97Pointer(self, address, ident="orphan")
                    print("WHITE SPACE", chunk, self.this)
                     
    def hunt(self, pattern):
        cuts = []
        for chunk in self.chunks:
            offset = 0
            while True:
                j = chunk.bits[offset:].find(pattern)
                if j < 0:
                    break
                cuts.append((chunk, offset + j, chunk.offset + offset + j))
                offset += j + 1
        return cuts

    def __getitem__(self, idx):
        return self.starts[idx]

    def get(self, idx):
        return self.starts.get(idx)

    def mkcut(self, idx):
        t = self.starts.get(idx)
        if not t:
            t = self.cut(idx)
        return t

    def cut(self, where, length=-1):
        for index, chunk in enumerate(self.chunks):
            assert self.starts.get(chunk.offset) == chunk, "0x%x -> %s vs %s" % (chunk.offset, str(self.starts.get(chunk.offset)), str(chunk))
            if not chunk.offset <= where < chunk.offset + len(chunk):
                continue

            if chunk.owner:
                raise MisFit("Has " + str(chunk) + " already owned " + str(chunk.owner) + " wanted 0x%x" % where)

            if chunk.offset == where and length in (-1, len(chunk)):
                return chunk
            if where > chunk.offset:
                i = where - chunk.offset
                c1 = Chunk(chunk.offset, chunk.bits[:i])
                chunk.bits = chunk.bits[i:]
                chunk.offset += i
                self.starts[chunk.offset] = chunk
                self.chunks.insert(index, c1)
                self.starts[c1.offset] = c1
                index += 1
            if length in (-1, len(chunk)):
                return chunk
            if length > len(chunk):
                raise MisFit("Has " + str(chunk) + " want 0x%x" % length)
            assert length < len(chunk)
            c1 = Chunk(chunk.offset, chunk.bits[:length])
            self.chunks.insert(index, c1)
            self.starts[c1.offset] = c1
            chunk.bits = chunk.bits[length:]
            chunk.offset += length
            self.starts[chunk.offset] = chunk
            return c1
        raise MisFit("Found nothing at 0x%x" % where)


    def render_chunks(self, fo, _this):
        fo.write("<H3>97 Seg</H3>\n")
        fo.write("<pre>\n")
        ocheck = 0
        for chunk in self.chunks:
            assert ocheck == chunk.offset
            ocheck += len(chunk)
            fo.write(str(chunk) + ":")
            if chunk.owner is None:
                fo.write(" ===================\n")
                render_chunk(fo, chunk)
            else:
                chunk.owner.render(chunk, fo)
        fo.write("</pre>\n")
        assert ocheck == len(self.this) * 8

