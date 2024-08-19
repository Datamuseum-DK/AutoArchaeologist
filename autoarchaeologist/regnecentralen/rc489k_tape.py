'''
   RC8000 Save Tapes
   -----------------
'''

import time

from ..generic import hexdump

from ..base import octetview as ov
from ..base import namespace

class DWord(ov.Struct):
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            w0_=ov.Be24,
            w1_=ov.Be24,
        )

    def render(self):
        yield "(0x%x" % self.w0.val + ",0x%x)" % self.w1.val

class ShortClock(ov.Be24):

    def render(self):
        if self.val == 0:
            yield "             "
        else:
            ut = (self.val << 19) * 100e-6
            t0 = (366+365)*24*60*60
            yield time.strftime("%Y%m%d-%H%M", time.gmtime(ut - t0 ))

class Rc489kEntryTail(ov.Struct):
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            nrec_=ov.Be24,
            volume_=ov.Text(12),
            tail0_=ShortClock,
            tail1_=ShortClock,
            tail2_=ov.Be24,
            tail3_=ov.Be24,
            tail4_=ov.Be24,
            #vertical=True,
        )

#################################################

class Rc489kSubCatEnt(ov.Struct):
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            f00_=ov.Be24,
            f01_=ov.Be24,
            f02_=ov.Be24,
            filename_=ov.Text(12),
            entry_tail_=Rc489kEntryTail,
        )

class Rc489kSubCat(ov.OctetView):
    def __init__(self, this, parent_namespace):
        this.add_type("Rc489kSubCat")
        print(this, self.__class__.__name__)
        super().__init__(this)
        nent = ov.Be24(self, 0x2fd).insert()
        ptr = 0
        self.dents = []
        for i in range(nent.val):
            if ptr >= len(this):
                break
            y = Rc489kSubCatEnt(self, ptr).insert()
            if y.f00.val not in (0x0, 0xffffff):
                self.dents.append(y)
            ptr = y.hi
            if (i % 15) == 14:
                ptr += 3
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
                priv = dent,
                this = that,
            )
        self.add_interpretation(more=False)

#################################################

class Rc489kSaveHead(ov.Struct):
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

class Rc489kSaveDirEnt(ov.Struct):
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            f00_=ov.Array(3, ov.Be24),
            filename_=ov.Text(12),
            f04_=Rc489kEntryTail,
            f06_=ov.Array(4, ov.Be24),
            f07_=ov.Text(12),
            f08_=ov.Array(4, ov.Be24),

            #f06_=ov.Array(3, ov.Be24),
            #f07_=Rc489kEntryTail,
        )

class Rc489kSaveSubHead(ov.Struct):
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
        self.done()

class Rc489kSaveDirSect(ov.Struct):
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            dirent_=ov.Array(0x300//87, Rc489kSaveDirEnt, vertical=True),
            pad_=(0x300 % 87),
            vertical=True,
        )

    def terminated(self):
        for de in self.dirent:
            if de.f00[2].val == 0:
                return True
        return False

class Rc489kSaveEntry(ov.Struct):
    def __init__(self, up, lo, hi):
        super().__init__(
            up,
            lo,
            dirent_=Rc489kSaveDirEnt,
            more=True,
        )
        self.done(hi - lo)

class Rc489kSaveTapeFile(ov.OctetView):
    def __init__(self, this):
        if this[:9] != b'save     ':
            return
        this.add_type("Rc489k_Save")
        print(this, self.__class__.__name__)
        super().__init__(this)

        self.namespace = DumpNameSpace(
            name='',
            separator='',
            root=this,
        )

        for rec in this.iter_rec():
            if rec.key[1] == 0:
                self.hdr = Rc489kSaveHead(self, 0).insert()
            elif rec.key[1] == 1 and len(rec) > 0x600:
                self.subhdr = Rc489kSaveSubHead(self, rec.lo, rec.hi).insert()
        adr = 0x696
        while True:
            y = Rc489kSaveDirSect(self, adr).insert()
            #print("XX", this, hex(adr), y.terminated(), y)
            if y.terminated():
                #ov.Opaque(self, y.hi + 0x2000, len(this)).insert()
                break
            adr = y.hi

        self.recs = []
        for rec in this.iter_rec():
            if rec.key[1] < 4:
                continue
            if len(rec) > 480:
                y = ov.Opaque(self, lo = rec.lo, hi = rec.hi).insert()
                self.recs.append(y)
            elif len(rec) == 480:
                self.do_recs()
                y = Rc489kSaveEntry(self, rec.lo, rec.hi).insert()
                self.recs.append(y)
                
        this.add_interpretation(self, self.namespace.ns_html_plain)
        self.add_interpretation(more=True)

    def do_recs(self):
        recs = self.recs
        self.recs = []
        if len(recs) == 0:
            return
        if not isinstance(recs[0], Rc489kSaveEntry):
            return
        fname = recs[0].dirent.filename.txt.strip()
        if fname == "":
            return
        that = self.this.create(
                records = [x.octets() for x in recs[1:]]
        )
        DumpNameSpace(
            name = fname,
            parent = self.namespace,
            priv = recs[0].dirent,
            this = that,
        )


#################################################

