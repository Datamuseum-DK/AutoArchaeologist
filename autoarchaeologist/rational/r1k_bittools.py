#!/usr/bin/env python3
# pylint: disable=E1101
'''
   R1000 Segmented Heaps
   =====================

'''

class MisFit(Exception):
    ''' bla '''

class NotText(Exception):
    ''' bla '''

class R1kSegChunk():

    '''
    A sequence of bits, represented as a python string "0101010101"
    '''

    def __init__(self, offset, bits):
        self.bits = bits
        self.begin = offset
        self.end = offset + len(bits)
        self.owner = None

    def __len__(self):
        return len(self.bits)

    def __str__(self):
        return "{R1kSegChunk 0x%x-0x%x/0x%x}" % (self.begin, self.end, len(self.bits))

    def __getitem__(self, idx):
        return self.bits[idx]

    def find(self, *args, **kwargs):
        ''' find sequence in chunk '''
        return self.bits.find(*args, **kwargs)

def render_chunk(fo, chunk, offset=0):
    '''
    Render the bits in a/our chunk
    compact all-zero chunks
    '''
    while offset < len(chunk):
        n = chunk.bits.find('1', offset)
        if n < 0:
            fo.write(" " * 39 + "0[0x%x]\n" % (len(chunk.bits) - offset))
            return
        if n - offset > 128:
            fo.write(" " * 39 + "0[0x%x]\n" % n)
            offset += n
        else:
            i = chunk.bits[offset:offset+128]
            fo.write(("0x%x " % int(i, 2)).rjust(39) + i + "\n")
            offset += len(i)

class R1kSegBase():

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
        self.begin = self.chunk.begin
        self.end = self.chunk.begin + len(self.chunk)
        self.fields = []
        self.compact = False

    def __str__(self):
        return "{@0x%x: " % self.begin + self.title + "}"

    def get_fields(self, *fields, offset=0):
        '''
        Create numerical fiels, starting at the first bit
        '''
        assert self.chunk
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
        render_chunk(fo, chunk, offset=offset)
        #for j in range(offset, len(chunk), 128):
        #    fo.write("    " + chunk.bits[j:j+128] + "\n")

    def render(self, chunk, fo):
        ''' Default render this bit-structure '''
        if self.title:
            fo.write(self.title)
        else:
            fo.write("=" * 40)
        if not self.compact:
            fo.write("\n")
        offset = self.render_fields(fo)
        if offset < len(chunk):
            self.render_bits(fo, chunk=chunk,offset=offset)

def make_one(self, attr, cls, func=None, **kwargs):
    '''
    Convenience function to propagate pointers
    Ignores zero values
    Detects already handled destinations
    '''
    a = getattr(self, attr)
    if not a:
        return None
    p = self.seg.mkcut(a)
    if self.seg.fdot:
        self.seg.fdot.write("X_%x -> X_%x\n" % (self.begin, a))
    if isinstance(p.owner, cls):
        return p.owner
    if p.owner:
        print(self.seg.this, "COLL 0x%x" % a, self, attr, p.owner)
        return None
    try:
        if func:
            return func(self.seg, a, **kwargs)
        return cls(self.seg, a, **kwargs)
    except MisFit as err:
        print(self.seg.this, "MISFIT 0x%x" % a, self, attr, err)

class BitPointer(R1kSegBase):
    ''' A pointer of some width '''
    def __init__(self, seg, address, size=32, **kwargs):
        super().__init__(
            seg,
            seg.cut(address, size),
            title="POINTER",
            **kwargs,
        )
        self.get_fields(("destination", 32))
        self.compact = True

class BitPointerArray(R1kSegBase):
    ''' A pointer of some width '''
    def __init__(self, seg, address, count, size=32, **kwargs):
        super().__init__(
            seg,
            seg.cut(address, count * size),
            title="POINTERARRAY",
            **kwargs,
        )
        offset = 0
        self.count = count
        self.size = size
        self.data = []
        for _i in range(count):
            self.data.append(int(self.chunk[offset:offset + size], 2))
            offset += size

    def render(self, _chunk, fo):
        ''' Only non-zero entries '''
        fo.write(self.title + "[0x%x×0x%x]\n" % (self.count, self.size))
        for i, j in enumerate(self.data):
            if j:
                fo.write(("[0x%x]:" % i).rjust(39) + " 0x%x\n" % j)

class ArrayString(R1kSegBase):
    ''' String on Array format'''
    def __init__(self, seg, address, **kwargs):
        p = seg.mkcut(address)
        i = int(p[32:64], 2)
        p = seg.cut(address, 64 + i * 8)
        super().__init__(seg, p, title="ARRAY_STRING", **kwargs)
        offset = self.get_fields(
            ("x", 32),
            ("y", 32)
        )
        _i, self.text = to_text(seg, self.chunk, offset, self.y)

    def render(self, _chunk, fo):
        ''' Single line '''
        fo.write(self.title)
        fo.write('[0x%x,0x%x] = "%s"\n' % (self.x, self.y, self.text))

