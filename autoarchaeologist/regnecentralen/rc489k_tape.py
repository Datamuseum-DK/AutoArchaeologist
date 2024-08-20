'''
   RC8000 Save Tapes
   -----------------
'''

import time

from ..generic import hexdump

from ..base import octetview as ov
from ..base import namespace

class Rc489kNameSpace(namespace.NameSpace):
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
            fn = y.filename.txt.strip()
            if " "  in fn:
                return
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
            mns = Rc489kNameSpace(
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
            tsave_=ov.Text(9),
            ttapename_=ov.Text(12),
            tfileno_=ov.Text(6),
            tvers_=ov.Text(6),
            tdate_=ov.Text(15),
            tseg_=ov.Text(9),
            tlbl_=ov.Text(15),
            f07_=ov.Text(9),
            f08_=ov.Be24,
            f09_=ov.Be24,
            segm_=ov.Be24,
            f11_=ov.Be24,
            f12_=ov.Be24,
            f13_=ov.Text(9),
            f14_=ov.Be24,
            f15_=ov.Be24,
            f16_=ov.Be24,
            f17_=ov.Be24,
            f18_=ov.Be24,
            f19_=ov.Be24,
            f20_=ov.Be24,
            f21_=ov.Be24,
            f22_=ov.Be24,
            f99_=ov.Array(6, ov.Be24),
            vertical=True,
        )

class Rc489kSaveDirEnt(ov.Struct):
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            f00_=ov.Array(3, ov.Be24),
            filename_=ov.Text(12),
            entry_tail_=Rc489kEntryTail,
            f06_=ov.Array(4, ov.Be24),
            f07_=ov.Text(12),
            f08_=ov.Array(4, ov.Be24),

            #f06_=ov.Array(3, ov.Be24),
            #f07_=Rc489kEntryTail,
        )

class Rc489kSaveDirExt(ov.Struct):
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            f00_=ov.Array(3, ov.Be24),
            filename_=ov.Text(12),
            entry_tail_=Rc489kEntryTail,
        )

class Rc489kSaveSubHead(ov.Struct):
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            f00_=ov.Array(8, ov.Be24),
            nvol_=ov.Be24,
            f01_=ov.Array(5, ov.Be24),
            vertical=True,
            more=True,
        )
        self.addfield("vols", ov.Array(self.nvol.val, ov.Text(12), vertical=True))
        self.addfield("lbl", ov.Text(12))
        self.done(0x300)

class Rc489kSaveDirSect(ov.Struct):
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            dirent_=ov.Array(0x300//87, Rc489kSaveDirEnt, vertical=True),
            pad__=(0x300 % 87),
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

class Rc489kDummy(ov.Struct):
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            f00_=ov.Text(64),
            more=True,
        )
        self.done(0x300)

class Rc489kEndOfDirectory(ov.Opaque):
    ''' ... '''

class Rc489kDataBlock(ov.Opaque):
    ''' ... '''

class Rc489kTodo():

    def __init__(self, up, entry):
        self.up = up
        self.de = entry
        self.filename = self.de.filename.txt.strip()
        self.flag = self.de.f00[0].val >> 12
        self.need = (self.de.entry_tail.nrec.val & 0xffff) * 0x300
        self.got = 0
        self.pieces = []

    def happy(self):
        #print(self.de.filename.txt, "?", self.flag, self.need, self.got)
        if self.flag in (0x000, 0x800):
             return True
        return self.need == self.got

    def feed(self, item):
        y = ov.Opaque(self.up, lo=item.lo, hi=item.hi).insert()
        y.rendered = "Data for " + self.de.filename.txt
        #print(self.de.filename.txt, "+", self.flag, self.need, self.got, hex(len(item)))
        # assert len(item) in (0x900, self.need - self.got)
        self.got += len(item)
        self.pieces.append(item)

