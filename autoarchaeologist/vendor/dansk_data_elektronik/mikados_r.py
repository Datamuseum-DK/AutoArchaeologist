#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   DDE SPC/1 Mikados "R" files
   ===========================

'''

from ...base import octetview as ov

class Unknown(ov.Struct):
    ''' ... '''

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            l1_=ov.Octet,
            t_=ov.Octet,
            more=True,
        )
        if self.l1.val + 1 - len(self) > 0:
            self.add_field("pad", self.l1.val + 1 - len(self))
        self.add_field("l2", ov.Octet)
        self.done()

class Title(ov.Struct):
    ''' ... '''
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            l1_=ov.Octet,
            t_=ov.Octet,
            name_=ov.Text(8),
            more=True,
        )
        if self.l1.val + 1 - len(self) > 0:
            self.add_field("pad", self.l1.val + 1 - len(self))
        self.add_field("l2", ov.Octet)
        self.done()

class Import(Title):
    ''' ... '''

class Export(Title):
    ''' ... '''

class Abs(Unknown):
    ''' ... '''

class Reloc(Unknown):
    ''' ... '''

class Extern(Unknown):
    ''' ... '''

class End(Unknown):
    ''' ... '''

class EOF(Unknown):
    ''' ... '''

RECTYP = {
    0x02: Title,
    0x04: Export,
    0x05: Import,
    0x08: Abs,
    0x09: End,
    0x0a: Reloc,
    0x0b: Extern,
    0x0f: EOF,
}

class MikadosR(ov.OctetView):
    ''' ... '''

    def __init__(self, this):
        if not this.has_note("Mikados_R"):
            return

        super().__init__(this)

        adr = 0
        while adr < len(this) and this[adr]:
            r = RECTYP.get(this[adr+1], Unknown)
            try:
                y = r(self, adr).insert()
            except Exception as err:
                this.add_note("BOGON")
                print(this, "ERR", hex(adr), r, err)
                break
            adr = y.hi
            if isinstance(y, EOF):
                break
        if adr + 4 < len(this):
            ov.Opaque(self, lo=adr + 4, hi=len(this)).insert()

        self.add_interpretation(more=False)
