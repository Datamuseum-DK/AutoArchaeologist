'''
   RC8000 Save Tapes
   -----------------
'''

from ..generic import hexdump

class Fields():

    def __init__(self, src, spec, header=None):
        self.fields = []
        self.fmtd = []
        self.spec = spec
        self.header = header

        def wrd(r):
            x = r.pop(0) << 16
            x |= r.pop(0) << 8
            x |= r.pop(0)
            return x

        length = 0
        for name, i in spec:
            if i[0] == "i":
                j = int(i[1:])
                length += j
            elif i == "w":
                length += 3
            elif i[0] == "s":
                j = int(i[1:])
                length += j
        src = list(src[:length].tobytes())
        for name, i in spec:
            if i[0] == "i":
                j = int(i[1:])
                while j:
                    src.pop(0)
                    j -= 1
            elif i == "w":
                self.fields.append(wrd(src))
                setattr(self, name, self.fields[-1])
                self.fmtd.append("0x%06x" % self.fields[-1])
            elif i[0] == "s":
                j = int(i[1:])
                k = bytearray(src[:j]).replace(b'\x00',b'\x20').decode("ascii")
                k = k.rstrip(" ")
                self.fields.append(k)
                setattr(self, name, k)
                self.fmtd.append(('"%s"' % k).ljust(j + 2))
                src = src[j:]
            else:
                assert False, i

    def render(self):
        if self.header:
            yield from self.header
        yield ", ".join(self.fmtd)

class Save_Header(Fields):

    def __init__(self, src, **kwargs):
        super().__init__(
            src,
            [
                ("c_save", 's9', ),
                ("volume", 's12', ),
                ("format", 's6', ),
                ("c_vers", 's6', ),
                ("vers", 's15', ),
                ("c_segm", 's5', ),
                ("segm", 's4', ),
                ("c_label", 's6', ),
                ("label", 's15', ),
                ("nl", 'i9', ),
                ("w0", 'w', ),		# Same as "segm. %d" in label
                ("w1", 'w', ),		# Max entries in Volidx
                ("w2", 'w', ),		# File entries in Saveidx
                ("s0", 's12', ),
                ("w3", 'w', ),
                ("w4", 'w', ),
                ("w5", 'w', ),		# 0x300 sectors in Saveidx
                ("w6", 'w', ),
                ("w7", 'w', ),
                ("w8", 'w', ),
                ("w9", 'w', ),
                ("w10", 'w', ),
            ],
            **kwargs,
        )

class Save_Saveidx(Fields):
    def __init__(self, src, **kwargs):
        super().__init__(
            src,
            [
                ("w0", 'w', ),
                ("w1", 'w', ),
                ("w2", 'w', ),
                ("name1", 's12', ),
                ("w3", 'w', ),
                ("name2", 's12', ),
                ("w4", 'w', ),
                ("w5", 'w', ),
                ("w6", 'w', ),
                ("w7", 'w', ),
                ("w8", 'w', ),
                ("w9", 'w', ),
                ("w10", 'w', ),
                ("w11", 'w', ),
                ("w12", 'w', ),
                ("name3", 's12', ),
                ("w13", 'w', ),
                ("w14", 'w', ),
                ("w15", 'w', ),
                ("w16", 'w', ),
            ],
            **kwargs,
        )

class Save_Volidx(Fields):
    def __init__(self, src, **kwargs):
        super().__init__(
            src,
            [
                ("w0", 'w', ),
                ("w1", 'w', ),
                ("w2", 'w', ),
                ("name1", 's12', ),
                ("w3", 'w', ),
                ("name2", 's12', ),
                ("w4", 'w', ),
                ("w5", 'w', ),
                ("w6", 'w', ),
                ("w7", 'w', ),
                ("w8", 'w', ),
            ],
            **kwargs,
        )

class Save_Filehdr(Fields):
    def __init__(self, src, **kwargs):
        super().__init__(
            src,
            [
                ("w0", 'w', ),
                ("w1", 'w', ),
                ("w2", 'w', ),
                ("filename", 's12', ),
                ("w3", 'w', ),
                ("name2", 's12', ),
                ("w4", 'w', ),
                ("w5", 'w', ),
                ("w6", 'w', ),
                ("w7", 'w', ),
                ("w8", 'w', ),
            ],
            **kwargs,
        )

    def __lt__(self, other):
        return self.filename < other.filename

class Sector():
    def __init__(self, src, width=16, header=None):
        self.src = src.rstrip(b'\x00')
        self.width = width
        self.header = header

    def render(self):
        if self.header:
            yield from self.header
        yield from hexdump.hexdump(self.src, width=self.width)

