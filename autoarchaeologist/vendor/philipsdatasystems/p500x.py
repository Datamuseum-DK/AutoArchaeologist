#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Philips P5002, P5003 etc.
   =========================

   These were text-processing microcomputers, but they evidently also had
   some kind of spread-sheet like facility.

   The P5003's lasting claim to fame, will probably be its cameo in Q's
   lab in the James Bond Movie "For Your Eyes Only".

   Usage
   -----

   .. code-block:: none

      from autoarchaeologist.vendor.philipsdatasystems import p500x
      …
      self.add_examiner(*p500x.ALL)

   Options
   -------
   
   .. code-block:: none

      p500x.P500x.OPT_CHECK_FREE_LIST = False

   Enable diagnostic check of free-list consistency.

   .. code-block:: none

      p500x.P500x.OPT_HUNT_ORPHANS = True

   Hunt for orphan/deleted files.

   Notes
   -----

   Reverse-engineered from a dozen of 8" floppy images.

   Note that formatting the floppy only writes four valid sectors
   per track, so to work with :ref:`FloppyTools` cache files, all
   addressing have to be by track&sector numbers.

   Test input
   ----------

   * QR:50006570 … QR:50006582

   Documentation
   -------------

   Very little documentation seems to have survived, archive.org has a few
   documents, none of them with any technical details.

   The floppy disk format is bespoke and supported in :ref:`FloppyTools`

