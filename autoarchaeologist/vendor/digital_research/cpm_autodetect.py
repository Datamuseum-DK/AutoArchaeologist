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
'''

from ...base import octetview as ov

VALID_DIRENT_STATUS = {
    0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f,
    0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f,
    0x20, 0x21,
    0xe5,
}

INTERLEAVE_BEASTIARIUM = [
    # [ desc, min(sector), max(sector), interleave_order ]
    [ "CR7_Diplomat", 1, 16, [1, 2, 5, 6, 9, 10, 13, 14, 3, 4, 7, 8, 11, 12, 15, 16] ],
]

class DiskGeomZone():
    ''' ... '''
    def __init__(self, clo, hlo, slo, chi, hhi, shi, l):
        self.cylinders = [clo, chi]
        self.heads = [hlo, hhi]
        self.sectors = [slo, shi]
        self.length = l
        self.rendered = None

    def merge(self, other):
        self.cylinders = [
            min(*self.cylinders, *other.cylinders),
            max(*self.cylinders, *other.cylinders)
        ]
        self.heads = [
            min(*self.heads, *other.heads),
            max(*self.heads, *other.heads)
        ]
        self.sectors = [
            min(*self.sectors, *other.sectors),
            max(*self.sectors, *other.sectors)
        ]
        self.rendered = None

    def __repr__(self):
        if not self.rendered:
            i = []
            i.append("c%d" % self.cylinders[0])
            if self.cylinders[1] > self.cylinders[0]:
                i[-1] += "…%d" % self.cylinders[1]
            i.append("h%d" % self.heads[0])
            if self.heads[1] > self.heads[0]:
                i[-1] += "…%d" % self.heads[1]
            i.append("s%d" % self.sectors[0])
            if self.sectors[1] > self.sectors[0]:
                i[-1] += "…%d" % self.sectors[1]
            i.append("b%d" % self.length)
            self.rendered = " ".join(i)
        return self.rendered

class Disk():
    ''' ... '''

    def __init__(self, this):

        self.cylinders = set()
        self.heads = set()
        self.sectors = set()
        self.lengths = set()
        self.zones = []

        self.build_zones(this)

    def build_zones(self, this):
        # We need more detailed metrics
        secs_by_track = {}
        length_by_track = {}
        tracks = set()
        for rec in this.iter_rec():
            trk = rec.key[:2]
            tracks.add(trk)
            if trk not in secs_by_track:
                secs_by_track[trk] = set()
                length_by_track[trk] = set()
            secs_by_track[trk].add(rec.key[2])
            length_by_track[trk].add(len(rec))

        # Build zones of identical tracks
        cur = None
        for trk in sorted(tracks):
            s = secs_by_track[trk]
            x = [length_by_track[trk], min(s), max(s)]
            if x != cur:
                cur = x
                self.zones.append(
                    DiskGeomZone(
                        trk[0],
                        trk[1],
                        min(s),
                        trk[0],
                        trk[1],
                        max(s),
                        list(length_by_track[trk])[0],
                    )
                )
            else:
                self.zones[-1].cylinders[1] = trk[0]
                self.zones[-1].heads[1] = trk[1]

        if len(self.zones) == 1:
            return

        # Defensively Merge zones allowing for missing sectors
        n = 0
        while n < len(self.zones) - 1:
            z1 = self.zones[n]
            z2 = self.zones[n+1]
            if z1.length != z2.length:
                n += 1
                continue

            if z1.sectors[1] == z2.sectors[1]:
                z1.merge(z2)
                self.zones.pop(n+1)
                continue

            if n + 2 < len(self.zones):
                z3 = self.zones[n+2]
                if z1.length == z3.length and z1.sectors[1] == z3.sectors[1]:
                    z1.merge(z2)
                    self.zones.pop(n+1)
                    continue
            n += 1
            continue

    def __repr__(self):
        return "<Disk " + ", ".join("(" + str(x) + ")" for x in self.zones) + ">"

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

    def __repr__(self):
        return "<DE »" + self.name.txt + "«>"

    def looks_sane(self):
        ''' Does this dirent look sane ? '''

        if self.status < 0x21:  # XXX: <= 0xf ?

            ns = set(i & 0x7f for i in self.name)

            if min(ns) < 0x20:
                # Control characters are never allowed
                return False

            if self.status < 0x20 and max(ns) == 0x20:
                # Filenames cannot be all blank
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
            if tree.this[adr] not in VALID_DIRENT_STATUS:
                self.done(len(rec))
                return
        self.credible = 0
        self.add_field("dirents", ov.Array(len(rec)//32, ProbeDirEnt))
        self.done()
        self.score()

    def score(self):
        ''' Tally up points for the credibilty of this sector '''
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
                self.credible = -1
                return
            else:
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

    GIVE_UP_CYLINDER = 5

    def __init__(self, this):

        if not hasattr(this, "iter_rec"):
            # We can only do this if we have CHS geometry
            return

        dsk = Disk(this)

        super().__init__(this)

        self.cand_tracks = {}
        first_good = self.find_candidate_directory_tracks()

        if not first_good:
            # This does not look like a CP/M filesystem
            return

        this.add_note("Probed_CPM")
        with this.add_utf8_interpretation("CP/M filesystem probe") as file:

            file.write("# Disk geometry " + str(dsk) + "\n")

            file.write("\n")
            file.write("First credible dirsect is:")
            file.write(" " + str(first_good.rec.key))
            file.write(" at 0x%x" % first_good.rec.lo)
            file.write(" attribute records found 0x%x" % first_good.attribs)
            file.write("\n")

            file.write("\n")
            file.write("Credible directory tracks:\n")
            credibility = 0
            for trk, i in self.cand_tracks.items():
                file.write(
                    "   " +
                    str(trk).ljust(7) +
                    " 0x%x " % i[0].lo +
                    "-".join("%d" % (1+x.credible) for x in i) +
                    "\n"
                )
                credibility += sum(x.credible for x in i if x.credible > 0)

            file.write("\n")
            file.write("Total credibility: %d\n" % credibility)

            file.write("\n")
            best_interleave = None
            if credibility == first_good.credible:
                file.write("Interleave cannot be determined, all credibility is in first dirsect\n")
            else:
                file.write("Possible interleaves in order of credibility:\n")
                file.write("\n")
                file.write("Penalty  Name         " + "Order".ljust(72) + "  Result\n")
                for penalty, desc, ileave, dirorder in self.find_credible_interleaves():
                    if best_interleave is None:
                        best_interleave = ileave
                    file.write("%7d" % penalty)
                    file.write("  " + desc.ljust(12))
                    file.write(" " + ("(" + "-".join(str(x) for x in ileave) + ")").ljust(72))
                    file.write("  " + str(dirorder) + "\n")

            file.write("\n")
            file.write("File & label names found:\n")

            if best_interleave is None:
                best_interleave = [x.rec.key[2] for x in self.cand_tracks[first_good.rec.key[:2]]]
                file.write("  (Using no interleave)\n")

            for dirsect in self.order_dir(best_interleave):
                if dirsect.credible > 0:
                    file.write("  0x%07x %s\n" % (dirsect.lo, str(dirsect.rec.key)))
                    for de in dirsect.dirents:
                        if de.status != 0xe5:
                            file.write("    " + str(de) + "\n")

    def find_credible_interleaves(self):
        '''
            Yield possible interleave orders by credibility
        '''

        ileaves = []

        for ileave, desc in self.possible_interleaves():
            penalty, dirorder = self.find_interleave_incredibility(ileave)
            if penalty < 0:
                continue
            ileaves.append((penalty, desc, ileave, dirorder))

        yield from sorted(ileaves)

    def possible_interleaves(self):
        '''
           Yield a the potential interleave orders
        '''

        sec_nos = set()
        for dirtrk in self.cand_tracks.values():
            for dirsect in dirtrk:
                sec_nos.add(dirsect.rec.key[2])
        lo_sect = min(sec_nos)
        hi_sect = max(sec_nos)

        for i in range(1, hi_sect // 2):  # Nyquist rulez.
            ileave = list(self.interleave(i, lo_sect, hi_sect))
            yield ileave, str(i)

        for desc, slo, shi, ileave in INTERLEAVE_BEASTIARIUM:
            if slo == lo_sect and shi == hi_sect:
                yield ileave, desc

    def find_interleave_incredibility(self, order):
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

        # Trim incredible and empty dirsects from the tail
        while dirorder and dirorder[-1] <= 0:
            dirorder.pop(-1)

        if -1 in dirorder:
            # This is patently impossible.
            return -1,[]

        penalty = 0
        for n in range(1, len(dirorder)-1):
            # whenever the next dirsect is more filled, we penalize
            # by the increase
            penalty += max(0, dirorder[n+1] - dirorder[n])

        # Empty directs inside the sequence are also penalized
        penalty += dirorder.count(0)

        return penalty, dirorder

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
	   "offset tracks" in the comment in [FW]drives.asm files.)

	   The directory sectors are laid out according to the
	   interleave rule, which is track by track, with zero head
	   and cylinder skew.
   
	   It follows that the first sector of the directory, must
	   be the first "logical" sector in a track, (logical = by
	   the interleave rule.)

	   It also follows, that no matter how many sectors the
	   directory might have, any subsequent track where the
	   first logical sector does not qualify as a directory
	   sector, means that the directory ends before that sector.

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

            # There are usually no more than a couple of "system tracks",
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

            if pds.credible < 0:
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
