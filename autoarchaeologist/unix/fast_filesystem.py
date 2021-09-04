'''
   Berkeley Fast File System
'''

import struct

import autoarchaeologist.unix.unix_fs as ufs

FFS_SUPERBLOCK = (
    ("fs_firstfield", "1L"),        # historic filesystem linked list,
    ("fs_unused_1", "1L"),          #     used for incore super blocks
    ("fs_sblkno", "1L"),            # offset of super-block in filesys
    ("fs_cblkno", "1L"),            # offset of cyl-block in filesys
    ("fs_iblkno", "1L"),            # offset of inode-blocks in filesys
    ("fs_dblkno", "1L"),            # offset of first data after cg
    ("fs_old_cgoffset", "1L"),      # cylinder group offset in cylinder
    ("fs_old_cgmask", "1L"),        # used to calc mod fs_ntrak
    ("fs_old_time", "1L"),          # last time written
    ("fs_old_size", "1L"),          # number of blocks in fs
    ("fs_old_dsize", "1L"),         # number of data blocks in fs
    ("fs_ncg", "1L"),               # number of cylinder groups
    ("fs_bsize", "1L"),             # size of basic blocks in fs
    ("fs_fsize", "1L"),             # size of frag blocks in fs
    ("fs_frag", "1L"),              # number of frags in a block in fs
    # these are configuration parameters
    ("fs_minfree", "1L"),           # minimum percentage of free blocks
    ("fs_old_rotdelay", "1L"),      # num of ms for optimal next block
    ("fs_old_rps", "1L"),           # disk revolutions per second
    # these fields can be computed from the others
    ("fs_bmask", "1L"),             # ``blkoff'' calc of blk offsets
    ("fs_fmask", "1L"),             # ``fragoff'' calc of frag offsets
    ("fs_bshift", "1L"),            # ``lblkno'' calc of logical blkno
    ("fs_fshift", "1L"),            # ``numfrags'' calc number of frags
    # these are configuration parameters
    ("fs_maxcontig", "1L"),         # max number of contiguous blks
    ("fs_maxbpg", "1L"),            # max number of blks per cyl group
    # these fields can be computed from the others
    ("fs_fragshift", "1L"),         # block to frag shift
    ("fs_fsbtodb", "1L"),           # fsbtodb and dbtofsb shift constant
    ("fs_sbsize", "1L"),            # actual size of super block
    ("fs_old_csmask", "1L"),        # old fs_csmask
    ("fs_old_csshift", "1L"),       # old fs_csshift
    ("fs_nindir", "1L"),            # value of NINDIR
    ("fs_inopb", "1L"),             # value of INOPB
    ("fs_old_nspf", "1L"),          # value of NSPF
    # yet another configuration parameter
    ("fs_optim", "1L"),             # optimization preference, see below
    ("fs_old_npsect", "1L"),        # # sectors/track including spares
    ("fs_old_interleave", "1L"),    # hardware sector interleave
    ("fs_old_trackskew", "1L"),     # sector 0 skew, per track
    ("fs_id", "1Q"),                # unique filesystem id
    # sizes determined by number of cylinder groups and their sizes
    ("fs_old_csaddr", "1L"),        # blk addr of cyl grp summary area
    ("fs_cssize", "1L"),            # size of cyl grp summary area
    ("fs_cgsize", "1L"),            # cylinder group size
    ("fs_spare2", "1L"),            # old fs_ntrak
    ("fs_old_nsect", "1L"),         # sectors per track
    ("fs_old_spc", "1L"),           # sectors per cylinder
    ("fs_old_ncyl", "1L"),          # cylinders in filesystem
    ("fs_old_cpg", "1L"),           # cylinders per group
    ("fs_ipg", "1L"),               # inodes per group
    ("fs_fpg", "1L"),               # blocks per group * fs_frag
    # this data must be re-computed after crashes
    ("fs_old_cstotal", "4L"),       # cylinder summary information

)
'''
/* these fields are cleared at mount time */
        int8_t   fs_fmod;               /* super block modified flag */
        int8_t   fs_clean;              /* filesystem is clean flag */
        int8_t   fs_ronly;              /* mounted read-only flag */
        int8_t   fs_old_flags;          /* old FS_ flags */
        u_char   fs_fsmnt[MAXMNTLEN];   /* name mounted on */
        u_char   fs_volname[MAXVOLLEN]; /* volume name */
        u_int64_t fs_swuid;             /* system-wide uid */
        int32_t  fs_pad;                /* due to alignment of fs_swuid */
/* these fields retain the current block allocation info */
        int32_t  fs_cgrotor;            /* last cg searched */
        void    *fs_ocsp[NOCSPTRS];     /* padding; was list of fs_cs buffers */
        struct   fs_summary_info *fs_si;/* In-core pointer to summary info */
        int32_t  fs_old_cpc;            /* cyl per cycle in postbl */
        int32_t  fs_maxbsize;           /* maximum blocking factor permitted */
        int64_t  fs_unrefs;             /* number of unreferenced inodes */
        int64_t  fs_providersize;       /* size of underlying GEOM provider */
'''

