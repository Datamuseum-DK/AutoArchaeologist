'''
   Autodetect UNIX filesystems
   ---------------------------

'''

import math

import struct

from . import unix_fs as ufs

from ..base import octetview as ov

ROOTFSMAGIC_BE = bytes.fromhex('''
    00 02 2e 00 00 00 00 00 00 00 00 00 00 00 00 00
    00 02 2e 2e 00 00 00 00 00 00 00 00 00 00 00 00
''')

ROOTFSMAGIC_LE = bytes.fromhex('''
    02 00 2e 00 00 00 00 00 00 00 00 00 00 00 00 00
    02 00 2e 2e 00 00 00 00 00 00 00 00 00 00 00 00
''')

class SuperBlockStable(ov.Struct):
    '''
        The first two fields of superblocks are almost never mucked up.
    '''
    def __init__(self, up, lo, short, long):
        super().__init__(
            up,
            lo,
            s_isize_=short,
            s_fsize_=long,
        )

class Daddr40(ov.Opaque):

    def __init__(self, up, lo):
        super().__init__(up, lo, width=40)

class Inode64(ov.Struct):
    def __init__(self, up, lo, short, long):
        super().__init__(
            up,
            lo,
            di_mode_=short,
            di_nlink_=short,
            di_uid_=short,
            di_gid_=short,
            di_size_=long,
            di_addr_=Daddr40,
            di_atime_=long,
            di_mtime_=long,
            di_ctime_=long,
        )
        self.ifmt = self.di_mode.val & ufs.UnixFileSystem.S_ISFMT

    def bnos(self, *args):
        adr = self.di_addr.octets()
        if len(args) == 3:
            a,b,c = args
            for i in range(0, len(adr)-3, 3):
                yield (adr[i+a] << 16) | (adr [i+b] << 8) | adr[i+c]
        elif len(args) == 4:
            a,b,c,d = args
            for i in range(0, len(adr)-4, 4):
                yield (adr[i+a] << 24) | (adr [i+b] << 16) | (adr[i+c] << 8) | adr[i+d]
        else:
            a,b,c,d,e,f = args
            for i in range(0, len(adr)-6, 6):
                yield (adr[i+a] << 16) | (adr [i+b] << 8) | adr[i+c]
                yield (adr[i+d] << 16) | (adr [i+e] << 8) | adr[i+f]
            yield (adr[i+a] << 16) | (adr [i+b] << 8) | adr[i+c]

    def possible_bnos(self):
        for bo in (
            (2, 0, 1),
            (0, 1, 2),
            (0, 2, 1),
        ):
            yield bo, list(self.bnos(*bo))

    def is_dir(self):
        if (self.di_mode.val & 0o170000) != 0o040000:
            return False
        if self.di_size.val >= len(self.this):
            return False
        if self.di_size.val & 0xf:
            return False
        # Directories cannot be sparse, check that non-zero block count
        # is credible for di_size.
        if sum(self.di_addr.octets()[:4]) == 0:
            return False
        bn3 = [self.bnos(0, 1, 2)]
        bn4 = [self.bnos(0, 1, 2, 3)]
        nbn3 = len(bn3) - bn3.count(0)
        nbn4 = len(bn4) - bn4.count(0)
        if not nbn3 and not nbn4:
            return False
        bpb3 = self.di_size.val / nbn3
        bpb4 = self.di_size.val / nbn4
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

class GuessedUnixFx(ufs.UnixFileSystem):

    def __init__(
        self,
        this,
        byte_order,
        block_size,
        block0,
    ):
        self.byte_order = byte_order
        self.block_size = block_size
        self.block0 = block0
        super().__init__(this)

