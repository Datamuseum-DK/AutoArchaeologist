#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Precursor to Veritas LVM/FS from Tolerant Systems Inc
   as implemented on Regnecentralen RC9000
'''

import struct

import .unix.unix_fs as ufs

# from fx.h
SUPERBLOCK = (
    ("fx_magic", "1L",),            #   0: magic number (0x00011955)
    ("fx_version", "1L",),          #   4: file system version
    ("fx_link", "1L",),             #   8: linked list of file systems
    ("fx_rlink", "1L",),            #   c:    used for incore super blocks
    ("fx_sblkno", "1L",),           #  10: addr of super-block in filesys
    ("fx_aublkno", "1L",),          #  14: offset of au-block in filesys
    ("fx_eblkno", "1L",),           #  18: offset of emap block(s) in filesys
    ("fx_iblkno", "1L",),           #  1c: offset of inode-blocks in filesys
    ("fx_dblkno", "1L",),           #  20: offset of first data after au
    ("fx_dupoffset", "1L",),        #  24: displacement of dup. control blks
    ("fx_uniqueid", "1Q",),         #  28: unique i.d. of this file system
    ("fx_time", "1L",),             #  30: last time written
    ("fx_size", "1L",),             #  34: number of blocks in fx
    ("fx_dsize", "1L",),            #  38: number of data blocks in fx
    ("fx_nau", "1L",),              #  3c: number of allocation units
    ("fx_bsize", "1L",),            #  40: size of basic blocks in fx
    ("fx_minfree", "1L",),          #  44: minimum percentage of free blocks
    ("fx_maxbpu", "1L",),           #  48: max number of blks per alloc unit
    ("fx_sbsize", "1L",),           #  4c: actual size of super block
    ("fx_nindir", "3L",),           #  50: values of NINDIR
    ("fx_inopb", "1L",),            #  5c: value of INOPB
    ("fx_sparecon", "5L",),         #  60: reserved for future constants
    ("fx_mount_time", "1L",),       #  74: time of last mount
    ("fx_dbpu", "1L",),             #  78: data blocks per allocation unit
    ("fx_ipu", "1L",),              #  7c: inodes per alloc unit
    ("fx_bpu", "1L",),              #  80: blocks per alloc unit
    ("fx_blocksfree", "1L",),       #  84:
    ("usum_us_ndir", "1L",),        #  88: number of allocated directories
    ("usum_us_nifree", "1L",),      #  8c: number of free inodes
    ("sb_090", "1L",),              #  90:
    ("sb_094", "1L",),              #  94:
    ("sb_098", "1L",),              #  98:
    ("sb_09c", "1L",),              #  9c:
    ("sb_0a0", "1L",),              #  a0:
    ("sb_0a4", "1L",),              #  a4:
    ("sb_0a8", "1L",),              #  a8:
    ("sb_0ac", "1L",),              #  ac:
    ("sb_0b0", "1L",),              #  b0:
    ("sb_0b4", "1L",),              #  b4:
    ("sb_0b8", "1L",),              #  b8:
    ("sb_0bc", "1L",),              #  bc:
    ("sb_0c0", "1L",),              #  c0:
    ("sb_0c4", "1L",),              #  c4:
    ("sb_0c8", "1L",),              #  c8:
    ("fx_fxmnt", "512B",),          #  cc: name mounted on
    ("fx_aurotor", "1L",),          #      last au searched
    # ... more, but mostly in-memory fields
)

# from inode.h
INODE = (
    ("di_mode", "1H",),             #   0: IFMT, permissions; see below.
    ("di_nlink", "1H",),            #   2: File link count.
    ("di_uid", "1H",),              #   4: File owner.
    ("di_gid", "1H",),              #   6: File group.
    ("di_size", "1L",),             #   8: File byte count.
    ("di_size_high", "1L",),        #  12: File byte count.
    ("di_atime", "1L",),            #  16: Last access time.
    ("di_atspare", "1L",),          #  20: Last access time.
    ("di_mtime", "1L",),            #  24: Last modified time.
    ("di_mtspare", "1L",),          #  28: Last modified time.
    ("di_ctime", "1L",),            #  32: Last inode change time.
    ("di_ctspare", "1L",),          #  36: Last inode change time.
    ("di_db", "8L",),               #  40: Direct disk blocks.
    ("di_ib", "3L",),               #  72: Indirect disk blocks.
    ("di_flags", "1L",),            #  84: Status flags (chflags).
    ("di_blocks", "1L",),           #  88: Blocks actually held.
    ("di_uniqe", "1Q",),            #  92: Unique i.d.
    ("di_itype", "1H",),            #  100: type.
    ("di_ptier", "1B",),            #  102: tier of primary extent
    ("di_stier", "1B",),            #  103: tier of secondary extent
    ("di_fnct", "1L",),             #  104: find_name count
    ("di_fwoct", "1L",),            #  108: find_without_name count
    ("di_fdsct", "1L",),            #  112: fd service count count
    ("di_spare", "2L",),            #  116: reserved, currently unused service count count
    ("di_magic", "1L",),            #  124: inode magic
)

class Directory(ufs.Directory):
    ''' Variable length dirent records (FFS style) '''

    def parse(self):
        ''' Parse FFS style directories '''
        for blk in self.inode:
            blk = blk.tobytes()
            while len(blk) > 0:
                words = struct.unpack(self.ufs.ENDIAN + "LHBB", blk[:8])
                name = blk[8:8+words[3]].decode(self.ufs.CHARSET)
                if not words[1]:
                    print("DIRENT zero lengt", words)
                    return
                blk = blk[words[1]:]
                yield words[0], name

class Inode(ufs.Inode):

    ''' Extent based inodes '''

    # The first entry in .di_db is primary extent size (.di_ptier)
    # The remaining entries (?) in .di_db are secondary extent size (.di_stier)
    # extent size is 1<<x sectors

    def __iter__(self):
        if self.di_type not in (0, self.ufs.S_IFDIR, self.ufs.S_IFREG):
            return
        yet = self.di_size
        extn = 0
        while yet > 0 and extn < len(self.di_db):
            if not extn:
                extsz = min(yet, 1024 << self.di_ptier)
            else:
                extsz = min(yet, 1024 << self.di_stier)
            offs = self.di_db[extn] << 10
            yield self.ufs.this[offs:offs+extsz]
            yet -= extsz
            extn += 1

class RC9000_FFS(ufs.UnixFileSystem):

    ''' A BSD-FFS derived filesystem '''

    FS_TYPE = "RC9000 FFS"
    INODE_SIZE = 0x80
    ENDIAN = ">"
    CHARSET = "iso8859-1"

    DIRECTORY = Directory

    sectorsize = 1024

    def speculate(self):
        ''' Not supported '''

    def get_superblock(self):
        ''' Get and fixup superblock so ufs. understands it '''
        self.sblock = self.this.record(
            SUPERBLOCK,
            offset = 0,
            endian = self.ENDIAN
        )
        self.sblock.add("fs_imax", self.sblock.fx_nau * self.sblock.fx_ipu)
        self.sblock.add("fs_nindir", 3)
        mpt = bytearray(self.sblock.fx_fxmnt)
        mpt = mpt.rstrip(b'\x00')
        self.sblock.add("fx_fxmnt", mpt)
        if False:
            for i, j in self.sblock:
                if isinstance(j, int):
                    print("  ", i, "0x%x" % j)
                else:
                    print("  ", i, j)

    def get_inode(self, inum):
        ''' Get and fix up inode so ufs. understands it '''
        offs = (inum // self.sblock.fx_ipu)  * self.sblock.fx_bpu * self.sectorsize
        offs += self.sblock.fx_iblkno * self.sectorsize
        offs += (inum % self.sblock.fx_ipu) << 7
        ino = self.this.record(
            INODE,
            offset = offs,
            endian = self.ENDIAN,
            use_type = Inode,
            ufs = self,
            name = "rc9k_ffs",
            di_inum = inum,
        )
        ino.di_mode |= ino.di_itype << 12
        ino.di_type = ino.di_mode & self.S_ISFMT
        return ino

    def get_blockx(self, bno):
        ''' Get a block '''
        offset =  bno * self.sectorsize
        return self.this[offset:offset+self.sectorsize]


class RC9000_FFS_Hunt(ufs.UnixFileSystem):

    ''' Hunt for RC9000 Filesystems on this artifact '''

    # We dont grok the pre-VxVM disk-slicing, so instead we brute-force
    # hunt for potential filesystems

    def __init__(self, this, sectorsize=1024):

        if this.top not in this.parents:
            return

        self.this = this
        self.sectorsize = sectorsize

        print("RC9K_FFS?", this)

        found = len(this)
        for offs in self.au_signatures():

            sblock = self.is_a_filesystem(offs)
            if not sblock:
                continue
            print(
                this,
                "+FS %06x" % offs,
                "%06x" % (sblock.fx_nau * sblock.fx_bpu),
                "%06x" % sblock.fx_size,
                sblock.fx_size,
            )
            found = min(found, offs)
            that = this.create(start=offs, stop = offs + sblock.fx_size * self.sectorsize)
            RC9000_FFS(that)
        if found < len(this):
            that = this.create(start=0x100000, stop = found)
            that.add_type("VxVM")

    def is_a_filesystem(self, offs):

        ''' Determine if there is a FS at this offset, and return its superblock '''

        # print("FS? %06x" % offs)
        # Read prospective superblock
        sblock = self.this.record(
            SUPERBLOCK,
            offset = offs,
            endian = ">"
        )

        # Check that inode 0…2 look right, and get inode 2
        rootino = self.is_first_inodesector(offs + sblock.fx_iblkno * self.sectorsize)
        if not rootino:
            #print("!RINO %06x" % offs)
            return None

        # Check that the first block of the root inode is a directory
        # with a first entry of { inum=2, name="." }
        ptr = offs + rootino.di_db[0] * self.sectorsize
        rdir = self.this[ptr:ptr + 12]
        if rdir.hex() != "00000002000c00012e000000":
            print("!RDIR %06x" % offs, rdir.hex())
            return None

        # Check that the rest of the CG's are there
        ncg = sblock.fx_nau
        cgdist = sblock.fx_bpu
        for cgno in range(ncg):
            if not self.is_au_signature(offs + cgno * cgdist * self.sectorsize):
                print(self.this, "!CG %06x" % offs, cgno)
                return None

        return sblock

    def is_first_inodesector(self, offs):

        ''' Check if this looks like the first inode sector '''

        ino = self.inode_at(offs + 0 * 128)
        if ino.di_mode:
            return None

        ino = self.inode_at(offs + 1 * 128)
        if ino.di_mode:
            return None

        ino = self.inode_at(offs + 2 * 128)
        if not ino.di_mode:
            return None

        if ino.di_size % self.sectorsize:
            return None

        return ino

    def inode_at(self, offs):

        ''' Return the inode at offset '''

        return self.this.record(
            INODE,
            offset = offs,
            endian = ">"
        )

    def is_au_signature(self, offs):

        ''' Check Allocation Unit signature '''

        if self.this[offs] != 0x00:
            return False
        if self.this[offs+1] != 0x01:
            return False
        if self.this[offs+2] != 0x19:
            return False
        if self.this[offs+3] != 0x55:
            return False
        return True

    def au_signatures(self):

        ''' Yield all the byte-offsets of sectors with a allocation unit signature '''

        for offs in range(0, len(self.this), self.sectorsize):
            if self.is_au_signature(offs):
                yield offs