FFS_CYLINDERGROUP = (
    ("cg_firstfield", "1L"),        # historic cyl groups linked list
    ("cg_magic", "1L"),             # magic number
    ("cg_old_time", "1L"),          # time last written
    ("cg_cgx", "1L"),               # we are the cgx'th cylinder group
    ("cg_old_ncyl", "1H"),          # number of cyl's this cg
    ("cg_old_niblk", "1H"),         # number of inode blocks this cg
    ("cg_ndblk", "1L"),             # number of data blocks this cg
    ("cg_cs", "4L"),                # cylinder summary information
)
'''
        u_int32_t cg_rotor;             /* position of last used block */
        u_int32_t cg_frotor;            /* position of last used frag */
        u_int32_t cg_irotor;            /* position of last used inode */
        u_int32_t cg_frsum[MAXFRAG];    /* counts of available frags */
        int32_t  cg_old_btotoff;        /* (int32) block totals per cylinder */
        int32_t  cg_old_boff;           /* (u_int16) free block positions */
        u_int32_t cg_iusedoff;          /* (u_int8) used inode map */
        u_int32_t cg_freeoff;           /* (u_int8) free block map */
        u_int32_t cg_nextfreeoff;       /* (u_int8) next available space */
        u_int32_t cg_clustersumoff;     /* (u_int32) counts of avail clusters */
        u_int32_t cg_clusteroff;                /* (u_int8) free cluster map */
        u_int32_t cg_nclusterblks;      /* number of clusters this cg */
        u_int32_t cg_niblk;             /* number of inode blocks this cg */
        u_int32_t cg_initediblk;                /* last initialized inode */
        u_int32_t cg_unrefs;            /* number of unreferenced inodes */
        int32_t  cg_sparecon32[1];      /* reserved for future use */
        u_int32_t cg_ckhash;            /* check-hash of this cg */
        ufs_time_t cg_time;             /* time last written */
        int64_t  cg_sparecon64[3];      /* reserved for future use */
        u_int8_t cg_space[1];           /* space for cylinder group maps */
'''

UFS1_INODE = (
    ("di_mode", "1H",),             #   0: IFMT, permissions; see below.
    ("di_nlink", "1H",),            #   2: File link count.
    ("di_freelink", "1L",),         #   4: SUJ: Next unlinked inode.
    ("di_size", "1Q",),             #   8: File byte count.
    ("di_atime", "1L",),            #  16: Last access time.
    ("di_atimensec", "1L",),        #  20: Last access time.
    ("di_mtime", "1L",),            #  24: Last modified time.
    ("di_mtimensec", "1L",),        #  28: Last modified time.
    ("di_ctime", "1L",),            #  32: Last inode change time.
    ("di_ctimensec", "1L",),        #  36: Last inode change time.
    ("di_db", "12L",),              #  40: Direct disk blocks.
    ("di_ib", "3L",),               #  88: Indirect disk blocks.
    ("di_flags", "1L",),            #  100: Status flags (chflags).
    ("di_blocks", "1L",),           #  104: Blocks actually held.
    ("di_gen", "1L",),              #  108: Generation number.
    ("di_uid", "1L",),              #  112: File owner.
    ("di_gid", "1L",),              #  116: File group.
    ("di_modrev", "1Q",),           #  120: i_modrev for NFSv4
)

