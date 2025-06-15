#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Rational R1000/s400 diskimages
   ==============================
'''

from ....generic import disk
from ....base import octetview as ov

from .defs import LSECSHIFT, SegNameSpace
from .superblock import SuperBlock
from .system import add_volume
from .world import WorldIndex
from .syslog import Syslog
from .etwas import Etwas6a1, Etwas58a, Etwas5e7, Etwas644, Etwas1331

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
        self.volnbr = self.sblk.volnbr.val
        self.namespace = SegNameSpace(
            name="",
            separator="",
        )

        if True:
            if self.sblk.at1331.lba.val:
                Etwas1331(self, self.sblk.at1331.lba.val, duplicated=True).insert()

        if True:
            if self.sblk.syslog.lba.val:
                Syslog(self, self.sblk.syslog.lba.val)

        if True:
            if self.sblk.at058a.lba.val:
                Etwas58a(self, self.sblk.at058a.lba.val, duplicated=True, span=213).insert()
            if self.sblk.at05e7.lba.val:
                Etwas5e7(self, self.sblk.at05e7.lba.val, duplicated=True, span=213).insert()
            if self.sblk.at0644.lba.val:
                Etwas644(self, self.sblk.at0644.lba.val, duplicated=True, span=213).insert()
            if self.sblk.at06a1.lba.val:
                Etwas6a1(self, self.sblk.at06a1.lba.val).insert()

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
        self.r1ksys = add_volume(this.top, self)

    def completed(self):
        ''' Call-back from system once it is done '''

        for i, j in self.gaps():
            ov.Hidden(self, lo=i, hi=j).insert()

        self.this.add_interpretation(self, self.namespace.ns_html_plain)
        self.this.add_interpretation(self, self.disk_picture)
        self.add_interpretation(title="Disk View", more=True)