class String(R1kSegBase):
    ''' A String of given length or as long as it looks likely '''
    def __init__(self, seg, address, length=-1, text=None, **kwargs):
        if length == -1:
            p = seg.mkcut(address)
            length, text = to_text(seg, p, 0, 999, no_fail=True)
            if not length:
                raise NotText("Not a String")
        super().__init__(
            seg,
            seg.cut(address, length * 8),
            title="STRING",
            **kwargs,
        )

        if not text:
            self.length, self.text = to_text(seg, self.chunk, 0, length)
        else:
            self.text = text

    def render(self, chunk, fo):
        ''' one line '''
        fo.write(self.title + ' "' + self.text + '"')
        if len(self.text) < 8:
            fo.write("\t[" + self.chunk.bits + "]\n")
        fo.write("\n")

def to_text(seg, chunk, pointer, length, no_fail=False):
    '''
       Convert chunk[pointer:pointer+length*8] to text
       Return number of bytes consumed and text
       no_fail=True can be used to discover length of text
    '''
    assert length > 0
    text = ""
    i = 0
    for i in range(length):
        char = int(chunk[pointer:pointer+8], 2)
        if not seg.type_case.valid[char]:
            if no_fail:
                return i, text
            raise NotText("0x%02x is not text" % char)
        text += seg.type_case.slugs[char]
        pointer += 8
    return i + 1, text

def hunt_array_strings(seg, chunk):
    ''' Find any strings on array format '''
    offset = 0
    candidates = []
    while len(chunk) - offset >= 72:
        c = chunk[offset:]
        i = c.find('0' * 31 + '1' + '0' * 24)
        if i < 0:
            break
        length = int(c[i+32:i+64], 2)
        if length < 3 or length > 200:
            offset += i + 32
            continue
        if i + 64 + length * 8 > len(c):
            offset += i + 32
            continue
        try:
            width, _text = to_text(seg, c, i + 64, length)
        except NotText:
            offset += i + 32
            continue
        assert width == length
        candidates.append(chunk.begin + offset + i)
        offset += i + 64 + 8 * length

    for offset in candidates:
        ArrayString(seg, offset, ident="hunted")

class StringCandidate():
    ''' A candidate String '''
    def __init__(self, type_case, chunk, offset, totext):
        self.type_case = type_case
        self.chunk = chunk
        self.offset = offset
        self.length = 0
        self.text = ""
        self.score = 0
        self.totext = totext

    def __str__(self):
        return "<SC 0x%x %d 0x%x " % (self.offset, self.score, self.length) + str(self.text) + ">"

    def __lt__(self, other):
        if self.score != other.score:
            return self.score < other.score
        if self.length != other.length:
            return self.length < other.length
        return self.offset > other.offset

    def add(self, val):
        ''' add a character '''
        self.length += 1
        self.text += self.type_case.slugs[val]
        c = "%c" % val
        if c.isupper():
            self.score += 3
        elif c.islower():
            self.score += 2
        elif c.isdigit():
            self.score += 2
        elif c == '␣':
            self.score += 1
        elif c == '@':
            self.score -= 1

def hunt_strings(seg, chunk, minlength=3):
    '''
    Find any strings in "naked" format
    This is slightly tricker than one might think, bacause
    many strings have "evil twins" shifted one bit left or right.
    We prefer strings based on their content and length.
    '''
    hits = []
    acc = 0
    cand = [None] * 8
    type_case = seg.this.type_case
    for n, i in enumerate(chunk.bits):
        acc = (acc + acc + ord(i) - 0x30) & 0xff
        if n < 7:
            continue
        r = n % 8
        if type_case.valid[acc]:
            if cand[r] is None:
                cand[r] = StringCandidate(type_case, chunk, n - 7, to_text)
            cand[r].add(acc)
        elif cand[r] is not None:
            j = cand[r]
            cand[r] = None
            if j.length >= minlength and j.score - j.length >= 6:
                hits.append(j)

    del cand
    hits.sort()
    offset = chunk.begin
    while hits:
        hit = hits.pop(-1)
        if hit.score - hit.length < 6:
            break
        String(seg, offset + hit.offset, hit.length, text = hit.text, ident="hunted")
        i = []
        for j in hits:
            if j.offset + j.length * 8 <= hit.offset:
                i.append(j)
            elif j.offset >= hit.offset + hit.length * 8:
                i.append(j)
        hits = i