class GuessUnixFs(ov.OctetView):

    SMALLEST_BLOCK_SIZE = (1 << 9)
    LARGEST_BLOCK_SIZE = (1 << 12)
    INODE_SIZE = 64
    INODE_CLASS = Inode64
    ROOTINO_OFFSET = 64

    def __init__(self, this):
        if this.top not in this.parents:
            return
        super().__init__(this)
        print(this, self.__class__.__name__)
        for off in range(0, len(this), self.SMALLEST_BLOCK_SIZE):
            if this[off:off+32] == ROOTFSMAGIC_BE:
                print(
                    self.this,
                    "Candidate rootdir at",
                    hex(off),
                    "Big-endian",
                )
                self.locate_root_ino(
                    off,
                    ov.Be16,
                    (ov.Be32, ov.L2301),
                )
            elif this[off:off+32] == ROOTFSMAGIC_LE:
                print(
                    self.this,
                    "Candidate rootdir at",
                    hex(off),
                    "Little-endian",
                )
                self.locate_root_ino(
                    off,
                    ov.Le16,
                    (ov.Le32, ov.L1032),
                )

    def locate_root_ino(self, rootdir_off, short, longs):

        # Count directory entries
        # XXX: Can this exceed rootino.di_size ?
        inums = set()
        for i in range(0x0, self.SMALLEST_BLOCK_SIZE, 0x10):
            adr = rootdir_off + i
            if self.this[adr + 2] == 0:
                break
            y = short(self, adr)
            if y.val == 0:
                break
            inums.add(y.val)
        inums = list(sorted(inums))

        print("  Inodes in rootdir", inums)
        if len(inums) == 1:
            print("    Not much we can do with an empty rootdir")
            return

        for long in longs:
            for rootino, bo, bsize, sblock, bnos in self.possible_root_inodes(
                rootdir_off,
                inums,
                short,
                long
            ):
                print("   ", long.__name__, hex(rootino.lo - self.ROOTINO_OFFSET), rootino)
                print("     ", bo, bsize, bnos)
                print("        ", sblock.s_isize, hex(bnos[0]), sblock.s_fsize)
        return

    def possible_root_inodes(self, rootdir_off, inums, short, long):
        '''
           A root node must be a directory, big enough to hold the
           inums we found in it, and those inums must be valid inodes
           too.
        '''
        rootino_off = rootdir_off + self.ROOTINO_OFFSET
        while rootino_off > 2 * self.SMALLEST_BLOCK_SIZE:
            rootino_off -= self.SMALLEST_BLOCK_SIZE
            rootino = Inode64(self, rootino_off, short, long)
            if not rootino.is_dir():
                continue
            if rootino.di_size.val < 0x10 * (len(inums) + 1):  # +1 for ..
                continue
            if not self.good_rootdir_inodes(rootino_off, inums, short, long):
                continue
            yield from self.possible_daddrs(rootino, rootdir_off, rootino_off, short, long)

    def possible_daddrs(self, rootino, rootdir_off, rootino_off, short, long):
            '''
               There are multiple weird way to encode block numbers into
               the 40 byte di_addr field.  The correct one must give a
               first blocknumber which is close to a multiple of a
               sensible blocksize.
               "close to" is fuzzy.  Block #0 can be anywhere from the
               first of N "boot-sectors" to the superblock.
            '''
            block0 = rootino_off - self.ROOTINO_OFFSET
            block0 -= self.SMALLEST_BLOCK_SIZE
            distance = rootdir_off - block0
            for bo, bnos in rootino.possible_bnos():
                 ratio = distance / bnos[0]
                 if ratio < .75 * self.SMALLEST_BLOCK_SIZE:
                      continue
                 if ratio > 1.25 * self.LARGEST_BLOCK_SIZE:
                      continue
                 pow2 = math.log(ratio) / math.log(2)
                 skew = math.modf(pow2)
                 if skew[0] < .8:
                      continue
                 bsize = 1 << round(pow2)
                 sboff = (rootino_off - self.ROOTINO_OFFSET) - bsize
                 sblock = SuperBlockStable(self, sboff, short, long)
                 if max(bnos) > sblock.s_fsize.val:
                      continue

                 rootblks = (rootino.di_size.val + bsize - 1) // bsize
                 # All the necessary rootdir block# must be non-null
                 if min(bnos[:rootblks]) == 0:
                      continue
                 # And the rest must be null
                 if max(bnos[rootblks:]) > 0:
                      continue
                 yield rootino, bo, bsize, sblock, bnos

    def good_rootdir_inodes(self, rootino_off, inums, short, long):
        for inum in inums:
            ino = Inode64(self, rootino_off + (inum - 2) * 64, short, long)
            if not ino.credible():
                return False
        return True
