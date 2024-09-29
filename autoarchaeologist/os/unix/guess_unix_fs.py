#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Autodetect UNIX filesystems
   ---------------------------
'''

from . import unix_fs as ufs

from ...base import octetview as ov

class Daddr40(ov.Opaque):
    ''' The daddr field of on-disk inodes is weird '''

    def __init__(self, up, lo):
        super().__init__(up, lo, width=40)

    def render(self):
        yield '-'.join("%02x" % x for x in self.octets())

class Inode64(ufs.Inode):
    ''' The classic 64 byte UNIX inode '''

    SIZE = 64

    def __init__(self, up, lo, short, long, byte_order=None):
        if lo + 64 > len(up.this):
            raise ufs.NotCredible("Inode at " + hex(lo))
        super().__init__(
            up,
            lo,
            vdi_mode_=short,
            vdi_nlink_=short,
            vdi_uid_=short,
            vdi_gid_=short,
            vdi_size_=long,
            vdi_addr_=Daddr40,
            vdi_atime_=long,
            vdi_mtime_=long,
            vdi_ctime_=long,
        )
        self.ifmt = self.vdi_mode.val & ufs.Inode.S_ISFMT
        if self.ifmt == 0:
            return

        self.di_type = self.vdi_mode.val & ufs.Inode.S_ISFMT
        self.di_mode = self.vdi_mode.val
        self.di_nlink = self.vdi_nlink.val
        self.di_size = self.vdi_size.val
        self.ufs = up
        self.long = long

        if byte_order is None:
            byte_order = (0, 1, 2)

        i = list(self.bnos(byte_order))

        self.di_db = i[:-3]
        self.di_ib = i[-3:]

    def bnos(self, byte_order):
        ''' Interpret vdi_addr according to byte order '''
        adr = self.vdi_addr.octets()
        if len(byte_order) == 3:
            a,b,c = byte_order
            for i in range(0, len(adr)-3, 3):
                yield (adr[i+a] << 16) | (adr [i+b] << 8) | adr[i+c]
        elif len(byte_order) == 4:
            a,b,c,d = byte_order
            for i in range(0, len(adr)-4, 4):
                yield (adr[i+a] << 24) | (adr [i+b] << 16) | (adr[i+c] << 8) | adr[i+d]
        else:
            a,b,c,d,e,f = byte_order
            for i in range(0, len(adr)-6, 6):
                yield (adr[i+a] << 16) | (adr [i+b] << 8) | adr[i+c]
                yield (adr[i+d] << 16) | (adr [i+e] << 8) | adr[i+f]
            yield (adr[i+a] << 16) | (adr [i+b] << 8) | adr[i+c]

    def is_dir(self):
        if (self.vdi_mode.val & 0o170000) != 0o040000:
            return False
        if self.vdi_size.val >= len(self.this):
            return False
        if self.vdi_size.val & 0xf:
            return False
        # Directories cannot be sparse, check that non-zero block count
        # is credible for di_size.
        if sum(self.vdi_addr.octets()[:4]) == 0:
            return False
        bn3 = [self.bnos((0, 1, 2))]
        bn4 = [self.bnos((0, 1, 2, 3))]
        nbn3 = len(bn3) - bn3.count(0)
        nbn4 = len(bn4) - bn4.count(0)
        if not nbn3 and not nbn4:
            return False
        bpb3 = self.vdi_size.val / nbn3
        bpb4 = self.vdi_size.val / nbn4
        if bpb3 > (1<<16) and bpb4 > (1<<16):
            return False
        return True

    def has_blocks(self):
        return self.ifmt in (
            ufs.UnixFileSystem.S_IFBLK,
            ufs.UnixFileSystem.S_IFREG,
        )

    def credible(self):
        if self.ifmt == ufs.UnixFileSystem.S_IFDIR:
            return self.is_dir()

        return self.ifmt in (
            ufs.UnixFileSystem.S_IFCHR,
            ufs.UnixFileSystem.S_IFBLK,
            ufs.UnixFileSystem.S_IFDIR,
            ufs.UnixFileSystem.S_IFCHR,
            ufs.UnixFileSystem.S_IFPIP,
            ufs.UnixFileSystem.S_IFREG,
        )

class DirBlock(ov.Struct):
    def __init__(self, tree, lo, hi, short):

        class DirEnt(ov.Struct):
            def __init__(self, tree, lo):
                super().__init__(
                    tree,
                    lo,
                    inum_=short,
                    fnam_=ov.Text(14),
                )

        super().__init__(
            tree,
            lo,
            dents_=ov.Array((hi-lo) // 16, DirEnt, vertical=True),
            vertical=True,
        )

    def __iter__(self):
        for dent in self.dents:
            if dent.inum.val:
                yield dent.inum.val, dent.fnam.full_text()

class UnixFsSblock():
    # Interface with unix_fs until that is redone
    fs_imax = 1<<20

class UnusedBlock(ov.Opaque):
    ''' ... '''

class UnixFs(ufs.UnixFileSystem):
    ''' Parameterized UNIX filesystem '''

    VERBOSE = False

    def __init__(
        self,
        this,
        byte_order,
        block_size,
        block_offset,
        inode2_offset,
        short,
        long,
        params,
    ):
        self.byte_order = byte_order
        self.block_size = block_size
        self.block_offset = block_offset
        self.inode2_offset = inode2_offset
        self.short = short
        self.long = long
        self.params = params
        if self.VERBOSE:
            print(this, str(self), "?")
        super().__init__(this)
        if not self.good:
            return
        self.rootdir.namespace.KIND = str(self)
        if self.VERBOSE:
            print(this, "commit", self)
        else:
            print(this, self)
        super().commit()

        for lo, hi in self.gaps():
            lo += self.block_size - 1
            lo &= ~(self.block_size - 1)
            while lo + self.block_size <= hi:
                y = UnusedBlock(self, lo=lo, width=self.block_size).insert()
                lo = y.hi
        self.add_interpretation(more=True, title=str(self))

    def __str__(self):
        return "UnixFS(" + ", ".join(
            (
                str(self.byte_order),
                hex(self.block_size),
                hex(self.block_offset),
                hex(self.inode2_offset),
                self.short.__name__,
                self.long.__name__,
            ) ) + ")"

    def get_inode(self, inum):
        ''' Get inode number inum '''
        lo = self.inode2_offset + (inum - 2) * self.params.INODE_CLASS.SIZE
        if lo + self.params.INODE_CLASS.SIZE > len(self.this):
            raise ufs.NotCredible("Inode past this ")
        ino = Inode64(
            self,
            lo,
            self.short,
            self.long,
            self.byte_order,
        )
        ino.di_inum = inum

        # Sanity-check
        if not ino.ifmt:
            raise ufs.NotCredible(
                "Inode has no ifmt " + str(inum) + " " + str(ino)
            )

        if ino.ifmt in (ino.S_IFDIR, ino.S_IFREG):
            # Block numbers must be credible
            for blockno in ino.di_db + ino.di_ib:
                if blockno:
                    hi = self.block_offset + (blockno + 1) * self.block_size
                    if hi > len(self.this):
                        raise ufs.NotCredible(
                            "Inode has block_no past this " + str(inum) + " " + str(ino)
                        )

            hasblocks = sum(ino.di_db) + sum(ino.di_ib)
            if ino.di_size:
                if not hasblocks:
                    raise ufs.NotCredible(
                        "Inode has size but no blocks " + str(inum) + " " + str(ino)
                    )

                # If there are too many block numbers, the blocksize is too large.
                nblk = (ino.di_size + self.block_size - 1) // self.block_size
                i = list(ino.di_db)
                while i and i[-1] == 0:
                    i.pop(-1)
                if nblk < len(i) and max(ino.di_db[nblk:]) > 0:
                    raise ufs.NotCredible(
                        "Inode has too many direct blocks " + str(inum) + " " + str(ino)
                    )
            elif hasblocks:
                raise ufs.NotCredible(
                    "Inode has no size but has blocks " + str(inum) + " " + str(ino)
                )

        ino.insert()
        return ino

    def get_superblock(self):
        # Interface with unix_fs until that is redone
        self.sblock = UnixFsSblock()
        self.sblock.fs_nindir = self.block_size // 4

    def get_block(self, blockno):
        ''' Get a logical disk block '''

        lo = self.block_offset + blockno * self.block_size
        hi = lo + self.block_size
        if hi > len(self.this):
            raise ufs.NotCredible("Block_no past this " + hex(blockno))
        return ov.Opaque(self, lo=lo, hi=hi)

    def parse_directory(self, inode):
        ''' Parse classical unix directory: 16bit inode + 14 char name '''
        n = 0
        for b in inode:
            db = self.params.DIR_CLASS(self, b.lo, b.hi, self.short).insert()
            for inum, fnam in db:
                if n == 0 and fnam != ".":
                    raise ufs.NotCredible("First dirent not '.' " + str(inode))
                if n == 1 and fnam != "..":
                    raise ufs.NotCredible("First dirent not '.' " + str(inode))
                n += 1
                yield inum, fnam

class GuessUnixFsLittleEndian(ov.OctetView):
    '''
       Attempt to instantiate a filesystem given a potential root inode
    '''

    ''' Little endian, sensible longs '''
    SHORT = ov.Le16
    LONG = ov.Le32

    DOT = b'.'.ljust(14, b'\x00')
    DOTDOT = b'..'.ljust(14, b'\x00')

    def __init__(self, up, this, root_inode_offset):
        self.params = up.params
        super().__init__(this)
        self.root_inode = self.params.INODE_CLASS(self, root_inode_offset, self.SHORT, self.LONG)
        for byte_order in up.params.POSSIBLE_BYTE_ORDERS:
            bnos = list(self.root_inode.bnos(byte_order))
            if max(bnos) * self.params.SMALLEST_BLOCK_SIZE >= len(self.this):
                continue
            while bnos and bnos[-1] == 0:
                bnos.pop(-1)
            if 0 in bnos:
                # Directories cannot be sparse
                continue
            for bsize, offset in self.find_rootdir(bnos):
                UnixFs(
                    self.this,
                    byte_order,
                    bsize,
                    offset,
                    self.root_inode.lo,
                    self.SHORT,
                    self.LONG,
                    self.params,
                )

    def find_rootdir(self, bnos):
        ''' Knowing what we know, can we find the root directory ? '''

        bsize = self.params.SMALLEST_BLOCK_SIZE >> 1
        while bsize <= self.params.LARGEST_BLOCK_SIZE:
            bsize <<= 1
            adr0 = self.root_inode.lo & ~(bsize - 1)
            off0 = self.root_inode.lo & (bsize - 1)
            if off0 > max(self.params.ROOTINO_INDEX) * self.params.INODE_CLASS.SIZE:
                # Root inode is too far into this block (= wrong block size)
                continue
            for boot_off in range(0, self.params.MAX_BOOTBLOCKS):
                adrr = adr0 + bnos[0] * bsize - boot_off * bsize
                if not 0 <= adrr < len(self.this):
                    continue

                # This stuff belongs in params.DIR_CLASS
                y = self.SHORT(self, adrr)
                if y.val != 2:
                    continue
                y = self.SHORT(self, adrr + 16)
                if y.val != 2:
                    continue
                if self.this[adrr + 2:adrr + 16] != self.DOT:
                    continue
                if self.this[adrr + 18:adrr + 32] != self.DOTDOT:
                    continue
                yield bsize, adr0 - boot_off * bsize

class GuessUnixFsLittleEndianBogus(GuessUnixFsLittleEndian):
    ''' Little endian bogus longs '''
    LONG = ov.L1032

class GuessUnixFsBigEndian(GuessUnixFsLittleEndian):
    ''' Big endian sensible longs '''
    SHORT = ov.Be16
    LONG = ov.Be32

class GuessUnixFsBigEndianBogus(GuessUnixFsBigEndian):
    ''' Big endian bogus longs '''
    LONG = ov.L2301

class GuessUnixFsParams():
    ''' Parameters constraining the search for UNIX filesystems '''

    MAX_BOOTBLOCKS = 4			# Number of blocks counted before first inode block
    SMALLEST_BLOCK_SIZE = 1 << 9	# Smallest block size
    LARGEST_BLOCK_SIZE = 1 << 12	# Largest block size
    ROOTINO_INDEX = (0, 1, 2)		# Where in first inode block is the root-inode
    POSSIBLE_BYTE_ORDERS = (		# How the on-disk inode stores block numbers
            (0, 1, 2),			# Can be 3, 4 or 6 (= 2*3) long
            (0, 2, 1),
            (1, 2, 0),
            (2, 1, 0),
            #(1, 0, 2),
            #(2, 0, 1),
    )
    MIN_ROOT_DIR_LEN = 32
    INODE_CLASS = Inode64		# Inode class
    DIR_CLASS = DirBlock		# Directory class

class GuessUnixFs(ov.OctetView):
    '''
       Try to spot any UNIX filesystems
    '''

    def __init__(self, this, params=None):
        if params is None:
            params = GuessUnixFsParams()
            self.params = params
        if this.top in this.parents:
            limit = len(this)
        else:
            limit = self.params.MAX_BOOTBLOCKS * self.params.LARGEST_BLOCK_SIZE
        super().__init__(this)

        # Hunt for a root-inode in all probable locations and byte-sexes
        for boff in range(0, limit, self.params.SMALLEST_BLOCK_SIZE):
            for index in self.params.ROOTINO_INDEX:
                for cls in (
                    GuessUnixFsLittleEndian,
                    GuessUnixFsLittleEndianBogus,
                    GuessUnixFsBigEndian,
                    GuessUnixFsBigEndianBogus,
                ):
                    ioff = index * self.params.INODE_CLASS.SIZE
                    try:
                        root_inode = self.params.INODE_CLASS(self, ioff + boff, cls.SHORT, cls.LONG)
                    except ufs.NotCredible:
                        continue
                    if root_inode.ifmt != root_inode.S_IFDIR:
                        continue
                    if root_inode.vdi_nlink.val < 2:
                        continue
                    if root_inode.vdi_size.val < self.params.MIN_ROOT_DIR_LEN:
                        continue
                    if not root_inode.is_dir():
                        continue

                    cls(self, self.this, root_inode.lo)
