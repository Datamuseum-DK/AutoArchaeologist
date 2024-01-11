#/usr/bin/env python3

'''
   Rational R1000/s400 diskimages
   ==============================
'''

from ..generic import disk
from ..base import octetview as ov

from .r1k_disk_defs import DoubleSectorBitView, LSECSHIFT
#from .r1k_disk_freelist import *
from .r1k_disk_superblock import SuperBlock

class R1KDisk(disk.Disk):
    '''
    A Single R1K Disk image
    -----------------------
    '''

    def __init__(self, this):

        if not this.top in this.parents:
            return

        super().__init__(
            this,
            geometry=[[1655, 15, 45, 1024]],
        )

        sbsect = DoubleSectorBitView(self, 2, 'SB', 'SuperBlock').insert()
        self.sblk = SuperBlock(sbsect.bv, 0).insert()

        self.sblk.freelist.commit(self)

        # Paint the unallocated sectors
        self.picture_legend['FR'] = "Free in BitMap"
        for lba in range(self.sblk.part3_lba_first.val, self.sblk.part3_lba_last.val + 1):
            if self.sblk.freelist.get_bit(lba) == '0':
                self.set_picture('FR', lo=lba << LSECSHIFT)

        for i, j in self.gaps():
            ov.Hidden(self, lo=i, hi=j).insert()

        this.add_interpretation(self, self.disk_picture, more=True)
        self.add_interpretation(title="Disk View", more=True)
