#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Microsoft FATFS

'''

import collections

from ...base import namespace
from ...base import octetview as ov

Geometry = collections.namedtuple(
    "Geometry",
    "cyl hd sect bps rsv nfat spcl rdir nfsc tsect",
)

# See for instance:
#    https://en.wikipedia.org/wiki/Design_of_the_FAT_file_system

GEOMETRIES = {
    0xffffff: [
        #        cyl hd sec   bps rsv nfat spcl rdir
        Geometry(40, 2,  8,  512,  1,   2,   2,  112, 0, 0),
    ],
    0xfffffe: [
        # cyl hd sec   bps rsv nfat spcl rdir
        Geometry(40, 1,  8,  512,  1,   2,   1,   64, 0, 0),
        Geometry(77, 1, 26,  128,  1,   2,   4,   68, 0, 0),
        Geometry(77, 1,  8, 1024,  1,   2,   4,  192, 0, 0),
        Geometry(77, 2,  8, 1024,  1,   2,   4,  192, 0, 0),
    ],
    0xfffffd: [
        # cyl hd sec   bps rsv nfat spcl rdir
        Geometry(40, 2,  9,  512,  1,   2,   2,  112, 0, 0),
        Geometry(77, 1, 26,  128,  4,   2,   4,   68, 0, 0),
        Geometry(77, 2, 26,  128,  4,   2,   4,   68, 0, 0),
    ],
    0xfffffc: [
        # cyl hd sec   bps rsv nfat spcl rdir
        Geometry(40, 1,  9,  512,  1,   2,   1,   64, 0, 0),
    ],
    0xfffffb: [
        # cyl hd sec   bps rsv nfat spcl rdir
        Geometry(80, 2,  8,  512,  1,   2,   2,  112, 0, 0),
    ],
    0xfffffa: [
        # cyl hd sec   bps rsv nfat spcl rdir
        Geometry(80, 1,  8,  512,  1,   2,   1,  112, 0, 0),
    ],
    0xfffff9: [
        # cyl hd sec   bps rsv nfat spcl rdir
        Geometry(80, 2, 15,  512,  1,   2,   1,  224, 0, 0),
        Geometry(80, 2,  9,  512,  1,   2,   1,  112, 0, 0),
        Geometry(80, 2, 18,  512,  1,   2,   1,  224, 0, 0),
    ],
    0xfffff8: [
        # cyl hd sec   bps rsv nfat spcl rdir
        Geometry(80, 1,  9,  512,  1,   2,   2,  112, 0, 0),
    ],
    0xfffff0: [
        # cyl hd sec   bps rsv nfat spcl rdir
        Geometry(80, 2, 18,  512,  1,   2,   1,  224, 0, 0),
        Geometry(80, 2, 36,  512,  1,   2,   2,  224, 0, 0),
    ],
}

def match_geometry(this, fat0):
    ''' Guess FAT parameters for artifacts without a BPB '''
    if len(this) in (286464,):
        # HP 150 ?
        return Geometry(66, 1, 16, 256, 1, 2, 4, 128, 3)
    if fat0 not in GEOMETRIES:
        return None
    for geometry in GEOMETRIES.get(fat0):
        size = geometry.cyl * geometry.hd * geometry.sect * geometry.bps
        if len(this) == size:
            return geometry
    for geometry in GEOMETRIES.get(fat0):
        size = geometry.cyl * geometry.hd * geometry.sect * geometry.bps
        print(this, "NoGeom?", hex(fat0), geometry, len(this), size)
    return None

class BiosParamBlock(ov.Struct):
    ''' ... '''

    # Field names mirro FreeBSD's msdosfs
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            vertical=True,
            bsJmp_=3,
            bsOem_=ov.Text(8),
            # From DOS2.0
            bsBytesPerSec_=ov.Le16,
            bsSectPerClust_=ov.Octet,
            bsResSectors_=ov.Le16,
            bsFATS_=ov.Octet,
            bsRootDirEnts_=ov.Le16,
            bsSectors_=ov.Le16,
            bsMedia_=ov.Octet,
            bsFATsecs_=ov.Le16,
            # From DOS3.0
            bsSectPerTrack_=ov.Le16,
            bsHeads_=ov.Le16,
            bsHiddenSecs_=ov.Le32,
            # From DOS3.2
            bpbHugeSectors_=ov.Le32, # DOS3.2: Le16, DOS3.31: Le32
            more=True,
        )
        if tree.this[lo + 0x26] in (0x28, 0x29):
            # From OS/2 1.0, DOS 4.0
            self.add_field("bsPhysDrive", ov.Octet)
            self.add_field("bsReserved", ov.Octet)
            self.add_field("bsExtBootSig", ov.Octet)
            self.add_field("bsVolId", ov.Le32)
            self.add_field("bsVolName", ov.Text(11))
            self.add_field("bsFsType", ov.Text(8))
        elif ov.Le32(tree, 0x24).val > 0x200000:
            # Seen om Concurrent DOS hard disk
            self.add_field("bsPhysDrive", ov.Octet)
            self.add_field("bsReserved", ov.Octet)
            self.add_field("bsExtBootSig", ov.Octet)
            self.add_field("bsUnknown", 11)
            self.add_field("bsVolName", ov.Text(12))
        else:
            self.add_field("bsBigFATsecs", ov.Le32)
            self.add_field("bsExtFlags", ov.Le16)
            self.add_field("bsFsInfo", ov.Le16)
            self.add_field("bsRootClust", ov.Le32)
            self.add_field("bsFSVers", ov.Le16)
            self.add_field("bsBackup", ov.Le16)
            self.add_field("bsReserved", ov.Text(12))

        self.done()
        if self.is_sane():
            if self.bsSectors.val:
                tsect = self.bsSectors.val
            else:
                tsect = self.bpbHugeSectors.val
            self.geom = Geometry(
                tsect // (self.bsHeads.val * self.bsSectPerTrack.val),
                self.bsHeads.val,
                self.bsSectPerTrack.val,
                self.bsBytesPerSec.val,
                self.bsResSectors.val,
                self.bsFATS.val,
                self.bsSectPerClust.val,
                self.bsRootDirEnts.val,
                self.bsFATsecs.val,
                tsect,
            )
        else:
            self.geom = None

    def is_sane(self):
        ''' Sanity check '''

        if not self.bsBytesPerSec.val in (128, 256, 512, 1024, 2048, 4096):
            # Improbable sector size
            return False
        if self.bsResSectors.val == 0:
            # BPB and FAT cannot overlap
            return False
        return True

class DirEnt(ov.Struct):
    '''
       Directory Entry
    '''

    def __init__(self, tree, lo, pns):
        super().__init__(
            tree,
            lo,
            vertical=False,
            name_=ov.Text(11),
            attr_=ov.Octet,
            locase_=ov.Octet,
            ctime_=ov.Le24,
            cdate_=ov.Le16,
            adate_=ov.Le16,
            hicl_=ov.Le16,
            mtime_=ov.Le16,
            mdate_=ov.Le16,
            cluster_=ov.Le16,
            length_=ov.Le32,
        )
        self.deleted = self[0] == 0xe5
        self.unused = self[0] == 0x00
        self.valid = not (self.deleted or self.unused)
        if self.name.txt == "_UNREAD__UN":
            self.valid = False
        self.subdir = None
        self.committed = False
        i = self.name.txt[:8].rstrip()
        j = self.name.txt[8:].rstrip()
        if j:
            i += '.' + j
        if self.valid:
            self.namespace = NameSpace(
                name=i,
                parent=pns,
                separator='\\',
                priv=self,
            )
        else:
            self.namespace = None

    def commit(self):
        ''' ... '''
        if self.committed:
            print(self.tree.this, self, "recursive commit")
            return
        self.committed = True
        if not self.valid:
            return
        if self.name[0] == 0x00 or self.name.txt == "_UNREAD__UN":
            return
        if (self.attr.val & 0x18) == 0:
            size = self.length.val
            if size == 0:
                return
            j = []
            for _lo, i in self.tree.get_chain(self, self.cluster.val):
                if size == 0:
                    break
                want = min(size, self.tree.clustersize)
                bite = i[:want]
                if len(bite) > 0:
                    j.append(bite)
                elif 0:
                    print(self.this, "Missing Chunk", size, hex(_lo), i, self.name)
                size -= want
            if j:
                that = self.tree.this.create(records=j, define_records=False)
                self.namespace.ns_set_this(that)
        if self.attr.val & 0x10:
            self.subdir = Directory(self.tree, self.namespace)
            for low, cluster in self.tree.get_chain(self, self.cluster.val):
                for adr in range(low, low + len(cluster), 0x20):
                    j = DirEnt(self.tree, adr, self.namespace).insert()
                    self.subdir.add_dirent(j)
            self.subdir.commit()


class FAT12(ov.Octets):
    ''' ... '''

    def __init__(self, tree, lo, width):
        super().__init__(tree, lo, width=width)
        self.clusters = []
        for i in range(0, width, 3):
            j = ((self[i + 1] & 0xf) << 8) | self[i]
            self.clusters.append(j)
            j = (self[i + 1] >> 4) | (self[i + 2] << 4)
            self.clusters.append(j)
        self.owner = [None] * len(self.clusters)

    def chain(self, owner,  first):
        ''' yield cluster numbers in chain '''

        while first < len(self.owner) and self.owner[first] is None:
            yield first
            self.owner[first] = owner
            first = self.clusters[first]
            if first >= 0xff0:
                return

    def render(self):
        for i in range(0, len(self.clusters), 16):
            yield ",".join("%03x" % x for x in self.clusters[i:i+16]) + " // [0x%x]" % i

class FAT16(ov.Struct):
    ''' ... '''

    def __init__(self, tree, lo, width):
        super().__init__(
            tree,
            lo,
            vertical=True,
            fat_=ov.Array(width // 2, ov.Le16, vertical=True)
        )
        self.owner = [None] * (width//2)

    def chain(self, owner,  first):
        ''' yield cluster numbers in chain '''

        while first < len(self.owner) and self.owner[first] is None:
            yield first
            self.owner[first] = owner
            first = self.fat[first].val
            if first >= 0xfff0:
                return

class NameSpace(namespace.NameSpace):
    ''' ... '''

    KIND = "FatFS"

    TABLE = (
        ("r", "attr"),
        ("r", "locase"),
        ("r", "created"),
        ("r", "accessed"),
        ("r", "hicl"),
        ("r", "modified"),
        ("r", "cluster"),
        ("r", "length"),
        ("l", "name"),
        ("l", "artifact"),
    )

    def time(self, arg):
        ''' Decode time '''
        hour = arg >> 11
        minute = (arg >> 5) & 0x3f
        second = 2 * (arg & 0x1f)
        return "%02d:%02d:%02d" % (hour, minute, second)

    def date(self, arg):
        ''' Decode date '''
        if arg == 0:
            return "0"
        year = 1980 + (arg >> 9)
        month = (arg >> 5) & 0xf
        day = arg & 0x1f
        return "%04d-%02d-%02d" % (year, month, day)

    def date_time(self, arg1, arg2):
        ''' Decode date + time of both valid '''
        if arg1 == 0 and arg2 == 0:
            return "0"
        return self.date(arg1) + " " + self.time(arg2)

    def ns_render(self):
        dent = self.ns_priv
        attr = ""
        for i, j in (
            (0x01, "R"),
            (0x02, "H"),
            (0x04, "S"),
            (0x08, "L"),
            (0x10, "D"),
            (0x20, "A"),
            (0x40, "x40"),
            (0x80, "x80"),
        ):
            if dent.attr.val & i:
                attr += j
        return [
            attr,
            hex(dent.locase.val),
            self.date_time(dent.cdate.val, dent.ctime.val),
            self.date(dent.adate.val),
            hex(dent.hicl.val),
            self.date_time(dent.mdate.val, dent.mtime.val),
            hex(dent.cluster.val),
            dent.length.val,
        ] + super().ns_render()

class Directory():
    ''' A (sub)directory '''

    def __init__(self, tree, nsp):
        self.tree = tree
        self.namespace = nsp
        self.committed = False
        self.dirents = []

    def add_dirent(self, dirent):
        ''' one more for the collection '''
        self.dirents.append(dirent)

    def commit(self):
        ''' Recurse '''
        if self.committed:
            print(self.tree.this, "recursive dir commit", self)
            return
        self.committed = True
        for dirent in self.dirents:
            dirent.commit()

class Cluster(ov.Opaque):
    ''' Cluster belonging to a file '''

    def __init__(self, tree, lo, width, owner):
        super().__init__(tree, lo, width=width)
        self.owner = owner

    def render(self):
        yield "Cluster(%s)" % self.owner.name.txt

class FatFs(ov.OctetView):
    ''' Only FAT12 for now '''

    def __init__(self, this):

        if len(this) < 40 * 1 * 9 * 512:
            return
        super().__init__(this)

        fat0 = ov.Le24(self, 0x200)
        if not 0xfffff0 <= fat0.val < 0xffffff:
            return

        bpb = BiosParamBlock(self, 0)
        ssz = bpb.bsBytesPerSec.val
        if ssz == 0 or ssz & (ssz-1):
            return

        if bpb.geom:
            bpb.insert()
            geometry = bpb.geom
            #print(this, "FatFs BPB")
            #print("\n".join(bpb.render()))
        else:
            geometry = match_geometry(this, fat0.val)
            print("FatFs TBL", this, geometry, self)

        if geometry is None or geometry.cyl == 0:
            #this.add_note("NotFat")
            #this.add_note("BadFatGeom")
            return

        print(this, "FatFS", geometry)
        this.add_note("FatFS")

        self.clustersize = geometry.bps * geometry.spcl
        nsectors = geometry.cyl * geometry.hd * geometry.sect
        clsz = geometry.bps * geometry.spcl
        ncluster = nsectors * geometry.bps // (clsz + 12)
        fatsize = ncluster + ncluster // 2
        if geometry.nfsc:
            fatsect = geometry.nfsc
        else:
            fatsect = (fatsize + geometry.bps - 1) // geometry.bps
        dirstart = geometry.rsv * geometry.bps
        if geometry.tsect < 65536:
            fatcl = FAT12
        else:
            fatcl = FAT16

        self.fat1 = fatcl(self, dirstart, fatsect * geometry.bps).insert()
        if geometry.nfat == 1:
            self.fat2 = self.fat1
        elif geometry.nfat == 2:
            self.fat2 = fatcl(self, self.fat1.hi, fatsect * geometry.bps).insert()
        else:
            print(this, "NFAT", geometry.nfat)
            return

        self.namespace = NameSpace(
            name="",
            root=this,
            separator="",
        )

        root = Directory(self, self.namespace)
        adr = self.fat2.hi
        for _i in range(geometry.rdir):
            j = DirEnt(self, adr, self.namespace).insert()
            adr = j.hi
            root.add_dirent(j)
        self.cluster2 = adr
        #print("CSZ", self.clustersize, hex(self.cluster2))

        root.commit()

        this.add_interpretation(self, self.namespace.ns_html_plain)

        self.add_interpretation(more=True, title="FatFS")

    def get_chain(self, owner, cluster):
        ''' Get contents of a chain '''
        for clno in self.fat1.chain(owner, cluster):
            i = self.cluster2 + (clno-2) * self.clustersize
            Cluster(self, i, self.clustersize, owner).insert()
            yield i, self.this[i:i+self.clustersize]