class DumpNameSpace(namespace.NameSpace):
    ''' ... '''

    TABLE = (
        ( "r", "dump_type"),
        ( "r", "entry_no"),
        ( "r", "num_segs"),
        ( "l", "volume"),
        ( "r", "tail0"),
        ( "r", "tail1"),
        ( "r", "tail2"),
        ( "r", "tail3"),
        ( "r", "tail4"),
        ( "r", "key"),
        ( "r", "bs_dev"),
        ( "r", "entry_base"),
        ( "l", "name"),
        ( "l", "artifact"),
    )

    def ns_render(self):
        meta = self.ns_priv
        if isinstance(meta, Rc489kSubCatEnt):
            return [
                "",
                "",
                meta.entry_tail.nrec.val,
                meta.entry_tail.volume.txt,
                str(meta.entry_tail.tail0),
                str(meta.entry_tail.tail1),
                hex(meta.entry_tail.tail2.val),
                hex(meta.entry_tail.tail3.val),
                hex(meta.entry_tail.tail4.val),
                "",
                "",
                "",
            ] + super().ns_render()
        if isinstance(meta, Rc489kDumpEntryRec):
            return [
                hex(meta.dump_type.val),
                hex(meta.entry_no.val),
                meta.num_segs.val,
                meta.entry_tail.volume.txt,
                str(meta.entry_tail.tail0),
                str(meta.entry_tail.tail1),
                hex(meta.entry_tail.tail2.val),
                hex(meta.entry_tail.tail3.val),
                hex(meta.entry_tail.tail4.val),
                str(meta.key),
                meta.bs_dev_spec.txt.strip(),
                str(meta.entry_base),
            ] + super().ns_render()
        return ["-"] * (len(self.TABLE)-2) + super().ns_render()

class Rc489kDumpLabel(ov.Struct):
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            id_=ov.Text(1*6),
            tapname_=ov.Text(2*6),
            filenumber_=ov.Text(1*6),
            state_=ov.Text(1*6),
            date_=ov.Text(1*6),
            hour_=ov.Text(1*6),
            segprblk_=ov.Text(1*6),
            dumplabel_=ov.Text(2*6),
            inorblank_=ov.Text(1*6),
            bsfilename_=ov.Text(2*6),
            vertical=True,
            more=True,
        )
        self.done(25*6)


class Rc489kDumpEntryRec(ov.Struct):
    def __init__(self, up, lo, hi):
        super().__init__(
            up,
            lo,
            rec_type_=ov.Be24,
            dump_type_=ov.Be24,
            entry_no_=ov.Be24,
            num_segs_=ov.Be24,
            entry_name_=ov.Text(12),
            entry_tail_=Rc489kEntryTail,
            key_=DWord,
            bs_dev_spec_=ov.Text(12),
            entry_base_=DWord,
            vertical=True,
            more=True,
        )
        self.done(25*6)

class Rc489kDumpSegment(ov.Struct):
    def __init__(self, up, lo, hi):
        super().__init__(
            up,
            lo,
            rec_type_=ov.Be24,
            segsize_=ov.Be24,
            entry_no_=ov.Be24,
            segs_no_=ov.Be24,
            more=True,
        )
        self.addfield("payload_", (hi-lo) - len(self))
        self.done()

class Rc489kDumpEnd(ov.Struct):
    def __init__(self, up, lo, hi):
        super().__init__(
            up,
            lo,
            rec_type_=ov.Be24,
            size_=ov.Be24,
            tot_entry_=ov.Be24,
            tot_segs_=ov.Be24,
            more=True,
        )
        self.done(25*6)

class Rc489kDumpContinue(ov.Struct):
    def __init__(self, up, lo, hi):
        super().__init__(
            up,
            lo,
            rec_type_=ov.Be24,
            size_=ov.Be24,
            tot_entry_=DWord,
            next_tape_=ov.Text(12),
            more=True,
        )
        self.done(25*6)

class Rc489kDumpTapeFile(ov.OctetView):
    def __init__(self, this):
        if this[:6] != b'dump  ':
            return
        this.add_type("Rc489k_Dump")
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
            first_word = ov.Be24(self, rec.lo).val
            if rec.key[1] == 0:
                y = Rc489kDumpLabel(self, rec.lo).insert()
            elif first_word == 1:
                self.proc_recs()
                y = Rc489kDumpEntryRec(self, rec.lo, rec.hi).insert()
                self.recs.append(y)
            elif first_word == 2:
                y = Rc489kDumpSegment(self, rec.lo, rec.hi).insert()
                self.recs.append(y)
            elif first_word == 3:
                y = Rc489kDumpEnd(self, rec.lo, rec.hi).insert()
            elif first_word == 4:
                y = Rc489kDumpContinue(self, rec.lo, rec.hi).insert()
            else:
                break

        self.proc_recs()
        this.add_interpretation(self, self.namespace.ns_html_plain)
        self.add_interpretation(more=True)

    def proc_recs(self):
        recs = self.recs
        self.recs = []
        if len(recs) == 0 or not isinstance(recs[0], Rc489kDumpEntryRec):
            return
        fname = recs[0].entry_name.txt.strip()
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
            if recs[0].entry_tail.tail3.val == 0xa000:
                Rc489kSubCat(that, tns)

#################################################

class Rc489kTape():

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
            that.add_type("Rc489k_TapeFile")
        self.recs = []
   
    def label_interpretation(self, file, _this):
        file.write("<H3>Label</H3>\n")
        file.write("<pre>\n")
        file.write(str(bytes(self.label)) + "\n")
        file.write("</pre>\n")