class RC8000_Save_Tape_001():
    '''
       Version ".001" is very easy to take apart, each file
       is prefixed with a "Filehdr" tape record which contains
       the filename.
    '''

    def __init__(self, this):
        self.this = this
        self.parts = []
        this.add_note("RC8000 Save (.001)")
        this.taken = self
        b = None
        fn = None
        hdr = None
        for r in this.iterrecords():
            if len(r) == 0x1e0:
                if hdr:
                    that = this.create(records=b)
                    self.parts.append((hdr, that))
                    if fn:
                        that.add_note(fn)
                    else:
                        print("**", that, fn)
                hdr = Save_Filehdr(r)
                b = []
                fn = hdr.filename
            elif b is not None:
                b.append(r)
        if self.parts:
            this.add_interpretation(self, self.html_parts)

    def html_parts(self, fo, _this):
        fo.write("<H3>RC 8000 SAVE (.001)</H3>\n")
        fo.write("<pre>\n")
        fo.write("<table>\n")
        for i, j in sorted(self.parts):
            fo.write("<tr>\n")
            fo.write("<td>")
            fo.write("\n".join(i.render()))
            fo.write("</td>")
            fo.write("<td>")
            fo.write(j.summary())
            fo.write("</td>")
            fo.write("</tr>\n")
        fo.write("</table>\n")
        fo.write("</pre>\n")


class RC8000_Save_Tape_003():

    def __init__(self, this):
        if not this.records or this.records[0] != 0x96:
            return
        self.hdr = Save_Header(this)
        if this[:4] not in (b'save',) or len(this) < 300:
            return
        if this[27:31] not in (b'vers',) or len(this) < 300:
            return
        print("?RC8000_Save_Tape", this, len(this.records), this[:4], this.parents[0].descriptions)
        self.this = this
        self.parts = []
        self.saveidx = []
        self.volidx = []
        offset = 0
        self.npre_sect = None
        self.nidx_sect = None
        self.nvolidx = 0
        self.nextra = 20
        self.ndata = 0
        for n, i in enumerate(self.this.records):
            r = self.this[offset:offset + i]
            self.parts.append("TapeBlock 0x%05d len=0x%x" % (n, len(r)))
            if n == 0:
                self.hdr = Save_Header(r)
                self.parts.append(self.hdr)
                self.npre_sect = 2
                self.nidx_sect = self.hdr.w5 - 2
                self.nvolidx = self.hdr.w1
            elif len(r) == 0x1e0:
                self.parts.append("\n\n")
                self.parts.append(Save_Filehdr(r))
                self.nextra = 0
                self.ndata = 1
            elif self.npre_sect or self.nidx_sect or self.nextra:
                for j in range(0, len(r), 0x300):
                    self.sector(n, r[j:j+0x300])
            elif self.ndata:
                self.ndata -= 1
                self.parts.append("  -- First data sector --")
                self.parts.append(Sector(r[:0x1000], 32))
            offset += i
        print("XXX", len(self.saveidx), self.hdr.w2)
        this.add_interpretation(self, self.html_block_list)
        this.add_note("RC8000 Save")

    def sector(self, _nbr, sec):
        self.parts.append(" [0x%x]" % len(sec))
        if self.npre_sect:
            self.npre_sect -= 1
            self.parts.append(Sector(sec, 32))
            return
        if self.nidx_sect:
            self.nidx_sect -= 1
            for i in range(0, len(sec) - 86, 87):
                x = sec[i:i+87]
                if not max(x):
                    self.parts.append("  -- end of saveidx --")
                    return
                j = Save_Saveidx(x)
                self.parts.append(j)
                self.saveidx.append(j)
            return
        if self.nvolidx and not len(sec) % 0x300:
            for i in range(0, len(sec) - 50, 51):
                x = sec[i:i+51]
                if not max(x):
                    self.parts.append("  -- end of volidx --")
                    self.nvolidx = 0
                    return
                j = Save_Volidx(x)
                self.parts.append(j)
                self.volidx.append(j)
                self.nvolidx -= 1
                if not self.nvolidx:
                    return
            return
        if self.nextra:
            self.nextra -= 1
            self.parts.append(Sector(sec, 32))
            return

    def html_block_list(self, fo, _this):
        fo.write("<H3>RC 8000 SAVE</H3>\n")
        fo.write("<pre>\n")
        try:
            self.html_block_list2(fo, _this)
        except Exception as error:
            print(self.this, "ERROR", error)
        fo.write("<pre>\n")

    def html_block_list2(self, fo, _this):
        for i in self.parts:
            if isinstance(i, str):
                fo.write(i + "\n")
            else:
                for j in i.render():
                    fo.write("  " + j + "\n")

def RC8000_Save_Tape(this):

    for r in this.iterrecords():
        if len(r) != 0x96 or r[:9].tobytes() != b'save     ':
            return
        break

    hdr = Save_Header(this)

    print("?RC8ST", this, "\n".join(hdr.render()))

    if hdr.c_save != "save":
        return
    if hdr.c_vers != "vers.":
        return
    if hdr.c_segm != "segm.":
        return
    if hdr.c_label != "label.":
        return

    if hdr.format == ".001":
        return RC8000_Save_Tape_001(this)
