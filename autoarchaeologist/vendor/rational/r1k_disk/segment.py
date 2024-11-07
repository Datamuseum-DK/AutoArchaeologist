#!/usr/bin/env python3

'''
   Worlds and trees thereof
   ========================
'''

from .defs import AdaArray, ELIDE_INDIR, LSECSHIFT, LSECSIZE, NameSpace
from .object import ObjSector, BadObject
from ...base import bitview as bv

UNREAD = memoryview(b'_UNREAD_' * (LSECSIZE // 8))

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
            yield self.bt_name + "(Indir elided)"
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

class SegmentDesc(bv.Struct):
    ''' ... '''
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            vertical=False,
            vpid_=-10,
            segno_=-24,
            snapshot_=-31,
            other2a_=-8,
            col9_=-9,
            other3a__=-17,	# 0x00200
            vol_=-4,
            other3c_=-13,
            bootno_=-10,
            col5b__=-10,	# 0x000
            col5d_=-32,
            version_=-22,
            npg_=-31,
            other6__=-14,	# 0x2005
            multiplier_=-32,
            aa_=AdaArray,
            ary_=bv.Array(10, Extent, vertical=False),
            mgr_=-8,
            mobj_=-32,
        )
        assert self.lo + 915 == self.hi
        self.namespace = None

        assert self.col5b_.val == 0
        assert self.other3a_.val == 0x200
        assert self.other6_.val == 0x2005

        while self.ary.array:
            if self.ary.array[-1].flg.val != 0:
                break
            self.ary.array.pop(-1)

    def commit(self, ovtree):
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
        #if self.vpid.val not in (1004, 1005, 1009,):
        #    return
        #if self.col9.val not in (0x7c, 0x7d, 0x81,):
        #    return
        for extent in extents:
            if extent is not None:
                lo = extent.lba.val << LSECSHIFT
                ovtree.set_picture('D', lo=lo, legend="Data")
                bits.append(ovtree.this[lo:lo+LSECSIZE])
            else:
                bits.append(UNREAD)
            #print("E", bits[-1])
        that = ovtree.this.create(records=bits)
        that.add_note('R1k_Segment')
        that.add_note("tag_%02x" % self.col9.val)
        that.add_note("vpid_%02x" % self.vpid.val)
        name = "%03x:%06x:%x" % (self.vpid.val, self.segno.val, self.version.val)
        self.namespace = NameSpace(
            parent = ovtree.namespace,
            name = name,
            priv = self,
            this = that,
        )
