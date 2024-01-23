#!/usr/bin/env python3

'''
   Syslog
   ======
'''

from ...base import bitview as bv

from .defs import SECTBITS, AdaArray, SectorBitView, DoubleSectorBitView, LSECSHIFT, OBJECT_FIELDS

class LogEntry(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            f0_=-32,
            txt_=bv.Text(80),
        )

class LogSect(bv.Struct):
    def __init__(self, ovtree, lo):
        sect = DoubleSectorBitView(ovtree, lo, 'SL', 'Syslog').insert()
        super().__init__(
            sect.bv,
            0,
            vertical=False,
            **OBJECT_FIELDS,
            ls0_=-15,
            cnt_=-4,
            aa_=AdaArray,
            more=True,
        )
        self.add_field(
            "logsectrec",
            bv.Array(self.cnt.val, LogEntry, vertical=True)
        )
        self.done(SECTBITS)
        self.insert()

class SyslogRec(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            f0_=-32,
            lba_=-24
        )

class Syslog(bv.Struct):
    '''
    A Syslog sector
    ---------------

    '''

    def __init__(self, ovtree, lba):
        sect = DoubleSectorBitView(ovtree, lba, 'SL', "Syslog").insert()
        super().__init__(
            sect.bv,
            0,
            vertical=False,
            **OBJECT_FIELDS,
            sl0_=-19,
            cnt_=-8,
            aa_=AdaArray,
            more=True,
        )
        self.add_field(
            "syslogrecs",
            bv.Array(self.cnt.val, SyslogRec, vertical=True)
        )
        self.done(SECTBITS)
        self.insert()
        self.ovtree = ovtree

        for slr in self.syslogrecs:
            LogSect(ovtree, slr.lba.val)

class DfsLog(bv.Struct):
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
            sl0_=15,
            cnt_=-4,
            aa_=AdaArray,
            more=True,
        )
        self.add_field(
            "ary",
            bv.Array(self.cnt.val, LogEntry, vertical=False)
        )
        self.done(SECTBITS)
        self.insert()
        self.ovtree = ovtree

