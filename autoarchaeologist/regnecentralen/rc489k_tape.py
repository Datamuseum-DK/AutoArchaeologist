'''
   RC8000 Save Tapes
   -----------------
'''

from ..generic import hexdump

from ..base import octetview as ov
from ..base import namespace

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
                ("w0", 'w', ),                # Same as "segm. %d" in label
                ("w1", 'w', ),                # Max entries in Volidx
                ("w2", 'w', ),                # File entries in Saveidx
                ("s0", 's12', ),
                ("w3", 'w', ),
                ("w4", 'w', ),
                ("w5", 'w', ),                # 0x300 sectors in Saveidx
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

    print(this)
    print("  ", bytes(this[(0,0)]))
    print("  ", bytes(this[(1,0)]))
    return
    for r in this.iter_rec():
        t = []
        for i in r[:64]:
            if 32 < i < 127:
                t.append("%c" % i)
            else:
                t.append("…")
        print(bytes(r[:24]).hex(), "".join(t), r.key, len(r))
    return

    for r in this.iter_chunks():
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

#################################################

class RC489K_SubCatEnt(ov.Struct):
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            f00_=ov.Be24,
            f01_=ov.Be24,
            f02_=ov.Be24,
            filename_=ov.Text(12),
            f04_=ov.Be24,
            vol_=ov.Text(12),
            f06_=ov.Be24,
            f07_=ov.Be24,
            f08_=ov.Be24,
            f09_=ov.Be24,
            f10_=ov.Be24,
        )

class RC489K_SubCat(ov.OctetView):
    def __init__(self, this, parent_namespace):
        this.add_type("RC8000_Subcat")
        print(this, self.__class__.__name__)
        super().__init__(this)
        nent = ov.Be24(self, 0x2fd).insert()
        ptr = 0
        self.dents = []
        for i in range(nent.val):
            if (i % 15) == 14:
                ptr += 3
            if ptr >= len(this):
                break
            y = RC489K_SubCatEnt(self, ptr).insert()
            if y.f00.val not in (0x0, 0xffffff):
                self.dents.append(y)
            ptr = y.hi
        for n, dent in enumerate(self.dents):
            begin = dent.f00.val >> 12
            if n + 1 == len(self.dents):
                end = len(this) // 0x300
            else:
                end = self.dents[n+1].f00.val >> 12
            # print(begin, end, len(this), dent)
            that = None
            if begin and end and end > begin:
                try:
                    that = this.create(
                        start = begin * 0x300,
                        stop = min(len(this), end * 0x300),
                    )
                except:
                    pass
            mns = DumpNameSpace(
                name = dent.filename.txt.strip(),
                parent = parent_namespace,
                # priv = recs[0],
                this = that,
            )
        self.add_interpretation(more=False)

#################################################

class RC489KSaveHead(ov.Struct):
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            f00_=ov.Text(9),
            f01_=ov.Text(12),
            f02_=ov.Text(6),
            f03_=ov.Text(6),
            f04_=ov.Text(15),
            f05a_=ov.Text(9),
            f05b_=ov.Text(15),
            f06_=ov.Text(9),
            f07_=ov.Be24,
            f08_=ov.Be24,
            f09_=ov.Be24,
            f10_=ov.Be24,
            f11_=ov.Be24,
            f12_=ov.Text(9),
            f13_=ov.Array(15, ov.Be24),
            vertical=True,
        )

class RC489KSaveDirEnt(ov.Struct):
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            f00_=ov.Array(3, ov.Be24),
            f03_=ov.Text(12),
            f04_=ov.Be24,
            f05_=ov.Text(12),
            f06_=ov.Array(9, ov.Be24),
            f07_=ov.Text(12),
            f08_=ov.Array(4, ov.Be24),
        )