class Rc489kSaveTapeFile(ov.OctetView):
    def __init__(self, this):
        if this[:9] != b'save     ':
            return
        this.add_type("Rc489k_Save")
        self.has480 = 480 in (len(x) for x in this.iter_rec())
        self.has300 = 300 in (len(x) for x in this.iter_rec())
        print(this, self.__class__.__name__)
        super().__init__(this)

        self.namespace = Rc489kNameSpace(
            name='',
            separator='',
            root=this,
        )

        self.hdr = Rc489kSaveHead(self, 0).insert()
        self.index = []
        if self.hdr.tvers.txt == "empty ":
            ov.Opaque(self, lo=self.hdr.hi, hi=len(this)).insert()
        elif self.has480:
            self.do_index()
            self.recs = []
            for rec in this.iter_rec():
                if rec.key < self.start_of_data.key:
                    continue
                elif rec.key == self.start_of_data.key:
                    y = ov.Opaque(self, lo = rec.lo, hi = rec.hi).insert()
                elif len(rec) == 480:
                    self.do_recs()
                    y = Rc489kSaveEntry(self, rec.lo, rec.hi).insert()
                    self.recs.append(y)
                elif self.recs and len(rec) > 480:
                    y = Rc489kDataBlock(self, lo = rec.lo, hi = rec.hi).insert()
                    self.recs.append(y)
        else:
            self.do_index()
            recs = [x for x in this.iter_rec()]
            while recs[0].key < self.start_of_data.key:
                recs.pop(0)
            todo = []
            while recs:
                if len(recs[0]) != 300:
                    while todo[0].happy():
                        self.finish_todo(todo.pop(0))
                    todo[0].feed(recs.pop(0))
                    continue
                todo = []
                rec = recs.pop(0)
                y = ov.Opaque(self, lo=rec.lo, hi=rec.hi).insert()
                y.rendered = "WorkPackageMarker"
 
                for n in range(3):
                     rec = recs.pop(0)
                     for x in range(0, len(rec), 0x300):
                         adr = rec.lo + x
                         for m in range(0x300 // 51):
                             z = Rc489kSaveDirExt(self, adr).insert()
                             adr = z.hi
                             todo.append(Rc489kTodo(self, z))
                #print("LL", this, len(todo))
                
        this.add_interpretation(self, self.namespace.ns_html_plain)
        self.add_interpretation(more=True)

    def finish_todo(self, todo):
        if len(todo.pieces) == 0:
            return
        first = todo.pieces[0].lo
        last = todo.pieces[0].hi
        that = self.this.create(start=first, stop=last, records=todo.pieces)
        tns = Rc489kNameSpace(
            name = todo.filename,
            parent = self.namespace,
            priv = todo.de,
            this = that,
        )
        if todo.de.entry_tail.tail3.val in (0xa000, ):
            Rc489kSubCat(that, tns)

    def iter_index(self):
        for rec in self.index:
            for dirent in rec.dirent:
                if dirent.f00[2].val == 0:
                    return
                yield dirent

    def do_index(self):
        self.subhdr = None
        self.bishdr = None
        for adr, rec in self.iter_index_blocks():
            if self.subhdr is None:
                self.subhdr = Rc489kSaveSubHead(self, adr).insert()
            elif self.bishdr is None:
                self.bishdr = ov.Opaque(self, adr, 0x300).insert()
            else:
                y = Rc489kSaveDirSect(self, adr).insert()
                self.index.append(y)

    def iter_index_blocks(self):
        for rec in self.this.iter_rec():
            if rec.key[1] == 0:
                continue
            if len(rec) == 300:
                self.start_of_data = rec
                return
            assert not (len(rec) % 0x300)
            for j in range(0, len(rec), 0x300):
                yield rec.lo + j, rec

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
        tns = Rc489kNameSpace(
            name = fname,
            parent = self.namespace,
            priv = recs[0].dirent,
            this = that,
        )
        if recs[0].dirent.entry_tail.tail3.val in (0xa000, ):
            Rc489kSubCat(that, tns)


#################################################

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
            #vertical=True,
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

        self.namespace = Rc489kNameSpace(
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
            tns = Rc489kNameSpace(
                name = fname,
                parent = self.namespace,
                priv = recs[0],
                this = that,
            )
            if recs[0].entry_tail.tail3.val in (0xa000, ):
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
        if not self.label:
            return
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

