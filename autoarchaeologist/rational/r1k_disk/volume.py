#/usr/bin/env python3

'''
   Rational R1000/s400 diskimages
   ==============================
'''

from ...generic import disk
from ...base import octetview as ov

from .defs import DoubleSectorBitView, LSECSHIFT
from .superblock import SuperBlock
from .system import add_volume
from .world import WorldIndex

class Volume(disk.Disk):
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

        self.sblk = SuperBlock(self, 2).insert()

        if False:
            self.completed()
            return

        if True:
            self.sblk.freelist.commit(self)

            # Paint the unallocated sectors
            self.picture_legend['FR'] = "Free in BitMap"
            for lba in range(
                self.sblk.part3_lba_first.val,
                self.sblk.part3_lba_last.val + 1
            ):
                if self.sblk.freelist.get_bit(lba) == '0':
                    self.set_picture('FR', lo=lba << LSECSHIFT)

        if True:
            self.worldindex = None
            if self.sblk.worlds.lba.val:
                self.worldindex = WorldIndex(self, self.sblk.worlds.lba.val)

        if True:
            self.sblk.do_badsect(self)
            self.sblk.do_replacesect(self)

        self.what = {}
        add_volume(self)

    def completed(self):
        ''' Call-back from system once it is done '''

        for i, j in self.gaps():
            ov.Hidden(self, lo=i, hi=j).insert()

        self.this.add_interpretation(self, self.disk_picture, more=True)
        self.add_interpretation(title="Disk View", more=True)

