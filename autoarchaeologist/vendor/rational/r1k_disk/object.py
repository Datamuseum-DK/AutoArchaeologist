#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Objects on disk
   ===============
'''

from ....base import bitview as bv

from .defs import SectorBitView, DoubleSectorBitView

class BadObject(Exception):
    ''' ... '''

class ObjHead(bv.Struct):
    '''
    Sector header for object
    '''
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            flag_=-1,
            obj1_=bv.Constant(6, 0x0),
            boot_=-16,  # [[Bits:30003857]] pg 134: Boot_Number
            obj3_=bv.Constant(10, 0x0),
            usq_=-32,   # [[Bits:30003857]] pg 134: Unique_Sequence_Number
            vol_=-5,
            lba_=-24,
        )

    def render(self):
        yield "{OBJ %x:%x:%x:%02x:%06x}" % (
            self.flag.val,
            self.boot.val,
            self.usq.val,
            self.vol.val,
            self.lba.val
        )

class ObjSector(bv.Struct):
    '''
    A sector with an object, possibly duplicated
    '''

    def __init__(
        self,
        ovtree,
        lba,
        what="??",
        legend="??",
        duplicated=False,
        **kwargs
    ):
        if duplicated:
            self.sect = DoubleSectorBitView(ovtree, lba, what, legend)
        else:
            self.sect = SectorBitView(ovtree, lba, what, legend)
        self.sect.insert()
        super().__init__(
            self.sect.bv,
            0,
            obj_=ObjHead,
            **kwargs,
        )
        if self.obj.vol.val != ovtree.volnbr:
            raise BadObject(
                "Bad Object: volnbr is 0x%x should be 0x%x" % (self.obj.vol.val, ovtree.volnbr))
        if self.obj.lba.val != lba:
            raise BadObject(
                "Bad Object: lba is 0x%x should be 0x%x" % (self.obj.lba.val, lba))

    def done(self):
        super().done(len(self.sect) << 3)
