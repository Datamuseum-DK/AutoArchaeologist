#!/usr/bin/env python3

'''
   Worlds and trees thereof
   ========================
'''

from .defs import AdaArray, ELIDE_INDIR
from .object import ObjSector, BadObject
from ...base import bitview as bv

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
            f0_=-32,
            f1_=-32,
            f2_=-32,
            multiplier_=-30,
            more=True,
        )
        if self.f0.val != 0x01000000:
            raise BadIndir("Indir wrong f0 (0x%x)" % self.f0.val)
        if self.f1.val != 0:
            raise BadIndir("Indir wrong f1 (0x%x)" % self.f1.val)
        if self.f2.val != 0x8144:
            raise BadIndir("Indir wrong f2 (0x%x)" % self.f2.val)
        self.add_field("aa", AdaArray)
        self.add_field("ary", bv.Array(162, Extent))
        self.done()
        while self.ary.array:
            if self.ary.array[-1].flg.val != 0:
                break
            self.ary.array.pop(-1)

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
            lib_=-10,
            col4_=-24,
            snapshot_=-31,
            other2a_=-8,
            col9_=-9,
            other3a__=-17,	# 0x00200
            vol_=-4,
            other3c_=-13,
            bootno_=-10,
            col5b__=-10,	# 0x000
            col5d_=-32,
            other5_=-22,
            npg_=-31,
            other6__=-14,	# 0x2005
            multiplier_=-32,
            aa_=AdaArray,
            ary_=bv.Array(10, Extent, vertical=False),
            mgr_=-8,
            mobj_=-32,
        )
        assert self.lo + 915 == self.hi
        self.bad = False

        assert self.col5b_.val == 0
        assert self.other3a_.val == 0x200
        assert self.other6_.val == 0x2005

        while self.ary.array:
            if self.ary.array[-1].flg.val != 0:
                break
            self.ary.array.pop(-1)

    def commit(self, ovtree):
        retval = []
        if self.other3c.val:
            return retval
        npg = 0
        lbas = []
        if self.multiplier.val == 1:
            for extent in self.ary.array:
                if extent.is_null():
                    lbas.append(None)
                else:
                    lbas.append(extent)
                    npg += 1
            if npg == self.npg.val:
                return []
        elif self.multiplier.val == 0xa2:
            indirs = []
            retval.append("  S " + str(self))
            for extent in self.ary.array:
                retval.append("  E " + str(extent))
                if extent.is_null():
                    lbas += [None] * self.multiplier.val
                    continue
                try:
                    indir = Indir1(ovtree, extent.lba.val)
                except BadObject as err:
                    retval.append("   " + str(err))
                    self.bad = True
                    return retval
                except BadIndir as err:
                    retval.append("   LBA is not Indir1 " + hex(extent.lba.val) + " " + str(err))
                    self.bad = True
                    return retval
                indirs.append(indir)
                retval.append("    I " + str(indir))
                lbas += list(indir.expand())
            if (len(lbas) - lbas.count(None)) == self.npg.val:
                retval = []
                for indir in indirs:
                    indir.insert()
        elif self.multiplier.val == 0xa2 * 0xa2:
            indirs = []
            retval.append("  S " + str(self))
            for extent2 in self.ary.array:
                retval.append("  E " + str(extent2))
                if extent2.is_null():
                    lbas += [None] * self.multiplier.val
                    continue
                try:
                    indir2 = Indir2(ovtree, extent2.lba.val)
                except BadObject as err:
                    retval.append("   " + str(err))
                    self.bad = True
                    return retval
                except BadIndir as err:
                    retval.append("   LBA is not Indir2 " + hex(extent2.lba.val) + " " + str(err))
                    self.bad = True
                    return retval
                indirs.append(indir2)
                retval.append("    I2 " + str(indir2))
                for extent1 in indir2.expand():
                    if extent1 is None:
                        lbas += [None] * 0xa2
                        continue
                    try:
                        indir1 = Indir1(ovtree, extent1.lba.val)
                    except BadObject as err:
                        retval.append("   " + str(err))
                        self.bad = True
                        return retval
                    except BadIndir as err:
                        retval.append("      LBA is not Indir2-1 " +  hex(extent1.lba.val) + " " + str(err))
                        self.bad = True
                        return retval
                    indirs.append(indir1)
                    retval.append("      I1 " + str(indir1))
                    lbas += list(x for x in indir1.expand())
            if (len(lbas) - lbas.count(None)) == self.npg.val:
                retval = []
                for indir in indirs:
                    indir.insert()
        if retval:
            self.bad = True
        return retval

    def render(self):
        if not self.bad:
            yield from super().render()
        else:
            for i in super().render():
                yield i + " BAD"
