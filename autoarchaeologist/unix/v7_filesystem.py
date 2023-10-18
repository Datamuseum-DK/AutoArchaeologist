'''
   UNIX v7 style filesystem
   ------------------------

   Quite, but probably not sufficiently configurable by subclassing.

'''

import struct

from . import unix_fs as ufs

class V7_Inode(ufs.Inode):
    '''
       UNIX V7 style inodes.

       32 bit quantities stored as two 16 bit words in BE order, even
       if the words themselves are LE order.
    '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fix_di_addr()

    def fix_di_addr(self):
        ''' convert .di_addr[] to .di_db[] and di.ib[] '''
        raw = self.di_addr
        tmp = []
        for i in range(1, len(raw), 3):
            tmp.append((raw[i + 2] << 16) | (raw[i + 1] << 8) | raw[i])

        self.di_ib = tmp[-3:]
        self.di_db = tmp[:-3]

    def indir_get(self, blk, idx):
        ''' word-swizzle blockno's from indirect blocks '''
        blk = blk[idx * 4:(idx + 1) * 4]
        if len(blk) != 4:
            return None
        words = struct.unpack(self.ufs.ENDIAN + "HH", blk)
        return self.ufs.get_block((words[0] << 16) | words[1])

class V7_Filesystem(ufs.UnixFileSystem):
    ''' The default parameters match V7/PDP '''

    FS_TYPE = "UNIX V7 Filesystem"

    ENDIAN = "<"
    NICFREE = 50
    NICINOD = 100
    DISK_OFFSET = 0x0
    SECTOR_SIZE = 0x200
    SUPERBLOCK_OFFSET = SECTOR_SIZE
    INODE_SIZE = 0x40
    NINDIR = SECTOR_SIZE // 4

    SBLOCK_LAYOUT = (
        ("s_isize", "1H"),
        ("s_fsize", "1X"),
        ("s_free", "%dX" % NICFREE),
        ("s_inode", "1H"),
        ("s_inode", "%dH" % NICINOD),
        ("s_flock", "1B"),
        ("s_ilock", "1B"),
        ("s_fmod", "1B"),
        ("s_ronly", "1B"),
    )

    INODE_LAYOUT = (
        ("di_mode", "1H"),
        ("di_nlink", "1H"),
        ("di_uid", "1H"),
        ("di_gid", "1H"),
        ("di_size", "1X"),
        ("di_addr", "40B"),
        ("di_atime", "1X"),
        ("di_mtime", "1X"),
        ("di_ctime", "1X"),
    )

    def get_superblock(self):
        ''' Read the superblock '''
        sblock = self.this.record(
            self.SBLOCK_LAYOUT,
            endian=self.ENDIAN,
            offset=self.DISK_OFFSET + self.SUPERBLOCK_OFFSET,
            name="sblock",
        )
        if not sblock:
            return
        if not sblock.s_isize or not sblock.s_fsize:
            return
        if sblock.s_isize > sblock.s_fsize:
            return
        if sblock.s_fsize * self.SECTOR_SIZE > len(self.this):
            return
        sblock.fs_nindir = self.NINDIR
        sblock.fs_imax = (sblock.s_isize - 2) * self.SECTOR_SIZE
        sblock.fs_imax //= self.INODE_SIZE
        sblock.fs_bmax = sblock.s_fsize
        self.sblock = sblock

    def get_inode(self, inum):
        ''' Return an inode '''
        inoa = self.DISK_OFFSET
        inoa += 2 * self.SECTOR_SIZE
        inoa += (inum - 1) * self.INODE_SIZE
        return self.this.record(
            self.INODE_LAYOUT,
            offset=inoa,
            endian=self.ENDIAN,
            use_type=V7_Inode,
            ufs=self,
            name="v7",
            di_inum=inum,
        )

    def get_block(self, blockno):
        ''' Return a block '''
        offset = blockno + self.DISK_OFFSET
        offset *= self.SECTOR_SIZE
        return self.this[offset:offset + self.SECTOR_SIZE]
