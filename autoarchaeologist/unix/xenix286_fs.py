'''
   Xenix 286 UFS fileystem with cylinder groups
   --------------------------------------------
'''

import struct

import autoarchaeologist.unix.unix_fs as ufs

class SysVInode(ufs.Inode):
    ''' System V inode '''

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

class Xenix_FileSystem(ufs.UnixFileSystem):
    ''' System V Filesystem '''

    FS_TYPE = "SysV Filesystem"
    NICFREE = 50
    NICINOD = 100
    CHARSET = "ISO-8859-1"
    INODE_SIZE = 0x40

    BMAPSIZE = 994
    MAXCGS = 80

    CYLGRP_LAYOUT = (
        ("cg_doffset", "1L"),
        ("cg_ioffset", "1L"),
        ("cg_dblocks", "1H"),
        ("cg_ifirst", "1H"),
        ("cg_number", "1B"),
        ("cg_currextent", "1B"),
        ("cg_lowat", "1H"),
        ("cg_hiwat", "1H"),
        ("cg_erotor", "1H"),
        ("cg_ilock", "1B"),
        ("cg_reserved", "9B"),
        ("cg_bits", "%dB" % BMAPSIZE),
    )

    FILSYS_LAYOUT = (
        ("fs_fname", "6B",),		# file system name
        ("fs_fpack", "6B",),		# pack name
        ("fs_fsize", "1L",),		# number of data blocks in fs
        ("fs_cgblocks", "1H",),		# number of blocks per cg
        ("fs_maxblock", "1L",),		# max disk block in fs
        ("fs_cginodes", "1H",),		# number of inodes per cg
        ("fs_maxino", "1H",),		# max inumber in fs
        ("fs_time", "1L",),		# time last modified
        ("fs_fmod", "1B",),		# modified flag
        ("fs_ronly", "1B",),		# read-only fs
        ("fs_clean", "1B",),		# fs was cleanly unmounted
        ("fs_type", "1B",),		# fs type and version
        ("fs_fnewcg", "1H",),		# contains FNEWCG
        ("fs_snewcg", "1H",),		# contains SNEWCG
        ("fs_ffree", "1L",),		# number of free data blocks in fs
        ("fs_ifree", "1H",),		# number of free inodes in fs
        ("fs_dirs", "1H",),		# number of directories in fs
        ("fs_extentsize", "1B",),	# native extent size
        ("fs_cgnum", "1B",),		# number of cg's in fs
        ("fs_cgrotor", "1B",),		# next cg to be searched
        ("fs_reserved", "15B",),	# reserved.
    )

    CGINFO_LAYOUT = (
        ("fs_cgincore", "1H",),		# points to buf structure in core
        ("fs_cgblk", "1L",),		# disk address of cg header
        ("fs_cgffree", "1H",),		# number of free data blocks in cg
        ("fs_cgifree", "1H",),		# number of free inodes in cg
        ("fs_cgdirs", "1H",),		# number of directories in cg
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
        if not self.this.has_type("XENIX Partition"):
            return

        self.SECTOR_SIZE = 1024
        self.ENDIAN = "<"

        sblock = self.this.record(
            self.FILSYS_LAYOUT,
            endian=self.ENDIAN,
            name="filsys",
        )
        if max(sblock.fs_fname):
            return
        if max(sblock.fs_fpack):
            return
        if max(sblock.fs_reserved):
            return
        if not sblock.fs_maxino:
            return

        sblock.cylinders = []
        off = sblock._size
        for i in range(0, self.MAXCGS):
            cginfo = self.this.record(
                self.CGINFO_LAYOUT,
                offset=off,
                endian=self.ENDIAN,
                name="cginfo",
            )
            if not cginfo.fs_cgblk:
                break
            cylgrp = self.this.record(
                self.CYLGRP_LAYOUT,
                offset=(cginfo.fs_cgblk - 1) * self.SECTOR_SIZE,
                cgoffset=cginfo.fs_cgblk * self.SECTOR_SIZE,
                endian=self.ENDIAN,
                name="cylgrp",
            )
            sblock.cylinders.append(cylgrp)
            off += cginfo._size
        
        sblock.fs_nindir = self.SECTOR_SIZE // 4
        sblock.fs_imax = sblock.fs_maxino - 1
        self.sblock = sblock

    def get_inode(self, inum):
        ''' Return an Inode '''
        cgn = inum // self.sblock.fs_cginodes
        irem = inum % self.sblock.fs_cginodes
        inoa = self.sblock.cylinders[cgn].cgoffset
        inoa += (irem - 1) * self.INODE_SIZE
        if inoa > len(self.this) - 64:
            return None
        return self.this.record(
            self.INODE_LAYOUT,
            offset=inoa,
            endian=self.ENDIAN,
            use_type=SysVInode,
            ufs=self,
            name="sysv",
            di_inum=inum,
        )

    def get_block(self, blockno):
        ''' Return a block '''
        offset = (blockno-1) * self.SECTOR_SIZE
        return self.this[offset:offset + self.SECTOR_SIZE]