'''

from ...base import octetview as ov
from ...base import namespace as ns

UNREAD = b'_UNREAD_' * (128//8)

#######################################################################

class AddressMark(ov.Struct):
    '''
       The 3 byte address-mark is integral to the sector, and contains
       at least one flag bit necessary for decoding the file-system.
    '''

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            sec_=ov.Octet,
            cyl_=ov.Octet,
            head_=ov.Octet,
        )
        self.val = sum(self)

    def render(self):
        yield "(%d, %d, %d, %d)".ljust(15) % (
            self.cyl.val,
            self.head.val,
            self.sec.val & 0x1f,
            self.sec.val >> 5,
        )

#######################################################################

class Dir(ov.Struct):
    '''
       There are two kinds of directory entries mixed in the directory table.
       Directories have 12 byte names, Files have 10 byte names and two byte
       sequence/ordering numbers.
       But we cannot tell which is which until we have traversed
       the `Graph` and since the rendering of Dir is purely diagnostic,
       we use the same layout for both.
    '''

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            name_=ov.Text(10),
            high_=ov.Octet,
            low_=ov.Octet,
        )
        self.val = sum(self)

class Graph(ov.Struct):
    '''
	This table holds four-octet tuples which form a cyclic graph
	of directory and filenames.  Probably for reasons of
	robustness, each sector is duplicated, which makes the code
        below a bit weird.
    '''

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            g_=ov.Array(256, 4, vertical=True),
            vertical=True,
        )
        self.nodes = []
        for n, i in enumerate(self.g):
            if n & 0x20:
                continue
            self.nodes.append(bytes(i))

    def iter_nodes(self):
        ''' iterate over the valid nodes '''
        for n, i in enumerate(self.nodes):
            x,y,z,w = i
            if w == 240:
                continue
            if 76 < w < 0xff:
                # Conveniently, this also handles _UNREAD_
                continue
            yield n,x,y,z,w

    def render(self):
        yield "Graph {"
        for n,x,y,z,w in self.iter_nodes():
            s = "0x%02x: next=0x%02x prev=0x%02x" % (n, x, y)
            if w == 0xff:
                t = " branch=0x%02x" % z
            else:
                t = " at=(%d, %d)" % (z, w)
            yield "  " + s + t
        yield "}"

class Duplicate(ov.Opaque):
    ''' ... '''

class SectorUseBitMap(ov.Opaque):
    ''' ... '''

class P500xMeta(ov.OctetView):
    '''
       The filesystem metadata object
       ==============================

       This "file" is always located at (20, 0) and has a list
       of sectors like any other file, but lacking the terminating
       flag.

       In difference from other files, the list of sectors is
       inside the "file", and furthermore the first sixteen sectors,
       in file order, are duplicated, yielding this layout:

           (20, 0) 0x000 sector list
           (20, 3) 0x080 sector list (again)
           (20, 6) 0x100 first sector of sector-inuse-bitmap
           (20, 9) 0x180 first sector of sector-inuse-bitmap (again)
           […]
           (20,24) 0x400 first sector of the graph
           (20,27) 0x480 first sector of the graph (again)
           (20,30) 0x500 second sector of the graph
           (20, 1) 0x580 second sector of the graph (again)
           […]
           (20,16) 0x800 first sector of directory
           (20,19) 0x880 second sector of directory
           […]
           
    '''
    def __init__(self, this):

        super().__init__(this, line_length=128)

        ov.Array(64, SectorReference, vertical=True, elide=(0,))(self, 0x0).insert()
        Duplicate(self, 0x80, 0x80).insert()

        for p in range(0x100, 0x400, 0x100):
            SectorUseBitMap(self, p, 0x80).insert()
            Duplicate(self, p + 0x80, 0x80).insert()

        n = (len(this) - 0x800) // 12
        self.dir = ov.Array(n, Dir, vertical=True, elide=(0,))(self, 0x800).insert()
        self.graph = Graph(self, lo=0x400).insert()

        self.add_interpretation(title="P500xMeta", more=False, elide=0)

    def iter_files(self):
        ''' Iterate the files in the graph+dir combo '''

        # first find the directories
        dirs = {}
        for n,_x,_y,_z,w in self.graph.iter_nodes():
            if w == 0xff:
                dirs[n] = self.dir[n]

        for n,_x,y,z,w in self.graph.iter_nodes():
            if w != 0xff:
                # Trace the back pointer to a directory
                while y not in dirs:
                    yy = self.graph.nodes[y][1]
                    assert y != yy
                    y = yy

                # We have found no documentation of how filenames were presented
                # so we have invented our own.
                path = self.this.type_case.decode_long(self.dir[y]).strip()
                path += "/%d.%d" % (self.dir[n].high.val, self.dir[n].low.val)
                subn = self.this.type_case.decode_long(self.dir[n].name).strip()
                if subn:
                    path += "_" + subn
                yield path, (z, w)


#######################################################################

class SectorReference(ov.Struct):
    '''
       The 2 byte pointers to sectors also contains flagbits in the
       upper part of the sector number.
    '''

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            sec_=ov.Octet,
            cyl_=ov.Octet,
        )
        self.c = self.cyl.val
        self.s = self.sec.val & 0x1f
        self.m = self.sec.val >> 5
        self.val = sum(self)

    def render(self):
        yield "(%2d, %2d, %d)".ljust(15) % (self.c, self.s, self.m)

class File(ov.Struct):
    '''
       A File is defined by a sector containing an array of `SectorReferences`
       and it is probably possible to link such sectors together for larger
       files, but we have no examples of that.

       Except for the filesystem metadata "file" at (20,0), the list of sectors
       seem to be terminated by the last `SectorReference` having a .m of 3.

    '''

    def __init__(self, tree, lo):
        for m, n in enumerate(range(3, 127, 2)):
            if tree.this[lo + n] > 0x1f:
                break
        super().__init__(
            tree,
            lo,
            am_=AddressMark,
            list_=ov.Array(m + 1, SectorReference, vertical=True, elide=(0,)),
            vertical=True,
            more=True,
        )

        if self.hi < lo + 127:
            self.add_field("pad_", lo + 127 - self.hi)

        # The fact that the directory object has "here" = (21, 0, 0) strongly suggests
        # that these two fields may be intended for a doubly linked list for files which
        # grow bigger than one sector's worth of `SectorReference`s.

        self.add_field("here", SectorReference)
        self.add_field("tail", SectorReference)

        self.done()

class Free(ov.Opaque):
    ''' ... '''

class Used(ov.Opaque):
    ''' ... '''

class P500xNs(ns.NameSpace):
    ''' Namespace for names in the directory '''
    KIND = "P500X"

class P500xNsOrphans(ns.NameSpace):
    ''' Namespace for orphans '''
    KIND = "P500X Orphans"

class P500x(ov.OctetView):

    ''' ... '''

    OPT_CHECK_FREE_LIST = False
    OPT_HUNT_ORPHANS = True

    # AddressMark + SectorReference[8]
    MAGIC = bytes.fromhex('a01400 0014 0314 0614 0914 0c14 0f14 1214 1514')

    def __init__(self, this):
        if this.top not in this.parents:
            return

        i = this.get_frag((20, 0, 0))
        if not i or i[:len(self.MAGIC)] != self.MAGIC:
            return

        super().__init__(this, line_length=131)

        # The used bit-map.
        self.ffrags = [
            this.get_frag((20, 0, 6)),
            this.get_frag((20, 0, 12)),
            this.get_frag((20, 0, 18)),
        ]

        self.used = set()
        meta = P500xMeta(self.get_file(20, 0))

        pns = P500xNs(name="", root=this, separator="/")
        ns.NameSpace(name="", parent=pns, this=meta.this)

        for path, where in meta.iter_files():
            self.used.add(where)
            that = self.get_file(*where)
            that.add_name(path)
            ns.NameSpace(
                name=path,
                parent=pns,
                this=that
            )

        this.add_interpretation(self, pns.ns_html_plain)

        if self.OPT_CHECK_FREE_LIST:
            # Audit sector-in-use map
            for frag in this.iter_rec():
                l = list(self.find(frag.lo, frag.hi))
                u = self.is_used(frag.key[0], frag.key[2])
                if len(l) == 0 and not u:
                    continue
                if len(l) > 0 and u:
                    continue
                print(this, frag.key, len(l), u, ",".join(str(type(x)) for x in l))

        if self.OPT_HUNT_ORPHANS:
            self.hunt_orphans()

        self.add_interpretation(title="HexDump", more=True)

    def hunt_orphans(self):
        '''
           Hunt orphans by finding sectors we have not used
           yet, with a mark bit.
        '''

        ons = P500xNsOrphans(name="", root=self.this, separator="")

        for rec in self.this.iter_rec():
            if len(set(rec.frag[3:])) == 1:
                ov.Opaque(self, lo=rec.lo, hi=rec.hi).insert()
            m = rec.frag[0] >> 5
            if m != 1:
                continue
            s = rec.frag[0] & 0x1f
            t = rec.frag[1]
            if t != rec.key[0] or s != rec.key[2]:
                continue
            if (t, s) in self.used:
                continue
            self.used.add((t,s))
            that = self.get_file(t, s)
            ns.NameSpace(
                name="~Orphan_%d_%d" % (t, s),
                parent=ons,
                this=that
            )

        self.this.add_interpretation(self, ons.ns_html_plain)

    def get_file(self, trk, sec):
        ''' Piece together a file '''
        frag = self.this.get_frag((trk, 0, sec))
        if not frag:
            return []
        fil = File(self, frag.lo).insert()
        if fil.here.c == 21 and trk == 20 and sec == 0:
            pass
        elif fil.here.s != sec or fil.here.c != trk:
            print(self.this, "File has notable HERE", hex(self.lo), fil.here, (trk, sec), frag)
        if fil.tail.val:
            print(self.this, "File has notable TAIL", hex(self.lo), fil.tail, (trk, sec), frag)
        r = []
        for i in fil.list:
            if i.val == 0:
                break
            m = i.m
            s = i.s
            c = i.c
            if s > 31 or c > 76 or m not in (0, 3):
                print("END", trk, sec, c, s, m)
                break
            f = self.this.get_frag((c, 0, s))
            if f is None:
                print(self.this, "Missing", c, s)
                r.append(UNREAD)
            else:
                Used(self, lo=f.lo, hi=f.hi).insert()
                r.append(f.frag[3:])
            if m == 3:
                break
        assert r
        that = self.this.create(records=r, define_records=False)
        return that

    def is_used(self, trk, sec):
        ''' Is a particular sector used '''
        idx = trk * 32 + sec
        frag = self.ffrags[idx >> 10].frag
        idx2 = idx & 0x3ff
        bits = frag[3 + (idx2 >> 3)]
        return bits & (0x80 >> (idx2 & 7))

ALL = [
    P500x,
]
