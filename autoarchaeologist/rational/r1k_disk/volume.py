#/usr/bin/env python3

'''
   Rational R1000/s400 diskimages
   ==============================
'''

from ...generic import disk
from ...base import octetview as ov
from ...base import bitview as bv

from .defs import DoubleSectorBitView, LSECSHIFT, OBJECT_FIELDS, AdaArray, SECTBITS
from .superblock import SuperBlock
from .system import add_volume
from .world import WorldIndex
from .syslog import Syslog, DfsLog


class Etwas1331(bv.Struct):
    '''
    Unknown
    ---------------

    '''

    def __init__(self, ovtree, lba):
        sect = DoubleSectorBitView(ovtree, lba, 'XX', "Unknown").insert()
        super().__init__(
            sect.bv,
            0,
            vertical=False,
            **OBJECT_FIELDS,
            sl0_=-16,
            cnt_=-5,
            aa_=AdaArray,
            more=True,
        )
        self.add_field(
            "ary",
            bv.Array(self.cnt.val, 0x17f, vertical=False)
        )
        self.done(SECTBITS)
        self.insert()
        self.ovtree = ovtree

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
            if self.sblk.at13ab.lba.val:
                DfsLog(self, self.sblk.at13ab.lba.val)

        if True:
            if self.sblk.at1331.lba.val:
                Etwas1331(self, self.sblk.at1331.lba.val)

        if True:
            if self.sblk.syslog.lba.val:
                Syslog(self, self.sblk.syslog.lba.val)

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

