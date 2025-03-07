#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   The disk superblock and related data structures
   ===============================================
'''

from ....base import bitview as bv

from .defs import SECTBITS, DoubleSectorBitView, DiskAddress
from .freelist import FreeList
from .badsect import BadSectorTable, ReplacementSectorTable

class Partition(bv.Struct):
    '''
    First and last sector specified in C/H/S 512B format
    ----------------------------------------------------
    '''

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            vertical=False,
            first_=DiskAddress,
            last_=DiskAddress
        )

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

class VolRec(bv.Struct):
    '''
    '''
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            vertical=False,
            flg_=-10,
            volid_=-49,
            f0_=-32,
        )

class SuperBlock(bv.Struct):
    '''
    The SuperBlock of the disk, shared between DFS and RFS
    ------------------------------------------------------

    '''

    def __init__(self, ovtree, lo):
        sect = DoubleSectorBitView(ovtree, lo, 'SB', 'SuperBlock').insert()
        super().__init__(
            sect.bv,
            0,
            vertical=True,
            magic_=-32,				# 0x00007fed
            at0020_const_=32,			# 0x00030000
            geometry_=DiskAddress,
            part_=bv.Array(5, Partition, vertical=True),
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
            volid_=-49,
            voltable_=bv.Array(32, VolRec, vertical=True),
            worlds_=DiskPointer,
            at1331_=DiskPointer,		#stage6_ptr
            at1349_=-5,
            syslog_=DiskPointer,
            logsects_=DiskPointer,
            at1408_=-8,
            snapshot1_=-24,
            boot_number_=-16,			# See [[Bits:30003857]] pg 134
            at1438_=-20,
            snapshot2_=-24,
            at1464_=-273,
            thisvolid_=-49,
            bootvolid_=-49,
            sbmagic_=-31,
            more=True,
        )
        self.done(SECTBITS * 2)

    def do_badsect(self, ovtree):
        i, j = self.partition_span(0)
        for lba in range(i, j + 1, 2):
            BadSectorTable(ovtree, lba).insert()

    def do_replacesect(self, ovtree):
        i, j = self.partition_span(1)
        for lba in range(i, j + 1, 2):
            ReplacementSectorTable(ovtree, lba).insert()

    def partition_span(self, partno):
        part = self.part.array[partno]
        return (
            self.diskaddress_to_lba(part.first),
            self.diskaddress_to_lba(part.last),
        )

    def diskaddress_to_lba(self, da):
        ''' Convert a 512b CHS to 1k LBA '''
        lba = da.cyl.val
        lba *= self.geometry.hd.val
        lba += da.hd.val
        lba *= self.geometry.sect.val
        lba += da.sect.val
        return lba >> 1
