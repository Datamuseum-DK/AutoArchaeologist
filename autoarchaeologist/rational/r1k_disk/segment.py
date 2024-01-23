#!/usr/bin/env python3

'''
   Worlds and trees thereof
   ========================
'''
    
from .defs import AdaArray, OBJECT_FIELDS, SectorBitView, SECTBITS, AdaArray
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
            yield "E" + self.is_valid + "{%x:%x:%x}" % (self.flg.val, self.e0.val, self.lba.val)

class BadIndir(Exception):
    ''' This is not the indir you are looking for '''

class Indir(bv.Struct):
                
    def __init__(self, ovtree, lba):
        id = ovtree.this.bits(lba << 13, 23)
        if int(id, 2) != 0x125:
            raise BadIndir("Indir id_kind not 0x125")
          
        sect = SectorBitView(ovtree, lba, 'IN', "Indirect").insert()
        super().__init__(
            sect.bv,
            0,
            vertical=False,
            **OBJECT_FIELDS,
            f0_=-32,
            f1_=-32,
            f2_=-32,
            multiplier_=-30,
            more=True,
        )
        if self.id_lba.val != lba:
            raise BadIndir("wrong id_lba")
        assert self.id_lba.val == lba
        assert self.f0.val == 0x01000000
        assert self.f1.val == 0
        assert self.f2.val == 0x8144
        self.add_field("aa", AdaArray)
        self.add_field("ary", bv.Array(162, Extent))
        self.done(SECTBITS)
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
            col5a_=-10,
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
            more=True,
        )

        assert self.col5b_.val == 0
        assert self.other3a_.val == 0x200
        assert self.other6_.val == 0x2005
        
        if self.lo + 915 != self.hi:
            print("H", self.hi - self.lo)
        self.done(915)
        while self.ary.array:
            if self.ary.array[-1].flg.val != 0:
                break
            self.ary.array.pop(-1)

    def commit(self, ovtree):
        retval = []
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
                except BadIndir as err:
                    retval.append("   LBA is not Indir1 " + hex(extent.lba.val) + " " + str(err))
                    return retval
                indirs.append(indir)
                retval.append("    I " + str(indir))
                lbas += [x for x in indir.expand()]
            if (len(lbas) - lbas.count(None)) == self.npg.val:
                retval = []
                for indir in indirs:
                    indir.insert()
            return retval
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
                except BadIndir as err:
                    retval.append("   LBA is not Indir2 " + hex(extent2.lba.val) + " " + str(err))
                    return retval
                indirs.append(indir2)
                retval.append("    I2 " + str(indir2))
                for extent1 in indir2.expand():
                    if extent1 is None:
                        lbas += [None] * 0xa2
                        continue
                    try:
                        indir1 = Indir1(ovtree, extent1.lba.val)
                    except BadIndir as err:
                        retval.append("      LBA is not Indir2-1 " +  hex(extent1.lba.val) + " " + str(err))
                        return retval
                    indirs.append(indir1)
                    retval.append("      I1 " + str(indir1))
                    lbas += [x for x in indir1.expand()]
            if (len(lbas) - lbas.count(None)) == self.npg.val:
                retval = []
                for indir in indirs:
                    indir.insert()
            return retval

        print("  S", self)
        for extent in self.ary.array:
            print("    E", extent)
        return []
