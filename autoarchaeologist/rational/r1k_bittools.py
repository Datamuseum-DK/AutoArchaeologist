'''
   R1000 Segmented Heaps
   =====================

'''

import tempfile
import html

class MisFit(Exception):
    ''' bla '''

class R1kSegChunk():

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
        return "{R1kSegChunk 0x%x-0x%x/0x%x}" % (self.offset, self.offset + len(self.bits), len(self.bits))

    def __getitem__(self, idx):
        return self.bits[idx]

def render_chunk(fo, chunk, offset=0):
    ''' Render the bits in a/our chunk '''
    if chunk.bits[offset:].find('1') < 0:
        fo.write(" " * 39 + "0[0x%x]\n" % len(chunk.bits[offset:]))
    else:
        for j in range(offset, len(chunk), 128):
            i = chunk.bits[j:j+128]
            fo.write(("0x%x " % int(i, 2)).rjust(39) + i + "\n")

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

class BitPointer(R1kSegBase):

    def __init__(self, seg, address, size=32, **kwargs):
        super().__init__(
            seg,
            seg.cut(address, size),
            title="POINTER",
            **kwargs,
        )
        self.get_fields(("destination", 32))
        self.compact = True

def to_text(input):
    assert not len(input) & 7
    text = ""
    for i in range(0, len(input), 8):
        char = int(input[i:i+8], 2)
        if 32 <= char <= 126:
            text += "%c" % char
        else:
            text += "\\x%02x" % char
    return text

class String(R1kSegBase):
    def __init__(self, seg, address, maxlen=128, **kwargs):
        p = seg.mkcut(address)
        i0 = int(p[:32], 2)
        assert i0 == 1
        i1 = int(p[32:64], 2)
        assert i1 < maxlen
        super().__init__(
            seg,
            seg.cut(address, 0x40 + i1 * 8),
            title="STRING",
            **kwargs,
        )
        assert len(self.chunk) == 0x40 + i1 * 8
        offset = self.get_fields(
            ("string_x", 32),
            ("string_y", 32),
        )
        assert self.string_x == 1
        assert self.string_y == i1
        self.text = to_text(self.chunk[offset:])

    def render(self, chunk, fo):
        fo.write('STRING "' + self.text + '"\n')
