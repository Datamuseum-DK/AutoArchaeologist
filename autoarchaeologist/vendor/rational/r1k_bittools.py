#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

# pylint: disable=E1101
'''
   R1000 Segmented Heaps
   =====================

'''

import html

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
        if self.owner:
            i = self.owner.__class__.__name__
            return "{%s 0x%05x/0x%x}" % (i, self.begin, len(self.bits))
        return "{R1kSegChunk 0x%05x/0x%x}" % (self.begin, len(self.bits))

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
    width = 128
    mask = width - 1
    residual = width - (chunk.begin & mask) # absolute alignment
    residual = 128 # relative alignment
    while offset < len(chunk):
        end = residual + ((offset + mask) & ~mask)
        end = min(end, len(chunk))
        n = chunk.bits.find('1', offset)
        t = "    0x%06x" % (offset + chunk.begin)
        t += " +0x%04x: " % offset
        if n < 0:
            t += "0x0 ".rjust(39)
            t += "[0x%02x] 0…" % (len(chunk) - offset)
            offset = len(chunk)
        elif n > offset + width:
            end = n & ~mask
            t += "0x0 ".rjust(39)
            t += "[0x%02x] 0…" % (end - offset)
            offset = end
        else:
            i = chunk.bits[offset:end]
            t += ("0x%x " % int(i, 2)).rjust(39)
            t += "[0x%02x]" % (end - offset)
            for j in range(0, len(i), 16):
                t += " " + i[j:j+16]
            offset += len(i)
        fo.write(t + "\n")

class R1kCut():
    '''
    Just leave a cut where the object will go
    '''
    def __init__(self, seg, address, **_kwargs):
        p = seg.starts.get(address)
        if not p:
            p = seg.mkcut(address)
        seg.dot.node(p, 'shape=plaintext', 'label="CUT\\n0x%x"' % address)
        return p

class R1kSegField():
    ''' Field in a R1kSegBase '''

    def __init__(self, up, offset, width, name, val):
        self.up = up
        self.offset = offset
        self.width = width
        self.name = name
        self.fmt = "0x%%0%dx" % (((width-1)>>2)+1)
        self.val = val

    def __str__(self):
        return self.render()

    def render(self):
        ''' ... '''
        if self.name[-4:] == "_txt":
            i = " " + self.name + " $0x%04x" % self.val
            tt = self.up.seg.txttab.get(self.val)
            if tt:
                i += " »" + tt.txt + "«"
            elif self.val:
                print("TXT miss", self.up, self.name, "$0x%04x" % self.val)
            return i
        elif self.name[-2:] == "_z" and not self.val:
            return ""
        elif self.name[-2:] == "_p" and not self.val:
            return ""
        elif self.name[-2:] == "_p":
            return " " + self.name + " → " + self.up.seg.label(self.val)
        return " " + self.name + " = " + self.fmt % self.val

class R1kSegBase():

    '''
    Base class for the bit-structures we find.
    '''

    def __init__(self, seg, chunk, title="", ident="", target=None):
        self.seg = seg
        self.chunk = chunk
        self.target = target
        if not title:
            title = self.__class__.__name__
        self.title = title
        if ident:
            self.title += " " + ident
        chunk.owner = self
        self.begin = self.chunk.begin
        self.end = self.chunk.begin + len(self.chunk)
        self.fields = []
        self.compact = False
        self.text = None
        self.offset = 0
        self.supress_zeros = False
        self.txttab = {}

        seg.dot.node(
           chunk,
           "shape=box",
           'label="%s\\n0x%x"' % (self.title.replace(" ", "\\n"), chunk.begin),
        )

    def __str__(self):
        return "{@0x%x: " % self.begin + self.title + "}"

    def __iter__(self):
        yield from self.fields

    def truncate(self):
        print("Change .truncate() to .finish()", self)
        return self.finish()

    def finish(self):
        '''
        Change the length of our chunk
        '''
        offset = self.offset
        self.chunk.owner = None
        self.chunk = self.seg.cut(self.begin, offset)
        self.chunk.owner = self
        self.end = self.chunk.begin + len(self.chunk)
        self.offset = offset
        for i in self.fields:
            if i.name[-2:] == "_z":
                if i.val:
                    print(self, "Zero field", i.name, "Has value", hex(i.val))
                i.fmt = "0x%x"
                continue
            if not i.val or i.name[-2:] != "_p":
                continue
            if self.target:
                y = make_one(self, i.name, self.target)
                if y:
                    self.seg.dot.edge(self, y)
            elif not 0x7f < i.val < len(self.seg.this) * 8:
                pass
            else:
                t = self.seg.starts.get(i.val)
                if t:
                    self.seg.dot.edge(self, t)
                else:
                    p = self.seg.mkcut(i.val)
                    self.seg.dot.edge(self, p)
        # self.seg.dot.write('X_0x%x -> X_0x%x [style=dotted]' % (self.begin, self.end))

    def get_fields(self, *fields):
        '''
        Create numerical fiels, starting at the first bit
        '''
        assert self.chunk
        for name, width in fields:
            if width < 0:
                width = len(self.chunk[self.offset:])
            if self.offset+width > len(self.chunk):
                print(
                    "Not enough data in",
                    self,
                    self.chunk,
                    "Len",
                    len(self.chunk),
                    "Offset",
                    self.offset,
                    "Width",
                    width
                )
            i = int(self.chunk[self.offset:self.offset+width], 2)
            setattr(self, name, i)
            self.fields.append(R1kSegField(self, self.offset, width, name, i))
            self.offset += width
        return self.offset

    def render_fields_compact(self, fo):
        ''' Render the fields on a single line'''
        retval = 0
        for fld in self.fields:
            if fld.val or not self.supress_zeros:
                fo.write(fld.render())
            retval = fld.offset + fld.width
        return retval

    def render_fields(self, fo):
        ''' Render the fields '''
        retval = 0
        for idx, fld in enumerate(self.fields):
            if self.supress_zeros and not fld.val:
                continue
            if not self.compact:
                fo.write("    0x%06x" % (fld.offset + self.begin))
                fo.write(" [0x%02x] +0x%04x:" % (idx, fld.offset))
            fo.write(fld.render())
            if not self.compact:
                if fld.name[-2:] != "_z":
                    fo.write(" [%s]" % self.chunk[fld.offset:fld.offset+fld.width])
                fo.write("\n")
            retval = fld.offset + fld.width
        if self.text is not None:
            fo.write(' "' + self.text + '"')
        fo.write('\n')
        return retval

    def render_bits(self, fo, chunk=None, offset=0):
        ''' Render the bits in a/our chunk '''
        if chunk is None:
            chunk = self.chunk
        render_chunk(fo, chunk, offset=offset)

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
    if cls is R1kCut:
        return p
    if isinstance(p.owner, cls):
        return p.owner
    if p.owner:
        print(self.seg.this, "COLL at 0x%x, Want:" % a, self, attr, cls, "Exiting:", p.owner)
        return None
    try:
        if func:
            y = func(self.seg, a, **kwargs)
        else:
            y = cls(self.seg, a, **kwargs)
        if y:
            self.seg.dot.edge(self.chunk, y.chunk)
        return y
    except MisFit as err:
        print(self.seg.this, "MISFIT at 0x%x" % a, "%s.%s:" % (str(self), attr), err)
        return False