class Directory(ufs.Directory):
    ''' Variable length dirent records '''

    def parse(self):
        ''' Parse FFS style directories '''
        for b in self.inode:
            b = b.tobytes()
            while len(b) > 0:
                words = struct.unpack(self.ufs.ENDIAN + "LHBB", b[:8])
                n = b[8:8+words[3]].decode(self.ufs.CHARSET)
                b = b[words[1]:]
                yield words[0], n

class FFS(ufs.UnixFileSystem):
    ''' Berkeley Fast Filesystem '''

    FS_TYPE = "BSD FFS/UFS1 Filesystem"
    CHARSET = "iso8859-1"

    DIRECTORY = Directory

    INODE_SIZE = 0x80

    MAGICS = (
        0x11954,	# Kirks birthday
        0x95014,	# Seen on HP-UX (30002742)
    )

    def get_superblock(self):
        ''' Get SuperBlock '''
        for sb_off in (65536, 8192, 0, 262144):
            if self.try_sblock(sb_off):
                break
        if self.sblock:
            self.sblock.fs_imax = self.sblock.fs_ncg * self.sblock.fs_ipg
            self.sblock.fs_bmax = self.sblock.fs_ncg * self.sblock.fs_fpg
            self.cylgroup = [self.cgget(ncg) for ncg in range(self.sblock.fs_ncg)]

    def try_sblock(self, offset):
        ''' Try to read SuperBlock at this offset '''
        if offset + 0x560 > len(self.this):
            return False
        i = self.this[offset + 0x55c:offset + 0x560]
        magic_be = struct.unpack(">1L", i)[0]
        magic_le = struct.unpack("<1L", i)[0]
        if magic_be in self.MAGICS:
            self.ENDIAN = ">"
        elif magic_le == self.MAGICS:
            self.ENDIAN = "<"
        else:
            if 0x19540119 in (magic_be, magic_le):
                print("XXX: UFS2 unhandled")
            return False

        self.sblock = self.this.record(
            FFS_SUPERBLOCK,
            offset=offset,
            endian=self.ENDIAN,
        )
        return True

    def cgget(self, cgnum):
        ''' Get Cylinder Group '''
        offset = self.sblock.fs_cblkno
        offset += cgnum * self.sblock.fs_fpg
        offset += self.sblock.fs_old_cgoffset * (cgnum & ~self.sblock.fs_old_cgmask)
        offset <<= self.sblock.fs_fshift
        return self.this.record(
            FFS_CYLINDERGROUP,
            offset=offset,
            endian=self.ENDIAN,
        )

    def get_inode(self, inum):
        ''' Get Inode '''
        cgn = inum // self.sblock.fs_ipg
        irem = inum % self.sblock.fs_ipg
        if cgn >= len(self.cylgroup):
            print("NO CG", inum, cgn, self.sblock)
            return None
        offset = self.cylgroup[cgn]._offset
        offset += ((self.sblock.fs_iblkno - self.sblock.fs_cblkno) << self.sblock.fs_fshift)
        offset += self.INODE_SIZE * irem
        return self.this.record(
            UFS1_INODE,
            offset=offset,
            endian=self.ENDIAN,
            use_type=ufs.Inode,
            ufs=self,
            name="ufs1",
            di_inum=inum,
       )

    def get_block(self, bno):
        ''' Get Block (Fragment) '''
        offset = bno << self.sblock.fs_fshift
        return self.this[offset:offset+self.sblock.fs_bsize]
