#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   RC4000/RC8000/RC9000 Save & Dump Tapes
   --------------------------------------

   This format is documented in 30007497:
	SW8010 System Utility - Save, Incsave; Load, Incload
	Chapter 7 "Exact Formats"

'''

from ...base import octetview as ov
from .rc489k_utils import Rc489kNameSpace, ShortClock, Rc489kBasePair, Rc489kEntryTail

class Rc489kSaveLabel(ov.Struct):
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,				# Description from 30007497 page 34 (pdf pg 40):
            program_=ov.Text(9),	# program name (save or incsave)
            tape_=ov.Text(12),		# current tape name
            fileno_=ov.Text(6),		#    and file number
            vers_=ov.Text(6),		# the text "vers." or "cont."
            date_=ov.Text(15),		#    followed by the dumptime
            seg_=ov.Text(9),		# the text "segm." followed by the maximal block length
					# in segments
            lbl_=ov.Text(6),		# the text "label." […] or "level."
            lbltext_=ov.Text(24),	#    followed by the label text […]
					#    and the characters <0>*5 <em>
            segm_=ov.Be24,		# maximal block length in segments
            maxpartial_=ov.Be24,	# maximal no of entries in partial catalogs
            scatentries_=ov.Be24,	# no of entries in the save catalog
            szcat_=ov.Text(12),		# name of save catalog
            entry_base_=Rc489kBasePair,	# lower entry base for save catalog
            szsavecat_=ov.Be24,		# size of save catalog in segments
            dumptime_=ShortClock,	# shortclock for dumptime (= tail (6) in save catalog
					# entry in main catalog
            version_=ov.Be24,		# version
            release_=ov.Be24,		# release <12 + subrelease
            lensynccat_=ov.Be24,	# length of sync block preceeding partial catalogs
					#    (halfwords)
            lensyncarea_=ov.Be24,	# length of sync block following areas (halfwords)
					# (only release 3.0 and newer)
            vertical=True,
        )

class Rc489kFirstWord(ov.Be24):

    def __init__(self, up, lo):
        super().__init__(up, lo)
        self.first_slice = self.val >> 12
        self.namekey = (self.val >> 3) & 0x1ff
        self.permkey = self.val & 7

    def render(self):
        yield "{1slice=0x%03x,namekey=0x%03x,permkey=0x%01x}" % (
            self.first_slice,
            self.namekey,
            self.permkey
        )

class Rc489kSaveDirEnt(ov.Struct):
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            first_word_=Rc489kFirstWord,
            entry_base_=Rc489kBasePair,
            filename_=ov.Text(12),
            entry_tail_=Rc489kEntryTail,
            scope_=ov.Be24,
            actual_scope_=ov.Be24,
            new_scope_=ov.Be24,
            disk_nbr_=ov.Be24,
            new_disk_=ov.Text(12),
            last_change_=ShortClock,
            vol_count_=ov.Be24,
            file_count_=ov.Be24,
            block_count_=ov.Be24,
        )
        self.namespace = Rc489kNameSpace(
            name = self.filename.txt,
            parent = self.tree.namespace,
            priv = self,
        )

    def ns_render(self):
        return [str(self.entry_base)] + self.entry_tail.ns_render()

class Rc489kSaveDirExt(ov.Struct):
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            first_word_=Rc489kFirstWord,
            entry_base_=Rc489kBasePair,
            filename_=ov.Text(12),
            entry_tail_=Rc489kEntryTail,
        )
        self.parts = []
        self.has = 0
        self.need = self.entry_tail.nseg * 0x300
        self.that = None

    def feed(self, rec):
        self.has += len(rec)
        y = ov.Opaque(self.tree, lo=rec.lo, hi=rec.hi).insert()
        y.rendered = "Data for " + self.filename.txt + " 0x%x" % (len(rec) // 0x300)
        y.rendered += " 0x%+x" % (self.need - self.has)
        self.parts.append(rec)
        #assert self.has <= self.need
        if self.has < self.need:
            return False
        #y = ov.Opaque(self.tree, lo=self.parts[0].lo, width=self.need).insert()
        #y.rendered = "Data for " + self.filename.txt + " 0x%x" % (len(y) // 0x300)
        #print(self.tree.this, "Y", "0x%x-0x%x" % (y.lo, y.hi), y)
        #if y.hi < self.parts[-1].hi:
        #    z = ov.Opaque(self.tree, lo= y.hi, hi= self.parts[-1].hi).insert()
        self.that = self.tree.this.create(records = self.parts)
        return True

    def ns_render(self):
        return self.entry_tail.ns_render()

class Rc489kSaveCatalogHead(ov.Struct):
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            cat_base_=Rc489kBasePair,		# catalog base
            std_base_=Rc489kBasePair,		# standard base
            user_base_=Rc489kBasePair,		# user base
            max_base_=Rc489kBasePair,		# max base
            n_disk_=ov.Be24,			# number of disks in the backing storage system
            n_tapes_=ov.Be24,			# max number of volume tapes (32)
            n_copies_=ov.Be24,			# number of copies specified
            n_volcopy1_=ov.Be24,		# number of volume tapes specified copy no 1
            n_volcopy2_=ov.Be24,		# number of volume tapes specified copy no 2
            max_tape_seg_=ov.Be24,		# max number of segments in one block on the tape
            vertical=True,
            more=True,
        )
        self.addfield("disknames", ov.Array(self.n_disk.val, ov.Text(12), vertical=True))
        self.addfield("tapenames1", ov.Array(32, ov.Text(12), vertical=True))
        self.addfield("tapenames2", ov.Array(32, ov.Text(12), vertical=True))
        while self.tapenames1.array and self.tapenames1.array[-1].txt.strip() == "":
            self.tapenames1.array.pop(-1)
        while self.tapenames2.array and self.tapenames2.array[-1].txt.strip() == "":
            self.tapenames2.array.pop(-1)
        nseg = (len(self) + 0x2ff) // 0x300
        self.done(nseg * 0x300)

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

class Rc489kSyncCat(ov.Opaque):
    ''' ... '''

class Rc489kSyncArea(ov.Opaque):
    ''' ... '''

class Rc489kRec(ov.Dump):
    ''' ... '''

    def render(self):
        yield "Rec[0x%x] " % (self.hi - self.lo)

class Rc489kSaveTapeFile(ov.OctetView):
    def __init__(self, this):
        if this[:9] != b'save     ':
            return
        this.add_type("Rc489k_Save")
        print(this, self.__class__.__name__)
        super().__init__(this)

        self.namespace = Rc489kNameSpace(
            name='',
            separator='',
            root=this,
        )

        self.recs = list(this.iter_rec())
        self.label = Rc489kSaveLabel(self, self.recs.pop(0).lo).insert()
        print(this, self.label)
        if self.label.vers.txt.strip() == "empty":
            return
        rec = self.recs.pop(0)
        self.cathead = Rc489kSaveCatalogHead(self, rec.lo).insert()
        ptr = self.cathead.hi
        self.dirents = []
        self.names = {}
        while len(self.dirents) < self.label.scatentries.val:
            if ptr == rec.hi:
                rec = self.recs.pop(0)
                ptr = rec.lo
            for i in range(8):
                if len(self.dirents) < self.label.scatentries.val:
                    y = Rc489kSaveDirEnt(self, ptr).insert()
                    self.dirents.append(y)
                    i = self.names.get(y.filename.txt)
                    if i is None:
                        i = []
                        self.names[y.filename.txt] = i
                    i.append(y)
                else:
                    y = ov.Opaque(self, ptr, width=87).insert()
                ptr = y.hi
            y = ov.Opaque(self, ptr, width = 0x300 % 87).insert()
            ptr = y.hi

        in_cat = True
        catlist = []
        cur = None
        while self.recs:
            rec = self.recs.pop(0)
            if len(rec) == 3 * self.label.lensynccat.val // 2:
                print("=" * 40, "INCAT")
                in_cat = True
                catlist = []
                cur = None
                Rc489kSyncCat(self, lo=rec.lo, hi=rec.hi).insert()
                continue
            if len(rec) == 3 * self.label.lensyncarea.val // 2:
                print("=" * 40, "INAREA")
                in_cat = False
                Rc489kSyncArea(self, lo=rec.lo, hi=rec.hi).insert()
                continue
            if in_cat:
                ptr = rec.lo
                while ptr < rec.hi:
                    for i in range(0x300 // 51):
                        if len(catlist) < self.label.maxpartial.val:
                            y = Rc489kSaveDirExt(self, lo=ptr).insert()
                            catlist.append(y)
                        else:
                            y = ov.Opaque(self, lo=ptr, width=51).insert()
                        ptr = y.hi
                    y = ov.Opaque(self, lo = ptr, width = 0x300 % 51).insert()
                    ptr = y.hi
                if len(catlist) >= self.label.maxpartial.val:
                    print("=" * 40, "CAT FULL")
                    in_cat = False
                else:
                    print(this, "GOT", len(catlist), "WANT", self.label.maxpartial.val)
            else:
                while cur is None and catlist:
                    cur = catlist.pop(0)
                    if cur.need == 0:
                        print("SKIP", cur)
                        cur = None
                        continue
                    if cur.first_word.first_slice == 0:
                        print("UNAVAIL", cur)
                        cur = None
                        continue
                if not cur:
                    break
                if cur.feed(rec):
                    for j in self.names[cur.filename.txt]:
                        print("Q", j.entry_base, cur.entry_base, cur.filename.txt)
                        if j.first_word.first_slice == cur.first_word.first_slice:
                            j.namespace.ns_set_this(cur.that)
                    cur = None
        while self.recs:
            rec = self.recs.pop(0)
            Rc489kRec(self, lo=rec.lo, hi=rec.hi).insert()

        print(this, "A")
        this.add_interpretation(self, self.namespace.ns_html_plain)
        print(this, "B")
        self.add_interpretation(more=True)
        print(this, "C")
