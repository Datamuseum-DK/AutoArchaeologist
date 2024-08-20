'''
   RC4000/RC8000/RC9000 Save & Dump Tapes
   --------------------------------------

'''

import time
import html

from ..base import octetview as ov
from ..base import namespace

class Rc489kNameSpace(namespace.NameSpace):
    ''' ... '''

    TABLE = (
        ( "r", "mode"),
        ( "r", "kind"),
        ( "r", "key"),
        ( "r", "nseg"),
        ( "l", "date"),
        ( "l", "docname"),
        ( "r", "w7"),
        ( "r", "w8"),
        ( "r", "w9"),
        ( "r", "w10"),
        ( "l", "name"),
        ( "l", "artifact"),
    )

    def ns_render(self):
        meta = self.ns_priv
        if hasattr(meta, "ns_render"):
            return meta.ns_render() + super().ns_render()
        return [html.escape(str(type(meta)))] + ["-"] * (len(self.TABLE)-3) + super().ns_render()

class DWord(ov.Struct):
    ''' A double word '''

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
    '''
       Time is kept in a double word (=48 bits) counting units of
       100µs since 1968-01-01T00:00:00 local time.

       A ShortClock throws the 5 MSB and 19 LSB bits away, which
       gives a resolution a tad better than a minute and a range
       of almost 28 years.
    '''

    def render(self):
        ''' Render as ISO8601 without timezone '''
        if self.val == 0:
            yield "                "
        else:
            ut = (self.val << 19) * 100e-6
            t0 = (366+365)*24*60*60
            yield time.strftime("%Y-%m-%dT%H:%M", time.gmtime(ut - t0 ))

class Rc489kEntryTail(ov.Struct):
    ''' The ten words which describe a file '''

    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            w1_=ov.Be24,		# really: size/modekind
            docname_=ov.Text(12),
            w6_=ShortClock,
            w7_=ov.Be24,
            w8_=ov.Be24,
            w9_=ov.Be24,
            w10_=ov.Be24,
            #vertical=True,
        )
        if self.w1.val >> 23:
            self.kind = self.w1.val & 0xfff
            self.mode = self.w1.val >> 12
            self.nseg = 0
        else:
            self.kind = 4
            self.mode = 0
            self.nseg = self.w1.val
        self.key = self.w9.val >> 12

    def raw_render(self):
        return [
            ("mode", "%d" % self.mode),
            ("kind", "%d" % self.kind),
            ("key", "%d" % self.key),
            ("nseg", "%d" % self.nseg),
            ("date", "%s" % str(self.w6)),
            ("docname", "%s" % self.docname.txt),
            ("w7", "0x%x" % self.w7.val),
            ("w8", "0x%x" % self.w8.val),
            ("w9", "0x%x" % self.w9.val),
            ("w10", "0x%x" % self.w10.val),
        ]

    def render(self):
        yield "{" + ", ".join("=".join(x) for x in self.raw_render()) + "}"

    def ns_render(self):
        return [x[1] for x in self.raw_render()]

#################################################
#
# A file can be a subdirectory if it has key=10

class Rc489kSubCatEnt(ov.Struct):
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            f00_=ov.Be24,
            f01_=ov.Be24,	# Probably base-low
            f02_=ov.Be24,	# Probably base-high
            filename_=ov.Text(12),
            entry_tail_=Rc489kEntryTail,
        )

    def ns_render(self):
        return self.entry_tail.ns_render()

class Rc489kSubCat(ov.OctetView):
    def __init__(self, this, parent_namespace):
        this.add_type("Rc489kSubCat")
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
                print("BOGOFN", y)
                return
            if y.f00.val not in (0x0, 0xffffff):
                self.dents.append(y)
            ptr = y.hi
            if (i % 15) == 14:
                ptr += 3
        if not self.dents:
            print(this, "No Subdir Dents")
            return
        if (self.dents[-1].f00.val // 64) * 0x300 < len(this):
            divisor = 64
        else:
            divisor = 4096
        print(this, self.__class__.__name__, "divisor=%d" % divisor)
        for dent self.dents:
            begin = (dent.f00.val // divisor) * 0x300
            end = begin + dent.entry_tail.nseg * 0x300
            that = None
            fn = dent.filename.txt.rstrip()
            if begin and begin < end <= len(this):
                y = ov.Opaque(self, lo=begin, hi=end).insert()
                y.rendered = "Data for " + fn
                that = this.create(start = begin, stop = end)
            else:
                print(this, "SubCat cannot", hex(begin), hex(end), hex(len(this)), fn)
            Rc489kNameSpace(
                name = fn,
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
        )

    def ns_render(self):
        return self.entry_tail.ns_render()

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
        self.need = self.de.entry_tail.nseg * 0x300
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
        self.start_of_data = None

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
                if rec.key == self.start_of_data.key:
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
            recs = list(this.iter_rec())
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

                for _n in range(3):
                    rec = recs.pop(0)
                    for x in range(0, len(rec), 0x300):
                        adr = rec.lo + x
                        for _m in range(0x300 // 51):
                            z = Rc489kSaveDirExt(self, adr).insert()
                            adr = z.hi
                            todo.append(Rc489kTodo(self, z))

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
        if todo.de.entry_tail.key == 10:
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
        for adr, _rec in self.iter_index_blocks():
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
            assert not len(rec) % 0x300
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
        if recs[0].dirent.entry_tail.key == 10:
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
    def __init__(self, up, lo):
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
            more=True,
        )
        self.done(25*6)

    def ns_render(self):
        return self.entry_tail.ns_render()

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
    def __init__(self, up, lo):
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
    def __init__(self, up, lo):
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
    '''
       save13 writes "dump" in the second tape block.
    '''

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
        for rec in this.iter_rec():
            first_word = ov.Be24(self, rec.lo).val
            if rec.key[1] == 0:
                y = Rc489kDumpLabel(self, rec.lo).insert()
            elif first_word == 1:
                self.proc_recs()
                y = Rc489kDumpEntryRec(self, rec.lo).insert()
                self.recs.append(y)
            elif first_word == 2:
                y = Rc489kDumpSegment(self, rec.lo, rec.hi).insert()
                self.recs.append(y)
            elif first_word == 3:
                y = Rc489kDumpEnd(self, rec.lo).insert()
            elif first_word == 4:
                y = Rc489kDumpContinue(self, rec.lo).insert()
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
            if recs[0].entry_tail.key == 10:
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
            if not self.label:
                return
            if rec.key[1] == 0:
                self.proc_recs()
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
