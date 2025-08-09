#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Worlds and trees thereof
   ========================
'''

from ....base import bitview as bv

from .defs import AdaArray, ELIDE_INDIR, LSECSHIFT, LSECSIZE, SegNameSpace
from .object import ObjSector
from . import user_data

UNREAD = memoryview(b'_UNREAD_' * (LSECSIZE // 8))

class UserData(bv.Bits):
    ''' USER_DATA field '''
    def __init__(self, tree, lo):
        super().__init__(tree, lo, width=9)
        self.val = int(self.bits(), 2)

    def render(self):
        yield "%03x(%s)" % (self.val, user_data.user_data_to_string(self.val))

class Family(bv.Struct):
    ''' ... '''
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            up_=-10,
            proc_=-10,
            seq_=-32,
        )

class Extent(bv.Struct):
    ''' ... '''
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            flg_=-2,
            e0_=-22,
            lba_=-24,
        )
        self.is_valid = ""

    def is_null(self):
        return self.flg.val == 0 and self.e0.val == 0 and self.lba.val == 0

    def render(self):
        if self.is_null():
            yield "Ø"
        else:
            yield "E" + self.is_valid + "{%x:%x:%06x}" % (self.flg.val, self.e0.val, self.lba.val)

class BadIndir(Exception):
    ''' This is not the indir you are looking for '''

class Indir(ObjSector):

    def __init__(self, ovtree, lba):
        super().__init__(
            ovtree,
            lba,
            what="IN",
            legend="Indirect",
            vertical=False,
            f0__=-32,
            f1__=-32,
            f2__=-32,
            multiplier_=-30,
            more=True,
        )
        if self.f0_.val != 0x01000000:
            raise BadIndir("Indir wrong f0_ (0x%x)" % self.f0_.val)
        if self.f1_.val != 0:
            raise BadIndir("Indir wrong f1_ (0x%x)" % self.f1_.val)
        if self.f2_.val != 0x8144:
            raise BadIndir("Indir wrong f2_ (0x%x)" % self.f2_.val)
        self.add_field("aa", AdaArray)
        self.add_field("ary", bv.Array(162, Extent))
        self.done()

    def expand(self):
        for extent in self.ary.array:
            if extent.is_null():
                yield None
            else:
                yield extent

    def render(self):
        if ELIDE_INDIR:
            yield self.__class__.__name__ + "(Indir elided)"
        else:
            yield from super().render()

class Indir1(Indir):
    ''' first level indirect '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.multiplier.val != 1:
            raise BadIndir("Indir1 multiplier not 1")

class Indir2(Indir):
    ''' second level indirect '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.multiplier.val != 0xa2:
            raise BadIndir("Indir2 multiplier not 0xa2")

class Segment():
    ''' A Segment '''

    def __init__(self, vpid, kind, id, version, this):
        self.vpid = vpid
        self.kind =  kind
        self.id =  id
        self.version = version
        self.this = this
        self.name = "%03x:%x:%06x" % (vpid, kind, id)
        this.add_note('R1k_Segment')
        this.add_name(self.name)

    def __repr__(self):
        return "<Segment " + self.name + "(0x%x)>" % self.version

class SegmentDesc(bv.Struct):
    '''
       other3c: (hypothesis)  Some kind of open/active/live
          0x0000 in all snapshots <= superblock.snapshot2
          0x0000 or 0x1000 in snapshots > superblock.snapshot2
    '''
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            vertical=False,
            vpid_=-10,
            kind_=-2,
            segid_=-22,
            snapshot_=-31,
            other2a_=-8,  # 0x02 probably "DELETED"
            user_data_=UserData,
            other3a__=bv.Constant(17, 0x200),
            vol_=-4,
            other3c_=-13,
            #bootno_=-10,
            #col5b__=bv.Constant(10, 0x0),
            #col5d_=-32,
            family_=Family,
            generation_=-22,
            npg_=-31,
            other6__=bv.Constant(14, 0x2005),
            multiplier_=-32,
            aa_=AdaArray,
            ary_=bv.Array(10, Extent, vertical=False),
            mgr_=-8,
            mobj_=-32,
        )
        assert self.lo + 915 == self.hi
        self.namespace = None

        while self.ary.array:
            if self.ary.array[-1].flg.val != 0:
                break
            self.ary.array.pop(-1)

    def commit(self, r1ksys, ovtree):
        if self.other3c.val:
            return
        npg = 0
        extents = []
        if self.multiplier.val == 1:
            for extent in self.ary.array:
                if extent.is_null():
                    extents.append(None)
                else:
                    extents.append(extent)
                    npg += 1
        elif self.multiplier.val == 0xa2:
            for extent in self.ary.array:
                if extent.is_null():
                    extents += [None] * self.multiplier.val
                else:
                    indir = Indir1(ovtree, extent.lba.val).insert()
                    extents += list(indir.expand())
        elif self.multiplier.val == 0xa2 * 0xa2:
            for extent2 in self.ary.array:
                if extent2.is_null():
                    extents += [None] * self.multiplier.val
                else:
                    indir2 = Indir2(ovtree, extent2.lba.val).insert()
                    for extent1 in indir2.expand():
                        if extent1 is None:
                            extents += [None] * 0xa2
                        else:
                            indir1 = Indir1(ovtree, extent1.lba.val).insert()
                            extents += list(x for x in indir1.expand())
        else:
            raise BadIndir("Wrong multiplier")

        if (len(extents) - extents.count(None)) != self.npg.val:
            raise BadIndir("Wrong npg")
        bits = []
        #print("O", self)
        while extents and extents[-1] is None:
            extents.pop(-1)
        if not extents:
            return
        for extent in extents:
            if extent is not None:
                lo = extent.lba.val << LSECSHIFT
                ovtree.set_picture('D', lo=lo, legend="Data")
                bits.append(ovtree.this[lo:lo+LSECSIZE])
            else:
                bits.append(UNREAD)
            #print("E", bits[-1])
        that = ovtree.this.create(records=bits)
        that.add_note("vpid_%04d" % self.vpid.val)
        that.add_note("tag_%03x" % self.user_data.val)
        seg = Segment(self.vpid.val, self.kind.val, self.segid.val, self.generation.val, that)
        r1ksys.add_segment(seg)
        
        self.namespace = SegNameSpace(
            parent = ovtree.namespace,
            name = seg.name + "(0x%x)" % self.generation.val,
            priv = self,
            this = that,
        )


    def doc(self, that):
        with that.add_utf8_interpretation("Segment") as file:
             self.vertical=True
             for i in self.render():
                 file.write(i + "\n")
             self.vertical=False
