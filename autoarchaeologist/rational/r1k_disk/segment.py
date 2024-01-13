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

    def check(self, ovtree):
        if self.lba.val == 0:
            return
        bits = ovtree.this.bits(self.lba.val << 13, 128)
        pat = bin((1<<24)|self.lba.val)[3:]
        if bits.find(pat) == 70:
            self.is_valid = "+"
        else:
            print("B %06x" % self.lba.val, bits[:70], bits[70:], pat, bits.find(pat))
            self.is_valid = "-"

    def render(self):
        if self.flg.val or self.e0.val or self.lba.val:
            yield "E" + self.is_valid + "{%x:%x:%x}" % (self.flg.val, self.e0.val, self.lba.val)
        else:
            yield "Ø"

class Indir(bv.Struct):
                
    def __init__(self, ovtree, lba):
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
            print("HH", hex(self.id_lba.val), hex(lba))
            self.status = '#'
            return
        assert self.id_lba.val == lba
        if self.f2.val != 0x8144:
            self.add_field("fill", 1024)
            self.status = '%'
            return
        self.add_field("aa", AdaArray)
        self.add_field("ary", bv.Array(162, Extent))
        self.done(SECTBITS)
        self.insert()
        while self.ary.array:
            if self.ary.array[-1].flg.val != 0:
                break
            self.ary.array.pop(-1)
        self.status = '*'
        if self.multiplier.val > 1:
            for ext in self.ary:
                if ext.lba.val == 0:
                    continue
                i = ovtree.what.get(ext.lba.val)
                if i:
                    #print("Already", hex(ext.lba.val), ovtree.what[ext.lba.val])
                    ext.is_valid = i.status
                    continue
                i = Indir(ovtree, ext.lba.val);
                ext.is_valid = i.status
                ovtree.what[ext.lba.val] = i

class Segment(bv.Struct):
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
        if self.lo + 915 != self.hi:
            print("H", self.hi - self.lo)
        self.done(915)
        while self.ary.array:
            if self.ary.array[-1].flg.val != 0:
                break
            self.ary.array.pop(-1)

    def check(self, ovtree):
        if self.multiplier.val == 1:
            return
        for ext in self.ary.array:
            ext.check(ovtree)

    def traverse(self, ovtree):
        if self.multiplier.val == 1:
            return
        for ext in self.ary.array:
            if ext.lba.val == 0:
                continue
            if ext.lba.val in ovtree.what:
                continue
            if ext.is_valid != '+':
                continue
            i = Indir(ovtree, ext.lba.val);
            ext.is_valid = i.status
            ovtree.what[ext.lba.val] = i


