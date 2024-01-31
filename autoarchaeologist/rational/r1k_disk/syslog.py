#!/usr/bin/env python3

'''
   Syslog
   ======
'''

from ...base import bitview as bv

from .defs import AdaArray, ELIDE_SYSLOG
from .object import ObjSector

class LogEntry(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            f0_=-32,
            txt_=bv.Text(80),
        )

class LogSect(ObjSector):
    def __init__(self, ovtree, lba):
        super().__init__(
            ovtree,
            lba,
            duplicated=True,
            what="SL",
            legend="Syslog",
            vertical=True,
            ls0_=-15,
            cnt_=-4,
            aa_=AdaArray,
            more=True,
        )
        self.add_field(
            "logsectrec",
            bv.Array(self.cnt.val, LogEntry, vertical=True)
        )
        self.done()
        self.insert()

    def render(self):
        if ELIDE_SYSLOG:
            yield self.bt_name + "(LogSect elided)"
        else:
            yield from super().render()

class SyslogRec(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            f0_=-32,
            lba_=-24
        )

class Syslog(ObjSector):
    '''
    A Syslog sector
    ---------------
    '''

    def __init__(self, ovtree, lba):
        super().__init__(
            ovtree,
            lba,
            duplicated=True,
            what="SL",
            legend="Syslog",
            vertical=True,
            sl0_=-19,
            cnt_=-8,
            aa_=AdaArray,
            more=True,
        )
        self.add_field(
            "syslogrecs",
            bv.Array(self.cnt.val, SyslogRec, vertical=True)
        )
        self.done()
        self.insert()

        for slr in self.syslogrecs:
            LogSect(ovtree, slr.lba.val)

    def render(self):
        if ELIDE_SYSLOG:
            yield self.bt_name + "(Syslog elided)"
        else:
            yield from super().render()
