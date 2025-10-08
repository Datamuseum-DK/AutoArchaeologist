#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   CP/M filesystems - Abstract Base Class
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   With big hat-tip to CPMTOOLS

'''

from ...base import octetview as ov
from ...base import namespace

from . import common

class Nonsense(Exception):
    ''' ... '''

class NotADir(Nonsense):
    ''' ... '''

class DirEnt(ov.Octets):
    ''' A CP/M directory entry of any kind '''
    def __init__(self, tree, lo):
        if tree.this[lo] not in common.VALID_DIRENT_STATUS:
            raise NotADir()
        super().__init__(tree, lo, width=0x20)
        self.status = self[0]
        self.flags = []
        name = []
        for i in range(1, 12):
            c = self[i]
            self.flags.append(c >> 7)
            name.append(self.this.type_case.slugs[c & 0x7f].long)
        ext = "".join(name[8:]).rstrip()
        name = "".join(name[:8]).rstrip()
        self.name = name
        if ext:
            self.name += "." + ext
        self.file_id = "0x%x:" % self[0] + self.name
        self.xl = self[12]
        self.bc = self[13]
        self.xh = self[14]
        self.rc = self[15]
        self.al = [self[x] for x in range(16, 32)]
        self.extent = (self.xl & 0x1f) | ((self.xh & 0x3f) << 5)
        self.segments = self.rc + ((self.extent & self.tree.EXTENT_MASK) << 7)
        self.extent >>= self.tree.EXTENT_MASK

    def __lt__(self, other):
        if self.status != other.status:
            return self.status < other.status
        if self.name != other.name:
            return self.name < other.name
        return self.extent < other.extent

    def blocks(self, width):
        ''' Yield the block numbers, using the given width '''
        if width == 8:
            yield from self.al
            return
        for i in range(0, len(self.al), 2):
            yield self.al[i] | (self.al[i+1] << 8)

    def render(self):
        if self.status == 0xe5:
            yield "Dirent {Status=0xe5}"
            return
        yield str(
           [
               self.status,
               self.name,
               self.extent,
               self.segments,
               "xl=%02x" % self.xl,
               "bc=%02x" % self.bc,
               "xh=%02x" % self.xh,
               "rc=%02x" % self.rc,
               "-".join(str(x) for x in self.flags),
               self.al,
           ]
        )

class DataBlock(ov.Opaque):
    ''' Data Block'''
    def __init__(self, tree, lo, width, dirent):
        super().__init__(
            tree,
            lo,
            width=width,
            rendered="DataBlock {»%s«}" % dirent.name
        )

class CpmNameSpace(namespace.NameSpace):
    ''' ... '''

    def ns_render(self):
        status, bc, frags = self.ns_priv
        l = [status, bc, frags]
        return l + super().ns_render()

    TABLE = [
        ["r", "user"],
        ["r", "bc"],
        ["r", "length"],
        ["l", "name"],
        ["l", "artifact"],
    ]

class CpmFile():
    ''' ... '''

    def __init__(self, tree, dirent):
        self.tree = tree
        self.dirents = [dirent]
        self.file_id = dirent.file_id
        self.frags = []
        self.sames = []
        self.eofs = []
        self.unreads = 0

    def add_dirent(self, dirent):
        ''' ... '''
        self.dirents.append(dirent)

    def make_frags(self):
        ''' Produce the sector fragments of this file '''
        self.frags = []
        self.sames = []
        self.dirents.sort()
        for de in self.dirents:
            ns = 0
            for bno in de.blocks(self.tree.BLOCK_NO_WIDTH):
                eofs = 0
                for sec in self.tree.getblock(bno):
                    ds = min(self.tree.SECTOR_SIZE, (de.segments - ns) << 7)

                    if sec is None:
                        self.unreads += 1
                        self.tree.debits += 1
                        self.sames.append(False)
                        if ds:
                            self.frags.append(b'_UNREAD_' * (ds // 8))
                    else:
                        if ds:
                            self.sames.append(
                                (min(sec.frag[:ds]), max(sec.frag[:ds]))
                            )
                            DataBlock(self.tree, sec.lo, ds, de).insert()
                            self.frags.append(sec.frag[:ds])
                            for i in sec.frag[:ds]:
                                if i == 0x1a:
                                    eofs += 1

                    ns += ds >> 7
                    if ns == de.segments:
                        break
                self.eofs.append(eofs)
                if ns == de.segments:
                    break
        # 0xe5 filled sectors at EOF are OK  (Only A BLock -1 sector ?)
        while self.sames and self.sames[-1] == (0xe5, 0xe5):
            self.sames.pop(-1)

    def investigate(self):
        '''
           Investigate if this file looks sensible
           =======================================

           If the directory does not reveal the interleave
           we come here to see if the files can do so.
        '''

        if not self.frags:
            self.make_frags()

        # 0xe5 sectors inside the file are suspect
        self.tree.debits += self.sames.count((0xe5, 0xe5))

        # Catch when the entire file was 0xe5
        if len(self.sames) == 0:
            self.tree.debits += 1

        # Files consisting of all zeros are suspect too
        if self.sames.count((0x0, 0x0)) == len(self.sames):
            self.tree.debits += 1

        # Does EOF only appears in the last block,
        if len(self.eofs) > 1 and self.eofs[-1] > 0 and max(self.eofs[:-1]) == 0:
            self.tree.credits += 1

    def commit(self):
        ''' ... '''

        if not self.frags:
            self.make_frags()

        if self.frags:
            y = self.tree.this.create(records=self.frags)
            if self.unreads:
                y.add_note("Unread_Sectors")
            CpmNameSpace(
                name = self.dirents[0].name,
                parent = self.tree.name_space,
                this = y,
                priv = (self.dirents[0].status, self.dirents[-1].bc, sum(len(x) for x in self.frags))
            )

class CpmFileSystem(ov.OctetView):
    '''
       The fundamental CP/M family filesystem class
       ============================================

       This level operates on filesystem logical blocks,
       and is invariant to interleaving and all that.
    '''

    SECTOR_SIZE = 0
    BLOCK_SIZE = 0
    N_DIRENT = 0
    BLOCK_NO_WIDTH = 0
    NAME = None
    SECTORS = []
    TRACKS = []
    EXTENT_MASK = 0

    def getblock(self, bno):
        ''' Yield the offset of the sectors in this block '''
        off = bno * self.BLOCK_SIZE
        for _nsec in range(self.BLOCK_SIZE // self.SECTOR_SIZE):
            tracksize = len(self.SECTORS) * self.SECTOR_SIZE
            track = off // tracksize
            if track >= len(self.TRACKS):
                self.debits += 1
                yield None
                off += self.SECTOR_SIZE
                continue
            sector = (off % tracksize) // self.SECTOR_SIZE
            chs = (*self.TRACKS[track], self.SECTORS[sector])
            try:
                frag = self.this.get_rec(chs)
                yield frag
            except KeyError:
                yield None
            off += self.SECTOR_SIZE

    def __init__(self, this, name=None, commit=True):

        self.this = this
        self.credits = 0
        self.debits = 0

        if name is not None:
            self.name = name
        if self.NAME is not None:
            self.name = self.NAME
        else:
            self.name = self.__class__.__name__

        self.build_signature()
        # print(this, self.signature)

        # The directory starts with block#0 but may not be an
        # integral number of blocks long.
        self.dir_blocks = (self.N_DIRENT * 0x20) // self.BLOCK_SIZE
        if self.N_DIRENT > (self.dir_blocks * self.BLOCK_SIZE // 0x20):
            self.dir_blocks += 1

        # Quick early check
        ngood = 0
        try:
            # Check if the sector size matches
            for blk in self.getblock(self.dir_blocks+1):
                if not blk or len(blk) != self.SECTOR_SIZE:
                    return

            # Check that directory lookes valid
            for off in self.iter_dir():
                i = this[off]
                if i not in common.VALID_DIRENT_STATUS:
                    return
                if i != 0xe5:
                    ngood += 1
        except KeyError:
            # When accessing nonexistent sectors
            return


        if not ngood:
            return

        super().__init__(this)

        bnos = set()
        self.directory = []
        for off in self.iter_dir():
            de = DirEnt(self, off).insert()
            if de.status == 0xe5:
                continue
            self.directory.append(de)
            if de.status < 0x10:
                self.credits += 1
                for bno in de.blocks(self.BLOCK_NO_WIDTH):
                    if bno == 0:
                        continue
                    if bno in bnos:
                        self.debits += 1
                    else:
                        bnos.add(bno)
        if not bnos:
            print(self.this, self.name, "no block numbers used in directory")
            return

        self.files = {}
        for de in self.directory:
            if de.status > 0x0f:
                continue
            if not de.name.strip():
                continue
            if de.file_id not in self.files:
                self.files[de.file_id] = CpmFile(self, de)
            else:
                self.files[de.file_id].add_dirent(de)

        if commit:
            self.commit()
        else:
            for file in self.files.values():
                try:
                    file.investigate()
                except KeyError:
                    self.debits += 1
                except IndexError:
                    self.debits += 1

    def __lt__(self, other):
        if self.credits != other.credits:
            return self.credits < other.credits
        return self.debits > other.debits

    def commit(self):
        ''' ... '''

        self.name_space = CpmNameSpace(
            name = '',
            root = self.this,
            separator = '',
        )

        for file in self.files.values():
            try:
                file.commit()
            except KeyError as err:
                print(self.this, self.name, "Probably missing sector", file, err)
            except IndexError as err:
                print(self.this, self.name, "Probably missing sector", file, err)

        if self.name_space.ns_children:
            self.this.add_interpretation(self, self.interpretation_html)
        self.add_interpretation(title="OctetView - " + self.name, more=True)
        self.this.add_type(self.name)
        self.this.add_note("CP/M-fs", self.signature)

    def build_signature(self):
        ''' Build a compact signature describing the filesystem layout '''
        prev = self.SECTORS[0]
        ils = [prev]
        for n in self.SECTORS[1:]:
            if n < prev:
                ils.append(n)
            prev = n
        self.signature = '_'.join(
            [
            str(self.SECTOR_SIZE),
            str(self.BLOCK_SIZE),
            "0x%x" % self.EXTENT_MASK,
            str(self.N_DIRENT),
            "*%d+" % (self.SECTORS[1] - self.SECTORS[0]) + "+".join(str(x) for x in ils),
            "%d:%d" % self.TRACKS[0],
            "%d:%d" % self.TRACKS[-1],
            ]
        )

    def iter_dir(self):
        ''' Iterate directory entry offsets in .this '''
        n = 0
        for bno in range(self.dir_blocks):
            for sect in self.getblock(bno):
                if sect is None:
                    self.debits += 1
                    continue
                for off in range(0, self.SECTOR_SIZE, 0x20):
                    yield sect.lo + off
                    n += 1
                    if n == self.N_DIRENT:
                        return

    def interpretation_html(self, file, this):
        ''' Namespace + filesystem metrics '''
        file.write("<H3>" + self.name + "</H3>\n")
        file.write("<pre>\n")
        file.write("Media:             ")
        file.write(str(self.this._key_min))
        file.write(" … " + str(self.this._key_max))
        file.write(" " + str(self.this._reclens))
        file.write("\n")
        file.write("Signature:         " + self.signature + "\n")
        file.write("Confidence score:  +" + str(self.credits) + "/-" + str(self.debits) + "\n")
        file.write("Sector size:       " + str(self.SECTOR_SIZE) + "\n")
        file.write("Block size:        " + str(self.BLOCK_SIZE) + "\n")
        file.write("Directory entries: " + str(self.N_DIRENT) + "\n")
        file.write("Block number size: " + str(self.BLOCK_NO_WIDTH) + "\n")
        file.write("Extent-mask:       0x%02x" % self.EXTENT_MASK + "\n")
        file.write("Sector-interleave: " + ", ".join(str(x) for x in self.SECTORS) + "\n")
        file.write("Tracks:            ")
        file.write(", ".join(str(x) for x in self.TRACKS[:6]))
        file.write(" […] ")
        file.write(", ".join(str(x) for x in self.TRACKS[-6:]))
        file.write("\n")
        file.write("</pre>\n")
        self.name_space.ns_html_plain_noheader(file, this)
