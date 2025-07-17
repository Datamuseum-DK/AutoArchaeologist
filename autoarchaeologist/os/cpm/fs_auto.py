#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Attempt to determine parameters of CP/M filesystems
   ===================================================

   For all the good things one can say about CP/M, it was
   a patently idiotic design decision to not write a parameter
   block for the filesystem somewhere on the disk.

   This code attempts to recover as many of the parameters
   as possible, using heuristics which are usually but not
   always true.

   Good source of info:

      https://seasip.info/Cpm/formats.html
'''

from ...base import octetview as ov
from . import common, fs_abc, fs_beastiarium

class ProbeDirEnt(ov.Struct):

    '''
       A DirEnt class for establishing credibility of something being a dirent
    '''

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            naked=True,
            status_=ov.Octet,
            name_=ov.Text(11),
            xl_=ov.Octet,
            bc_=ov.Octet,
            xh_=ov.Octet,
            rc_=ov.Octet,
            al_=16,
        )
        self.fname = "%02x:" % self[0] + "".join("%c" % (self[x]&0x7f) for x in range(1,12))
        self.ignore = len(self.name.txt.strip()) == 0

    def __repr__(self):
        return "<DE »" + self.name.txt + "«>"

    def looks_sane(self):
        ''' Does this dirent look sane ? '''

        if self.status < 0x21:  # XXX: <= 0xf ?

            ns = set(i & 0x7f for i in self.name)

            if min(ns) < 0x20:
                # Control characters are never allowed
                return False

            x = set(self[y] for y in range(len(self)))
            if len(x) == 1:
                # Entire entry cannot be all the same value
                return False

        return True

class ProbeDirSec(ov.Struct):

    '''
       A class for establishing credibility of something being a sector of dirents
    '''

    def __init__(self, tree, rec):
        super().__init__(tree, rec.lo, more=True)
        self.rec = rec
        self.credible = -1
        self.attribs = 0
        for adr in range(rec.lo, rec.hi, 32):
            # Quick check for impossibility
            if tree.this[adr] not in common.VALID_DIRENT_STATUS:
                self.done(len(rec))
                return
        self.credible = 0
        self.add_field("dirents", ov.Array(len(rec)//32, ProbeDirEnt))
        self.done()
        self.score()

    def __str__(self):
        return "<PDS %s %d>" % (str(self.rec), self.credible)

    def score(self):
        ''' Tally up points for the credibilty of this sector '''
        #if self.rec.key[0] > 0:
        #    self.credible = -1
        #    return
        for n, de in enumerate(self.dirents):
            if de.status == 0xe5:
                pass
            elif de.status == 0x21:
                # 0x21 are attribute records for CCPM and if they
                # are used, the last of every four dirents must be one.
                if n & 3 != 3:
                    # 0x21 is out of place
                    self.credible = -1
                    return
                self.attribs += 1
            elif not de.looks_sane():
                #print("CR2", self.rec, self.credible, de)
                self.credible = -1
                return
                #if self.rec.key != (0,3,10):
                #    return
            elif max(de.al) > 0:
                self.credible += 1
        if self.attribs == 0:
            return
        if self.attribs != len(self) // 128:
            self.credible = -1
            return
        self.credible += 1

class ProbeCpmFileSystem(ov.OctetView):

    '''
       Probe an artifact to find out if it holds a CP/M family filesystem
       and determine as many parameters as we can.
    '''

    # The number of "system tracks", or "offset tracks" as they are officially
    # named, is usually just the couple necessary to boot CP/M, so we do not
    # examine the entire artifact.

    # Bits:30005606 has two directories? (cyl 2&6)

    GIVE_UP_CYLINDER = 10

    def __init__(self, this):

        if this.top not in this.parents:
            return
        if not hasattr(this, "iter_rec"):
            # We can only do this if we have CHS geometry
            return

        super().__init__(this)

        self.cand_tracks = {}
        self.first_good = self.find_candidate_directory_tracks()
        self.block_size = None
        self.candidates = []
        self.extent_mask = 0

        if not self.first_good:
            # This does not look like a CP/M filesystem
            return

        tfn = this.tmpfile_for()
        with open(tfn.filename, "w", encoding="utf8") as self.log:

            self.log.write("Geometry: " + str([self.this._key_min, self.this._key_max]) + "\n")
            self.report_dir_tracks()

            self.bnw = self.block_no_width()

            self.find_block_size()

            self.dir_interleave()

            top_credits = None
            top_debits = None
            top = None
            for cand in sorted(self.candidates, reverse=True):
                self.log.write("+%4d -%4d " % (cand.credits, cand.debits) + str(cand) + "\n")
                score = cand.credits - cand.debits
                if top is not None and top > score:
                    break
                if top_credits is not None and top_credits > cand.credits:
                    break
                if top_debits is not None and top_debits < cand.debits:
                    break
                cand.commit()
                if top_credits is None:
                    top = score
                    top_credits = cand.credits
                    top_debits = cand.debits

        with self.this.add_utf8_interpretation(
            "CP/M filesystem probe",
            more=False,
        ) as file:
            for i in open(tfn.filename):
                file.write(i)

    def find_block_size(self):
        self.log.write("\n")
        bsize = 0
        files = {}
        for dent in self.iter_dirents():
            if dent.status > 0xf or dent.ignore:
                continue
            if dent.fname not in files:
                files[dent.fname] = []
            files[dent.fname].append(dent)

        def is_cont(x):
            for n, i in enumerate(x):
                if i != n:
                    return False
            return True

        for fk, dl in files.items():
            el = list(sorted((x.xh << 5) | x.xl for x in dl))
            while el and el[-1] == 0:
                el.pop(-1)
            if is_cont(el):
                continue
            self.extent_mask = 1

        for dent in self.iter_dirents():
            if dent.status > 0xf or dent.ignore:
                continue
            rc = dent.rc + ((dent.xl & self.extent_mask) << 7)
            l = list(self.block_nos(dent))
            if 0 in l:
                c = l.index(0)
            else:
                c = len(l)

            self.log.write(dent.fname + " rc=0x%03x" % rc)
            self.log.write(" c=0x%03x" % c + " " + str(dent) + "\n")
            if c > 0:
                bsize = max(bsize, (rc << 7) / c)
        i = 1
        while i < bsize:
            i += i
        self.log.write("Block Size %.2f %d extent_mask = 0x%x\n" % (bsize, i, self.extent_mask))
        # print(self.this, "Block Size %.2f %d\n" % (bsize, i))
        self.block_size = i


    def report_dir_tracks(self):
        self.log.write("\n")
        self.log.write("First credible dirsect is:")
        self.log.write(" " + str(self.first_good.rec.key))
        self.log.write(" at 0x%x" % self.first_good.rec.lo)
        self.log.write(" with 0x%x attribute records" % self.first_good.attribs)
        self.log.write("\n")

        self.log.write("\n")
        self.log.write("Credible directory tracks:\n")
        credibility = 0
        for trk, i in self.cand_tracks.items():
            self.log.write(
                "   " +
                str(trk).ljust(7) +
                " 0x%x " % i[0].lo +
                "-".join("%d" % (1+x.credible) for x in i) +
                "\n"
            )
            credibility += sum(x.credible for x in i if x.credible > 0)

        self.log.write("\n")
        self.log.write("Total credibility: %d\n" % credibility)

    def block_no_width(self):

        b8 = set()
        b16 = set()
        coll8 = 0
        hole8 = 0
        coll16 = 0
        hole16 = 0
        for dent in self.iter_dirents():
            #print("D", dent)

            l = list(dent.al)
            while l and l[-1] == 0:
                l.pop(-1)
            hole8 += l.count(0)

            for w8 in l:
                if w8 == 0:
                    break
                if w8 in b8:
                    coll8 += 1
                else:
                    b8.add(w8)

            l = []
            for i in range(0, len(dent.al), 2):
                w16 = dent.al[i] | (dent.al[i+1] << 8)
                l.append(w16)
            while l and l[-1] == 0:
                l.pop(-1)
            hole16 += l.count(0)

            for w16 in l:
                if w16 == 0:
                    break
                if w16 in b16:
                    coll16 += 1
                else:
                    b16.add(w16)

        if not b8 or not b16:
            print(self.this, "Nothing")
            retval = None
        else:
            over8 = (max(b8)<<10) > len(self.this)
            over16 = (max(b16)<<10) > len(self.this)
            ok8 = not over8 and not coll8 and not hole8
            ok16 = not over16 and not coll16 and not hole16
            if ok8 and not ok16:
                what = "ok8"
                retval = 8
            elif ok16 and not ok8:
                what = "ok16"
                retval = 16
            elif ok16 and ok8 and (len(self.this) << 10) < 0x100:
                what = "small8"
                retval = 8
            elif ok16 and ok8:
                what = "big8"
                retval = 8
            elif coll8 or hole8:
                what = "guess16"
                retval = 16
            else:
                what = "TBD"
                retval = None

            self.log.write('\n')
            self.log.write("Block number width: " + what + "\n")
            self.log.write('\n')
            self.log.write("   8 " + " ".join([
                    "%5d" % coll8,
                    "%5d" % min(b8),
                    "%5d" % max(b8),
                    "%5d" % hole8,
                    "%6s" % str(over8),
                ]) + "\n")
            self.log.write("  16 " + " ".join([
                    "%5d" % coll16,
                    "%5d" % min(b16),
                    "%5d" % max(b16),
                    "%5d" % hole16,
                    "%6s" % str(over16),
                ]) + "\n")
        if retval == 8:
            self.block_nos = self.block_nos_are_8
        else:
            self.block_nos = self.block_nos_are_16
        return retval


    def block_nos_are_8(self, dent):
        ''' ... '''
        yield from dent.al

    def block_nos_are_16(self, dent):
        ''' ... '''
        for i in range(0, len(dent.al), 2):
            yield dent.al[i] | (dent.al[i+1] << 8)


    def iter_dirents(self):
        for trk in self.cand_tracks.values():
            for sect in trk:
                if sect.credible < 0:
                    continue
                for dent in sect.dirents:
                    if dent.status < 0x10:
                        yield dent

    def dir_interleave(self):

        file = self.log

        self.best_interleave = None
        self.best_ndirsect = None

        file.write("\n")
        file.write("Candidate interleaves in order of directory credibility:\n")
        file.write("\n")
        file.write("Penalty  Name         " + "Order".ljust(72) + "  Resulting dir order\n")
        min_track = self.first_good.rec.key[0]
        max_track = 0
        max_head = 0
        for rec in self.this.iter_rec():
            max_track = max(rec.key[0], max_track)
            max_head = max(rec.key[1], max_head)
        candidate_interleaves = list(self.find_credible_interleaves())
        for penalty, desc, ileave, dirorder, ndirsect in candidate_interleaves:
            if self.best_interleave is None:
                self.best_interleave = ileave
                self.best_ndirsect = ndirsect
            file.write("%7d" % penalty)
            file.write("  " + desc.ljust(12))
            file.write(" " + ("(" + "-".join(str(x) for x in ileave) + ")").ljust(72))
            file.write("  " + str(dirorder))

            if not ndirsect:
                file.write("\n")
                continue

            trks = [
                    (c, h) for c in range(min_track, max_track + 1) for h in range(max_head + 1)
                ]
            while trks[0] < self.first_good.rec.key[:2]:
                trks.pop(0)
            class CpmFSAuto(fs_abc.CpmFileSystem):
                SECTOR_SIZE = len(self.first_good)
                SECTORS = ileave
                TRACKS = trks
                BLOCK_SIZE = self.block_size
                BLOCK_NO_WIDTH = self.bnw
                N_DIRENT = ndirsect * (len(self.first_good) // 0x20)
                EXTENT_MASK = self.extent_mask

            try:
                x = CpmFSAuto(self.this, commit=False)
            except fs_abc.Nonsense:
                continue
            if x.credits:
                self.candidates.append(x)
            file.write("   +%d/-%d" % (x.credits, x.debits))
            file.write("\n")

        for cls in fs_beastiarium.GEOMETRY_BEASTIARIUM:
            try:
                x = cls(self.this, commit=False)
            except fs_abc.Nonsense:
                continue
            if x.credits:
                self.candidates.append(x)
            file.write("From the beastiarium: " + x.name)
            file.write("   +%d/-%d" % (x.credits, x.debits))
            file.write("\n")

        file.write("\n")
        file.write("File & label names found:\n")

        if self.best_interleave is None:
            self.best_interleave = [
                x.rec.key[2] for x in self.cand_tracks[self.first_good.rec.key[:2]]
            ]
            file.write("  (Using no interleave)\n")

        for dirsect in self.order_dir(self.best_interleave):
            if dirsect.credible > 0:
                file.write("  0x%07x %s\n" % (dirsect.lo, str(dirsect.rec.key)))
                #file.write("  0x%07x %s cred=%d\n" % (dirsect.lo, str(dirsect.rec.key), dirsect.credible))
                for de in dirsect.dirents:
                    if de.status <= 0x20:
                        file.write("    " + str(de) + "\n")

    def find_credible_interleaves(self):
        '''
            Yield possible interleave orders by credibility
        '''

        ileaves = []

        for ileave, desc in self.possible_interleaves():
            penalty, dirorder, ndirsec = self.determine_interleave_credibility(ileave)
            if penalty < 0:
                continue
            ileaves.append((penalty, desc, ileave, dirorder, ndirsec))

        yield from sorted(ileaves)

    def possible_interleaves(self):
        '''
           Yield all potential interleave orders
        '''

        sec_nos = set()
        for dirtrk in self.cand_tracks.values():
            for dirsect in dirtrk:
                sec_nos.add(dirsect.rec.key[2])
        lo_sect = min(sec_nos)
        hi_sect = max(sec_nos)

        for i in range(1, hi_sect // 2):  # Nyquist rulez ?
            ileave = list(self.interleave(i, lo_sect, hi_sect))
            yield ileave, "normal-%d" % i

        for desc, ileave in fs_beastiarium.INTERLEAVE_BEASTIARIUM:
            if min(ileave) == lo_sect and max(ileave) == hi_sect:
                yield ileave, desc

    def determine_interleave_credibility(self, order):
        '''
           Return the incredibility score for a proposed interleave order
           --------------------------------------------------------------

	   At a minimum, an interleave order cannot put any incredible
	   dirsects before any dirsects with valid entries.

	   Because the allocation order is first fit, the canonical
	   pattern is a sequence of full dirsects, a partially full
	   dirsect followed by empty dirsects.  The pattern degrades
	   when files are deleted, and can break down entirely when
           a lot of files are deleted.

           Return value:
              (incredibility, [fill order of dirsects])
          
           incredibility is: 
               negative - Impossible ordering
               zero     - perfect pattern
               positive - Increasingly incredible

        '''

        dirorder = [x.credible for x in self.order_dir(order)]
        # self.log.write("DIL " + str(order) + " > " + str(dirorder) + "\n")

        # Trim incredible and empty dirsects from the tail
        while dirorder and dirorder[-1] <= 0:
            dirorder.pop(-1)

        if -1 in dirorder:
            # This order is patently impossible.
            # print(self.this, "DO", dirorder, order)
            return -1,[], 0

        penalty = 0
        for n in range(1, len(dirorder)-1):
            # whenever the next dirsect is more filled, we penalize
            # by the increase
            penalty += max(0, dirorder[n+1] - dirorder[n])

        # Empty directs inside the sequence are also penalized
        penalty += dirorder.count(0)

        return penalty, dirorder, len(dirorder)

    def order_dir(self, interleave):
        '''
           Yield the dirsects in interleave order
        '''

        for dirtrk in self.cand_tracks.values():
            dirsects = {}
            for dirsect in dirtrk:
                dirsects[dirsect.rec.key[2]] = dirsect
            for n in interleave:
                yield dirsects[n]

    def find_candidate_directory_tracks(self):
        '''
           Find the set of tracks which may be part of the directory
           ---------------------------------------------------------

	   The directory starts after the "System tracks".  (aka.
	   "offset tracks" in the comments in [FW]drives.asm files.)

	   The directory sectors are laid out according to the
	   interleave rule, which is track by track, with zero head
	   and cylinder skew.
   
	   It follows that the first sector of the directory, must
	   be the first "logical" sector in a track, (logical = by
	   the interleave rule.)

	   It also follows, that no matter how many sectors the
	   directory might have, any subsequent track where the
	   first logical sector does not qualify as a directory
	   sector, means that the directory ends before that track.

	   In the absense of head and cylinder skew, assuming that
	   the first physical sector in a track is also the first
	   logical sector in it, holds up pretty well, but we can
           make no assumptions about any other physical sector's 
           logical number.  The first physical sector may be number
           zero or one.

	   All directory entries in a directory sector must be
	   recognizable for what they are to the CP/M kernel, that
	   means that the first byte of every 32 can have only
           the following values:

               0x00-0x1f  Entry in use. 
               0x20       Label entry.
               0x21       Attribute record.
               0xe5       Entry not in use.

	   The choice of 0xe5 is a bit of a bother, because that
	   is a "clock breaker" often used in formatting, so all
	   unwritten sectors are valid, but empty, directory sectors.

	   Attribute records either occur in all (x mod 4 == 3)
	   positions in the directory, or not at all.

	   File- and label names use the upper bit for flags, but
	   the lower 7 bits cannot be less than 0x20 (ie: no control
	   characters).

           Only labels are allows to be blank (all 0x20)

	   Directory entries are allocated first-fit, but there is
	   no compaction, so there is no guarantee that any entries
	   are in use in the first, or in fact any, directory sector,
           but it is a pretty good bet, that there is at least one
           entry in use in the first track of the directory.

        '''
        first_good = None
        attribs = 0
        non_dir_sectors = False
        for rec in self.this.iter_rec():

            # There are usually just a few "system tracks",
            if rec.key[0] >= self.GIVE_UP_CYLINDER:
                break

            trk = rec.key[:2]
            ctrk = self.cand_tracks.get(trk)
            pds = ProbeDirSec(self, rec)
            if ctrk and ctrk[0].credible < 0 and ctrk[0].rec.key[2] < 2:
                # If the first logical&physical sector in a track is not
                # not a credible directory sector, none of the other ones
                # will be either, so we can skip them.
                continue

            if ctrk is None:

                # If previous track of the directory had non-directory
                # sectors, it was the final track of the directory.
                if first_good and non_dir_sectors:
                    break

                # If the first logical&physical sector of a new track is not
                # credible, or lacks attributes when we have seen them, the
                # directory is over and we can stop.
                if first_good and rec.key[2] < 2:
                    if pds.credible < 0 or (attribs and pds.attribs == 0):
                        break

                if not first_good:
                    # Wrong for multi-track directory filesystems, where all
                    # entries in the initial track(s) of the directory are
                    # unused.
                    self.cand_tracks = {}
                    self.non_dir_sectors = False

                ctrk = []
                self.cand_tracks[trk] = ctrk

            ctrk.append(pds)

            if first_good and pds.credible < 0:
                non_dir_sectors = True

            if pds.credible > 0:
                attribs += pds.attribs

            if not first_good and pds.credible > 0:
                # Remember the first non-empty directory sector.
                first_good = pds

        return first_good

    def interleave(self, n, first, last):
        ''' Yield interleaved sequence of sectors '''
        offset = first
        last -= offset
        sects = set(range(last + 1))
        cur = 0
        while sects:
            if cur > last:
                cur -= 1 + last
            if cur in sects:
                yield cur + offset
                sects.discard(cur)
                cur += n
            else:
                cur += 1
