#!/usr/bin/env python3

'''
   Global definitions for the disk layout
   ======================================

   There are clues about the overall layout in the documentatin
   for the RECOVERY.M200 program, which can be found at:

       [[Bits:30000972|Rational 1000, Command Interfaces]] (pdf page 51)

   or in RECOVERY.HLP in the DFS filesystem:

       https:/datamuseum.dk/aa/r1k_dfs/34/344289524.html

   Also very detailed information starting pdf page 20 of:

   [[Bits:30003857|Epsilon - Principles of Operation Vol II - Ada specs (APIs) - April 24, 1986]]

   but it is not entirely clear how precisely that matches the running system.

'''

from ...generic import disk
from ...base import bitview as bv

LSECSHIFT = 10
LSECSIZE = 1 << LSECSHIFT
SECTSHIFT = LSECSHIFT + 3
SECTBITS = 1 << SECTSHIFT

OBJECT_FIELDS = {
    "id_kind_": -23,
    "id_word_": -42,
    "id_vol_": -5,
    "id_lba_": -24,
}

ELIDE_FREELIST = True
ELIDE_BADLIST = False

class DiskAddress(bv.Struct):
    '''
    A C/H/S 512B disk-address in the superblock
    -------------------------------------------
    '''

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            flg_=-1,
            cyl_=-15,
            hd_=-8,
            sect_=-8
        )

    def chs(self):
        return (self.cyl.val, self.hd.val, self.sect.val)

    def render(self):
        yield "0x%x(%d/%d/%d)" % (self.flg.val, self.cyl.val, self.hd.val, self.sect.val)


class Doubled(disk.Sector):
    ''' Much of the metadata is redundantly stored in two sectors '''

    def render(self):
        yield "Doubled"

def double_sector(obj, tree, lba, picture):
    '''
       Claim & color two sectors, check they are identical
    '''
    lo = lba << LSECSHIFT
    sec0 = tree.this[lo : lo + LSECSIZE]
    sec1 = tree.this[lo + LSECSIZE : lo + LSECSIZE * 2]
    if sec0 != sec1:
        print("Double Fault", hex(lo), type(obj))
        print("  ", sec0.hex())
        print("  ", sec1.hex())
    y = Doubled(tree, lo = lo + LSECSIZE).insert()
    y.picture(picture)
    tree.set_picture(picture, lo=lo)

class SectorBitView(bv.OvBits):
    '''
       A bitview of a single sector
    '''

    def __init__(self, tree, lba, picture, legend):
        tree.picture_legend[picture] = legend
        tree.set_picture(picture, lo=lba << LSECSHIFT)
        super().__init__(
            tree,
            lba << LSECSHIFT,
            width = LSECSIZE,
        )

class DoubleSectorBitView(bv.OvBits):
    '''
       A bitview of a doubled sector
    '''

    def __init__(self, tree, lba, picture, legend):
        tree.picture_legend[picture] = legend
        double_sector(self, tree, lba, picture)
        super().__init__(
            tree,
            lba << LSECSHIFT,
            width = LSECSIZE,
        )

class AdaArray(bv.Struct):
    ''' ... '''
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            vertical=False,
            a1_=-32,
            a2_=-32,
            a3_=-32,
            a4_=-32,
        )
        assert self.a1.val == 0x40
        assert self.a3.val == 0x1

    def render(self):
        yield "0x%x*0x%x" % ((self.a2.val - 0x40) // self.a4.val, self.a4.val)

     
