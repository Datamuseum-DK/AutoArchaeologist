'''
   RC4000/RC8000/RC9000 Dump Tapes
   -------------------------------

'''

from ..base import octetview as ov
from .rc489k_utils import ShortClock, Rc489kNameSpace, Rc489kEntryTail, DWord

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
        return ["?"] + self.entry_tail.ns_render()

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
        for dent in self.dents:
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
        return ["?"] + self.entry_tail.ns_render()

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