class BitPointer(R1kSegBase):
    ''' A pointer of some width '''
    def __init__(self, seg, address, size=32, target=None, **kwargs):
        super().__init__(
            seg,
            seg.cut(address, size),
            title="POINTER",
            **kwargs,
        )
        self.compact = True
        self.get_fields(
            ("ptr_p", size)
        )
        self.finish()

class BitPointerArray(R1kSegBase):
    ''' A pointer of some width '''
    def __init__(self, seg, address, count, size=32, **kwargs):
        super().__init__(
            seg,
            seg.cut(address, count * size),
            **kwargs,
        )
        self.supress_zeros = True
        for i in range(count):
            self.get_fields(
                ("ptr_0x%x_p" % i, size)
            )
        self.finish()

class PointerArray(R1kSegBase):
    ''' Array format'''
    def __init__(self, seg, address, width=32, **kwargs):
        p = seg.mkcut(address)
        i = int(p[32:64], 2)
        p = seg.cut(address, 64 + i * width)
        super().__init__(seg, p, title="PointerArray", **kwargs)
        self.supress_zeros = True
        self.get_fields(
            ("x", 32),
            ("y", 32)
        )
        for j in range(i):
            self.get_fields(
                ("a_%x_p" % j, width)
            )
        self.finish()

class Array(R1kSegBase):
    ''' Array format'''
    def __init__(self, seg, address, width=8, **kwargs):
        p = seg.mkcut(address)
        i = int(p[32:64], 2)
        p = seg.cut(address, 64 + i * width)
        super().__init__(seg, p, title="ARRAY", **kwargs)
        self.get_fields(
            ("x", 32),
            ("y", 32)
        )
        for j in range(i):
            self.get_fields(
                ("a_%x_n" % j, width)
            )
        self.finish()

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
        seg.dot.node(self, 'shape=plaintext', 'label="%s"' % html.escape(self.text))

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

        seg.dot.write('T_0x%x [shape=plaintext, label="%s"]' % (self.begin, html.escape(self.text)))
        seg.dot.write('X_0x%x -> T_0x%x' % (self.begin, self.begin))


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
    assert length >= 0
    text = ""
    i = 0
    for i in range(length):
        if no_fail and pointer + 8 > len(chunk):
            return i, text
        char = int(chunk[pointer:pointer+8], 2)
        slug = seg.type_case[char]
        if not slug:
            if no_fail:
                return i, text
            raise NotText("0x%02x is not text" % char)
        text += slug.long
        pointer += 8
    return i + 1, text

def hunt_array_strings(seg, chunk):
    ''' Find any strings on array format '''
    offset = 0x80
    candidates = []
    pattern = '0' * 31 + '1' + '0' * 20
    print("LC", len(chunk))
    while len(chunk) - offset >= 72:
        i = chunk.find(pattern, offset)
        if i < 0:
            break
        offset = i
        p = chunk[i:i+64]
        length = int(p[32:], 2)
        if not length:
            offset += 32
            continue
        if length < 3 or length > 200:
            offset += 32
            continue
        if offset + 64 + length * 8 > len(chunk):
            offset += 32
            continue
        try:
            width, _text = to_text(seg, chunk, offset + 64, length)
        except NotText as err:
            offset += 32
            continue

        assert width == length
        print("! 0x%x" % offset, _text)
        candidates.append(chunk.begin + offset)
        offset += 64 + 8 * length

    for offset in sorted(candidates, reverse=True):
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
        if type_case[acc]:
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
