#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Xenix 286 UFS fileystem with cylinder groups
   ============================================
'''

from . import unix_fs as ufs
from ...base import octetview as ov

class FilSys(ov.Struct):

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            fs_fname_=ov.Text(6),	# file system name
            fs_fpack_=ov.Text(6),	# pack name
            fs_fsize_=ov.Le32,		# number of data blocks in fs
            fs_cgblocks_=ov.Le16,	# number of blocks per cg
            fs_maxblock_=ov.Le32,	# max disk block in fs
            fs_cginodes_=ov.Le16,	# number of inodes per cg
            fs_maxino_=ov.Le16,		# max inumber in fs
            fs_time_=ov.Le32,		# time last modified
            fs_fmod_=ov.Octet,		# modified flag
            fs_ronly_=ov.Octet,		# read-only fs
            fs_clean_=ov.Octet,		# fs was cleanly unmounted
            fs_type_=ov.Octet,		# fs type and version
            fs_fnewcg_=ov.Le16,		# contains FNEWCG
            fs_snewcg_=ov.Le16,		# contains SNEWCG
            fs_ffree_=ov.Le32,		# number of free data blocks in fs
            fs_ifree_=ov.Le16,		# number of free inodes in fs
            fs_dirs_=ov.Le16,		# number of directories in fs
            fs_extentsize_=ov.Octet,	# native extent size
            fs_cgnum_=ov.Octet,		# number of cg's in fs
            fs_cgrotor_=ov.Octet,	# next cg to be searched
            vertical=True,
            more = True,
        )
        if not self.fs_fmod.val & 0x80:
            self.add_field("fs_reserved", 15)
        self.done()
        self.credible = False
        if max(self.fs_fname):
            return
        if max(self.fs_fpack):
            return
        if not self.fs_fsize.val:
            return
        if not self.fs_cgblocks.val:
            return
        if not self.fs_cginodes.val:
            return
        if not self.fs_maxblock.val:
            return
        if not self.fs_maxino.val:
            return
        if self.fs_time.val == self.fs_maxblock.val:
            return
        #if self.fs_maxino.val % self.fs_cginodes.val:
        #    return
        self.credible = True

class CgInfo(ov.Struct):

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            fs_cgincore_=ov.Le16,	# points to buf structure in core
            fs_cgblk_=ov.Le32,		# disk address of cg header
            fs_cgffree_=ov.Le16,	# number of free data blocks in cg
            fs_cgifree_=ov.Le16,	# number of free inodes in cg
            fs_cgdirs_=ov.Le16,		# number of directories in cg
        )

class CylGrp(ov.Struct):

    def __init__(self, tree, lo, bmapsize):
        super().__init__(
            tree,
            lo,
            cg_doffset_=ov.Le32,
            cg_ioffset_=ov.Le32,
            cg_dblocks_=ov.Le16,
            cg_ifirst_=ov.Le16,
            cg_number_=ov.Octet,
            cg_currextent_=ov.Octet,
            cg_lowat_=ov.Le16,
            cg_hiwat_=ov.Le16,
            cg_erotor_=ov.Le16,
            cg_ilock_=ov.Octet,
            cg_reserved_=9,
            cg_bits_=bmapsize,
            vertical=True,
        )


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

    LOWEST_INODE = 1

    FS_TYPE = "SysV Filesystem"
    NICFREE = 50
    NICINOD = 100
    CHARSET = "ISO-8859-1"
    INODE_SIZE = 0x40

    BMAPSIZE = 994
    MAXCGS = 80

    MAGIC = {
        bytes.fromhex("fd187e20"): ">",
        bytes.fromhex("207e18fd"): "<",
    }

    nindir = 1024 // 4

    def __init__(self, this):
        if not this.has_type("XENIX Partition"):
            return
        self.good = False
        self.rootdir = False
        super().__init__(this)
        print(this, "XFS?", self.good)
        if not self.good:
            self.add_interpretation()
            return
        print(this, "XFSRD", self.rootdir)
        if self.rootdir:
            super().commit()
        self.add_interpretation()

    def get_superblock(self):
        ''' Read the superblock '''
        if not self.this.has_type("XENIX Partition"):
            return

        self.SECTOR_SIZE = 1024
        self.ENDIAN = "<"

        sblock = FilSys(self, 0).insert()
        print(self.this, "XFS", "\n".join(sblock.render()))
        if not sblock.credible:
            return

        print(self.this, "XFSa")

        if sblock.fs_fmod.val:
            return

        ncg = sblock.fs_maxino.val // sblock.fs_cginodes.val
        if sblock.fs_maxino.val % sblock.fs_cginodes.val:
            ncg += 1
        cgs = ov.Array(
            sblock.fs_maxino.val // sblock.fs_cginodes.val,
            CgInfo,
            vertical=True,
        )(self, sblock.hi).insert()

        sblock.cylinders = []

        for cginfo in cgs:
            print(self.this, "CGI", "\n".join(cginfo.render()))
            if not cginfo.fs_cgblk.val:
                print(self.this, "BAD CGI")
                break
            cylgrp = CylGrp(self, (cginfo.fs_cgblk.val - 1) * self.SECTOR_SIZE, self.BMAPSIZE).insert()
            cylgrp.offset=(cginfo.fs_cgblk.val - 1) * self.SECTOR_SIZE
            cylgrp.cgoffset=cginfo.fs_cgblk.val * self.SECTOR_SIZE
            sblock.cylinders.append(cylgrp)

        if not sblock.cylinders:
            return

        sblock.fs_nindir = self.SECTOR_SIZE // 4
        sblock.fs_imax = sblock.fs_maxino.val - 1
        self.sblock = sblock

    def get_inode(self, inum):
        ''' Return an Inode '''
        cgn = inum // self.sblock.fs_cginodes.val
        irem = inum % self.sblock.fs_cginodes.val
        inoa = self.sblock.cylinders[cgn].cgoffset
        inoa += (irem - 1) * self.INODE_SIZE
        if inoa > len(self.this) - 64:
            return None
        retval = ufs.Inode64(self, inoa, ov.Le16, ov.Le32, (2, 1, 0)).insert()
        retval.di_inum = inum
        print(self.this, "XIN", hex(inum), retval, retval.di_inum, retval.di_db)
        return retval

    def get_block(self, blockno):
        ''' Return a block '''
        offset = (blockno-1) * self.SECTOR_SIZE
        if offset >= len(self.this) - self.SECTOR_SIZE:
            return None
        retval = ov.Opaque(self, lo=offset, width=self.SECTOR_SIZE)
        print(self.this, "XGB", hex(blockno), hex(offset))
        return retval

    def parse_directory(self, inode):
        ''' Parse classical unix directory: 16bit inode + 14 char name '''
        print(self.this, "XPD", inode, inode.di_db)
        for b in inode:
            b.insert()
            print(self.this, "XPDD", b, b.octets()[:32].hex())
            if b.octets()[:8] == b'_UNREAD_':
                continue
            yield from ufs.DirBlock(self, b.lo, b.hi, ov.Le16).insert()
