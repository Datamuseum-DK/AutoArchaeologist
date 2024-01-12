#!/usr/bin/env python3

'''
   The disk superblock and related data structures
   ===============================================
'''

from ...base import bitview as bv

from .defs import SECTBITS
from .freelist import FreeList

class DiskAddress(bv.Struct):
    '''
    A C/H/S 512B disk-address in the superblock
    -------------------------------------------
    '''

    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            flg_=-1,
            cyl_=-15,
            hd_=-8,
            sect_=-8
        )
        self.lba_ = None

    def lba(self):
        ''' return 1K Logical Block Address, (depending on which field in SB) '''
        if self.lba_ is None:
            if self == self.up.sb.geometry:
                self.lba_ = self.cyl * self.hd * self.sect // 2
            else:
                geom = self.up.sb.geometry
                self.lba_ = ((self.cyl * geom.hd + self.hd) * geom.sect + self.sect) // 2
        return self.lba_

class Partition(bv.Struct):
    '''
    First and last sector specified in C/H/S 512B format
    ----------------------------------------------------
    '''

    def __init__(self, up, lo):
        super().__init__(up, lo, vertical=False, first_=DiskAddress, last_=DiskAddress)

    def lba(self):
        ''' Return first+last LBA '''
        return (self.first.lba(), self.last.lba())

class DiskPointer(bv.Struct):
    '''
    Pointer to something on disk
    ----------------------------

    '''
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            f0_=-65,
            volume_=-4,
            lba_=-24,
        )

#################################################################################################

class SuperBlock(bv.Struct):
    '''
    The SuperBlock of the disk, shared between DFS and RFS
    ------------------------------------------------------

    '''

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            vertical=True,
            magic_=-32,				# 0x00007fed
            at0020_const_=32,			# 0x00030000
            geometry_=DiskAddress,
            part0_=Partition,
            part1_=Partition,
            part2_=Partition,
            part3_=Partition,
            part4_=Partition,
            at01a0_=-16,
            volserial_=bv.Text(10, rstrip=True),
            at0200_const_=128,			# 0
            at0280_const_=75,			# 0x0000000000a4c70f07c00000000000
            at0300_=DiskPointer,
            volname_=bv.Text(32, rstrip=True),
            volnbr_=-5,
            at042d_const_=10,			# 3
            part3_lba_first_=-24,
            part3_lba_last_=-24,
            freelist_=FreeList,
            at0573_=-23,
            at058a_=DiskPointer,
            at05e7_=DiskPointer,
            at0644_=DiskPointer,
            at06a1_=DiskPointer,
            at06fe_=-49,
            at072f_=bv.Array(32, -91, vertical=True),
            at128f_=-69,
            worldidx_=-24,
            at12ec_=-69,
            at1331_=-24,			#stage6_ptr
            at1349_=-74,
            syslog_=-24,
            at13ab_=-69,
            at13f0_=-24,
            at1408_=-8,
            snapshot1_=-24,
            reboots_=-16,
            at1438_=-20,
            snapshot2_=-24,
            at1464_=-149,
            at14f9_=-156,
            at1595_=-16,
            at15a5_=-48,
            sbmagic_=-32,
            more=True,
        )
        self.done(SECTBITS)
