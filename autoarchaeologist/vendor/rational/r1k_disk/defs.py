#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

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

from ....base import bitview as bv
from ....base import namespace as ns

ELIDE_FREELIST = True
ELIDE_BADLIST = True
ELIDE_SYSLOG = True
ELIDE_INDIR = True

LSECSHIFT = 10
LSECSIZE = 1 << LSECSHIFT
SECTSHIFT = LSECSHIFT + 3
SECTBITS = 1 << SECTSHIFT

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


class SectorBitView(bv.OvBits):
    '''
       A bitview of a single sector
    '''

    def __init__(self, tree, lba, picture, legend):
        lo = lba << LSECSHIFT
        tree.picture_legend[picture] = legend
        tree.set_picture(picture, lo=lo)
        super().__init__(tree, lo, width = LSECSIZE)

class DoubleSectorBitView(bv.OvBits):
    '''
       A bitview of a doubled sector
    '''

    def __init__(self, tree, lba, picture, legend):
        lo = lba << LSECSHIFT
        sec0 = tree.this[lo : lo + LSECSIZE]
        sec1 = tree.this[lo + LSECSIZE : lo + LSECSIZE * 2]
        if sec0 != sec1:
            print("Double Fault lba=", hex(lba), picture, legend)
            print("  ", sec0.hex())
            print("  ", sec1.hex())
        tree.picture_legend[picture] = legend
        tree.set_picture(picture, lo=lo)
        tree.set_picture(picture, lo=lo + LSECSIZE)
        super().__init__(tree, lo, width = LSECSIZE * 2)

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
        if self.a1.val != 0x40 or self.a3.val != 1:
            print("BAD AA", hex(self.a1.val), hex(self.a3.val))
        assert self.a1.val == 0x40
        assert self.a3.val == 0x1

    def render(self):
        yield "0x%x*0x%x" % ((self.a2.val - 0x40) // self.a4.val, self.a4.val)

class NameSpace(ns.NameSpace):
    ''' ... '''

    TABLE = (
        ("r", "snapshot"),
        ("r", "other2a"),
        ("r", "col9"),
        ("r", "vol"),
        ("r", "other3c"),
        ("r", "bootno"),
        ("r", "col5d"),
        ("r", "version"),
        ("r", "npg"),
        ("r", "mgr"),
        ("r", "mobj"),
        ("l", "name"),
        ("l", "artifact"),
    )

    def ns_render(self):
        seg = self.ns_priv
        return [
            hex(seg.snapshot.val),
            hex(seg.other2a.val),
            hex(seg.col9.val),
            hex(seg.vol.val),
            hex(seg.other3c.val),
            hex(seg.bootno.val),
            hex(seg.col5d.val),
            hex(seg.version.val),
            hex(seg.npg.val),
            hex(seg.mgr.val),
            hex(seg.mobj.val),
        ] + super().ns_render()