class RC489KSaveSubHead(ov.Struct):
    def __init__(self, up, lo, hi):
        super().__init__(
            up,
            lo,
            f00_=ov.Array(8, ov.Be24),
            nvol_=ov.Be24,
            f01_=ov.Array(5, ov.Be24),
            vertical=True,
            more=True,
        )
        self.addfield("vols", ov.Array(self.nvol.val, ov.Text(12)))
        self.addfield("lbl", ov.Text(12))
        #self.addfield("pad", 0x100 - len(self))
        self.addfield("pad", 0x200 - len(self))
        self.addfield("pad", 0x300 - len(self))
        self.addfield("pad", 0x400 - len(self))
        self.addfield("pad", 0x420 - len(self))
        self.addfield("pad", 0x440 - len(self))
        self.addfield("pad", 0x500 - len(self))
        self.addfield("pad", 0x600 - len(self))
        self.addfield("dent", ov.Array((hi - self.hi)//87, RC489KSaveDirEnt, vertical=True))

        self.done()
        print(hex(lo), hex(hi), hex(self.lo), hex(self.hi))

class RC489KSaveTapeFile(ov.OctetView):
    def __init__(self, this):
        if this[:9] != b'save     ':
            return
        this.add_type("RC8000_Save")
        print(this, self.__class__.__name__)
        super().__init__(this)

        self.namespace = DumpNameSpace(
            name='',
            separator='',
            root=this,
        )

        for rec in this.iter_rec():
            if rec.key[1] == 0:
                self.hdr = RC489KSaveHead(self, 0).insert()
            if rec.key[1] == 1 and len(rec) > 0x600:
                self.subhdr = RC489KSaveSubHead(self, rec.lo, rec.hi).insert()

        ov.Opaque(self, 0x2000, len(this)).insert()

        self.add_interpretation(more=True)


#################################################

class DumpNameSpace(namespace.NameSpace):
    ''' ... '''

    TABLE = (
        ( "r", "f02"),
        ( "r", "f03"),
        ( "r", "nrec"),
        ( "l", "volume"),
        ( "r", "f04"),
        ( "r", "f05"),
        ( "r", "f06"),
        ( "r", "f07"),
        ( "r", "f08"),
        ( "r", "f09"),
        ( "r", "f10"),
        ( "l", "vol2"),
        ( "r", "f12"),
        ( "r", "f13"),
        ( "l", "name"),
        ( "l", "artifact"),
    )

    def ns_render(self):
        meta = self.ns_priv
        if not meta:
            return ["-"] * (len(self.TABLE)-2) + super().ns_render()
        return [
            hex(meta.f02.val),
            hex(meta.f03.val),
            meta.nrec.val,
            meta.volume.txt,
            hex(meta.f04.val),
            hex(meta.f05.val),
            hex(meta.f06.val),
            hex(meta.f07.val),
            hex(meta.f08.val),
            hex(meta.f09.val),
            hex(meta.f10.val),
            meta.vol2.txt,
            hex(meta.f12.val),
            hex(meta.f13.val),
        ] + super().ns_render()

class RC8000_HdrRec(ov.Struct):
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            f00_=ov.Text(72),
        )

class RC8000_DumpRec(ov.Struct):
    def __init__(self, up, lo, hi):
        super().__init__(
            up,
            lo,
            f00_=ov.Be24,
            f01_=ov.Be24,
            f02_=ov.Be24,
            f03_=ov.Be24,
            more=True,
        )
        if self.f00.val == 1:
            self.addfield("filename", ov.Text(12))
            self.addfield("nrec", ov.Be24)
            self.addfield("volume", ov.Text(12))
            self.addfield("f04", ov.Be24)
            self.addfield("f05", ov.Be24)
            self.addfield("f06", ov.Be24)
            self.addfield("f07", ov.Be24)
            self.addfield("f08", ov.Be24)
            self.addfield("f09", ov.Be24)
            self.addfield("f10", ov.Be24)
            self.addfield("vol2", ov.Text(12))
            self.addfield("f12", ov.Be24)
            self.addfield("f13", ov.Be24)
            self.addfield("pad_", (hi-lo) - len(self))
            self.done()
        elif self.f00.val == 2:
            self.addfield("payload_", (hi-lo) - len(self))
            self.done()
        else:
            self.addfield("pad_", (hi-lo) - len(self))
            self.done()

class RC489KDumpTapeFile(ov.OctetView):
    def __init__(self, this):
        if this[:6] != b'dump  ':
            return
        this.add_type("RC8000_Dump")
        print(this, self.__class__.__name__)
        super().__init__(this)

        self.namespace = DumpNameSpace(
            name='',
            separator='',
            root=this,
        )

        self.recs = []
        hdr = None
        for rec in this.iter_rec():
            if rec.key[1] == 0:
                y = RC8000_HdrRec(self, rec.lo).insert()
            else:
                y = RC8000_DumpRec(self, rec.lo, rec.hi).insert()
                if y.f00.val == 1:
                    self.proc_recs()
                if y.f00.val > 2:
                    break
                self.recs.append(y)

        self.proc_recs()
        this.add_interpretation(self, self.namespace.ns_html_plain)
        self.add_interpretation(more=True)

    def proc_recs(self):
        recs = self.recs
        self.recs = []
        if len(recs) == 0 or recs[0].f00.val != 1:
            return
        fname = recs[0].filename.txt.strip()
        if len(recs) > 1:
            that = self.this.create(
                records = [x.payload_.octets() for x in recs[1:]]
            )
            that.add_name(fname)
            tns = DumpNameSpace(
                name = fname,
                parent = self.namespace,
                priv = recs[0],
                this = that,
            )
            if recs[0].f07.val == 0xa000:
                RC489K_SubCat(that, tns)

#################################################

class RC489K_Tape():

    def __init__(self, this):
        if not this.top in this.parents:
            return

        self.this = this
        self.recs = []
        self.label = None
    
        for rec in this.iter_rec():
            if rec.key == (0, 0):
                if rec[:4] != b'VOL1':
                    return
                print(this, self.__class__.__name__)
                self.label = rec
                continue
            if rec.key[1] == 0:
                self.proc_recs()
                recs = []
            self.recs.append(rec)
        self.proc_recs()
        if self.label:
            this.add_interpretation(self, self.label_interpretation)
        this.add_interpretation(self, this.html_interpretation_children)

    def proc_recs(self):
        if len(self.recs) > 0:
            that = self.this.create(
                start = self.recs[0].lo,
                stop = self.recs[-1].hi,
                records = self.recs,
            )
            that.add_type("RC8000_TapeFile")
        self.recs = []
   
    def label_interpretation(self, file, _this):
        file.write("<H3>Label</H3>\n")
        file.write("<pre>\n")
        file.write(str(bytes(self.label)) + "\n")
        file.write("</pre>\n")

