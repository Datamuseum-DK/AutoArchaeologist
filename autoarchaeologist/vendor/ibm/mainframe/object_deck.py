#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Punched card text
   =================
'''

from ....base import octetview as ov


class ESDsymb(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            f01_=ov.Text(8),
            f08_=ov.Text(1),
            f09_=ov.Text(3),
            f12_=ov.Text(1),
            f13_=ov.Text(3),
        )

class EsdRec(ov.Struct):
    ''' https://www.ibm.com/docs/en/zos/2.1.0?topic=output-esd-record-format '''

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            f01_=1,
            esd_=ov.Text(3),
            spc1_=ov.Text(6),
            cnt_=ov.Text(2),
            spc2_=ov.Text(2),
            esdid_=2,
            symb_=ov.Array(3, ESDsymb, vertical=True),
            f65_=ov.Text(8),
            f73_=ov.Text(8),
            vertical=True,
            more=True,
        )
        self.done(-80)
        assert len(self) == 80

class TxtBody(ov.Dump):

    def __init__(self, tree, lo):
        super().__init__(tree, lo, hi=lo + 56)

class TxtRec(ov.Struct):
    ''' https://www.ibm.com/docs/en/zos/2.1.0?topic=output-txt-record-format '''

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            f01_=1,
            esd_=ov.Text(3),
            f05_=ov.Text(1),
            f06_=ov.Text(3),
            f09_=ov.Text(2),
            f11_=ov.Text(2),
            f13_=ov.Text(2),
            f15_=2,
            f17_=TxtBody,
            f73_=ov.Text(8),
            vertical=True,
            more=True,
        )
        self.done(-80)
        assert len(self) == 80

class RldEntry(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            f01_=2,
            f03_=2,
            f05_=1,
            f16_=3,
        )


class RldRec(ov.Struct):
    ''' https://www.ibm.com/docs/en/zos/2.1.0?topic=output-rld-record-format '''

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            f01_=1,
            esd_=ov.Text(3),
            f05_=ov.Text(6),
            f11_=ov.Text(2),
            f13_=ov.Text(4),
            f17_=ov.Array(7, RldEntry, vertical=True),
            f73_=ov.Text(8),
            vertical=True,
            more=True,
        )
        self.done(-80)
        assert len(self) == 80

class EndRec(ov.Struct):
    ''' https://www.ibm.com/docs/en/zos/2.1.0?topic=output-end-record-format '''

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            f01_=1,
            esd_=ov.Text(3),
            f05_=ov.Text(1),
            f06_=ov.Text(3),
            f09_=ov.Text(6),
            f15_=ov.Text(2),
            f17_=ov.Text(8),
            f25_=ov.Text(4),
            f29_=4,
            f33_=ov.Text(1),
            f34_=ov.Text(19),
            f53_=ov.Text(19),
            f72_=ov.Text(1),
            f73_=ov.Text(8),
            vertical=True,
            more=True,
        )
        self.done(-80)
        assert len(self) == 80

class ObjectDeck(ov.OctetView):

    def __init__(self, this):
        if this[0] != 0x02:
            return

        super().__init__(this)
        for ptr in range(0, len(this), 80):
            t = this.type_case.decode(this[ptr+1:ptr+4])
            if t == "ESD":
                EsdRec(self, ptr).insert()
            elif t == "TXT":
                TxtRec(self, ptr).insert()
            elif t == "RLD":
                RldRec(self, ptr).insert()
            elif t == "END":
                EndRec(self, ptr).insert()
            else:
                print(t)
                ov.Octets(self, ptr, hi=ptr+80).insert()

        self.add_interpretation("Object Deck")
