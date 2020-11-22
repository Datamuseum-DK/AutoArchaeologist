'''
   System V UFS filesystems
'''

import autoarchaeologist.unix.unix_fs as ufs

class SysVInode(ufs.Inode):
    ''' System V inode '''

    def __init__(self, ufs, **kwargs):
        super().__init__(ufs, **kwargs)
        self.fix_di_addr()

    def fix_di_addr(self):
        ''' convert .di_addr[] to .di_db[] and di.ib[] '''
        raw = self.di_addr
        tmp = []
        if self.ufs.ENDIAN == "<":
            for i in range(0, len(raw) - 3, 3):
                tmp.append((raw[i + 2] << 16) | (raw[i + 1] << 8) | raw[i + 0])
        else:
            for i in range(0, len(raw) - 3, 3):
                tmp.append((raw[i + 0] << 16) | (raw[i + 1] << 8) | raw[i + 2])

        self.di_db = tmp[:-3]
        self.di_ib = tmp[-3:]

class SysVFileSystem(ufs.UnixFileSystem):
    ''' System V Filesystem '''

    FS_TYPE = "SysV Filesystem"
    NICFREE = 50
    NICINOD = 100
    CHARSET = "ISO-8859-1"
    INODE_SIZE = 0x40

    SBLOCK_LAYOUT = (
        ("s_isize", "1H"),
        ("s_fsize", "1L"),
        ("s_nfree", "1H"),
        ("s_nfree", "%dL" % NICFREE),
        ("s_ninode", "1H"),
        ("s_inode", "%dH" % NICINOD),
        ("s_flock", "1B"),
        ("s_ilock", "1B"),
        ("s_fmod", "1B"),
        ("s_ronly", "1B"),
        ("s_time", "1L"),
        ("s_dinfo", "4H"),
        ("s_tfree", "1L"),
        ("s_tinode", "1H"),
        ("s_fname", "6B"),
        ("s_fpack", "6B"),
        ("s_start", "1H"),
        ("s_lowfree", "1H"),
        ("s_ctime", "1L"),
        ("s_fill", "12L"),
        ("s_state", "1L"),
        ("s_magic", "1L"),
        ("s_type", "1L"),
    )

    INODE_LAYOUT = (
        ("di_mode", "1H"),
        ("di_nlink", "1H"),
        ("di_uid", "1H"),
        ("di_gid", "1H"),
        ("di_size", "1L"),
        ("di_addr", "40B"),
        ("di_atime", "1L"),
        ("di_mtime", "1L"),
        ("di_ctime", "1L"),
    )

    MAGIC = {
        bytes.fromhex("fd187e20"): ">",
        bytes.fromhex("207e18fd"): "<",
    }

    def get_superblock(self):
        ''' Read the superblock '''
        i = self.this[0x3f8:0x3fc].tobytes()
        self.ENDIAN = self.MAGIC.get(i)
        if not self.ENDIAN:
            return
        print("?SysVFIleSystem", self.this,  i.hex())

        sblock = ufs.Struct(
            name="sblock",
            **self.read_struct(
                self.SBLOCK_LAYOUT,
                0x200,
            )
        )
        if sblock.s_type == 3:
            self.SECTOR_SIZE = 2048
            self.FS_TYPE = "UNIX UFS 2K Filesystem"
        elif sblock.s_type == 2:
            self.SECTOR_SIZE = 1024
            self.FS_TYPE = "UNIX UFS 1K Filesystem"
        elif sblock.s_type == 1:
            self.SECTOR_SIZE = 512
            self.FS_TYPE = "UNIX UFS 512B Filesystem"

        sblock.fs_nindir = self.SECTOR_SIZE // 4
        sblock.fs_imax = (sblock.s_isize - 2) * self.SECTOR_SIZE
        sblock.fs_imax //= self.INODE_SIZE
        self.sblock = sblock

    def get_inode(self, inum):
        ''' Return an Inode '''
        inoa = 2 * self.SECTOR_SIZE
        inoa += (inum - 1) * self.INODE_SIZE
        return SysVInode(
            self,
            name="sysv",
            di_inum=inum,
            **self.read_struct(self.INODE_LAYOUT, inoa)
        )

    def get_block(self, blockno):
        ''' Return a block '''
        offset = blockno * self.SECTOR_SIZE
        return self.this[offset:offset + self.SECTOR_SIZE]
