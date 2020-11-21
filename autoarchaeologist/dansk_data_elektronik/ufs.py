
import autoarchaeologist.unix.v7_filesystem as v7fs

class DDE_UFS(v7fs.Unix_Filesystem):

    def __init__(self, this):

        if this[0x3f8:0x3fc] != b'\xfd\x18\x7e\x20':
            return

        print("?DDE_2K_UFS", this,  this[0x3f8:0x3fc])

        super().__init__(this)

        self.ENDIAN = ">"
        self.NICFREE = 50
        self.NICINOD = 100
        self.CHARSET = "ISO-8859-1"

        self.sblock_layout = (
            ("s_isize", "1H"),
            ("s_fsize", "1L"),
            ("s_nfree", "1H"),
            ("s_nfree", "%dL" % self.NICFREE),
            ("s_ninode", "1H"),
            ("s_inode", "%dH" % self.NICINOD),
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

        self.inode_layout = (
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

        self.sblock = self.read_superblock()
        if self.sblock.s_type == 3:
            self.SECTOR_SIZE = 2048
            self.fs_type = "UNIX UFS 2K Filesystem"
        elif self.sblock.s_type == 2:
            self.SECTOR_SIZE = 1024
            self.fs_type = "UNIX UFS 1K Filesystem"
        elif self.sblock.s_type == 1:
            self.SECTOR_SIZE = 512
        else:
            print("DDE_UFS invalid s_type", self.sblock)
            return

        self.INODE_OFFSET = self.DISK_OFFSET + 2 * self.SECTOR_SIZE

        self.discover()
        this.add_type("DDE_2K_UFS")

    def fix_di_addr(self, raw):
        ''' convert Dinode.di_addr to block numbers '''
        retval = []
        for i in range(0, len(raw) - 3, 3):
            retval.append((raw[i + 0] << 16) | (raw[i + 1] << 8) | raw[i + 2])
        return retval
